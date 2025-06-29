import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="CalMate",
    page_icon="📅",
    layout="wide"
)

# API endpoint
import os

# Get API URL from environment variable or use default
API_URL = os.getenv("BACKEND_URL", "http://localhost:10000")

# Title and description
st.title("CalMate - Calendar Management")

# Chat interface
st.header("Chat with CalMate")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm here to help you manage your calendar. You can ask me to book meetings, check availability, or cancel bookings."
    })

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Show loading state
    with st.spinner("Thinking..."):
        try:
            # Send request to API with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={"message": prompt, "history": st.session_state.messages},
                        timeout=10  # Set timeout
                    )
                    
                    if response.status_code == 200:
                        # Add assistant response to chat history
                        response_data = response.json()
                        assistant_response = response_data["response"].get("response", "I'm sorry, I couldn't process that.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_response
                        })
                        break
                    else:
                        if attempt == max_retries - 1:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                        else:
                            time.sleep(1)  # Wait before retry
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        st.error(f"Error connecting to API: {str(e)}")
                    else:
                        time.sleep(1)  # Wait before retry
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    # Rerun to display the new message
    st.rerun()
