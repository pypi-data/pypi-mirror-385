import json
from abc import abstractmethod
from typing import Callable

from openai.types.chat import ChatCompletionFunctionToolParam

from verifiers.envs.tool_env import ToolEnv
from verifiers.types import ChatCompletionMessageToolCall, Message, Messages, State
from verifiers.utils.async_utils import maybe_await
from verifiers.utils.tool_utils import convert_func_to_oai_tool


class StatefulToolEnv(ToolEnv):
    def __init__(
        self,
        tools: list[Callable] | None = None,
        max_turns: int = 10,
        error_formatter: Callable[[Exception], str] = lambda e: f"{str(e)}",
        **kwargs,
    ):
        super().__init__(
            tools=tools,
            max_turns=max_turns,
            error_formatter=error_formatter,
            **kwargs,
        )
        self.tools: list[Callable] = tools or []
        self.oai_tools: list[ChatCompletionFunctionToolParam] = [
            convert_func_to_oai_tool(tool) for tool in self.tools
        ]
        self.tool_map: dict[str, Callable] = {
            getattr(tool, "__name__", tool.__class__.__name__): tool
            for tool in self.tools
        }
        self.skipped_args: dict[str, list[str]] = {}
        self.max_turns: int = max_turns
        self.error_formatter: Callable[[Exception], str] = error_formatter

    def add_tool(self, tool: Callable, args_to_skip: list[str] = []):
        self.tools.append(tool)
        oai_tool = convert_func_to_oai_tool(tool)
        for arg in args_to_skip:
            assert "function" in oai_tool
            assert "parameters" in oai_tool["function"]
            if (
                "properties" in oai_tool["function"]["parameters"]
                and isinstance(oai_tool["function"]["parameters"]["properties"], dict)
                and arg in oai_tool["function"]["parameters"]["properties"]
            ):
                oai_tool["function"]["parameters"]["properties"].pop(arg)
            if (
                "required" in oai_tool["function"]["parameters"]
                and isinstance(oai_tool["function"]["parameters"]["required"], list)
                and arg in oai_tool["function"]["parameters"]["required"]
            ):
                oai_tool["function"]["parameters"]["required"].remove(arg)
        if self.oai_tools is None:
            self.oai_tools = []
        self.oai_tools.append(oai_tool)
        tool_name = getattr(tool, "__name__", tool.__class__.__name__)
        self.tool_map[tool_name] = tool
        self.skipped_args[tool_name] = args_to_skip

    def remove_tool(self, tool: Callable):
        self.tools.remove(tool)
        tool_name = getattr(tool, "__name__", tool.__class__.__name__)
        self.oai_tools = [
            oai_tool
            for oai_tool in self.oai_tools
            if oai_tool["function"]["name"] != tool_name
        ]
        self.tool_map.pop(tool_name)
        self.skipped_args.pop(tool_name)

    @abstractmethod
    def update_tool_args(
        self,
        tool_name: str,
        tool_args: dict,
        messages: Messages,
        state: State,
        **kwargs,
    ) -> dict:
        """Update tool arguments and/or state (in-place) based on messages and state."""
        pass

    async def call_tool(
        self, tool_name: str, tool_args: dict, tool_call_id: str, **kwargs
    ) -> Message:
        """Call a tool based on JSON command."""
        try:
            tool_func = self.tool_map[tool_name]
            result = await maybe_await(tool_func, **tool_args)
            return {
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call_id,
            }
        except Exception as e:
            return {
                "role": "tool",
                "content": self.error_formatter(e),
                "tool_call_id": tool_call_id,
            }

    async def env_response(
        self, messages: Messages, state: State, **kwargs
    ) -> tuple[Messages, State]:
        assert isinstance(messages, list)
        assert "tool_calls" in messages[-1]
        tool_messages = []
        for tool_call in messages[-1]["tool_calls"]:
            assert isinstance(tool_call, ChatCompletionMessageToolCall)
            tool_name: str = tool_call.function.name
            tool_args: dict = json.loads(tool_call.function.arguments)
            tool_call_id: str = tool_call.id or ""
            tool_args = self.update_tool_args(
                tool_name, tool_args, messages, state, **kwargs
            )
            tool_message: Message = await self.call_tool(
                tool_name, tool_args, tool_call_id
            )
            tool_messages.append(tool_message)
        return tool_messages, state
