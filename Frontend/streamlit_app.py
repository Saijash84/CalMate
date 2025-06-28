# streamlit_app.py

import streamlit as st
import requests
from datetime import datetime

# Function definitions
def fetch_events():
    try:
        res = requests.post(API_URL, json={"message": "list"})
        data = res.json()
        response_text = data.get("response", {}).get("response", "")
        
        upcoming, held = [], []
        if "Here are your upcoming events" in response_text:
            parts = response_text.split("\n\n")
            if len(parts) > 1:
                upcoming = [line for line in parts[0].split("\n")[1:] if line.strip()]
                held = [line for line in parts[1].split("\n")[1:] if line.strip()]
            else:
                upcoming = [line for line in parts[0].split("\n")[1:] if line.strip()]
        elif "You have no events scheduled." in response_text:
            upcoming, held = [], []
        st.session_state.events = {"upcoming": upcoming, "held": held}
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")
        st.error(f"Response data: {res.text if hasattr(res, 'text') else 'No response data'}")

def handle_message(message):
    with st.spinner("Thinking..."):
        try:
            res = requests.post(API_URL, json={"message": message})
            res.raise_for_status()
            data = res.json()
            reply = data["response"]["response"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            fetch_events()
            st.experimental_rerun()
        except Exception as e:
            reply = f"❌ Error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

st.set_page_config(page_title="CalMate", page_icon="📅", layout="wide")

API_URL = "http://localhost:8000/chat"

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.75rem;
        font-size: 1rem;
        border-radius: 0.5rem;
    }
    .event-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .event-time {
        color: #6c757d;
        font-size: 0.9rem;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 CalMate: Your Smart Calendar Assistant")
st.caption("Book, edit, cancel, and view your events with natural language.")

st.info(
    "💡 **How to use CalMate:**\n"
    "- Book an event: `Book an event tomorrow at 10am for 1 hour with Alice`\n"
    "- Cancel an event: `Cancel my last event` or `Cancel my 2pm event`\n"
    "- Edit an event: `Reschedule my next event to Friday at 3pm`\n"
    "- List events: `What are my events this week?`\n"
    "- Check availability: `When am I free tomorrow?`\n"
    "- You can also use natural language like 'Add a call after lunch next Monday.'"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "events" not in st.session_state:
    st.session_state.events = {"upcoming": [], "held": []}

# Main chat area
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Display chat history
    for msg in st.session_state.messages:
        message_class = "assistant-message" if msg["role"] == "assistant" else "user-message"
        st.markdown(f"<div class='{message_class}'>"
                    f"{msg['content']}"
                    f"</div>", unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        handle_message(prompt)

    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar menu
with st.sidebar:
    st.header("📅 Menu")
    
    # Quick action buttons
    st.subheader("Quick Actions")
    if st.button("Book Event"):
        st.session_state.messages.append({"role": "user", "content": "Book a new event"})
        handle_message("Book a new event")
    if st.button("Cancel Event"):
        st.session_state.messages.append({"role": "user", "content": "Cancel an event"})
        handle_message("Cancel an event")
    if st.button("Edit Event"):
        st.session_state.messages.append({"role": "user", "content": "Edit an event"})
        handle_message("Edit an event")
    if st.button("List Events"):
        st.session_state.messages.append({"role": "user", "content": "List my events"})
        handle_message("List my events")
    if st.button("Check Availability"):
        st.session_state.messages.append({"role": "user", "content": "When am I free tomorrow?"})
        handle_message("When am I free tomorrow?")
    
    # Events display
    st.markdown("---")
    st.subheader("Upcoming Events")
    fetch_events()
    if st.session_state.events["upcoming"]:
        for event in st.session_state.events["upcoming"]:
            with st.container():
                st.markdown(f"<div class='event-card'>"
                           f"<strong>{event.split(' on ')[0]}</strong><br>"
                           f"<span class='event-time'>{event.split(' on ')[1]}</span>"
                           f"</div>", unsafe_allow_html=True)
    else:
        st.write("No upcoming events.")
    
    st.subheader("Past Events")
    if st.session_state.events["held"]:
        for event in st.session_state.events["held"]:
            with st.container():
                st.markdown(f"<div class='event-card'>"
                           f"<strong>{event.split(' on ')[0]}</strong><br>"
                           f"<span class='event-time'>{event.split(' on ')[1]}</span>"
                           f"</div>", unsafe_allow_html=True)
    else:
        st.write("No past events.")
