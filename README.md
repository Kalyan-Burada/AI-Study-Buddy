🎓 AI Study Buddy
A personal AI-powered study assistant built with Streamlit and Google's Gemini API. This application offers multiple learning modes to help students, developers, and lifelong learners study more effectively.

✨ Features
🎯 Smart Study Planner: Create personalized study plans tailored to your subject, goals, duration, and current skill level. The plan is generated in a structured JSON format and displayed as an interactive timeline.

💬 AI Tutor Chat: Engage in a real-time conversational chat with an AI tutor. Ask questions on any topic, and receive clear, helpful explanations with examples and analogies.

📊 Practice & Test: Generate a customizable set of practice problems (multiple-choice, short answer, etc.) on any topic and difficulty level. Check your answers and get instant explanations.

🧠 Mind Map Generator: Visualize complex topics by generating a structured mind map. It outlines the central topic, key branches, subtopics, and core concepts, helping you understand relationships and connections.

📚 Topic Research: Get comprehensive summaries of any research topic, including key points, historical context, current developments, and related topics, all compiled by the AI.

🚀 How to Run
Prerequisites
Python 3.8+

A Google Gemini API key

Setup
Clone the repository (if applicable) or save the code into a Python file (e.g., app.py).

Install the required libraries:

Bash

pip install streamlit google-generativeai
Set up your Gemini API Key:

Create a file named config.py in the same directory.

Add your API key to this file as a variable named GEMINI_API_KEY.

If you don't have a key, get one from the Google AI Studio.

Python

# config.py
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
APP_TITLE = "AI Study Buddy"
APP_ICON = "🧠" # Or another emoji
Run the Streamlit application:

Bash

streamlit run app.py
The application will open in your default web browser.

💻 Code Structure
app.py: The main application file containing all the Streamlit UI components and AI logic.

config.py: A configuration file to store the API key and app metadata.

🎨 Custom Styling
The application uses custom CSS to provide a clean, dark, and professional user interface. This includes styles for:

A vibrant hero section with gradients and animations.

Distinctive containers and cards for each feature.

Customized radio buttons, sliders, and text inputs to match the dark theme.

Color-coded message bubbles for the AI Tutor chat.
