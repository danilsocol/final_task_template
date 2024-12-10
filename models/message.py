from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]
    session_id: str
    last_activity: datetime = Field(default_factory=datetime.now)
    
    def update_activity(self):
        self.last_activity = datetime.now()

class ChatHistoryForModel(BaseModel):
    messages: List[ChatMessage]
    session_id: str
    last_activity: datetime = Field(default_factory=datetime.now)
    
    def update_activity(self):
        self.last_activity = datetime.now()