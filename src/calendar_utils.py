# calendar_utils.py
import os
import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
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

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarUtils:
    """
    Utility class for authenticating with Google Calendar, checking availability, and booking events.
    """
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        
        try:
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        os.getenv('GOOGLE_CLIENT_SECRET_PATH', 'credentials.json'),
                        SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            logging.info("Successfully authenticated with Google Calendar")
            
        except Exception as e:
            logging.error(f"Failed to authenticate with Google Calendar: {str(e)}")
            self.service = None

    def create_event(self, event_details: dict) -> dict:
        """Create a new calendar event"""
        try:
            if not self.service:
                return {"error": "Calendar service not available"}
            
            event = self.service.events().insert(calendarId='primary', body=event_details).execute()
            return {
                "id": event['id'],
                "summary": event['summary'],
                "start": event['start']['dateTime'],
                "end": event['end']['dateTime']
            }
        except Exception as e:
            logging.error(f"Failed to create event: {str(e)}")
            return {"error": str(e)}

    def get_calendar_events(self, start_time: datetime.datetime, end_time: datetime.datetime) -> List[dict]:
        """Get events within a time range"""
        try:
            if not self.service:
                return []
            
            timezone = pytz.timezone('UTC')
            start_time = timezone.localize(start_time)
            end_time = timezone.localize(end_time)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            logging.error(f"Failed to get events: {str(e)}")
            return []

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            if not self.service:
                return False
            
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception as e:
            logging.error(f"Failed to delete event: {str(e)}")
            return False

    def update_event(self, event_id: str, event_details: dict) -> dict:
        """Update an existing event"""
        try:
            if not self.service:
                return {"error": "Calendar service not available"}
            
            event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_details
            ).execute()
            return {
                "id": event['id'],
                "summary": event['summary'],
                "start": event['start']['dateTime'],
                "end": event['end']['dateTime']
            }
        except Exception as e:
            logging.error(f"Failed to update event: {str(e)}")
            return {"error": str(e)}

    def get_free_busy(self, start_time: datetime.datetime, end_time: datetime.datetime) -> dict:
        """Check if a time slot is free"""
        try:
            if not self.service:
                return {"busy": True}
            
            timezone = pytz.timezone('UTC')
            start_time = timezone.localize(start_time)
            end_time = timezone.localize(end_time)
            
            body = {
                "timeMin": start_time.isoformat(),
                "timeMax": end_time.isoformat(),
                "items": [{"id": 'primary'}]
            }
            
            result = self.service.freebusy().query(body=body).execute()
            return result['calendars']['primary']
        except Exception as e:
            logging.error(f"Failed to check free/busy: {str(e)}")
            return {"busy": True}

    def find_available_slots(self, start_time: datetime.datetime, end_time: datetime.datetime,
                           duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Find available time slots within the given time range"""
        events = self.get_calendar_events(start_time, end_time)
        slots = []
        
        current_time = start_time
        while current_time + datetime.timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + datetime.timedelta(minutes=duration_minutes)
            
            # Check if this slot overlaps with any existing events
            slot_available = True
            for event in events:
                event_start = datetime.datetime.fromisoformat(event['start']['dateTime'])
                event_end = datetime.datetime.fromisoformat(event['end']['dateTime'])
                
                if (current_time < event_end and slot_end > event_start):
                    slot_available = False
                    break
            
            if slot_available:
                slots.append({
                    'start': current_time,
                    'end': slot_end,
                    'formatted': f"{current_time.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}",
                    'duration': duration_minutes
                })
            
            current_time = slot_end
        
        return slots

    def format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format an event for display"""
        if 'start' in event and 'dateTime' in event['start']:
            start = datetime.datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.datetime.fromisoformat(event['end']['dateTime'])
            
            return {
                'id': event.get('id', ''),
                'summary': event.get('summary', 'No title'),
                'start_time': start.strftime('%I:%M %p'),
                'end_time': end.strftime('%I:%M %p'),
                'date': start.strftime('%Y-%m-%d'),
                'duration': int((end - start).total_seconds() / 60)
            }
        return event

    def get_todays_events(self) -> List[Dict[str, Any]]:
        """Get all events for today"""
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(now.date(), datetime.time.min)
        midnight_tomorrow = midnight + datetime.timedelta(days=1)
        
        events = self.get_calendar_events(midnight, midnight_tomorrow)
        return [self.format_event(e) for e in events]

    def get_weeks_events(self) -> List[Dict[str, Any]]:
        """Get all events for the next week"""
        now = datetime.datetime.now()
        start = datetime.datetime.combine(now.date(), datetime.time.min)
        end = start + datetime.timedelta(days=7)
        
        events = self.get_calendar_events(start, end)
        return [self.format_event(e) for e in events]

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

    def find_available_slots_legacy(self, time_min: datetime.datetime, time_max: datetime.datetime, duration_minutes: int, timezone: str = 'UTC'):
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

    def create_event_legacy(self, start: datetime.datetime, end: datetime.datetime, summary: str, description: Optional[str] = None, attendees: Optional[List[str]] = None, timezone: str = 'UTC'):
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