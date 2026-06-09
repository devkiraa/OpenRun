from pydantic import BaseModel
from typing import List, Optional, Union

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: Optional[str] = "openrun"
    messages: List[Message]
    stream: Optional[bool] = False
    chat_id: Optional[str] = None
    stop: Optional[Union[str, List[str]]] = None
