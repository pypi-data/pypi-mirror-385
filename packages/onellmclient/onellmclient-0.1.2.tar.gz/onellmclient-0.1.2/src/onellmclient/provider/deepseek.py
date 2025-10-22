from typing import List, Dict, Optional, Literal, Any
from .openai import openai_completion_tools, openai_completion_messages
import json
import copy


def deepseek_completion_payload(
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

    _messages = copy.deepcopy(messages)
    _tools = copy.deepcopy(tools)

    if schema is not None:
        payload["response_format"] = {
            "type": "json_object",
        }
        if instructions is None:
            instructions = ""

        instructions += f"\n\nIMPORTANT: YOU MUST RESPOND IN THE JSON SCHEMA FORMAT SPECIFIED BELOW (WITHOUT ANY OTHER TEXT):\n\n{json.dumps(schema,indent=2,ensure_ascii=False)}"

    if instructions is not None:
        _messages.insert(0, {"role": "system", "content": instructions})

    # print(messages)
    payload["messages"] = openai_completion_messages(_messages)

    if _tools is not None:
        payload["tools"].extend(openai_completion_tools(_tools))

    if reasoning_effort is not None:
        pass  # deepseek does not support reasoning_effort

    if temperature is not None:
        payload["temperature"] = temperature

    if web_search:
        raise NotImplementedError("web_search is not supported for deepseek")

    if tool_choice is not None:
        payload["tool_choice"] = tool_choice
    print("payload", payload)
    return payload
