from pydantic import BaseModel
from typing import Literal, List, Any, Optional

Role = Literal["user", "assistant", "tool", "developer", "system", "model"]


class UnifiedBaseModel(BaseModel):
    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)


class UnifiedToolCall(UnifiedBaseModel):
    id: Optional[str] = None
    name: str
    arguments: Optional[dict] = None


class UnifiedToolResult(UnifiedBaseModel):
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class UnifiedTextMessageContent(UnifiedBaseModel):
    type: Literal["text"]
    content: str
    id: Optional[str] = None


class UnifiedToolCallMessageContent(UnifiedBaseModel):
    type: Literal["tool_call"]
    content: UnifiedToolCall


class UnifiedToolResultMessageContent(UnifiedBaseModel):
    type: Literal["tool_result"]
    content: UnifiedToolResult


class UnifiedMessage(UnifiedBaseModel):
    role: Optional[Role] = None
    content: (
        List[
            UnifiedTextMessageContent
            | UnifiedToolCallMessageContent
            | UnifiedToolResultMessageContent
        ]
        | str
    )
