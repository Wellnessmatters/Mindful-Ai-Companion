import streamlit as st
import openai
import os
from datetime import datetime
import json
from PIL import Image
import io
# Load your uploaded logo from the repo (exact filename!)
logo = Image.open("Mindful_AI-removebg-preview.png")

# Convert to bytes buffer for favicon (this helps Cloud)
buf = io.BytesIO()
logo.save(buf, format="PNG")
byte_im = buf.getvalue()
st.set_page_config(
    page_title="Mindful AI Companion",
    page_icon=byte_im,  # Your lotus PNG as favicon!
    layout="centered",
    initial_sidebar_state="expanded",
)
# -------------------------- CONFIG --------------------------
st.title("🧠 Mindful AI Companion")
st.markdown("### Your 24/7 Mental Wellness Companion")
st.caption("Your 24/7 personal mental wellness coach • Always here to listen")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        "I'm an AI companion designed to help you manage stress, anxiety, and daily emotions. "
        "I'm not a therapist, but I can offer support, coping tools, and mindfulness exercises."
    )
    
    st.header("Upgrade for More 💎")
    # ── Premium upgrade button ──
PREMIUM_URL = "https://wellnessmatters12.gumroad.com/l/wvjaec"   # ← CHANGE THIS LINE

st.link_button(
    "Unlock Premium ($4.99/mo)",
    PREMIUM_URL,
    type="primary",
    help="Unlimited chats • Advanced mood insights • Custom plans • Ad-free",
    use_container_width=True)
    st.caption("Data is private • No accounts needed yet")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi there 👋 I'm your AI wellness companion. How are you feeling today? "
                       "You can tell me anything — I'm here to listen without judgment."
        }
    ]

if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

# Mood quick select
st.subheader("How are you feeling right now?")
mood_cols = st.columns(5)
moods = [("😊 Great", "great"), ("😐 Okay", "okay"), ("😔 Low", "low"), ("😰 Anxious", "anxious"), ("😴 Tired", "tired")]
selected_mood = None
for col, (emoji_label, mood_key) in zip(mood_cols, moods):
    if col.button(emoji_label, use_container_width=True):
        selected_mood = mood_key
        st.session_state.mood_history.append({"date": datetime.now().isoformat(), "mood": mood_key})
        st.success(f"Logged: Feeling {mood_key}")
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Share what's on your mind..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # System prompt for consistent wellness coaching
            system_prompt = {
                "role": "system",
                "content": (
                    "You are Mindful AI, a compassionate, non-judgmental mental wellness companion. "
                    "You help users with stress, anxiety, low mood, burnout, and daily challenges. "
                    "Use empathy first. Offer practical tools: breathing exercises, journaling prompts, "
                    "cognitive reframing, mindfulness tips. Never diagnose or replace therapy. "
                    "If someone seems in crisis, gently suggest professional help (e.g., crisis hotlines). "
                    "Keep responses warm, concise, and actionable. Use emojis sparingly for warmth."
                )
            }

            # Prepare messages for API
            api_messages = [system_prompt] + st.session_state.messages[-10:]  # Last 10 for context

            try:
                # Replace with your API key or use st.secrets
                client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast and cheap (~$0.15 per 1M tokens)
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                ai_reply = response.choices[0].message.content
            except Exception as e:
                ai_reply = (
                    "I'm having trouble connecting right now. Please try again in a moment. "
                    "In the meantime, try this quick breathing exercise: Inhale for 4, hold for 4, exhale for 6. 🌬️"
                )

        st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# Mood insights (basic version)
if len(st.session_state.mood_history) > 2:
    st.sidebar.header("Your Mood Trend")
    recent_moods = [entry["mood"] for entry in st.session_state.mood_history[-7:]]
    mood_map = {"great": 5, "okay": 3, "low": 1, "anxious": 2, "tired": 2}
    scores = [mood_map.get(m, 3) for m in recent_moods]
    avg = sum(scores) / len(scores)
    if avg >= 4:
        st.sidebar.success("You're trending positive lately! 🌟")
    elif avg >= 2.5:
        st.sidebar.info("Mixed feelings — that's normal.")
    else:
        st.sidebar.warning("You've had some tough days. Be gentle with yourself.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit • Not a substitute for professional care")
