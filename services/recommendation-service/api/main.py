from fastapi import FastAPI
from api.routes import recommend
import uvicorn

app = FastAPI()

app.include_router(recommend.router, prefix="/recommend")

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",  # module:app path
        host="0.0.0.0",  # listen on all interfaces
        port=8000,
        reload=True      # enable hot reload in dev
    )