# CalMate - Calendar Management Assistant

A conversational AI agent that helps users manage their Google Calendar through natural language interactions. The agent can book meetings, check availability, cancel bookings, and view schedules using a modern Streamlit interface.

## Features

- Natural language booking: "Book a meeting with John tomorrow at 2pm"
- Availability checking: "When am I free tomorrow?"
- Meeting cancellation: "Cancel my meeting with John"
- Schedule viewing: "What's my schedule for this week?"
- Modern Streamlit interface with chat and quick actions
- Integration with Google Calendar
- Secure OAuth2 authentication
- Persistent chat history
- Real-time availability checking

## Project Structure

```
.
├── Backend/           # Backend FastAPI application
├── Frontend/         # Streamlit frontend application
├── src/              # Main source code

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with the following variables:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_TOKEN_PATH=token.json
GOOGLE_CLIENT_SECRET_PATH=credentials.json
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

3. Run the services:
```bash
# In one terminal (backend)
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In another terminal (frontend)
cd Frontend
streamlit run streamlit_app.py
```

### Deploy to Render

1. Create a Render account if you don't have one

2. Set up environment variables in Render:
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET
   - GOOGLE_REDIRECT_URI
   - OPENAI_API_KEY

3. Connect your GitHub repository to Render

4. Render will automatically deploy both services using the configuration in `render.yaml`

## Usage

The application provides a conversational interface where you can interact with the calendar agent using natural language. You can:
- Book events: "Book a meeting with John tomorrow at 2pm"
- Cancel events: "Cancel my meeting with John"
- Edit events: "Move my meeting with John to 3pm"
- Check availability: "When am I free tomorrow?"
- List events: "What's my schedule for this week?"

## Project Structure

```
.
├── Frontend/          # Streamlit frontend application
├── src/              # Backend source code
│   ├── __init__.py
│   ├── agent.py      # LangGraph-based conversation agent
│   ├── calendar_utils.py  # Google Calendar integration
│   ├── database.py   # Database operations
│   └── main.py       # FastAPI application
├── requirements.txt   # Python dependencies
└── README.md         # Documentation
```

## Security

- All sensitive credentials are stored in environment variables
- OAuth2 authentication is used for Google Calendar integration
- Database credentials are not exposed

## Local Development

1. Clone the repository
2. Create a `.env` file with your Google OAuth credentials
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run Frontend/streamlit_app.py
   ```