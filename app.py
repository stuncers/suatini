import streamlit as st
import requests
import uuid
import time

# 1. Page Configuration
st.set_page_config(page_title="Suat's AI Assistant", page_icon="🤖")
st.title("🤖 Chat with Suat's AI Assistant")

# Sidebar
with st.sidebar:
    st.header("Connect with Me")
    st.link_button("📅 Book a Call", "https://calendly.com/s-tuncersuat/15min")

# 2. Simple Authentication System
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Initialize Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if not st.session_state.authenticated:
    st.markdown("""
    Welcome! I am an AI agent trained on Suat's professional background. 
    I can answer questions about his **resume, technical skills, and projects**.

    If you would like to schedule a meeting directly, please use the 'Book a Call' button located in the left sidebar.
    
    *If you are a recruiter or hiring manager, please enter your access code below.*
    
    *Need a code? Reach out to **s.tuncersuat@gmail.com** or [LinkedIn](https://www.linkedin.com/in/suat-tuncer).*
    """)

    # Custom CSS to hide the "Press Enter to submit" instruction
    st.markdown("""
        <style>
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

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

# --- TABS ---
tab_chat, tab_arch = st.tabs(["💬 Chat", "🛠️ Architecture"])

with tab_chat:
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Suggested Questions
    # Only show if no conversation has started yet (len == 1 means just the assistant greeting)
    if len(st.session_state.messages) == 1:
        # Custom CSS for minimalist buttons
        st.markdown("""
            <style>
            /* Style the buttons to be pill-shaped and minimalist */
            div.stButton > button {
                border-radius: 20px;
                border: 1px solid #4b4b4b;
                background-color: transparent;
                color: #e0e0e0;
                font-size: 0.8rem;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
            }
            
            div.stButton > button:hover {
                border-color: #ff4b4b;
                color: #ff4b4b;
                background-color: rgba(255, 75, 75, 0.1);
            }
            </style>
        """, unsafe_allow_html=True)

        # Spacer to push buttons to the bottom-ish of the screen
        st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)

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

with tab_arch:
    st.header("System Architecture")
    st.markdown("This agent uses a **RAG (Retrieval-Augmented Generation)** pipeline to answer questions based on my resume and portfolio.")
    
    st.graphviz_chart("""
    digraph G {
        rankdir=LR;
        node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial"];
        
        User [shape=ellipse, fillcolor=lightgrey];
        Streamlit [label="Streamlit App\n(Frontend)"];
        n8n [label="n8n Workflow\n(Orchestrator)", fillcolor=orange];
        Pinecone [label="Pinecone\n(Vector DB)", fillcolor=lightgreen];
        OpenAI [label="OpenAI GPT-4o\n(LLM)", fillcolor=lightyellow];
        GoogleSheets [label="Google Sheets\n(Analytics & Logging)", fillcolor=lightpink];
        
        User -> Streamlit [label="Asks Question"];
        Streamlit -> n8n [label="Webhook (JSON)"];
        n8n -> Pinecone [label="Semantic Search"];
        Pinecone -> n8n [label="Retrieved Context"];
        n8n -> OpenAI [label="Prompt + Context"];
        OpenAI -> n8n [label="Answer"];
        n8n -> Streamlit [label="Response"];
        n8n -> GoogleSheets [label="Log Chat", style=dashed];
    }
    """)
    
    st.info("""
    **How it works:**
    1. **Ingestion**: My resume and project files are embedded and stored in **Pinecone**.
    2. **Retrieval**: When you ask a question, **n8n** searches Pinecone for relevant chunks of text.
    3. **Generation**: The retrieved text + your question are sent to **GPT-4o** to generate an accurate answer.
    4. **Analytics**: Every interaction is logged to **Google Sheets** for quality monitoring.
    """)
