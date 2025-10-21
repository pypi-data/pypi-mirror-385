"""Sync OpenAI client implementation"""

import os
import openai
from jiter import from_json
from typing import Literal, List, Iterator
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from jetflow.core.action import BaseAction
from jetflow.core.message import Message, Action, Thought, WebSearch
from jetflow.core.events import MessageStart, MessageEnd, ContentDelta, ThoughtStart, ThoughtDelta, ThoughtEnd, ActionStart, ActionDelta, ActionEnd, StreamEvent
from jetflow.clients.base import BaseClient


class OpenAIClient(BaseClient):
    provider: str = "OpenAI"
    supports_thinking: List[str] = ['gpt-5', 'o1', 'o3', 'o4']

    def __init__(
        self,
        model: str = "gpt-5",
        api_key: str = None,
        temperature: float = 1.0,
        reasoning_effort: Literal['minimal', 'low', 'medium', 'high'] = 'medium',
        tier: str = "tier-3"
    ):
        self.model = model
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.tier = tier

        self.client = openai.OpenAI(
            base_url="https://api.openai.com/v1",
            api_key=api_key or os.environ.get('OPENAI_API_KEY'),
            timeout=300.0,
        )

    def _supports_thinking(self) -> bool:
        """Check if the model supports extended thinking"""
        return any(self.model.startswith(prefix) for prefix in self.supports_thinking)

    def _c(self, text: str, color: str) -> str:
        """Color text for terminal output"""
        colors = {
            'yellow': '\033[93m',
            'dim': '\033[2m',
            'reset': '\033[0m'
        }
        return f"{colors.get(color, '')}{text}{colors['reset']}"

    def stream(
        self,
        messages: List[Message],
        system_prompt: str,
        actions: List[BaseAction],
        allowed_actions: List[BaseAction] = None,
        enable_web_search: bool = False,
        verbose: bool = True
    ) -> List[Message]:
        """Stream a completion with the given messages. Returns list of Messages (multiple if web searches occur)."""
        items = [item for message in messages for item in message.openai_format()]

        params = {
            "model": self.model,
            "instructions": system_prompt,
            "input": items,
            "tools": [action.openai_schema for action in actions],
            "stream": True
        }

        # Only include reasoning for gpt-5 and o- models
        if self.model.startswith("gpt-5") or self.model.startswith("o-"):
            params["reasoning"] = {"effort": self.reasoning_effort, "summary": "auto"}

        if enable_web_search:
            params['tools'].append({"type": "web_search"})

        if allowed_actions and len(allowed_actions) == 1:
            params['tool_choice'] = {"type": "function", "name": allowed_actions[0].name}

        elif allowed_actions and len(allowed_actions) > 1:
            params['tool_choice'] = {
                "type": "allowed_tools",
                "mode": "auto",
                "tools": [
                    {"type": "function", "name": action.name}
                    for action in allowed_actions
                ]
            }

        return self._stream_with_retry(params, verbose)

    def stream_events(
        self,
        messages: List[Message],
        system_prompt: str,
        actions: List[BaseAction],
        allowed_actions: List[BaseAction] = None,
        enable_web_search: bool = False,
        verbose: bool = True
    ) -> Iterator[StreamEvent]:
        """Stream a completion and yield events in real-time"""
        items = [item for message in messages for item in message.openai_format()]

        params = {
            "model": self.model,
            "instructions": system_prompt,
            "input": items,
            "tools": [action.openai_schema for action in actions],
            "stream": True
        }

        # Only include reasoning for gpt-5 and o- models
        if self.model.startswith("gpt-5") or self.model.startswith("o-"):
            params["reasoning"] = {"effort": self.reasoning_effort, "summary": "auto"}

        if enable_web_search:
            params['tools'].append({"type": "web_search"})

        if allowed_actions and len(allowed_actions) == 1:
            params['tool_choice'] = {"type": "function", "name": allowed_actions[0].name}

        elif allowed_actions and len(allowed_actions) > 1:
            params['tool_choice'] = {
                "type": "allowed_tools",
                "mode": "auto",
                "tools": [
                    {"type": "function", "name": action.name}
                    for action in allowed_actions
                ]
            }

        yield from self._stream_events_with_retry(params, verbose)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=10.0),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.BadRequestError,
            openai.APIConnectionError,
            openai.RateLimitError
        )),
        reraise=True
    )
    def _stream_events_with_retry(self, params: dict, verbose: bool) -> Iterator[StreamEvent]:
        """Create and consume a streaming response with retries, yielding events"""
        stream = self.client.responses.create(**params)
        yield from self._stream_completion_events(stream, verbose)

    def _stream_completion_events(self, response, verbose: bool) -> Iterator[StreamEvent]:
        """Stream a chat completion and yield events"""
        completion = Message(
            role="assistant",
            status="in_progress",
            content="",
            thoughts=[],
            actions=[]
        )
        tool_call_arguments = ""
        current_web_search = None  # Track active web search

        # Yield message start
        yield MessageStart(role="assistant")

        for event in response:

            if event.type == 'response.created':
                pass

            elif event.type == 'response.in_progress':
                pass

            elif event.type == 'response.output_item.added':

                if event.item.type == 'reasoning':
                    thought = Thought(id=event.item.id, summaries=[])
                    completion.thoughts.append(thought)
                    # Yield thought start event
                    yield ThoughtStart(id=thought.id)

                elif event.item.type == 'function_call':
                    tool_call_arguments = ""
                    action = Action(
                        id=event.item.call_id,
                        name=event.item.name,
                        status="streaming",
                        body={},
                        external_id=event.item.id
                    )
                    completion.actions.append(action)
                    # Yield action start event
                    yield ActionStart(id=action.id, name=action.name)

                elif event.item.type == 'message':
                    completion.external_id = event.item.id
                    if verbose:
                        print("", flush=True)  # Add separator before response

                elif event.item.type == 'web_search_call':
                    # Create new web search message
                    current_web_search = Message(
                        role="assistant",
                        status="completed",
                        web_search=WebSearch(id=event.item.id, query="")
                    )

            elif event.type == 'response.reasoning_summary_part.added':
                completion.thoughts[-1].summaries.append("")

            elif event.type == 'response.reasoning_summary_text.delta':
                completion.thoughts[-1].summaries[-1] += event.delta
                # Yield thought delta event
                yield ThoughtDelta(
                    id=completion.thoughts[-1].id,
                    delta=event.delta
                )

            elif event.type == 'response.reasoning_summary_text.done':
                completion.thoughts[-1].summaries[-1] = event.text
                # Yield thought end event
                yield ThoughtEnd(
                    id=completion.thoughts[-1].id,
                    thought=event.text
                )

            elif event.type == 'response.reasoning_summary_part.done':
                completion.thoughts[-1].summaries[-1] = event.part.text

            elif event.type == 'response.function_call_arguments.delta':
                tool_call_arguments += event.delta
                try:
                    body_json = from_json(
                        (tool_call_arguments.strip() or "{}").encode(),
                        partial_mode="trailing-strings"
                    )

                    if type(body_json) is not dict:
                        continue

                    completion.actions[-1].body = body_json
                    # Yield action delta event
                    yield ActionDelta(
                        id=completion.actions[-1].id,
                        name=completion.actions[-1].name,
                        body=body_json
                    )

                except ValueError:
                    continue

            elif event.type == 'response.function_call_arguments.done':
                completion.actions[-1].status = 'parsed'
                # Yield action end event
                yield ActionEnd(
                    id=completion.actions[-1].id,
                    name=completion.actions[-1].name,
                    body=completion.actions[-1].body
                )

            elif event.type == 'response.output_text.delta':
                completion.content += event.delta
                # Yield content delta event
                yield ContentDelta(delta=event.delta)

            elif event.type == 'response.output_text.done':
                # Add spacing after content finishes streaming
                if verbose and completion.content:
                    print("\n\n", sep="", end="")

            elif event.type == 'response.content_part.done':
                pass

            elif event.type == 'response.output_item.done':

                if event.item.type == 'web_search_call':
                    # Populate web search message with query and results
                    current_web_search.web_search.query = event.item.action.query
                    # TODO: Extract results from event.item.action.sources if available
                    # Yield separate MessageEnd for this web search
                    yield MessageEnd(message=current_web_search)
                    current_web_search = None

            elif event.type == 'response.completed':
                usage = event.response.usage

                completion.uncached_prompt_tokens = (
                    usage.input_tokens - usage.input_tokens_details.cached_tokens
                )
                completion.cached_prompt_tokens = usage.input_tokens_details.cached_tokens
                completion.thinking_tokens = usage.output_tokens_details.reasoning_tokens
                completion.completion_tokens = usage.output_tokens - completion.thinking_tokens

        completion.status = 'completed'

        # Yield message end event
        yield MessageEnd(message=completion)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=10.0),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.BadRequestError,
            openai.APIConnectionError,
            openai.RateLimitError
        )),
        reraise=True
    )
    def _stream_with_retry(self, params: dict, verbose: bool) -> List[Message]:
        """Create and consume a streaming response with retries"""
        stream = self.client.responses.create(**params)
        return self._stream_completion(stream, verbose)

    def _stream_completion(self, response, verbose: bool) -> List[Message]:
        """Stream a chat completion and return list of Messages (main message + web searches)"""
        completion = Message(
            role="assistant",
            status="in_progress",
            content="",
            thoughts=[],
            actions=[]
        )
        tool_call_arguments = ""
        messages = []  # Collect all messages (web searches interleaved)

        for event in response:

            if event.type == 'response.created':
                pass

            elif event.type == 'response.in_progress':
                pass

            elif event.type == 'response.output_item.added':

                if event.item.type == 'reasoning':
                    completion.thoughts.append(
                        Thought(id=event.item.id, summaries=[])
                    )
                    if verbose:
                        print(self._c("Thinking: ", "yellow") + "\n\n", sep="", end="")

                elif event.item.type == 'function_call':
                    tool_call_arguments = ""
                    action = Action(
                        id=event.item.call_id,
                        name=event.item.name,
                        status="streaming",
                        body={},
                        external_id=event.item.id
                    )
                    completion.actions.append(action)

                elif event.item.type == 'message':
                    completion.external_id = event.item.id
                    if verbose:
                        print("", flush=True)  # Add separator before response

                elif event.item.type == 'web_search_call':
                    # Create separate web search message
                    web_search_msg = Message(
                        role="assistant",
                        status="completed",
                        web_search=WebSearch(id=event.item.id, query="")
                    )
                    messages.append(web_search_msg)
                    if verbose:
                        print("Searching Web: ", sep="", end="")

            elif event.type == 'response.reasoning_summary_part.added':
                completion.thoughts[-1].summaries.append("")
                if verbose:
                    print("- ", sep="", end="")

            elif event.type == 'response.reasoning_summary_text.delta':
                completion.thoughts[-1].summaries[-1] += event.delta
                if verbose:
                    print(event.delta, sep="", end="")

            elif event.type == 'response.reasoning_summary_text.done':
                completion.thoughts[-1].summaries[-1] = event.text
                if verbose:
                    print("\n\n")

            elif event.type == 'response.reasoning_summary_part.done':
                completion.thoughts[-1].summaries[-1] = event.part.text

            elif event.type == 'response.function_call_arguments.delta':
                tool_call_arguments += event.delta
                try:
                    body_json = from_json(
                        (tool_call_arguments.strip() or "{}").encode(),
                        partial_mode="trailing-strings"
                    )

                    if type(body_json) is not dict:
                        continue

                    completion.actions[-1].body = body_json

                except ValueError:
                    continue

            elif event.type == 'response.function_call_arguments.done':
                completion.actions[-1].status = 'parsed'

            elif event.type == 'response.output_text.delta':
                # Print header on first content delta
                if verbose and completion.content == "":
                    print(self._c('Assistant:', 'cyan') + "\n\n", sep="", end="")

                completion.content += event.delta
                if verbose:
                    print(event.delta, sep="", end="")

            elif event.type == 'response.output_text.done':
                # Add spacing after content finishes streaming
                if verbose and completion.content:
                    print("\n\n", sep="", end="")

            elif event.type == 'response.content_part.done':
                pass

            elif event.type == 'response.output_item.done':

                if event.item.type == 'web_search_call':
                    # Populate web search message with query (find the most recent web search message)
                    for msg in reversed(messages):
                        if msg.web_search and not msg.web_search.query:
                            msg.web_search.query = event.item.action.query
                            # TODO: Extract results from event.item.action.sources if available
                            break
                    if verbose:
                        print(f"{event.item.action.query}\n\n")

            elif event.type == 'response.completed':
                usage = event.response.usage

                completion.uncached_prompt_tokens = (
                    usage.input_tokens - usage.input_tokens_details.cached_tokens
                )
                completion.cached_prompt_tokens = usage.input_tokens_details.cached_tokens
                completion.thinking_tokens = usage.output_tokens_details.reasoning_tokens
                completion.completion_tokens = usage.output_tokens - completion.thinking_tokens

        completion.status = 'completed'

        # If no web searches, return just the main message
        if not messages:
            return [completion]

        # Otherwise, append main completion and return all messages
        # Order: web searches (chronological) + main completion (thoughts/content/actions)
        messages.append(completion)
        return messages
