from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict] = None

class Quote(BaseModel):
    id: int
    text: str
    author: Optional[str]
    tags: Optional[List[str]] = None
    source: Optional[str] = None

    class Config:
        orm_mode = True
