import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Fetch the key from the environment
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("Error: API Key not found in .env file.")

# 1. Configuration & Rebranding
st.set_page_config(page_title="Pure Fit", layout="wide", page_icon="🏋️‍♂️")

# 2. Initialize Session State
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        'goals': 'Lose 10 pounds and gain muscle',
        'conditions': 'None',
        'routines': 'Sedentary, 2 days of walking',
        'preferences': 'High protein, Vegetarian',
        'restrictions': 'No dairy',
        'sleep_hours': '7',
        'stress_level': 'Medium'
    }

# 3. Core AI Function (Fixed for 404 and Multimodal errors)
def get_gemini_response(prompt, image_data=None):
    # Using 'gemini-2.5-flash' for the best stability across regions
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        if image_data:
            # Correct format for passing Image + Text
            response = model.generate_content([prompt, image_data[0]])
        else:
            # Text-only call
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}. Please check your API key and internet connection."

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    return None

# --- APP UI ---
st.title("⚡ Pure Fit: AI Performance Coach")
st.markdown("---")

tab_setup, tab_workout, tab_meal, tab_analysis, tab_recovery, tab_chat = st.tabs([
    "🎯 Goal Assessment", 
    "💪 Workout Planning",
    "🥗 Meal Planning", 
    "📸 Food Analysis", 
    "🛌 Recovery & Lifestyle",
    "💡 Health Insights"
])

# TAB 1: INITIAL SETTING & GOAL ASSESSMENT
with tab_setup:
    st.subheader("📋 Your Fitness Profile")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            goals = st.text_area("Primary Goals", value=st.session_state.health_profile['goals'])
            routines = st.text_area("Current Routine/Level", value=st.session_state.health_profile['routines'])
            conditions = st.text_input("Medical Conditions", value=st.session_state.health_profile['conditions'])
        with col2:
            prefs = st.text_area("Food Preferences", value=st.session_state.health_profile['preferences'])
            restric = st.text_area("Dietary Restrictions", value=st.session_state.health_profile['restrictions'])
            sleep = st.select_slider("Avg Sleep Hours", options=["<5", "6", "7", "8", "9+"], value=st.session_state.health_profile['sleep_hours'])
            
        if st.form_submit_button("Update Pure Fit Profile"):
            st.session_state.health_profile.update({
                'goals': goals, 'routines': routines, 'conditions': conditions,
                'preferences': prefs, 'restrictions': restric, 'sleep_hours': sleep
            })
            st.success("Profile Analyzed! Your plans will now be tailored.")

# TAB 2: PERSONALIZED WORKOUT PLANNING
with tab_workout:
    st.subheader("🏋️‍♂️ AI Strength & Conditioning")
    col_w1, col_w2 = st.columns([1, 2])
    with col_w1:
        equipment = st.multiselect("Available Equipment", ["Full Gym", "Dumbbells", "Bodyweight", "Bands"])
        days = st.slider("Days per week", 1, 7, 3)
        
    if st.button("Generate My Workout Plan"):
        with st.spinner("Building your split..."):
            prompt = f"Trainer Mode: Create a {days}-day split for: {st.session_state.health_profile['goals']} with {equipment} equipment."
            st.markdown(get_gemini_response(prompt))

# TAB 3: MEAL PLANNING
with tab_meal:
    st.subheader("🥗 Precision Nutrition")
    if st.button("Generate Weekly Meal Plan"):
        with st.spinner("Optimizing macros..."):
            prompt = f"Nutritionist Mode: 7-day plan for {st.session_state.health_profile['goals']}. Prefs: {st.session_state.health_profile['preferences']}. Restric: {st.session_state.health_profile['restrictions']}."
            st.markdown(get_gemini_response(prompt))

# TAB 4: FOOD ANALYSIS
with tab_analysis:
    st.subheader("📸 Instant Macro Analysis")
    uploaded_file = st.file_uploader("Snap a photo of your meal", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        with st.spinner("Loading Image..."):
         st.image(Image.open(uploaded_file), width=400)
        if st.button("Analyze Plate"):
            with st.spinner("Analyzing Plate..."):
             img_data = input_image_setup(uploaded_file)
             st.markdown(get_gemini_response("Analyze macros and calories in this food image.", img_data))

# TAB 5: RECOVERY & LIFESTYLE
with tab_recovery:
    st.subheader("🛌 Recovery & Human Optimization")
    if st.button("Generate Recovery Protocol"):
        with st.spinner("Generating Content..."):
         prompt = f"Coach Mode: Suggest recovery tips for someone sleeping {st.session_state.health_profile['sleep_hours']} hours with this routine: {st.session_state.health_profile['routines']}"
         st.markdown(get_gemini_response(prompt))

# TAB 6: HEALTH INSIGHTS
with tab_chat:
    st.subheader("💡 Pure Fit Knowledge Base")
    query = st.text_input("Ask a health question:")
    if st.button("Ask Expert"):
        st.markdown(get_gemini_response(f"Answer using science: {query}"))

st.markdown("---")
st.caption("Pure Fit AI is an assistant. Always consult a physician before starting new programs.")