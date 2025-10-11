import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Explicitly load .env file from project directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# Load Gemini key (local first, then Streamlit Cloud)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# App configuration
APP_TITLE = "AI-Powered Study Buddy"
APP_ICON = "📚"
