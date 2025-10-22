from typing import List, Dict, Optional, Literal, Any
from .openai import openai_completion_tools
import copy


def xai_tools(tools: list[dict]) -> list[dict]:
    converted = openai_completion_tools(tools)
    for tool in converted:
        if "parameters" not in tool["function"]:
            tool["function"]["parameters"] = {} # xai does not support empty parameters
    return converted


def xai_payload(
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
    _tools = copy.deepcopy(tools)
    payload = {
        "model": model,
        "tools": [],
    }

    if instructions is not None:
        _messages.insert(0, {"role": "system", "content": instructions})

    payload["messages"] = _messages

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

    if _tools is not None:
        payload["tools"].extend(xai_tools(_tools))

    if reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort

    if temperature is not None:
        payload["temperature"] = temperature

    if web_search:
        payload["tools"].append({"type": "web_search"})

    if tool_choice is not None:
        payload["tool_choice"] = tool_choice
    return payload
