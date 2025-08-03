from fastapi import APIRouter
from app.core.agent import agent
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    return agent.answer(payload.message)
