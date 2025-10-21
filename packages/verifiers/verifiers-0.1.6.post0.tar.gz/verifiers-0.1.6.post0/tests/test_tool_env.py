"""Tests for the ToolEnv class."""

import json

import pytest

from tests.conftest import faulty_tool
from verifiers.envs.tool_env import ToolEnv


def _build_tool_call(name: str, arguments: dict, tool_call_id: str = "call_0"):
    from openai.types.chat.chat_completion_message_tool_call import (
        ChatCompletionMessageToolCall,
        Function,
    )

    return ChatCompletionMessageToolCall(
        id=tool_call_id,
        type="function",
        function=Function(name=name, arguments=json.dumps(arguments)),
    )


class TestToolEnv:
    @pytest.mark.asyncio
    async def test_tool_env_calls_tool(self, mock_tool_env, mock_openai_client):
        tool_call = _build_tool_call("square_tool", {"x": 4})
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call],
        }
        user_message = {"role": "user", "content": "Square 4"}

        mock_openai_client.add_chat_response(
            messages=[user_message],
            response="Using tool",
            tool_calls=[tool_call],
        )
        mock_openai_client.add_chat_response(
            messages=[
                user_message,
                assistant_message,
                {"role": "tool", "content": "16", "tool_call_id": "call_0"},
            ],
            response="Done",
        )

        completion, state = await mock_tool_env.rollout(
            client=mock_openai_client,
            model="test-model",
            prompt=[user_message],
            answer="",
        )

        tool_messages = [m for m in completion if m.get("role") == "tool"]
        assert tool_messages and tool_messages[0]["content"] == "16"
        assert state["responses"][0].choices[0].message.tool_calls is not None

    @pytest.mark.asyncio
    async def test_tool_env_completion_without_tool_calls(
        self, mock_tool_env, mock_openai_client
    ):
        mock_openai_client.add_chat_response(
            messages=[{"role": "user", "content": "Hello"}],
            response="Hi",
        )

        completion, state = await mock_tool_env.rollout(
            client=mock_openai_client,
            model="test-model",
            prompt=[{"role": "user", "content": "Hello"}],
            answer="",
        )

        assert len(state["responses"]) == 1
        assert completion[-1]["role"] == "assistant"
        assert completion[-1]["content"] == "Hi"
        assert state["turn"] == 1

    @pytest.mark.asyncio
    async def test_tool_env_error_handling(
        self, mock_openai_client, sample_chat_dataset
    ):
        class ErrorToolEnv(ToolEnv):
            def __init__(self, **kwargs):
                super().__init__(tools=[faulty_tool], **kwargs)

        env = ErrorToolEnv(
            client=mock_openai_client,
            model="test-model",
            dataset=sample_chat_dataset,
        )

        tool_call = _build_tool_call("faulty_tool", {})

        mock_openai_client.add_chat_response(
            messages=[{"role": "user", "content": "Invoke"}],
            response="Using tool",
            tool_calls=[tool_call],
        )

        completion, _ = await env.rollout(
            client=mock_openai_client,
            model="test-model",
            prompt=[{"role": "user", "content": "Invoke"}],
            answer="",
        )

        tool_messages = [m for m in completion if m.get("role") == "tool"]
        assert tool_messages and "failure" in tool_messages[0]["content"]
