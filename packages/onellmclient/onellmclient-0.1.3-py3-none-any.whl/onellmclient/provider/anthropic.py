from anthropic.types.message import Message as AnthropicMessage
from ..types import (
    UnifiedMessage,
    UnifiedToolCall,
    UnifiedTextMessageContent,
    UnifiedToolCallMessageContent,
)
from typing import List, Dict, Any, Optional, Literal
import json
import warnings


def anthropic_messages(messages: List[Dict[str, Any]]) -> list:
    """
    将 UnifiedMessage 转换为 Anthropic 的 messages 格式
    """
    converted = []
    for message in messages:
        message_content = message.get("content")
        if isinstance(message_content, list):
            contents = []
            for content in message_content:
                if content.type == "text":
                    contents.append({"type": "text", "text": content.get("content")})
                elif content.type == "tool_call":
                    contents.append(
                        {
                            "type": "tool_use",
                            "id": content.content.id,
                            "name": content.content.name,
                            "input": content.content.arguments,
                        }
                    )
                elif content.type == "tool_result":
                    contents.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content.content.tool_call_id,
                            "content": content.content.content,
                        }
                    )
            converted.append({"role": message.get("role"), "content": contents})
        else:
            converted.append(
                {"role": message.get("role"), "content": message.get("content")}
            )
    return converted


def anthropic_response_convert(response: AnthropicMessage) -> UnifiedMessage:
    """
    将 Anthropic 的 response 转换为统一格式
    """
    role = response.role
    contents = []

    for response_content in response.content:

        if response_content.type == "text":
            if response_content.text is not None:
                contents.append(
                    UnifiedTextMessageContent(
                        type="text", content=response_content.text
                    )
                )
        elif response_content.type == "tool_use":
            unified_tool_call = UnifiedToolCall(
                id=response_content.id,
                name=response_content.name,
                arguments=response_content.input,
            )
            contents.append(
                UnifiedToolCallMessageContent(
                    type="tool_call", content=unified_tool_call
                )
            )

    return UnifiedMessage(
        role=role,
        content=contents,
    )


def anthropic_tools(tools: list[dict]) -> list[dict]:
    """
    parameters 字段改为 input_schema 字段
    """
    converted = []
    for tool in tools:
        _converted = {
            "name": tool["name"],
            "description": tool["description"],
        }
        if "parameters" in tool:
            _converted["input_schema"] = tool["parameters"]
        else:
            # Anthropic要求每个工具都必须有input_schema，即使没有参数也要提供空schema
            _converted["input_schema"] = {
                "type": "object",
                "properties": {},
                "required": [],
            }
        converted.append(_converted)
    return converted


def anthropic_payload(
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
        "messages": anthropic_messages(messages),
        "stream": False,
        "max_tokens": 8192 * 2,
        "system": instructions,
        "tools": [],
    }

    if reasoning_effort is not None:
        if reasoning_effort == "off":
            payload["thinking"] = {"type": "disabled"}
        else:
            budget_map = {
                "minimal": int(payload["max_tokens"] * 0.6 * 0.25),
                "low": int(payload["max_tokens"] * 0.6 * 0.5),
                "medium": int(payload["max_tokens"] * 0.6 * 0.75),
                "high": int(payload["max_tokens"] * 0.6 * 1),
            }
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget_map[reasoning_effort],
            }

    if tools is not None:
        payload["tools"].extend(anthropic_tools(tools))

    if schema is not None:
        warnings.warn(
            "schema is not supported for Anthropic, will be converted to system instruction"
        )
        if payload["system"] is None:
            payload["system"] = ""
        payload[
            "system"
        ] += f"\n\nIMPORTANT: YOU MUST RESPOND IN THE JSON SCHEMA FORMAT SPECIFIED BELOW (WITHOUT ANY OTHER TEXT):\n\n{json.dumps(schema,indent=2,ensure_ascii=False)}"

    if temperature is not None:
        payload["temperature"] = round(temperature / 2, 1)

    if web_search:
        payload["tools"].append(
            {"type": "web_search_20250305", "name": "web_search"}
        )

    if tool_choice is not None:
        tool_choice_map = {
            "auto": "auto",
            "none": "none",
            "required": "any",
        }
        payload["tool_choice"] = {"type": tool_choice_map[tool_choice]}

    return payload

