from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.documents import router as docs_router
from app.routes.conversations import router as conversations_router
from app.routes.messages import router as messages_router
import os

app=FastAPI()

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    docs_router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    conversations_router,
    prefix="/conversations",
    tags=["Conversations"]
)

app.include_router(
    messages_router,
    prefix="/conversations",
    tags=["Messages"]
)