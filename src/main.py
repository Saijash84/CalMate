# main.py
from src.agent import handle_user_message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.database import init_db

# Initialize database
init_db()

app = FastAPI(
    title="CalMate API",
    description="API for calendar management and booking",
    version="1.0.0"
)

# Configure CORS to allow specific origins
import os

# Get frontend URL from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "https://calmate-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Add exception handler
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "status": "healthy",
        "description": "CalMate API",
        "documentation": "https://your-domain/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to keep the service alive"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: dict

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        response = handle_user_message(
            chat_request.message,
            chat_request.history
        )
        return ChatResponse(response=response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ChatResponse(response={"response": str(e)})
