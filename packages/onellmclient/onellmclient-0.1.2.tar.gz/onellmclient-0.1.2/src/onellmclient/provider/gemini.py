from google.genai.types import GenerateContentResponse as GeminiResponse
from ..types import (
    UnifiedMessage,
    UnifiedToolCall,
    UnifiedTextMessageContent,
    UnifiedToolCallMessageContent,
    UnifiedToolResult,
    UnifiedToolResultMessageContent,
)
import json
from typing import List, Dict, Any, Optional, Literal


def gemini_messages(messages: List[Dict[str, Any]]) -> list[dict]:
    """
    将 UnifiedMessage 转换为 Gemini 的 contents 格式
    """
    converted = []
    for message in messages:
        # 处理角色映射：assistant -> model, 其他保持不变

        role = "model" if message.get("role") == "assistant" else message.get("role")

        if isinstance(message.get("content"), list):
            parts = []
            for content in message.get("content"):
                if content.type == "text":
                    parts.append({"text": content.get("content")})
                elif content.type == "tool_call":
                    parts.append(
                        {
                            "function_call": {
                                "name": content.get("content").get("name"),
                                "args": content.get("content").get("arguments") or {},
                            }
                        }
                    )
                elif content.type == "tool_result":
                    parts.append(
                        {
                            "function_response": {
                                "name": content.content.name,
                                "response": json.loads(content.content.content),
                            }
                        }
                    )
            converted.append({"role": role, "parts": parts})
        else:
            # 纯字符串内容
            converted.append(
                {"role": role, "parts": [{"text": message.get("content")}]}
            )

    return converted


def gemini_tools(tools: list[dict]) -> list[dict]:
    """
    将统一工具格式转换为 Gemini 的 functionDeclarations 格式
    """
    function_declarations = []
    for tool in tools:
        function_declaration = {
            "name": tool["name"],
            "description": tool["description"],
        }
        if "parameters" in tool:
            function_declaration["parameters"] = tool["parameters"]
        else:
            # Gemini 如果没有参数，可以省略 parameters 字段
            pass
        function_declarations.append(function_declaration)

    return [{"function_declarations": function_declarations}]


def gemini_response_convert(response: GeminiResponse) -> UnifiedMessage:
    """
    将 Gemini 的 response 转换为统一格式
    """

    role = response.candidates[0].content.role

    if role != "model":
        raise ValueError(f"Gemini response role is not model: {role}")

    role = "assistant"
    contents = []

    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text is not None:
            contents.append(UnifiedTextMessageContent(type="text", content=part.text))

        if hasattr(part, "function_call") and part.function_call is not None:
            unified_tool_call = UnifiedToolCall(
                id=part.function_call.id if hasattr(part.function_call, "id") else None,
                name=(
                    part.function_call.name
                    if hasattr(part.function_call, "name")
                    else None
                ),
                arguments=(
                    part.function_call.args
                    if hasattr(part.function_call, "args")
                    else None
                ),
            )
            contents.append(
                UnifiedToolCallMessageContent(
                    type="tool_call", content=unified_tool_call
                )
            )

        # 处理 function_response（虽然模型通常不会返回这个，但为了完整性）
        if hasattr(part, "function_response") and part.function_response is not None:
            unified_tool_result = UnifiedToolResult(
                type="tool_result",
                content=str(part.function_response.response),
                tool_call_id=part.function_response.name,  # 使用函数名作为标识
            )
            contents.append(
                UnifiedToolResultMessageContent(
                    type="tool_result", content=unified_tool_result
                )
            )

    return UnifiedMessage(
        role=role,
        content=contents,
    )


def gemini_payload(
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
) -> dict:
    payload = {
        "model": model,
        "contents": gemini_messages(messages),
        "config": {"tools": []},
    }

    if instructions is not None:
        payload["config"]["system_instruction"] = instructions

    if schema is not None:
        payload["config"]["response_mime_type"] = "application/json"
        payload["config"]["response_schema"] = schema

    if tools is not None:
        payload["config"]["tools"].append({"function_declarations": tools})

    if temperature is not None:
        payload["config"]["temperature"] = temperature

    if web_search:
        payload["config"]["tools"].append({"google_search": {}})

    if tool_choice is not None:
        function_calling_config_map = {
            "auto": "AUTO",
            "none": "NONE",
            "required": "ANY",
        }
        payload["config"]["tool_config"] = {
            "function_calling_config": {
                "mode": function_calling_config_map[tool_choice]
            }
        }

    if reasoning_effort is not None:
        max_budget = 32768 if "pro" in model else 24576
        budget_map = {
            "off": 0,
            "minimal": int(max_budget * 0.25),
            "low": int(max_budget * 0.5),
            "medium": int(max_budget * 0.75),
            "high": max_budget,
        }
        payload["config"]["thinking_config"] = {
            "include_thoughts": False,
            "thinking_budget": budget_map[reasoning_effort],
        }

    return payload

