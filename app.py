import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import os
from pydantic import BaseModel, Field
from typing import List
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & DEEP DARK CSS INJECTION
# ==========================================
st.set_page_config(page_title="Nexus", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Ultra-Dark Cyberpunk Theme
dark_system_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&family=Inter:wght@400;600;800&display=swap');

/* Hide Default Streamlit Header, Deploy Button, Menu, and Footer */
header, [data-testid="stHeader"], .stAppHeader, #MainMenu, footer, .stDeployButton {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}

/* Base Body and App Canvas */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #03060d !important;
    color: #e0f2fe !important;
}

/* Remove Top Padding/Whitespace */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
}

/* Dark Styling for All Input Boxes */
div[data-baseweb="input"], input, textarea, div[data-baseweb="select"] {
    background-color: #0a1124 !important;
    color: #00f0ff !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 6px !important;
}

div[data-baseweb="select"] > div {
    background-color: #0a1124 !important;
    color: #00f0ff !important;
}

/* Custom Cyber Terminal Box for Command Prompt Area */
.terminal-box {
    background: #060d1f;
    border: 1px solid #00f0ff;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    margin-top: 10px;
    margin-bottom: 10px;
}

.terminal-header {
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #00f0ff;
    letter-spacing: 1px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Cyber Title Styling */
.cyber-title {
    font-size: 2.2rem;
    font-weight: 800;
    font-family: 'Fira Code', monospace;
    background: linear-gradient(90deg, #ffffff 0%, #00f0ff 50%, #0055ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
    margin-bottom: 0px;
}

/* Metric Cards */
.metric-card {
    background: rgba(10, 18, 38, 0.8);
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 6px;
    padding: 12px 18px;
    box-shadow: inset 0 0 15px rgba(0, 85, 255, 0.15);
}

.metric-label {
    font-family: 'Fira Code', monospace;
    font-size: 0.7rem;
    color: #00f0ff;
    text-transform: uppercase;
}

.metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
}

/* Expanders / Exercise Cards */
.streamlit-expanderHeader {
    background: #081024 !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    color: #ffffff !important;
    font-family: 'Fira Code', monospace !important;
}

.streamlit-expanderContent {
    background: #040814 !important;
    border: 1px solid rgba(0, 85, 255, 0.3) !important;
    border-top: none !important;
}

/* Primary Execution Button */
.stButton>button {
    background: linear-gradient(135deg, #0055ff 0%, #00f0ff 100%) !important;
    color: #000000 !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
}

/* Sidebar Dark Styling */
[data-testid="stSidebar"] {
    background-color: #02040a !important;
    border-right: 1px solid rgba(0, 240, 255, 0.2);
}
</style>
"""
st.markdown(dark_system_css, unsafe_allow_html=True)

# ==========================================
# 2. AI CONFIGURATION & SCHEMAS
# ==========================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["AQ.Ab8RN6IsK_iQO1Oe0KofwD-75khI0cRXyV2pp9vwn8vgStXtGw"])
else:
    genai.configure(api_key="AQ.Ab8RN6IsK_iQO1Oe0KofwD-75khI0cRXyV2pp9vwn8vgStXtGw")

class Exercise(BaseModel):
    name: str = Field(description="Name of exercise")
    reps: str = Field(description="Sets x Reps string")
    target_muscle: str
    form_instructions: str
    common_mistakes: str

class WorkoutPlan(BaseModel):
    workout_summary: str
    exercises: List[Exercise]
    diet_plan: List[str]
    voice_greeting: str

# Use stable model endpoint
model = genai.GenerativeModel("gemini-3.6-flash")

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.markdown("<h3 style='color:#00f0ff; font-family:\"Fira Code\";'>⚡ Configuration</h3>", unsafe_allow_html=True)

name = st.sidebar.text_input("USER_ID", "Mr. Manu")
goal = st.sidebar.selectbox("PRIMARY_OBJECTIVE", ["Muscle Gain", "Fat Loss", "Strength & Power"])
focus = st.sidebar.selectbox("TARGET_SYSTEM", ["Abs & Core", "Biceps & Arms", "Triceps & Chest", "Full Body", "Legs"])
diet = st.sidebar.selectbox("FUEL_PROTOCOL", ["High Protein", "Vegan", "Keto", "Balanced"])

execute_btn = st.sidebar.button("Talk to Nexus", use_container_width=True)

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)
    except Exception as e:
        pass

# ==========================================
# 4. MAIN DASHBOARD DISPLAY
# ==========================================
st.markdown("<div class='cyber-title'>Nexus</div>", unsafe_allow_html=True)
st.markdown("<p style='color:#00f0ff; font-family:\"Fira Code\"; font-size:0.85rem;'>SYSTEM STATUS: <span style='color:#ffffff;'>ACTIVE</span> | WAKE WORD: <span style='color:#00f0ff;'>'Nexus'</span></p>", unsafe_allow_html=True)

# Metric Bar
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>User Node</div><div class='metric-value'>{name}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Target Vector</div><div class='metric-value'>{focus}</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Objective</div><div class='metric-value'>{goal}</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Fuel Type</div><div class='metric-value'>{diet}</div></div>", unsafe_allow_html=True)

# ==========================================
# 5. COMMAND PROMPT AREA
# ==========================================
st.markdown("""
<div class="terminal-box">
    <div class="terminal-header">
        <span>⚡</span> <span>Talk to Nexus</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Styled Text Input Prompt
user_text = st.text_input("PROMPT_INPUT", placeholder="Say 'Nexus' or type a command...", label_visibility="collapsed")

# ==========================================
# 6. FIXED SPEECH RECOGNITION (WAKE & RESPOND)
# ==========================================
wake_word_js = """
<script>
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (window.SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const lastIndex = event.results.length - 1;
        const transcript = event.results[lastIndex][0].transcript.trim();
        console.log("Heard:", transcript);

        // Check if user spoke 'nexus'
        if (transcript.toLowerCase().includes('nexus')) {
            // 1. Find text input box and fill spoken text
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                if (input.placeholder.includes('Say') || input.ariaLabel === 'PROMPT_INPUT') {
                    input.value = transcript;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });

            // 2. Click the 'Talk to Nexus' button automatically
            setTimeout(() => {
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.innerText.includes('Talk to Nexus')) {
                        btn.click();
                    }
                });
            }, 300);
        }
    };

    recognition.onerror = (e) => { recognition.start(); };
    recognition.onend = () => { recognition.start(); };
    recognition.start();
}
</script>
"""
components.html(wake_word_js, height=0, width=0)

# ==========================================
# 7. AI RESPONSE ENGINE
# ==========================================
if execute_btn or user_text:
    prompt = f"""
    You are Nexus AI, an elite futuristic fitness and nutrition coach.
    User Profile: Name: {name}, Goal: {goal}, Focus Area: {focus}, Diet: {diet}.
    Custom Input from user: {user_text if user_text else 'Wake word activated standard protocol initialization.'}
    
    Return a structured json matching the exact schema:
    1. 'voice_greeting' greeting for {name} addressing their input directly.
    2. 'workout_summary' string.
    3. 'exercises' list with detailed exercise information.
    4. 'diet_plan' list of fuel tips.
    """
    
    with st.spinner("Processing System Protocol..."):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=WorkoutPlan
                )
            )
            
            plan_data = json.loads(response.text)
            
            # Speak and display
            speak_text(plan_data["voice_greeting"])
            st.code(f"Nexus: {plan_data['workout_summary']}", language="bash")

            col1, col2 = st.columns([2, 1])

            # Workout Section
            with col1:
                st.markdown(f"### {focus.upper()}")
                for idx, ex in enumerate(plan_data["exercises"], 1):
                    with st.expander(f"[{idx:02d}] {ex['reps']} >> {ex['name']}"):
                        st.markdown(f"**🎯 TARGET SUBSYSTEM:** `{ex['target_muscle']}`")
                        st.markdown(f"**📋 FORM INSTRUCTIONS:**\n{ex['form_instructions']}")
                        st.markdown(f"**⚠️ RUNTIME ERRORS TO AVOID:**\n{ex['common_mistakes']}")

            # Diet Section
            with col2:
                st.markdown(f"### FUEL MATRIX - {diet.upper()}")
                for meal in plan_data["diet_plan"]:
                    st.markdown(f"* `{meal}`")

        except Exception as e:
            st.error(f"System Error: {e}")