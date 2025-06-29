# main.py
import os
import sys

# Add the project root to PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agent import parse_input_node, handle_user_message, BookingState, handle_booking, handle_availability, handle_cancellation, handle_edit, handle_list, handle_help
from src.calendar_utils import GoogleCalendarUtils
from src.database import init_db

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize calendar
calendar_utils = GoogleCalendarUtils()

calendar_available = calendar_utils.authenticate()

# Initialize FastAPI app
app = FastAPI(
    title="CalMate API",
    description="API for calendar management and booking",
    version="1.0.0",
    debug=True
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "https://calmate-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_msg = data.get("message", "")
        
        if not user_msg:
            return {"response": "Please provide a message"}
            
        # Get chat history
        messages = data.get("messages", [])
        
        # Initialize LangGraph state
        state = BookingState()
        state.context_event = get_context_event_from_history(messages) if messages else None
        
        # Process input
        state = parse_input_node(state, user_msg, messages)
        
        # Handle response
        if state.response:
            return {"response": state.response}
            
        # Handle different intents
        intent = state.slots.get("intent", "unknown")
        
        if intent == "book":
            response = handle_booking(state.slots)
        elif intent == "check":
            response = handle_availability(state.slots)
        elif intent == "cancel":
            response = handle_cancellation(state.slots)
        elif intent == "edit":
            response = handle_edit(state.slots)
        elif intent == "list":
            response = handle_list(state.slots)
        elif intent == "help":
            response = handle_help()
        else:
            response = {"response": "I'm not sure what you want to do. Try asking for help."}
            
        logger.info(f"Processed message: {user_msg} -> {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "status": "healthy",
        "description": "CalMate API",
        "documentation": "https://your-domain/api/docs"
    }
