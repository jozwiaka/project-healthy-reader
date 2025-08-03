import os
import sys
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
COMMON_DIR = os.path.join(PROJECT_DIR, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)
    
from fastapi import FastAPI
from api.routes import chat, quotes

app = FastAPI(title="Quote Agent")

app.include_router(chat.router, prefix="/api/v1/quote-agent/chat", tags=["chat"])
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["quotes"])
