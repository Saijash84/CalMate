# calendar_utils.py
import os
import datetime
from typing import List, Optional, Tuple
import re
import dateparser
import pytz
import logging
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from src.database import save_booking, get_last_booking, cancel_booking, update_booking, list_bookings
from src.utils import extract_intent, extract_slots

def get_credentials_info():
    """Get Google Calendar API credentials from environment variables."""
    return {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
    }

class GoogleCalendarUtils:
    """
    Utility class for authenticating with Google Calendar, checking availability, and booking events.
    """
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """
        Authenticate the user with Google OAuth2 and initialize the Calendar API service.
        """
        creds_info = get_credentials_info()
        
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                token_data = json.load(token)
                self.creds = Credentials.from_authorized_user_info(token_data)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    creds_info,
                    ['https://www.googleapis.com/auth/calendar']
                )
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_free_busy(self, time_min: datetime.datetime, time_max: datetime.datetime, timezone: str = 'UTC'):
        """
        Query the user's Google Calendar for busy slots between time_min and time_max.
        Returns a list of (start, end) tuples for busy periods.
        """
        try:
            body = {
                "timeMin": time_min.isoformat(),
                "timeMax": time_max.isoformat(),
                "timeZone": timezone,
                "items": [{"id": "primary"}]
            }
            response = self.service.freebusy().query(body=body).execute()
            
            if "calendars" in response and "primary" in response["calendars"]:
                busy_slots = response["calendars"]["primary"].get("busy", [])
                return [(datetime.datetime.fromisoformat(slot["start"]), datetime.datetime.fromisoformat(slot["end"])) for slot in busy_slots]
            
            return []
        except Exception as e:
            print(f"Error getting free/busy: {e}")
            return []

    def find_available_slots(self, time_min: datetime.datetime, time_max: datetime.datetime, duration_minutes: int, timezone: str = 'UTC'):
        """
        Find available time slots of a given duration between time_min and time_max.
        Returns a list of (start, end) tuples for available periods.
        """
        busy_slots = self.get_free_busy(time_min, time_max, timezone)
        current = time_min
        available = []
        
        while current + datetime.timedelta(minutes=duration_minutes) <= time_max:
            is_available = True
            for busy_start, busy_end in busy_slots:
                if (current <= busy_end and busy_start <= current + datetime.timedelta(minutes=duration_minutes)):
                    is_available = False
                    break
            
            if is_available:
                available.append((current, current + datetime.timedelta(minutes=duration_minutes)))
            
            current += datetime.timedelta(minutes=15)
        
        return available

    def create_event(self, start: datetime.datetime, end: datetime.datetime, summary: str, description: Optional[str] = None, attendees: Optional[List[str]] = None, timezone: str = 'UTC'):
        """
        Create a new event in the user's Google Calendar.
        Returns the created event resource.
        """
        event = {
            'summary': summary,
            'description': description or '',
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': timezone,
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            return created_event
        except Exception as e:
            print(f"Error creating event: {e}")
            return {'error': str(e)}

    def check_availability(self, start: datetime.datetime, end: datetime.datetime):
        """Return busy slots between start and end."""
        return self.get_free_busy(start, end)

    def book_event(self, summary: str, start: datetime.datetime, end: datetime.datetime):
        """Book an event and return the event details."""
        return self.create_event(start, end, summary)

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def handle_user_message(user_msg):
    intent = extract_intent(user_msg)
    slots = extract_slots(user_msg)
    # Use intent and slots to call DB functions and return response
    # Example: if intent == "cancel", call cancel_booking(...)
    # Return a dict with the result and a user-friendly message