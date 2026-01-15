import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from agents.graph_agent import GraphAgent
from voice.stt import STTProvider
from voice.tts import TTSProvider

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Auto Dealership Voice Assistant", 
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        font-weight: bold;
    }
    .call-btn>button {
        background-color: #2ecc71;
        color: white;
        height: 5em;
        font-size: 1.5em;
    }
    .end-btn>button {
        background-color: #e74c3c;
        color: white;
    }
    .chat-container {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    try:
        st.session_state.agent = GraphAgent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}. Check API Key.")
if "stt" not in st.session_state:
    st.session_state.stt = STTProvider()
if "tts" not in st.session_state:
    st.session_state.tts = TTSProvider()
if "call_active" not in st.session_state:
    st.session_state.call_active = False

# --- Sidebar (Dashboard) ---
with st.sidebar:
    st.header("🚗 Dashboard")
    bookings_file = "data/bookings.json"

    def load_bookings():
        if os.path.exists(bookings_file):
            with open(bookings_file, "r") as f:
                return json.load(f)
        return []

    bookings_data = load_bookings()
    if bookings_data:
        df = pd.DataFrame(bookings_data)
        if not df.empty:
            cols = ["car_model", "date", "time"]
            display_df = df[cols] if all(c in df.columns for c in cols) else df
            st.dataframe(display_df, hide_index=True, use_container_width=True)
    else:
        st.info("No bookings yet.")

    if st.button("Refresh Data"):
        st.rerun()

# --- Main Interface ---
st.title("Auto Dealership Assistant")

# Logic to handle Greeting on Call Start
def start_call():
    st.session_state.call_active = True
    st.session_state.messages = []
    
    greeting = "Hello! Thanks for calling the Auto Dealership. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    
    # We can't easily trigger TTS *during* the rerun logic without blocking, 
    # so we'll set a flag to speak it on the next render.
    st.session_state.should_greet = True

def end_call():
    st.session_state.call_active = False
    st.session_state.messages = []

# --- View: Call Start Screen ---
if not st.session_state.call_active:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 👋 Ready to help you book a test drive!")
        st.write("")
        st.write("")
        # Using a container to center visually
        with st.container():
            st.markdown('<div class="call-btn">', unsafe_allow_html=True)
            if st.button("📞 Start Call", key="start_call_btn", on_click=start_call):
                pass # Logic handled in on_click
            st.markdown('</div>', unsafe_allow_html=True)

# --- View: Active Call Screen ---
else:
    # Header Controls
    col_head1, col_head2 = st.columns([5, 1])
    with col_head2:
        st.markdown('<div class="end-btn">', unsafe_allow_html=True)
        if st.button("End Call", on_click=end_call):
            pass
        st.markdown('</div>', unsafe_allow_html=True)

    # Handle Greeting TTS (One-time)
    if st.session_state.get("should_greet", False):
        greeting = st.session_state.messages[0]["content"]
        with st.spinner("Agent Greeting..."):
            st.session_state.tts.speak(greeting)
        st.session_state.should_greet = False

    # Display Chat History
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Processing Logic
    def process_user_input(user_text):
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_text)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response_text = st.session_state.agent.process_input(user_text)
            st.markdown(response_text)
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        with st.spinner("Speaking..."):
            st.session_state.tts.speak(response_text)
        
        st.rerun()

    # --- Continuous Conversation Loop ---
    
    # Placeholder for status
    status_placeholder = st.empty()
    
    # Check if we should listen automatically
    if st.session_state.call_active:
        
        # 1. Listen
        status_placeholder.info("👂 Listening...")
        # Shorten duration slightly for better responsiveness or keep 5s
        voice_text = st.session_state.stt.listen(prompt="Auto-Listen")
        
        if voice_text:
            # Reset silence counter
            st.session_state.silence_count = 0
            
            # 2. Process
            status_placeholder.info("🧠 Thinking...")
            process_user_input(voice_text) # This handles TTS and Rerun
            
        else:
            # Handle Silence
            st.session_state.silence_count = st.session_state.get("silence_count", 0) + 1
            status_placeholder.warning("No speech detected.")
            
            if st.session_state.silence_count >= 2:
                # Ask user to speak again after 2 failed attempts
                nudge = "I didn't hear anything. Are you still there?"
                st.session_state.messages.append({"role": "assistant", "content": nudge})
                with st.spinner("Speaking..."):
                    st.session_state.tts.speak(nudge)
                st.session_state.silence_count = 0 # Reset or keep counting? Reset to avoid loop spam
                st.rerun()
            else:
                # Just rerun to listen again immediately
                st.rerun()
