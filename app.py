import streamlit as st
import requests
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Suat's AI Assistant", page_icon="🤖")
st.title("🤖 Chat with Suat's AI Assistant")

# 2. Simple Authentication System
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Initialize Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if not st.session_state.authenticated:
    st.markdown("### 🔒 Access Required")
    st.write("Please enter the access code provided to you.")
    st.write("Reach out to s.tuncersuat@gmail.com or https://www.linkedin.com/in/suat-tuncer for access code.")
    
    with st.form("auth_form"):
        password = st.text_input("Access Code", type="password")
        submitted = st.form_submit_button("Enter")
        
        if submitted:
            # Access secrets correctly
            if password in st.secrets["RECRUITER_KEYS"]:
                st.session_state.authenticated = True
                st.session_state.access_code = password
                st.success("Access Granted! Loading chat...")
                st.rerun()
            else:
                st.error("Invalid Access Code")
    st.stop() 

# 3. Chat Interface Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Suat's AI assistant. Ask me anything about his experience."}
    ]

import time

def stream_data(text):
    """Yields text word by word with a slight delay to simulate typing."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

def handle_chat(user_prompt):
    """Handles sending the user prompt to n8n and updating the chat history."""
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.spinner("Thinking..."):
        try:
            # Prepare payload
            payload = {
                "text": user_prompt,
                "sessionId": st.session_state.session_id,
                "accessCode": st.session_state.get("access_code", "unknown")
            }
            
            # Debug: Print payload to terminal
            print(f"Sending payload to n8n: {payload}")

            # Call n8n
            response = requests.post(
                st.secrets["N8N_WEBHOOK_URL"],
                json=payload
            )
            
            if response.status_code == 200:
                # Adjust 'output' to match your n8n JSON key
                bot_answer = response.json().get("Bot Answer", "I couldn't process that response.")
            else:
                bot_answer = f"Error: Status {response.status_code}"
                
        except Exception as e:
            bot_answer = f"Connection failed: {str(e)}"

    with st.chat_message("assistant"):
        st.write_stream(stream_data(bot_answer))
    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
    
    # Force a rerun to update the UI immediately (hides buttons, shows new history)
    st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested Questions
# Only show if no conversation has started yet (len == 1 means just the assistant greeting)
if len(st.session_state.messages) == 1:
    # Custom CSS for minimalist buttons and positioning
    st.markdown("""
        <style>
        /* Style the buttons to be pill-shaped and minimalist */
        div.stButton > button {
            border-radius: 20px;
            border: 1px solid #4b4b4b;
            background-color: transparent;
            color: #e0e0e0;
            font-size: 0.01rem;
            padding: 0.2rem 0rem;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            border-color: #ff4b4b;
            color: #ff4b4b;
            background-color: rgba(255, 75, 75, 0.1);
        }

        /* Position the container at the bottom, just above the chat input */
        /* We target the last horizontal block in the main container */
        div[data-testid="stHorizontalBlock"]:last-of-type {
            position: fixed;
            bottom: 115px; /* Adjust based on chat input height */
            left: 0;
            right: 0;
            margin: 0 auto;
            max-width: 700px; /* Match Streamlit's main column width */
            z-index: 99;
            padding: 1 1rem;
            background: transparent;
        }
        
        /* Hide the element decoration/border if any */
        div[data-testid="stHorizontalBlock"]:last-of-type > div {
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)

    questions = [
        "What is your experience with Python?",
        "How can I contact you?",
        "Tell me about your data science projects."
    ]
    
    # Use columns to center the buttons and make them smaller
    # Using 3 columns for 3 questions
    cols = st.columns(3)
    for i, question in enumerate(questions):
        if cols[i].button(question, use_container_width=True): # Use container width to fill the small columns evenly
            handle_chat(question)

# Chat Input
if prompt := st.chat_input("Ask about my projects..."):
    handle_chat(prompt)
