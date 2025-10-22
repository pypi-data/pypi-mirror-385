from openai.types.responses.response import Response as OpenAIResponse
from openai.types.chat.chat_completion import ChatCompletion as OpenAIChatCompletion
from ..types import (
    UnifiedMessage,
    UnifiedToolCall,
    UnifiedTextMessageContent,
    UnifiedToolCallMessageContent,
)
import json
from typing import List, Dict, Any, Optional, Literal
import copy


def openai_json_schema(schema: dict) -> dict:
    """
    给 schema 的 type=object 递归添加 additionalProperties=False
    """
    if "type" in schema and schema["type"] == "object":
        schema["additionalProperties"] = False
        for _, value in schema["properties"].items():
            openai_json_schema(value)
    return schema


def openai_tools(tools: list[dict]) -> list[dict]:
    """
    给 tools 的 type=function 添加 function 字段
    """
    converted = []
    for tool in tools:
        tool["type"] = "function"
        if "parameters" in tool:
            tool["parameters"] = openai_json_schema(tool["parameters"])
        else:
            tool["parameters"] = {}
        converted.append(tool)

    return converted


def openai_completion_tools(tools: list[dict]) -> list[dict]:
    """
    给 tools 的 type=function 添加 function 字段
    """
    converted = []
    for tool in tools:
        converted.append({"type": "function", "function": tool})
    return converted


def openai_response_convert(response: OpenAIResponse) -> UnifiedMessage:
    """
    将 OpenAI 的 response 转换为统一格式
    """

    role = None
    contents = []

    for output in response.output:
        if output.type == "message":
            role = output.role
            for output_content in output.content:
                if output_content.type == "output_text":
                    contents.append(
                        UnifiedTextMessageContent(
                            type="text", content=output_content.text, id=output.id
                        )
                    )
        elif output.type == "function_call":
            unified_tool_call = UnifiedToolCall(
                id=output.call_id,
                name=output.name,
                arguments=json.loads(output.arguments),
            )
            contents.append(
                UnifiedToolCallMessageContent(
                    type="tool_call", content=unified_tool_call
                )
            )

    return UnifiedMessage(role=role, content=contents)


def openai_messages(messages: List[Dict[str, Any]]) -> list:
    """
    将 UnifiedMessage 转换为 OpenAI 的 messages 格式
    """
    converted = []
    for message in messages:
        message_content = message.get("content")
        if isinstance(message_content, list):
            for content in message_content:
                if content.type == "text":
                    _message = {
                        "type": "message",
                        "content": content.get("content"),
                        "role": message.get("role"),
                    }

                    if message.get("role") == "assistant":
                        _message["id"] = content.get("id")

                    converted.append(_message)
                elif content.type == "tool_call":
                    converted.append(
                        {
                            "type": "function_call",
                            # 'id':None,
                            "call_id": content.content.id,
                            "name": content.content.name,
                            "arguments": json.dumps(content.content.arguments),
                        }
                    )
                elif content.type == "tool_result":
                    converted.append(
                        {
                            "type": "function_call_output",
                            "call_id": content.content.tool_call_id,
                            "output": content.content.content,
                        }
                    )
        else:
            converted.append(
                {"role": message.get("role"), "content": message.get("content")}
            )
    return converted


def openai_completion_messages(messages: List[Dict[str, Any]]) -> list:
    """
    将 UnifiedMessage 转换为 OpenAI 的 messages 格式
    """
    converted = []
    for message in messages:
        role = message.get("role")
        message_content = message.get("content")
        text_content = None
        tool_call_content = []
        if isinstance(message_content, list):
            for content in message_content:
                if content.type == "text":
                    text_content = content.get("content")
                elif content.type == "tool_call":
                    tool_call_content.append(
                        {
                            "type": "function",
                            "id": content.content.id,
                            "function": {
                                "name": content.content.name,
                                "arguments": json.dumps(content.content.arguments),
                            },
                        }
                    )
                elif content.type == "tool_result":
                    converted.append(
                        {
                            "role": "tool",
                            "tool_call_id": content.content.tool_call_id,
                            "content": content.content.content,
                        }
                    )
            _converted = {
                "role": role,
                "content": text_content,
            }
            if tool_call_content:
                _converted["tool_calls"] = tool_call_content
        else:
            converted.append({"role": role, "content": message_content})
    return converted


def openai_payload(
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
    _messages = copy.deepcopy(messages)
    payload = {
        "model": model,
        "input": openai_messages(_messages),
        "stream": False,
        "instructions": instructions,
        "tools": [],
    }
    _tools = copy.deepcopy(tools)
    if schema is not None:
        payload["text"] = {
            "format": {
                "type": "json_schema",
                "schema": openai_json_schema(schema),
                "name": "json_response",
                "strict": True,
            }
        }

    if tools is not None:
        payload["tools"].extend(openai_tools(_tools))

    if temperature is not None and not model.startswith(
        "gpt-5"
    ):  # gpt-5 not support temperature
        payload["temperature"] = temperature

    if reasoning_effort is not None:
        if reasoning_effort == "off":
            raise ValueError("reasoning_effort off is not supported")
        payload["reasoning"] = {"effort": reasoning_effort}

    if web_search:
        payload["tools"].append({"type": "web_search"})

    if tool_choice is not None:
        payload["tool_choice"] = tool_choice
    # print(json.dumps(payload, indent=2))
    return payload


def openai_completion_payload(
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
        "tools": [],
    }

    if instructions is not None:
        messages.insert(0, {"role": "system", "content": instructions})

    # print(messages)
    payload["messages"] = messages

    if schema is not None:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "json_response",
                "description": "The response should be a JSON object",
                "strict": True,
                "schema": schema,
            },
        }

    if tools is not None:
        payload["tools"].extend(openai_tools(tools))

    if reasoning_effort is not None:
        payload["resoning_effort"] = reasoning_effort

    if temperature is not None:
        payload["temperature"] = temperature

    if web_search:
        pass

    if tool_choice is not None:
        payload["tool_choice"] = tool_choice

    return payload


def openai_completion_response_convert(
    response: OpenAIChatCompletion,
) -> UnifiedMessage:
    # print(response)
    role = response.choices[0].message.role
    contents = []

    if response.choices[0].message.content is not None:
        contents.append(
            UnifiedTextMessageContent(
                type="text", content=response.choices[0].message.content
            )
        )

    if response.choices[0].message.tool_calls is not None:
        for tool_call in response.choices[0].message.tool_calls:
            contents.append(
                UnifiedToolCallMessageContent(
                    type="tool_call",
                    content=UnifiedToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    ),
                )
            )

    return UnifiedMessage(
        role=role,
        content=contents,
    )
