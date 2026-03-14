"""BaseAgent — Claude API tool_use agentic loop."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from anthropic import Anthropic

from moatlab.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all MoatLab agents.

    Implements the Claude API tool_use loop: send message → receive tool_use
    requests → execute tools → feed results back → repeat until end_turn.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list[dict],
        tool_dispatch: dict[str, Callable],
        model: str | None = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_dispatch = tool_dispatch
        self.model = model or settings.default_model

        client_kwargs = {"api_key": settings.anthropic_api_key}
        if settings.anthropic_base_url:
            client_kwargs["base_url"] = settings.anthropic_base_url
        self.client = Anthropic(**client_kwargs)

    def run(self, user_input: str, max_iterations: int = 20) -> str:
        """Run the agent loop and return the final text response."""
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_input}
        ]

        for _ in range(max_iterations):
            response = self.client.messages.create(
                model=self.model,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
                max_tokens=8192,
            )

            # Collect text and tool_use blocks
            tool_use_blocks = []
            text_parts = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            # If no tool calls, we're done
            if response.stop_reason == "end_turn" or not tool_use_blocks:
                return "\n".join(text_parts)

            # Append assistant message with all content blocks
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and collect results
            tool_results = []
            for tool_block in tool_use_blocks:
                result = self._execute_tool(tool_block.name, tool_block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        logger.warning(f"[{self.name}] 达到最大迭代次数 {max_iterations}")
        return "\n".join(text_parts) if text_parts else "分析未能在限定步数内完成。"

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result as a JSON string."""
        func = self.tool_dispatch.get(tool_name)
        if func is None:
            error = f"未知工具: {tool_name}"
            logger.error(f"[{self.name}] {error}")
            return json.dumps({"error": error})

        try:
            logger.info(f"[{self.name}] 调用工具 {tool_name}({tool_input})")
            result = func(**tool_input)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            error = f"工具 {tool_name} 执行失败: {e}"
            logger.error(f"[{self.name}] {error}")
            return json.dumps({"error": error})
