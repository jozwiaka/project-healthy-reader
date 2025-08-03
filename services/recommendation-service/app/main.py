import os
import sys
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
COMMON_DIR = os.path.join(PROJECT_DIR, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)
    
from fastapi import FastAPI
from api.routes import recommend

app = FastAPI()
app.include_router(recommend.router, prefix="/recommend")
