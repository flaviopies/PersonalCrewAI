import streamlit as st
from personal_crew.crew import create_crew
import json
from datetime import datetime
import re
import platform, sys

if platform.system() != "Windows":
    # só em Linux/Cloud, onde sqlite3 padrão é antigo
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Set page config
st.set_page_config(
    page_title="Personal CrewAI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Main Streamlit interface
st.title("🤖 Personal CrewAI Assistant")
st.write("""
Welcome to your personal AI assistant team! This application uses CrewAI to coordinate multiple specialized 
agents to help you with various tasks. The manager agent will coordinate with specialized agents to help 
you achieve your goals.
""")

# User input
user_input = st.text_area("What would you like help with?", height=100)

def format_event_response(response):
    """Format the event information in a more readable way."""
    try:
        # Clean up markdown formatting
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        
        # Split events into sections
        sections = re.split(r'\d+\.\s+', clean_text)
        sections = [s.strip() for s in sections if s.strip()]
        
        formatted_text = ""
        for section in sections:
            if section:
                # Extract event details
                lines = section.split('\n')
                event_name = lines[0].strip()
                details = '\n'.join(lines[1:]).strip()
                
                # Format with emojis and better structure
                formatted_text += f"🎉 {event_name}\n"
                formatted_text += f"   {details}\n\n"
        
        return formatted_text or response
    except Exception:
        return response

formatted_response = None
result = None

if st.button("Submit Request"):
    if user_input:
        try:
            with st.spinner("Searching for current events and activities..."):
                # Create and execute the crew
                crew = create_crew(user_input)
                result = crew.kickoff()
                
                # Extract and format the main response
                if isinstance(result, dict) and 'tasks_output' in result and result['tasks_output']:
                    task_output = result['tasks_output'][0]
                    if hasattr(task_output, 'raw'):
                        response_text = task_output.raw
                        if not isinstance(response_text, str):
                            response_text = str(response_text)
                        formatted_response = format_event_response(response_text)
                    else:
                        formatted_response = "No readable response available."
                else:
                    formatted_response = str(result)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "user", 
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": formatted_response,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display chat history first
st.header("💬 Chat History")
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "timestamp" in message:
                st.caption(f"Sent at: {datetime.fromisoformat(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

# Display current response if available
if formatted_response:
    st.header("📝 Current Response")
    st.write(formatted_response)
    
    # Technical details in an expander
    if result:
        with st.expander("🔍 Technical Details"):
            # Show token usage if available
            if isinstance(result, dict) and 'token_usage' in result:
                st.subheader("Token Usage")
                token_usage = result['token_usage']
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Total Tokens", token_usage.total_tokens)
                with cols[1]:
                    st.metric("Prompt Tokens", token_usage.prompt_tokens)
                with cols[2]:
                    st.metric("Completion Tokens", token_usage.completion_tokens)
                with cols[3]:
                    st.metric("Cached Tokens", token_usage.cached_prompt_tokens)
            
            # Show raw response
            st.subheader("Raw Response")
            st.json(str(result)) 