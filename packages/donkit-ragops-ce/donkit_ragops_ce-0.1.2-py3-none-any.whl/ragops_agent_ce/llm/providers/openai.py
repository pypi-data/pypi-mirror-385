from __future__ import annotations

from typing import Any

import httpx

from ...config import Settings, load_settings
from ..base import LLMProvider
from ..types import LLMResponse, Message, ToolCall, ToolFunctionCall, ToolSpec


class OpenAIProvider(LLMProvider):
    name: str = "openai"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._client = httpx.Client(
            base_url="https://api.openai.com/v1",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def supports_tools(self) -> bool:
        return True

    def generate(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        tools: list[ToolSpec] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": model or self.settings.llm_model or "gpt-4o-mini",
            "messages": [m.model_dump(exclude_none=True) for m in messages],
            "stream": False if stream is False else True,
        }
        if tools:
            payload["tools"] = [t.model_dump(exclude_none=True) for t in tools]
            payload["tool_choice"] = "auto"
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        resp = self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]["message"]
        content: str = choice.get("content") or ""
        tool_calls_data = choice.get("tool_calls") or []
        tool_calls: list[ToolCall] | None = None
        if tool_calls_data:
            tool_calls = []
            for tc in tool_calls_data:
                fn = tc["function"]
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", ""),
                        function=ToolFunctionCall(
                            name=fn.get("name", ""), arguments=fn.get("arguments", "{}")
                        ),
                    )
                )
        return LLMResponse(content=content, tool_calls=tool_calls, raw=data)
