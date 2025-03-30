import os
from fastapi import FastAPI
from utils.logger import setup_logger
from api.endpoints import router
import uvicorn
from dotenv import load_dotenv

load_dotenv()

fastapi_port = int(os.getenv("FASTAPI_PORT", "9000"))

setup_logger()

app = FastAPI(
    title="RAG System",
    description="Retrieval-Augmented Generation API"
)

app.include_router(router)

if __name__ == "__main__":
    print(f"Starting server on port {fastapi_port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=fastapi_port,
        timeout_keep_alive=120
    )