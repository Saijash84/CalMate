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
│   ├── __init__.py
│   ├── agent.py      # NLP agent implementation
│   ├── calendar_utils.py  # Google Calendar integration
│   ├── database.py   # Database operations
│   ├── main.py       # FastAPI application
│   └── utils.py      # Utility functions
├── requirements.txt   # Python dependencies
├── render.yaml       # Render deployment configuration
├── runtime.txt       # Runtime specification
└── README.md         # Documentation
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your Google Calendar API credentials:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
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

## Deployment

The application can be deployed to Render with two services:
1. Backend API (FastAPI)
2. Frontend (Streamlit)

## Usage

You can interact with the calendar agent through:
1. The Streamlit frontend interface
2. Direct API calls to the FastAPI endpoints

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