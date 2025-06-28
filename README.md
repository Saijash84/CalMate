# Calendar Agent

A FastAPI-based calendar booking assistant that integrates with Google Calendar and provides natural language processing capabilities for booking, editing, and managing calendar events.

## Features

- Natural language processing for booking events
- Integration with Google Calendar
- Event management (book, edit, cancel)
- Availability checking
- Secure OAuth2 authentication
- Streamlit-based frontend interface

## Project Structure

```
.
├── Backend/           # Backend FastAPI application
├── Frontend/         # Streamlit frontend application
├── src/              # Main source code

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with the following variables:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
OPENAI_API_KEY=your_openai_key
```

3. Run the backend:
```bash
python -m uvicorn src.main:app --reload
```

4. Run the frontend:
```bash
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
├── Backend/           # Backend code (FastAPI)
├── Frontend/          # Frontend code (Streamlit)
├── src/              # Source code
│   ├── __init__.py
│   ├── agent.py      # NLP agent implementation
│   ├── calendar_utils.py  # Google Calendar integration
│   ├── database.py   # Database operations
│   ├── main.py       # FastAPI application
│   └── utils.py      # Utility functions
├── requirements.txt   # Python dependencies
├── render.yaml        # Render deployment configuration
├── Procfile          # Process configuration
├── runtime.txt       # Python runtime version
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