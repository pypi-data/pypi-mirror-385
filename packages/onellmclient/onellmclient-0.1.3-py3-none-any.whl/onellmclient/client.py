from typing import Any, Dict, List, Optional, Literal
from openai import OpenAI
import json
from anthropic import Anthropic
from google.genai import Client as Gemini
from .provider.openai import openai_response_convert, openai_payload, openai_completion_response_convert
from .provider.anthropic import anthropic_response_convert, anthropic_payload
from .provider.gemini import gemini_response_convert, gemini_payload
from .types import UnifiedToolResultMessageContent, UnifiedMessage, UnifiedToolResult
from .provider.deepseek import deepseek_completion_payload
from .provider.xai import xai_payload

class Client:
    """统一 LLM 客户端：对齐主要厂商的文本/聊天接口签名。"""

    _openai: Optional[OpenAI]
    _anthropic: Optional[Anthropic]
    _gemini: Optional[Gemini]
    _deepseek: Optional[OpenAI] # DeepSeek API 是 OpenAI 的兼容接口
    _xai: Optional[OpenAI]

    def __init__(
        self,
        openai: Optional[Dict[Literal["key", "base"], str]] = None,
        anthropic: Optional[Dict[Literal["key", "base"], str]] = None,
        gemini: Optional[Dict[Literal["key", "base"], str]] = None,
        deepseek: Optional[Dict[Literal["key", "base"], str]] = None,
        xai: Optional[Dict[Literal["key", "base"], str]] = None,
    ) -> None:
        if openai is not None:
            if openai["key"] is None:
                raise ValueError("OpenAI API key is not set")
            self._openai = OpenAI(api_key=openai["key"], base_url=openai["base"])

        if anthropic is not None:
            if anthropic["key"] is None:
                raise ValueError("Anthropic API key is not set")
            self._anthropic = Anthropic(
                api_key=anthropic["key"], base_url=anthropic["base"]
            )

        if gemini is not None:
            if gemini["key"] is None:
                raise ValueError("Gemini API key is not set")
            self._gemini = Gemini(
                api_key=gemini["key"], http_options={"base_url": gemini["base"]}
            )

        if deepseek is not None:
            if deepseek["key"] is None:
                raise ValueError("DeepSeek API key is not set")
            self._deepseek = OpenAI(api_key=deepseek["key"], base_url=deepseek["base"])

        if xai is not None:
            if xai["key"] is None:
                raise ValueError("XAI API key is not set")
            self._xai = OpenAI(api_key=xai["key"], base_url=xai["base"])

    def get_client(self, provider: str) -> Any:
        if provider == "openai":
            return self._openai
        elif provider == "anthropic":
            return self._anthropic
        elif provider == "gemini":
            return self._gemini
        elif provider == "deepseek":
            return self._deepseek
        elif provider == "xai":
            return self._xai
        raise ValueError(f"Unsupported provider: {provider}")

    def completion(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        instructions: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        reasoning_effort: Optional[
            Literal["off", "minimal", "low", "medium", "high"]
        ] = None,
        temperature: Optional[float] = None,
        web_search: bool = False,
        tool_choice: Optional[Literal["auto", "none", "required"]] = None,
    ) -> UnifiedMessage:
        """
        统一LLM接口

        Args:
            provider: 提供商
            model: 模型
            messages: 消息
            instructions: 指令
            schema: 模式
            tools: 工具
            reasoning_effort: 推理力度
            temperature: 温度，范围0-2
            web_search: 网络搜索

        Returns:
            UnifiedMessage: 统一响应
        """

        if provider == "openai":
            payload = openai_payload(
                model,
                messages,
                instructions,
                schema,
                tools,
                reasoning_effort,
                temperature,
                web_search,
                tool_choice,
            )
            response = self._openai.responses.create(**payload)
            return openai_response_convert(response)

        elif provider == "anthropic":
            payload = anthropic_payload(
                model,
                messages,
                instructions,
                schema,
                tools,
                reasoning_effort,
                temperature,
                web_search,
                tool_choice,
            )
            response = self._anthropic.messages.create(**payload)
            return anthropic_response_convert(response)

        elif provider == "gemini":
            payload = gemini_payload(
                model,
                messages,
                instructions,
                schema,
                tools,
                reasoning_effort,
                temperature,
                web_search,
                tool_choice,
            )
            response = self._gemini.models.generate_content(**payload)
            return gemini_response_convert(response)

        elif provider == "deepseek":
            payload = deepseek_completion_payload(
                model,
                messages,
                instructions,
                schema,
                tools,
                reasoning_effort,
                temperature,
                web_search,
                tool_choice,
            )
            response = self._deepseek.chat.completions.create(**payload)
            return openai_completion_response_convert(response)

        elif provider == "xai":
            payload = openai_payload(
                model,
                messages,
                instructions,
                schema,
                tools,
                reasoning_effort,
                temperature,
                web_search,
                tool_choice,
            )
            response = self._xai.responses.create(**payload)
            return openai_response_convert(response)

        raise NotImplementedError(f"Unsupported provider: {provider}")

    def agent(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        instructions: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        reasoning_effort: Optional[
            Literal["off", "minimal", "low", "medium", "high"]
        ] = None,
        temperature: Optional[float] = None,
        web_search: bool = False,
        tool_choice: Optional[Literal["auto", "none", "required"]] = None,
    ) -> UnifiedMessage:
        """
        自动执行 tool call ，返回最后结果
        """
        callable_map = {}
        if tools is not None:
            for tool in tools:
                callable_map[tool["name"]] = tool["handler"]
                del tool["handler"]

        def has_tool_call(message: UnifiedMessage) -> bool:
            if isinstance(message.content, list):
                for content in message.content:
                    if content.type == "tool_call":
                        return True
            return False

        max_tool_call_count = 10
        tool_call_count = 0

        while True:
            response = self.completion(
                provider=provider,
                model=model,
                messages=messages,
                instructions=instructions,
                schema=schema,
                tools=tools,
                reasoning_effort=reasoning_effort,
                temperature=temperature,
                web_search=web_search,
                tool_choice=tool_choice,
            )

            # print(response)

            if not has_tool_call(response):
                return response

            tool_call_count += 1
            if tool_call_count >= max_tool_call_count:
                raise Exception(
                    f"Tool call count exceeded max_tool_call_count: {max_tool_call_count}"
                )

            messages.append(response)

            tool_results = []
            for content in response.content:
                if content.type == "tool_call":
                    try:
                        arguments = content.content.arguments or {}
                        result = {
                            "result": callable_map[content.content.name](**arguments)
                        }
                    except ValueError as e:
                        result = {"error": str(e)}

                    tool_results.append(
                        UnifiedToolResultMessageContent(
                            type="tool_result",
                            content=UnifiedToolResult(
                                content=json.dumps(result),
                                tool_call_id=content.content.id,
                                name=content.content.name,
                            ),
                        )
                    )

            messages.append(
                UnifiedMessage(
                    role="user",
                    content=tool_results,
                )
            )
