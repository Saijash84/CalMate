import streamlit as st
import requests
import json

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

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Send request to API
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": prompt, "history": st.session_state.messages}
        )
        
        if response.status_code == 200:
            # Add assistant response to chat history
            response_data = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["response"].get("response", "I'm sorry, I couldn't process that.")
            })
            
            # Rerun to display the new message
            st.rerun()
            
        else:
            st.error(f"Error: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
