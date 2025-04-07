import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import os
import speech_recognition as sr
import time

# Download necessary NLTK corpora
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("MY_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Function to analyze mood (using TextBlob sentiment analysis)
def analyze_mood(text):
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0:
        return "Positive 😊"
    elif sentiment < 0:
        return "Negative 😞"
    else:
        return "Neutral 😐"
# Function to get detailed encouragement, including music, quotes, messages, and a joke
def get_encouragement(mood, user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = (f"The user is feeling {mood}. They said: '{user_input}'. "
                  f"Provide a detailed response including:\n"
                  f"- A powerful quote to start with\n"
                  f"- An encouraging message (5 lines)\n"
                  f"- Three to four motivational quotes (in bullet points)\n"
                  f"- Three to four music recommendations suited for their mood\n"
                  f"- End with a light-hearted joke to make them smile.")
        response = model.generate_content(prompt)
        
        # Ensure AI always provides a response
        if not response.text.strip():
            response.text = ("Start with this powerful quote:\n"
                             "\"The only way to do great work is to love what you do.\" - Steve Jobs\n\n"
                             "Here are some ways to lift your spirits:\n"
                             "- Stay positive and remind yourself of your strengths.\n"
                             "- Listen to uplifting music.\n"
                             "- Take deep breaths and relax.\n"
                             "- Here's a joke to make you smile: Why don’t skeletons fight each other? They don’t have the guts.")
        return response.text
    except Exception:
        return ("Start with this powerful quote:\n"
                "\"The only way to do great work is to love what you do.\" - Steve Jobs\n\n"
                "Here are some ways to lift your spirits:\n"
                "- Stay positive and remind yourself of your strengths.\n"
                "- Listen to uplifting music.\n"
                "- Take deep breaths and relax.\n"
                "- Here's a joke to make you smile: Why don’t skeletons fight each other? They don’t have the guts.")
# Function to get meditation and exercise suggestions
def get_meditation_and_exercises(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"They said: '{user_input}'. Provide meditation exercises and physical activities to help."
        response = model.generate_content(prompt)
        
        # Ensure AI always provides a response
        if not response.text.strip():
            response.text = "Try breathing exercises, light stretching, or a short walk to clear your mind."
        return response.text
    except Exception:
        return "Try breathing exercises, light stretching, or a short walk to clear your mind."
    
# Function to convert speech to text using speech_recognition library
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now!")
        audio = recognizer.listen(source)
        try:
            # Recognizing speech using Google's Speech Recognition API
            text = recognizer.recognize_google(audio)
            st.write("You said: " + text)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
            return ""
# Initialize session state for user input
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Streamlit UI setup
st.set_page_config(page_title="Your Wellbeing Friend", page_icon="🌱", layout="centered")
st.title("Your Wellbeing Friend 🌱")
st.write("Enter how you're feeling, and I'll suggest something to brighten your day!")

# User Input for Journal (messages won't persist after leaving the app)
user_input = st.text_area("How are you feeling today? (This is your Journal, it won't be saved after you leave)", "")
if st.button("Start the Magic!🪄"):
    if user_input.strip():
        st.session_state.user_input = user_input
        st.success("Magic started! Check the encouragement tab for suggestions. ✨")
    else:
        st.warning("Please enter a journal entry!")

# Button for Speech-to-Text functionality
if st.button("🎤 Use Speech to Text"):
    speech_input = speech_to_text()
    if speech_input.strip():
        st.session_state.user_input = speech_input
        st.success("Your speech has been converted to text!")

# Function to add a customizable timer in the sidebar with enhanced UI and stop feature
def meditation_timer():
    # Style the sidebar with a background color and title
    st.sidebar.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: #F4F9FF;
        }
        .sidebar header {
            font-size: 20px;
            color: #4B9E8A;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.sidebar.header("🧘‍♀️ Meditation Timer")
    
    # Ask the user to select a meditation duration using the slider
    duration_minutes = st.sidebar.slider(
        "Select Meditation Duration (minutes)",
        min_value=1, max_value=60, value=5, step=1, help="Choose how long you want to meditate"
    )
    
    # Show a message with the selected duration
    st.sidebar.write(f"🕰️ **Selected Meditation Duration**: {duration_minutes} minutes.")
    
    # Add buttons to start and stop the timer
    start_button = st.sidebar.button("✨ Start Meditation Timer")
    stop_button = st.sidebar.button("❌ Stop Meditation Timer")
    
    # Timer state to track whether it's running
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False

    # If the user presses the "Start Meditation Timer" button, begin the countdown
    if start_button and not st.session_state.timer_running:
        st.session_state.timer_running = True
        total_seconds = duration_minutes * 60  # Convert minutes to seconds
        countdown_seconds = total_seconds
        
        # Display initial countdown info with a welcoming emoji
        timer_text = f"🔮 **Starting meditation...** Focus on your breath for {duration_minutes} minutes."
        timer_display = st.empty()
        
        # Countdown loop
        while countdown_seconds > 0 and st.session_state.timer_running:
            minutes, seconds = divmod(countdown_seconds, 60)
            timer_display.markdown(f"**⏳ Time remaining**: {minutes} min {seconds} sec", unsafe_allow_html=True)
            time.sleep(1)  # Wait for 1 second
            countdown_seconds -= 1
        
        # Once the timer reaches 0, or if the timer is stopped, display a meditation completed message
        if st.session_state.timer_running:
            timer_display.markdown("🎉 **Meditation Completed!** 🧘‍♀️✨")
            st.balloons()  # Celebrate with balloons
        else:
            timer_display.markdown("⏹️ **Meditation Stopped!** 🛑")
        
        # Reset timer state
        st.session_state.timer_running = False

    # If the user presses the "Stop Meditation Timer" button, stop the timer
    if stop_button and st.session_state.timer_running:
        st.session_state.timer_running = False
        st.write("🛑 **Timer stopped!**")
        # Optional: Reset the timer to its initial state
        st.session_state.timer_running = False

# Call the meditation_timer function
meditation_timer()


# Tabs: Encouragement (Includes Music, Quotes, and Encouragement), Meditation & Exercises
tabs = st.selectbox("Select your Wellbeing Activity", ["💡 Encouragement", "🧘 Meditation & Exercises"])

if st.session_state.user_input.strip():
    mood = analyze_mood(st.session_state.user_input)
    
    if tabs == "💡 Encouragement":
        st.subheader("💡 Your Personalized Encouragement")
        encouragement = get_encouragement(mood, st.session_state.user_input)
        st.write(encouragement)
    
    elif tabs == "🧘 Meditation & Exercises":
        st.subheader("🧘 Meditation and Exercises")
        meditation_suggestions = get_meditation_and_exercises(st.session_state.user_input)
        st.write(meditation_suggestions)

# Instructions for Enabling Dark Mode in Streamlit
st.sidebar.header("Settings")
st.sidebar.write("To enable dark mode, go to Streamlit settings (top right menu) and switch the theme to 'Dark'.")
