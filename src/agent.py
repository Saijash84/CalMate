from langgraph import StateGraph, State
from typing import Dict, Any, Optional, List
import datetime
import pytz
import dateparser
import re
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Calendar API credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']

class BookingState(State):
    slots: Dict[str, Any] = {}
    response: Optional[str] = None
    busy: bool = False
    context_event: Optional[Dict[str, Any]] = None

def parse_input_node(state: Dict[str, Any], user_msg: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Parse user input and extract relevant information"""
    try:
        # Extract intent
        intent = extract_intent(user_msg)
        
        # Extract datetime
        datetime_obj = extract_datetime(user_msg)
        
        # Extract duration
        duration = extract_duration(user_msg)
        
        # Extract attendees
        attendees = extract_attendees(user_msg)
        
        # Format response
        state["slots"] = {
            "intent": intent,
            "datetime": datetime_obj.isoformat() if datetime_obj else None,
            "duration": duration,
            "attendees": attendees,
            "raw": user_msg
        }
        
        return state
    except Exception as e:
        state["response"] = f"Error parsing input: {str(e)}"
        return state

def extract_intent(user_msg: str) -> str:
    """Extract intent from user message"""
    msg = user_msg.lower()
    if any(w in msg for w in ["cancel", "delete", "remove"]):
        return "cancel"
    if any(w in msg for w in ["edit", "reschedule", "move", "change"]):
        return "edit"
    if any(w in msg for w in ["book", "schedule", "set up", "add"]):
        return "book"
    if any(w in msg for w in ["list", "show", "what", "upcoming", "events", "history", "held"]):
        return "list"
    if any(w in msg for w in ["free", "available", "slots"]):
        return "check"
    if any(w in msg for w in ["help", "how"]):
        return "help"
    return "unknown"

def extract_datetime(text: str) -> Optional[datetime.datetime]:
    """Extract datetime from text using dateparser"""
    try:
        return dateparser.parse(text)
    except:
        return None

def extract_duration(text: str) -> int:
    """Extract duration in minutes from text"""
    duration = re.search(r'(\d+)\s*(?:hour|hr|minute|min)', text.lower())
    if duration:
        value = int(duration.group(1))
        unit = "hour" if "hour" in text.lower() else "minute"
        return value * 60 if unit == "hour" else value
    return 30  # Default duration

def extract_attendees(text: str) -> List[str]:
    """Extract attendees from text"""
    attendees = re.findall(r'with\s+([\w\s]+)', text.lower())
    return [a.strip() for a in attendees if a.strip()]

def parse_input_node(user_msg: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse user input and extract relevant information"""
    try:
        # Extract intent
        intent = extract_intent(user_msg)
        
        # Extract datetime
        datetime_obj = extract_datetime(user_msg)
        
        # Extract duration
        duration = extract_duration(user_msg)
        
        # Extract attendees
        attendees = extract_attendees(user_msg)
        
        # Format response
        response = {
            "intent": intent,
            "datetime": datetime_obj.isoformat() if datetime_obj else None,
            "duration": duration,
            "attendees": attendees,
            "raw": user_msg
        }
        
        return response
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to parse input: {str(e)}"
        }

def handle_user_message(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user message based on parsed input"""
    try:
        intent = parsed_input.get("intent", "unknown")
        
        if intent == "book":
            return handle_booking(parsed_input)
        elif intent == "check":
            return handle_availability_check(parsed_input)
        elif intent == "cancel":
            return handle_cancellation(parsed_input)
        elif intent == "view":
            return handle_view_schedule(parsed_input)
        else:
            return {
                "operation": "unknown_intent",
                "details": "I'm not sure what you want to do. Please try again."
            }
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to handle message: {str(e)}"
        }

def handle_booking(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle booking a new event"""
    try:
        # Extract booking details
        summary = parsed_input.get("summary", "Meeting")
        start_time = parsed_input.get("datetime")
        duration = parsed_input.get("duration", 30)
        attendees = parsed_input.get("attendees", [])
        
        if not calendar_available:
            return {
                "operation": "warning",
                "details": "Calendar service is not available. Running in simulation mode."
            }
            
        # Create event details
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': parsed_input.get("timezone", "UTC")
            },
            'end': {
                'dateTime': (start_time + datetime.timedelta(minutes=duration)).isoformat(),
                'timeZone': parsed_input.get("timezone", "UTC")
            },
            'attendees': [{'email': attendee} for attendee in attendees]
        }
        
        # Create the event
        created_event = calendar_utils.create_event(event)
        
        return {
            "operation": "booked",
            "details": f"Successfully booked meeting: {summary} at {start_time.strftime('%I:%M %p')}"
        }
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to book meeting: {str(e)}"
        }

def handle_availability_check(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle checking calendar availability"""
    try:
        start_time = parsed_input.get("datetime")
        duration = parsed_input.get("duration", 30)
        
        if not calendar_available:
            return {
                "operation": "warning",
                "details": "Calendar service is not available. Running in simulation mode."
            }
            
        end_time = start_time + datetime.timedelta(minutes=duration)
        
        events = calendar_utils.get_calendar_events(start_time, end_time)
        
        if not events:
            return {
                "operation": "available",
                "details": f"You are free from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}"
            }
        else:
            return {
                "operation": "busy",
                "details": f"You have meetings during that time: {', '.join(e['summary'] for e in events)}"
            }
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to check availability: {str(e)}"
        }

def handle_cancellation(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle canceling an event"""
    try:
        summary = parsed_input.get("summary", "Meeting")
        
        if not calendar_available:
            return {
                "operation": "warning",
                "details": "Calendar service is not available. Running in simulation mode."
            }
            
        # Find and delete the event
        events = calendar_utils.get_calendar_events(
            datetime.datetime.now() - datetime.timedelta(days=7),
            datetime.datetime.now() + datetime.timedelta(days=7)
        )
        
        for event in events:
            if event['summary'].lower() == summary.lower():
                calendar_utils.delete_event(event['id'])
                return {
                    "operation": "canceled",
                    "details": f"Successfully canceled meeting: {summary}"
                }
        
        return {
            "operation": "not_found",
            "details": f"No meeting found with title: {summary}"
        }
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to cancel meeting: {str(e)}"
        }

def handle_view_schedule(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """Handle viewing calendar schedule"""
    try:
        start_time = parsed_input.get("datetime")
        duration = parsed_input.get("duration", 1440)  # Default to full day
        
        if not calendar_available:
            return {
                "operation": "warning",
                "details": "Calendar service is not available. Running in simulation mode."
            }
            
        end_time = start_time + datetime.timedelta(minutes=duration)
        
        events = calendar_utils.get_calendar_events(start_time, end_time)
        
        if not events:
            return {
                "operation": "viewed",
                "details": "No meetings scheduled during that time"
            }
        else:
            event_list = "\n".join([
                f"- {e['summary']} at {datetime.datetime.fromisoformat(e['start']['dateTime']).strftime('%I:%M %p')}"
                for e in events
            ])
            return {
                "operation": "viewed",
                "details": f"Your meetings:\n{event_list}"
            }
    except Exception as e:
        return {
            "operation": "error",
            "details": f"Failed to view schedule: {str(e)}"
        }

def ask_for_missing_info_node(state: dict):
    slots = state.get("slots", {})
    if not slots.get("date/time"):
        state["response"] = "When would you like to schedule it?"
    elif not slots.get("intent"):
        state["response"] = "Would you like to book a meeting or just check availability?"
    return state


def check_calendar_node(state: dict):
    slots = state.get("slots", {})
    try:
        dt = datetime.datetime.fromisoformat(slots["date/time"])
        duration = slots.get("duration", 30)
        end = dt + datetime.timedelta(minutes=duration)
        busy = calendar_utils.get_free_busy(dt, end)
        state["busy"] = bool(busy)
    except Exception as e:
        state["response"] = f"Couldn't parse date/time: {e}"
    return state


def suggest_alternatives_node(state: dict):
    slots = state.get("slots", {})
    dt = datetime.datetime.fromisoformat(slots["date/time"])
    duration = slots.get("duration", 30)
    end = dt + datetime.timedelta(hours=2)

    alternatives = calendar_utils.find_available_slots(dt, end, duration)
    if alternatives:
        times = [f"{s[0].strftime('%A %I:%M %p')} - {s[1].strftime('%I:%M %p')}" for s in alternatives]
        state["response"] = "You're busy at that time. Available options: " + ", ".join(times)
    else:
        state["response"] = "No alternative free slots found."
    return state


def confirm_booking_node(state: dict):
    slots = state.get("slots", {})
    try:
        dt = datetime.datetime.fromisoformat(slots["date/time"])
        duration = slots.get("duration", 30)
        end = dt + datetime.timedelta(minutes=duration)
        summary = slots.get("summary", "Meeting")

        event = calendar_utils.create_event(dt, end, summary)
        if 'error' in event:
            state["response"] = f"Failed to book: {event['error']}"
        else:
            state["response"] = f"✅ Meeting '{summary}' booked on {dt.strftime('%A, %B %d at %I:%M %p')}"
    except Exception:
        state["response"] = "Booking failed. Please try again."
    return state


def end_conversation_node(state: dict):
    if not state.get("response"):
        state["response"] = "Let me know if you want to schedule another meeting."
    return state


def build_agent():
    graph = StateGraph(BookingState)

    graph.add_node("parse_input", parse_input_node)
    graph.add_node("ask_for_missing_info", ask_for_missing_info_node)
    graph.add_node("check_calendar", check_calendar_node)
    graph.add_node("suggest_alternatives", suggest_alternatives_node)
    graph.add_node("confirm_booking", confirm_booking_node)
    graph.add_node("end_conversation", end_conversation_node)

    graph.add_edge("parse_input", "ask_for_missing_info")
    graph.add_edge("ask_for_missing_info", "check_calendar")
    graph.add_conditional_edges(
        "check_calendar",
        lambda s: "suggest_alternatives" if s.get("busy") else "confirm_booking"
    )
    graph.add_edge("suggest_alternatives", "end_conversation")
    graph.add_edge("confirm_booking", "end_conversation")

    graph.set_entry_point("parse_input")
    graph.set_finish_point("end_conversation")

    return graph.compile(), None


def extract_intent(user_msg):
    msg = user_msg.lower()
    if any(w in msg for w in ["cancel", "delete", "remove"]):
        return "cancel"
    if any(w in msg for w in ["edit", "reschedule", "move", "change"]):
        return "edit"
    if any(w in msg for w in ["book", "schedule", "set up", "add"]):
        return "book"
    if any(w in msg for w in ["list", "show", "what", "upcoming", "events", "history", "held"]):
        return "list"
    if any(w in msg for w in ["free", "available", "slots"]):
        return "check"
    if any(w in msg for w in ["help", "how"]):
        return "help"
    return "unknown"


def extract_attendees(user_msg):
    match = re.search(r"with ([A-Za-z ,and]+)", user_msg, re.I)
    if match:
        names = re.split(r",| and ", match.group(1))
        return [n.strip().title() for n in names if n.strip()]
    return []


def extract_reference(user_msg):
    time_match = re.search(r"(\d{1,2}(:\d{2})?\s*(am|pm)?)", user_msg, re.I)
    summary_match = re.search(r"(event|call|appointment) (about|on|for) ([^,\\.]+)", user_msg, re.I)
    if time_match:
        return time_match.group(0)
    if summary_match:
        return summary_match.group(3).strip()
    if "last" in user_msg.lower():
        return "last"
    if "next" in user_msg.lower():
        return "next"
    if any(w in user_msg.lower() for w in ["it", "that", "this"]):
        return "context"
    return None


def extract_slots(user_msg, context_event=None):
    import logging
    found = search_dates(user_msg, settings={"RETURN_AS_TIMEZONE_AWARE": True, "DATE_ORDER": "DMY"})
    dt = None
    if found:
        dt = found[0][1]
        # If time is missing, try to extract it manually
        if dt.hour == 0 and dt.minute == 0:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', user_msg, re.I)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                ampm = time_match.group(3).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                dt = dt.replace(hour=hour, minute=minute)
    duration = 30
    if re.search(r"1 ?hour", user_msg, re.I):
        duration = 60
    elif re.search(r"(\d+)\s*min", user_msg, re.I):
        duration = int(re.search(r"(\d+)\s*min", user_msg, re.I).group(1))
    elif re.search(r"(\d+)\s*hour", user_msg, re.I):
        duration = int(re.search(r"(\d+)\s*hour", user_msg, re.I).group(1)) * 60
    elif context_event and context_event.get("duration"):
        duration = context_event["duration"]
    summary_match = re.search(r"for ([^,\\.;]+)", user_msg, re.I)
    summary = summary_match.group(1).strip() if summary_match else (context_event["summary"] if context_event and context_event.get("summary") else "Event")
    tz_match = re.search(r"([A-Za-z]+/[A-Za-z_]+)", user_msg)
    timezone = tz_match.group(1) if tz_match else (context_event["timezone"] if context_event and context_event.get("timezone") else "UTC")
    attendees = extract_attendees(user_msg) or (context_event["attendees"] if context_event and context_event.get("attendees") else [])
    vague_words = ["next week", "someday", "later", "soon", "whenever", "some time", "not sure"]
    ambiguity = (dt is None) or any(w in user_msg.lower() for w in vague_words)
    reference = extract_reference(user_msg)
    # Logging for debugging
    logging.info(f"Parsed datetime: {dt}, duration: {duration}, timezone: {timezone}, ambiguity: {ambiguity}")
    return {
        "datetime": dt.isoformat() if dt else None,
        "duration": duration,
        "summary": summary,
        "timezone": timezone,
        "attendees": attendees,
        "ambiguity": ambiguity,
        "reference": reference
    }


def find_booking_by_reference(reference, context_event=None):
    bookings = list_bookings()
    if not bookings:
        return None
    if reference == "last":
        return bookings[-1]
    if reference == "next":
        return bookings[0]
    if reference == "context" and context_event:
        # Try to match by context event's summary and time
        for b in bookings:
            if (context_event.get("summary") and context_event["summary"].lower() in b[1].lower()) or \
               (context_event.get("datetime") and context_event["datetime"] in b[3]):
                return b
    for b in bookings:
        if reference and (reference in b[3] or reference.lower() in b[1].lower()):
            return b
    return None



def get_context_event_from_history(messages):
    # Find the last assistant message with a booking or event in the response
    for msg in reversed(messages):
        if msg["role"] == "assistant" and "event" in msg["content"].lower():
            # Try to extract event details from the message
            # This is a simple heuristic; you can make it more robust if you store structured data in the session
            match = re.search(r"'(.+?)' (?:booked|scheduled|updated|cancelled).*?for ([\w, :]+)", msg["content"])
            if match:
                summary = match.group(1)
                dt_str = match.group(2)
                dt = dateparser.parse(dt_str)
                return {
                    "summary": summary,
                    "datetime": dt.isoformat() if dt else None,
                    "duration": 30,
                    "timezone": "UTC",
                    "attendees": []
                }
    return None


def handle_user_message(user_msg, messages=None):
    """
    user_msg: str, the current user message
    messages: list of dicts, the chat history (each dict: {"role": "user"/"assistant", "content": str})
    """
    try:
        context_event = get_context_event_from_history(messages) if messages else None
        intent = extract_intent(user_msg)
        slots = extract_slots(user_msg, context_event)
        result = {}

        if intent == "book":
            if slots["ambiguity"]:
                return {"response": "Please specify a clear date and time for your event."}
            
            start_time = slots["datetime"]
            end_time = (dateparser.parse(slots["datetime"]) + datetime.timedelta(minutes=slots["duration"])).isoformat()
            
            for b in list_bookings():
                if b[3] == start_time and b[6] == 'active':
                    return {"response": "You already have an event at that time."}
            
            event_id = f"evt_{int(datetime.now().timestamp())}"
            save_booking(slots["summary"], event_id, start_time, end_time, slots["timezone"])
            response = f"Event '{slots['summary']}' booked for {start_time} ({slots['timezone']})."
            if slots["attendees"]:
                response += f" Attendees: {', '.join(slots['attendees'])}."
            return {"response": response}
        
        elif intent == "cancel":
            ref = slots.get("reference")
            booking = find_booking_by_reference(ref, context_event) if ref else get_last_booking()
            if booking:
                cancel_booking(booking[0])
                return {"response": f"Cancelled event: '{booking[1]}' at {booking[3]}"}
            return {"response": "No matching event found to cancel."}
        
        elif intent == "edit":
            ref = slots.get("reference")
            booking = find_booking_by_reference(ref, context_event) if ref else get_last_booking()
            if booking:
                if slots["ambiguity"]:
                    return {"response": "Please specify the new date/time or summary for your event."}
                
                start_time = slots["datetime"]
                end_time = (dateparser.parse(slots["datetime"]) + datetime.timedelta(minutes=slots["duration"])).isoformat()
                update_booking(booking[0], slots["summary"], start_time, end_time, slots["timezone"])
                return {"response": f"Updated event to '{slots['summary']}' at {start_time} ({slots['timezone']})."}
            return {"response": "No matching event found to edit."}
        
        elif intent == "list":
            bookings = list_bookings()
            if not bookings:
                return {"response": "No events found."}
            response = "Your events:\n"
            for b in bookings:
                response += f"- {b[1]} at {b[3]} ({b[5]})\n"
            return {"response": response}
        
        elif intent == "check":
            start_time = slots["datetime"]
            end_time = (dateparser.parse(slots["datetime"]) + datetime.timedelta(minutes=slots["duration"])).isoformat()
            available = check_availability(start_time, end_time)
            if available:
                return {"response": f"You are free from {start_time} to {end_time}"}
            return {"response": f"You have events during that time"}
        
        elif intent == "help":
            return {"response": "I can help you with:\n- Booking new events\n- Cancelling events\n- Editing events\n- Listing your events\n- Checking availability\nJust let me know what you'd like to do!"}
        
        return {"response": "I'm not sure what you want to do. Try asking for help."}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}
