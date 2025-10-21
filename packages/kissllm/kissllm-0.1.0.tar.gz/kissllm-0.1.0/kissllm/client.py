import json
import logging
from typing import Any, Dict, List, Optional, Union

from openai.types.completion import Completion

from kissllm.io import IOChannel, IOTypeEnum
from kissllm.observation.decorators import observe
from kissllm.providers import get_provider_driver
from kissllm.stream import CompletionStream
from kissllm.tools import ToolManager, ToolMixin
from kissllm.utils import format_prompt

logger = logging.getLogger(__name__)


class State:
    def __init__(
        self,
        use_flexible_toolcall=True,
        tool_registry=None,
    ):
        self._messages: List[Dict[str, Any]] = []
        self.use_flexible_toolcall = use_flexible_toolcall
        self.tool_registry = tool_registry

        self._last_message = None

    def last_message(self):
        return self._last_message

    def get_messages(self):
        final_messages = [msg.copy() for msg in self._messages]
        for msg in final_messages:
            msg.pop("local_metadata", None)
        return final_messages

    async def accumulate_response(self, response):
        if isinstance(response, CompletionStream):
            response = await response.accumulate_stream()
        return response

    async def handle_response(self, raw_resp, stream):
        messages = self._messages
        should_cont = False
        if not stream:
            # Pass the client's tool registry to the response object
            response = CompletionResponse(
                raw_resp,
                self.tool_registry,
                use_flexible_toolcall=self.use_flexible_toolcall,
            )
        else:
            # Pass the client's tool registry to the stream object
            response = CompletionStream(
                raw_resp,
                self.tool_registry,
                use_flexible_toolcall=self.use_flexible_toolcall,
            )
        response = await self.accumulate_response(response)
        content = response.choices[0].message.content or ""
        self._last_message = content
        if not response.get_tool_calls():
            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                }
            )
            should_cont = False
        else:
            if self.use_flexible_toolcall:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                    }
                )
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": response.get_tool_calls(),
                    }
                )

            tool_results = await response.get_tool_results()
            for result in tool_results:
                messages.append(result)
            should_cont = True
        return should_cont

    async def get_tool_params(self):
        if self.use_flexible_toolcall:
            tools = None
            tool_choice = None
        else:
            if self.tool_registry:
                tools = await self.tool_registry.get_tool_specs() or None
            else:
                tools = None
            tool_choice = "auto"

        return tools, tool_choice

    async def inject_tools_into_messages(self):
        """Inject tools information into messages."""
        if self.tool_registry:
            tool_specs = await self.tool_registry.get_tool_specs() or None
        else:
            tool_specs = None

        if not tool_specs:
            return

        messages = self._messages
        if any(
            [m.get("local_metadata", {}).get("type") == "tool_spec" for m in messages]
        ):
            return

        tools_sys = """
# Tool Use
You can call external tools to help complete tasks.

## Important Notes:
- You can only get tool results in the NEXT message, NOT immediately.
- NEVER generate or simulate tool results yourself.

## Tool Calling Flow:
1. You output <tool_call> requests in your reply.
2. The system executes the tool and returns the result in the NEXT message.
3. You process the tool results in the next round.

## Tool Calling Format:
1. Use JSON inside <tool_call> tags. **Make sure the json is valid. All string values must be properly escaped.**
2. Generate a unique ID for each call.
3. Follow the exact schema and provide all required parameters.
4. Each <tool_call> must start on a new line.
5. For long strings, use `ref:raw_tool_argument_<index>` to reference raw text in the message. The `<index>` must be unique within a single reply.
For example:

<tool_call>{"id": "tool_call_00001", "name": "demo_func_name", "arguments": {"demo_arg": "multiline\ndemo_value\nwith \"quotes\""}}</tool_call>

is the same with:

<tool_call>{"id": "tool_call_00001", "name": "demo_func_name", "arguments": {"demo_arg": "ref:raw_tool_argument_1"}}</tool_call>
<raw_tool_argument_1>
multiline
demo value
with "quotes"
</raw_tool_argument_1>

## Tool Calling Revoke:
If you find yourself gives wrong tool call in **this reply earlier**, you can use <revoke_tool_call> to revoke the earlier tool call of **this replay**. For example:
<revoke_tool_call>tool_call_00001</revoke_tool_call>

## Tool Calling Rules:
1. Understand the user's request before calling any tools.
2. If no tool is needed, respond naturally.
3. You may make multiple tool calls if necessary.
"""

        tools_user = "\n## Available Tool Specifications:\n" + "\n".join(
            [self._generate_tool_text(t) for t in tool_specs]
        )

        tools_msg = tools_sys + tools_user

        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                messages.insert(
                    i + 1,
                    {
                        "role": "user",
                        "content": tools_msg,
                        "local_metadata": {"type": "tool_spec"},
                    },
                )
                break
        else:
            # If no system message found, insert tools text
            messages.insert(
                0,
                {
                    "role": "user",
                    "content": tools_msg,
                    "local_metadata": {"type": "tool_spec"},
                },
            )

    def _generate_tool_text(self, tool_spec) -> str:
        func = tool_spec["function"]
        name = func["name"]
        description = func["description"]
        params = func["parameters"]["properties"]
        required = func["parameters"]["required"]
        for k, v in params.items():
            if k in required:
                v["required"] = True
        tool_text = f"""
### {name}
Params: {json.dumps(params)}
Description:
{description}
        """
        return tool_text


class CompletionResponse(ToolMixin):
    def __init__(
        self,
        response: Completion,
        tool_registry: Optional[ToolManager],
        use_flexible_toolcall=True,
    ):
        self.__dict__.update(response.__dict__)
        ToolMixin.__init__(self, tool_registry, use_flexible_toolcall)


class LLMClient:
    """Unified LLM Client for multiple model providers"""

    def __init__(
        self,
        provider: str | None = None,
        provider_model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        io_channel: IOChannel | None = None,
    ):
        """
        Initialize LLM client with specific provider.

        Args:
            provider: Provider name (e.g. "openai", "anthropic").
            provider_model: Provider along with default model to use (e.g., "openai/gpt-4").
            api_key: Provider API key.
            base_url: Provider base URL.
        """
        self.default_model = None
        if provider_model:
            self.provider, self.default_model = provider_model.split("/", 1)
        if provider:
            self.provider = provider
        if self.provider is None:
            raise ValueError(
                "Provider must be specified either through provider or provider_model parameter"
            )
        self.provider_driver = get_provider_driver(self.provider)(
            self.provider, api_key=api_key, base_url=base_url
        )
        self.io_channel = io_channel

    def get_model(self, model):
        if model is None:
            model = self.default_model
        if model is None:
            raise ValueError(
                "Model must be specified either through model or provider_model parameter"
            )
        return model

    @observe
    async def async_completion(
        self,
        messages: List[Dict[str, str]],
        model: str | None = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: Optional[bool] = False,
        tools: Optional[List[Dict[str, Any]]] | bool = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs,
    ) -> Any:
        """Execute LLM completion with provider-specific implementation"""
        model = self.get_model(model)

        final_messages = [msg.copy() for msg in messages]
        for msg in final_messages:
            msg.pop("local_metadata", None)

        if self.io_channel:
            channel = self.io_channel.create_sub_channel(IOTypeEnum.prompt_message)
            await channel.write(
                content=final_messages,
            )

        logger.debug("===Raw Prompt Messages:===")
        logger.debug(format_prompt(final_messages))

        res = await self.provider_driver.async_completion(
            messages=final_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        return res

    async def async_completion_multi_round(
        self,
        state: State,
        model: str | None = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: Optional[bool] = False,
        max_steps=10,
        **kwargs,
    ):
        """Execute LLM completion with automatic tool execution until no more tool calls"""
        # Use registered tools from the client's registry if tools parameter is True
        step = 0
        tools, tool_choice = await state.get_tool_params()

        while step < max_steps:
            step += 1
            response = await self.async_completion(
                messages=state.get_messages(),
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs,
            )
            continu = await state.handle_response(response, stream)
            if not continu:
                break
