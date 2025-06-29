import streamlit as st
import requests
import json
from datetime import datetime
import time
import pytz

# Configure page
st.set_page_config(
    page_title="CalMate",
    page_icon="📅",
    layout="wide"
)

# API endpoint
import os

# Get API URL from environment variable or use default
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Navigation menu
with st.sidebar:
    st.markdown("# Navigation")
    st.markdown("- [Home](#calmate-calendar-management)")
    st.markdown("- [Book a Meeting](#book-a-meeting)")
    st.markdown("- [Check Availability](#check-availability)")
    st.markdown("- [Cancel Booking](#cancel-booking)")
    st.markdown("- [View Schedule](#view-schedule)")
    st.markdown("---")
    st.markdown("# Quick Actions")
    st.markdown("- [Book a Meeting](#book-a-meeting)")
    st.markdown("- [Check Availability](#check-availability)")
    st.markdown("- [Cancel Booking](#cancel-booking)")

# Main content
st.title("CalMate - Calendar Management")

# Home Section
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Welcome to CalMate")
    st.markdown("""
    Your intelligent calendar assistant that helps you manage your schedule with natural language.
    Just type what you want to do and CalMate will take care of it!
    """)
    
    # Quick stats
    st.subheader("Quick Stats")
    col1, col2, col3 = st.columns(3)
    
    # Get upcoming events
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": "List my upcoming events"},
            timeout=10
        )
        if response.status_code == 200:
            events = response.json().get("response", "No events found")
            st.info(f"Upcoming Events: {events}")
        else:
            st.error(f"Failed to fetch events: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")

with col2:
    st.header("Quick Actions")
    action = st.selectbox(
        "What would you like to do?",
        ["Book a Meeting", "Check Availability", "Cancel Booking", "View Schedule"]
    )
    
    if action == "Book a Meeting":
        st.markdown("---")
        st.subheader("Book a Meeting")
        with st.form("booking_form_1"):
            summary = st.text_input("Meeting Title", "Team Meeting")
            date = st.date_input("Date", datetime.now().date())
            time = st.time_input("Time", datetime.now().time())
            duration = st.number_input("Duration (minutes)", min_value=15, value=30, step=15)
            attendees = st.text_input("Attendees (comma-separated)", "")
            
            if st.form_submit_button("Book Meeting"):
                with st.spinner("Booking your meeting..."):
                    try:
                        message = f"Book a meeting titled '{summary}' on {date} at {time} for {duration} minutes"
                        if attendees:
                            message += f" with {attendees}"
                        
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"message": message},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()["response"]
                            st.success(result)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error booking meeting: {str(e)}")
    
    elif action == "Check Availability":
        st.markdown("---")
        st.subheader("Check Availability")
        with st.form("availability_form_1"):
            date = st.date_input("Check Date", datetime.now().date())
            time = st.time_input("Check Time", datetime.now().time())
            duration = st.number_input("Duration (minutes)", min_value=15, value=30, step=15)
            
            if st.form_submit_button("Check Availability"):
                with st.spinner("Checking availability..."):
                    try:
                        message = f"Check my availability on {date} at {time} for {duration} minutes"
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"message": message},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()["response"]
                            st.info(result)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error checking availability: {str(e)}")
    
    elif action == "Cancel Booking":
        st.markdown("---")
        st.subheader("Cancel Booking")
        with st.form("cancel_form_1"):
            event_title = st.text_input("Event Title to Cancel", "")
            
            if st.form_submit_button("Cancel Booking"):
                with st.spinner("Cancelling booking..."):
                    try:
                        message = f"Cancel the meeting titled '{event_title}'"
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"message": message},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()["response"]
                            st.success(result)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error cancelling booking: {str(e)}")
    
    elif action == "View Schedule":
        st.markdown("---")
        st.subheader("View Schedule")
        with st.form("view_form_1"):
            date = st.date_input("View Schedule For", datetime.now().date())
            
            if st.form_submit_button("View Schedule"):
                with st.spinner("Fetching your schedule..."):
                    try:
                        message = f"Show my schedule for {date}"
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"message": message},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()["response"]
                            st.info(result)
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error viewing schedule: {str(e)}")

# Chat interface
st.markdown("---")
with st.chat_message("assistant"):
    st.write("Hi! I'm here to help you manage your calendar. What would you like to do?")

# Chat interface
st.markdown("---")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("Ask me anything!", key="chat_input_1"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": prompt, "messages": st.session_state.messages},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()["response"]
                st.session_state.messages.append({"role": "assistant", "content": data})
                st.rerun()
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")    
    with col1:
        st.metric("Upcoming Events", "0")
    with col2:
        st.metric("Today's Meetings", "0")
    with col3:
        st.metric("Free Time", "0")

with col2:
    # Chat interface
    with st.chat_message("assistant"):
        st.write("Hi! I'm here to help you manage your calendar. What would you like to do?")
    
    if prompt := st.chat_input("Ask me anything!"):
        st.chat_message("user").write(prompt)
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": prompt},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.chat_message("assistant").write(data["response"])
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Upcoming Events Section
st.header("Upcoming Events")
try:
    response = requests.post(
        f"{API_URL}/chat",
        json={"message": "Show me my upcoming events"},
        timeout=10
    )
    
    if response.status_code == 200:
        events = response.json()["response"]
        if events:
            for event in events:
                st.write(f"- {event['details']}")
        else:
            st.info("No upcoming events scheduled.")
except Exception as e:
    st.error(f"Error fetching events: {str(e)}")

# Availability Section
st.header("Availability")
with st.form("availability_form"):
    date = st.date_input("Select date")
    time = st.time_input("Select time")
    duration = st.slider("Duration (minutes)", 15, 120, 30)
    
    if st.form_submit_button("Check Availability"):
        try:
            message = f"Check my availability on {date} at {time} for {duration} minutes"
            with st.spinner("Checking availability..."):
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"message": message},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()["response"]
                    if isinstance(result, dict):
                        st.write(result["details"])
                    else:
                        st.write(result)
                else:
                    st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error checking availability: {str(e)}")

# Book Meeting Section
st.header("Book Meeting")
with st.form("booking_form"):
    summary = st.text_input("Meeting Title")
    attendees = st.text_input("Attendees (comma separated)")
    date = st.date_input("Date")
    time = st.time_input("Time")
    duration = st.slider("Duration (minutes)", 15, 120, 30)
    
    if st.form_submit_button("Book Meeting"):
        try:
            message = f"Book a meeting titled '{summary}' with {attendees} on {date} at {time} for {duration} minutes"
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": message},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()["response"]
                st.success(result["details"])
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error booking meeting: {str(e)}")

# View Schedule Section
st.header("View Schedule")
with st.form("view_form"):
    period = st.selectbox("View period", ["Today", "Tomorrow", "This Week", "Next Week"])
    
    if st.form_submit_button("View Schedule"):
        try:
            message = f"Show me my schedule for {period.lower()}"
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": message},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()["response"]
                st.write(result["details"])
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error viewing schedule: {str(e)}")
