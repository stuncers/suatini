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
    st.write("Reach out to s.tuncersuat@gmail.com for access code.")
    
    password = st.text_input("Access Code", type="password")
    
    if st.button("Enter"):
        # Access secrets correctly
        if password in st.secrets["RECRUITER_KEYS"]:
            st.session_state.authenticated = True
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about my projects..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            # Call n8n
            response = requests.post(
                st.secrets["N8N_WEBHOOK_URL"],
                json={
                    "text": prompt,
                    "sessionId": st.session_state.session_id
                }
            )
            
            if response.status_code == 200:
                # Adjust 'output' to match your n8n JSON key
                bot_answer = response.json().get("Bot Answer", "I couldn't process that response.")
            else:
                bot_answer = f"Error: Status {response.status_code}"
                
        except Exception as e:
            bot_answer = f"Connection failed: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(bot_answer)
    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
