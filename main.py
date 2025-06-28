# main.py
from Backend.agent import handle_user_message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Backend.database import init_db

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: dict

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    response = handle_user_message(
        chat_request.message,
        chat_request.history
    )
    return ChatResponse(response=response)
