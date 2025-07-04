import re
import dateparser
import pytz
from datetime import datetime, timedelta


def extract_intent(user_msg):
    """
    Extracts the intent from the user's message.
    Returns one of: 'book', 'cancel', 'edit', 'list', 'help'
    """
    lower_msg = user_msg.lower()
    
    if any(word in lower_msg for word in ['book', 'schedule', 'create', 'add', 'make']):
        return 'book'
    elif any(word in lower_msg for word in ['cancel', 'delete', 'remove']):
        return 'cancel'
    elif any(word in lower_msg for word in ['edit', 'change', 'modify']):
        return 'edit'
    elif any(word in lower_msg for word in ['list', 'show', 'view']):
        return 'list'
    else:
        return 'help'


def extract_attendees(user_msg):
    """
    Extracts attendees from the user's message.
    """
    # Simple pattern to extract names after "with" or "and"
    attendees = []
    words = user_msg.lower().split()
    
    for i, word in enumerate(words):
        if word in ['with', 'and']:
            # Take the next word as attendee
            if i + 1 < len(words):
                attendees.append(words[i + 1])
                
    return attendees


def extract_reference(user_msg):
    """
    Extracts a reference number from the user's message.
    """
    # Look for numbers that could be reference numbers
    numbers = re.findall(r'\b\d{3,}\b', user_msg)
    if numbers:
        return numbers[0]
    return None


def extract_slots(user_msg, context_event=None):
    """
    Extracts time slots from the user's message.
    Returns a list of tuples (start_time, end_time)
    """
    # Use dateparser to find dates/times in the message
    dates = search_dates(user_msg, languages=['en'])
    
    if not dates:
        return []
    
    slots = []
    for date in dates:
        dt = date[1]
        # If we have a context event, use its timezone
        if context_event and 'timezone' in context_event:
            tz = pytz.timezone(context_event['timezone'])
            dt = dt.astimezone(tz)
        
        # Create a slot that's 1 hour long
        start_time = dt.isoformat()
        end_time = (dt + timedelta(hours=1)).isoformat()
        slots.append((start_time, end_time))
    
    return slots


def format_event_natural(event):
    """
    Formats an event in natural language.
    """
    if isinstance(event, dict):
        # Dictionary format
        start = datetime.fromisoformat(event['start_time'])
        end = datetime.fromisoformat(event['end_time'])
        summary = event['summary']
        timezone = event.get('timezone', 'UTC')
    else:
        # Tuple format from database
        _, summary, _, start_time, end_time, timezone, _ = event
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    
    # Convert to UTC if timezone is not already set
    if start.tzinfo is None:
        start = pytz.UTC.localize(start)
    if end.tzinfo is None:
        end = pytz.UTC.localize(end)
    
    # Convert to local timezone for display
    if timezone:
        start = start.astimezone(pytz.timezone(timezone))
        end = end.astimezone(pytz.timezone(timezone))
    
    # Format time in 12-hour format with AM/PM
    start_time_str = start.strftime('%I:%M %p')
    end_time_str = end.strftime('%I:%M %p')
    
    # Get day name and date
    day_name = start.strftime('%A')
    date_str = start.strftime('%B %d, %Y')
    
    # Format the time range
    time_range = f"{start_time_str} to {end_time_str}"
    
    # Return formatted string
    if summary:
        return f"{summary} on {day_name} ({date_str}) from {time_range}"
    else:
        return f"Busy from {time_range} on {day_name} ({date_str})"


def find_booking_by_reference(reference, context_event=None):
    """
    Finds a booking by reference number.
    """
    if not reference:
        return None
    
    # This function would typically query the database
    # For now, we'll just return a dummy event
    return {
        'summary': f'Booking #{reference}',
        'start_time': datetime.now().isoformat(),
        'end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
        'attendees': ['John Doe']
    }
