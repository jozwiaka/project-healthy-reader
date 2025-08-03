import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # module:app path
        host="0.0.0.0",  # listen on all interfaces
        port=8000,
        reload=True      # enable hot reload in dev
    )