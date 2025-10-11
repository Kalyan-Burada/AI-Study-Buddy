import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import re
from config import GEMINI_API_KEY, APP_TITLE, APP_ICON
try:
    # Optional: nicer containers/styles if available
    from streamlit_extras.stylable_container import stylable_container
except Exception:  # pragma: no cover
    stylable_container = None

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .result-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .quiz-question {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #ddd;
    }
    
    .flashcard {
        width: 100%;
        height: 200px;
        perspective: 1000px;
        margin: 1rem 0;
    }
    
    .flashcard-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        cursor: pointer;
    }
    
    .flashcard-inner.flipped {
        transform: rotateY(180deg);
    }
    
    .flashcard-front, .flashcard-back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .flashcard-front {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .flashcard-back {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        transform: rotateY(180deg);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    @media (max-width: 768px) {
        .feature-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .flashcard {
            height: 150px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini
def initialize_gemini():
    if not GEMINI_API_KEY:
        st.error("⚠️ Please set your GEMINI_API_KEY in the .env file")
        st.stop()
    
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

# Initialize the model
model = initialize_gemini()

# Sidebar navigation
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1rem;">
    <h2>{APP_ICON} {APP_TITLE}</h2>
    <p style="color: #666;">Your AI-powered learning companion</p>
</div>
""", unsafe_allow_html=True)

# Navigation menu
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["📘 Explain Concept", "📝 Summarize Notes", "❓ Generate Quiz", "🎴 Flashcards"]
)

# Main content area
st.markdown(f"""
<div class="main-header">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>Transform your learning experience with AI-powered tools</p>
</div>
""", unsafe_allow_html=True)

# Explain Concept Page
if page == "📘 Explain Concept":
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("📘 Explain Concept")
    st.write("Enter any topic or concept you'd like explained in simple terms.")
    
    topic = st.text_area(
        "What would you like me to explain?",
        placeholder="e.g., Photosynthesis, Machine Learning, World War II, etc.",
        height=100
    )
    
    if st.button("🚀 Generate Explanation", key="explain_btn"):
        if topic:
            with st.spinner("🤖 AI is explaining the concept..."):
                try:
                    prompt = f"Explain '{topic}' in simple, easy-to-understand terms. Use analogies and examples where helpful. Keep it concise but comprehensive."
                    response = model.generate_content(prompt)
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("### 💡 Explanation")
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error generating explanation: {str(e)}")
        else:
            st.warning("Please enter a topic to explain.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Summarize Notes Page
elif page == "📝 Summarize Notes":
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("📝 Summarize Notes")
    st.write("Paste your notes or text below to get a clear, concise summary.")
    
    notes = st.text_area(
        "Paste your notes here:",
        placeholder="Enter your notes, lecture content, or any text you'd like summarized...",
        height=200
    )
    
    summary_length = st.selectbox(
        "Summary length:",
        ["Brief (2-3 sentences)", "Medium (1 paragraph)", "Detailed (2-3 paragraphs)"]
    )
    
    if st.button("📝 Generate Summary", key="summary_btn"):
        if notes:
            with st.spinner("🤖 AI is summarizing your notes..."):
                try:
                    length_instruction = {
                        "Brief (2-3 sentences)": "in 2-3 sentences",
                        "Medium (1 paragraph)": "in one paragraph",
                        "Detailed (2-3 paragraphs)": "in 2-3 paragraphs"
                    }[summary_length]
                    
                    prompt = f"Summarize the following text {length_instruction}. Focus on the key points and main ideas:\n\n{notes}"
                    response = model.generate_content(prompt)
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("### 📋 Summary")
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
        else:
            st.warning("Please enter some notes to summarize.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Generate Quiz Page
elif page == "❓ Generate Quiz":
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("❓ Generate Quiz")
    st.write("Create quizzes from your text or topic.")
    
    quiz_input = st.text_area(
        "Enter topic or paste text for quiz generation:",
        placeholder="Enter a topic or paste your study material...",
        height=150
    )
    
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions:", 3, 15, 5)
    with col2:
        quiz_type = st.selectbox(
            "Quiz type:",
            ["Mixed (MCQ + True/False)", "Multiple Choice Only", "True/False Only", "Short Answer Only"]
        )
    
    if st.button("🎯 Generate Quiz", key="quiz_btn"):
        if quiz_input:
            with st.spinner("🤖 AI is generating your quiz..."):
                try:
                    if quiz_type == "Mixed (MCQ + True/False)":
                        prompt = f"""Create a quiz with {num_questions} questions based on: {quiz_input}
                        
                        Format: Mix of multiple choice questions (with 4 options each) and true/false questions.
                        Return in this exact JSON format:
                        {{
                            "questions": [
                                {{
                                    "type": "mcq",
                                    "question": "Question text?",
                                    "options": ["A", "B", "C", "D"],
                                    "correct": "A",
                                    "explanation": "Brief explanation"
                                }},
                                {{
                                    "type": "true_false",
                                    "question": "Statement to evaluate",
                                    "correct": true,
                                    "explanation": "Brief explanation"
                                }}
                            ]
                        }}"""
                    elif quiz_type == "Multiple Choice Only":
                        prompt = f"""Create {num_questions} multiple choice questions based on: {quiz_input}
                        
                        Each question should have 4 options (A, B, C, D).
                        Return in this exact JSON format:
                        {{
                            "questions": [
                                {{
                                    "type": "mcq",
                                    "question": "Question text?",
                                    "options": ["A", "B", "C", "D"],
                                    "correct": "A",
                                    "explanation": "Brief explanation"
                                }}
                            ]
                        }}"""
                    elif quiz_type == "True/False Only":
                        prompt = f"""Create {num_questions} true/false questions based on: {quiz_input}
                        
                        Return in this exact JSON format:
                        {{
                            "questions": [
                                {{
                                    "type": "true_false",
                                    "question": "Statement to evaluate",
                                    "correct": true,
                                    "explanation": "Brief explanation"
                                }}
                            ]
                        }}"""
                    else:  # Short Answer Only
                        prompt = f"""Create {num_questions} short answer questions based on: {quiz_input}
                        
                        Return in this exact JSON format:
                        {{
                            "questions": [
                                {{
                                    "type": "short_answer",
                                    "question": "Question text?",
                                    "answer": "Expected answer",
                                    "explanation": "Brief explanation"
                                }}
                            ]
                        }}"""
                    
                    response = model.generate_content(prompt)
                    
                    try:
                        # Try to extract JSON from the response text
                        match = re.search(r'\{[\s\S]*\}', response.text)
                        if match:
                            json_str = match.group(0)
                            quiz_data = json.loads(json_str)
                            questions = quiz_data.get("questions", [])
                            
                            st.markdown('<div class="result-card">', unsafe_allow_html=True)
                            st.markdown("### 🎯 Generated Quiz")
                            
                            for i, q in enumerate(questions, 1):
                                st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
                                st.markdown(f"**Question {i}:** {q['question']}")
                                
                                if q['type'] == 'mcq':
                                    for j, option in enumerate(q['options']):
                                        st.markdown(f"   {chr(65+j)}. {option}")
                                    st.markdown(f"**Answer:** {q['correct']}")
                                elif q['type'] == 'true_false':
                                    st.markdown(f"**Answer:** {'True' if q['correct'] else 'False'}")
                                else:  # short_answer
                                    st.markdown(f"**Answer:** {q['answer']}")
                                
                                st.markdown(f"**Explanation:** {q['explanation']}")
                                st.markdown('</div>', unsafe_allow_html=True)
                            

                            # Download button
                            quiz_text = f"Quiz Generated from: {quiz_input}\n\n"
                            for i, q in enumerate(questions, 1):
                                quiz_text += f"Question {i}: {q['question']}\n"
                                if q['type'] == 'mcq':
                                    for j, option in enumerate(q['options']):
                                        quiz_text += f"   {chr(65+j)}. {option}\n"
                                    quiz_text += f"Answer: {q['correct']}\n"
                                elif q['type'] == 'true_false':
                                    quiz_text += f"Answer: {'True' if q['correct'] else 'False'}\n"
                                else:
                                    quiz_text += f"Answer: {q['answer']}\n"
                                quiz_text += f"Explanation: {q['explanation']}\n\n"
                            

                            st.download_button(
                                label="📥 Download Quiz as Text",
                                data=quiz_text,
                                file_name="quiz.txt",
                                mime="text/plain"
                            )
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        else:
                            st.error("Failed to find JSON in the response. Please try again.")
                            st.text(response.text)
                    except Exception as e:
                        st.error(f"Failed to parse quiz response: {str(e)}")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
        else:
            st.warning("Please enter a topic or text for quiz generation.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Flashcards Page
elif page == "🎴 Flashcards":
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("🎴 Flashcards")
    st.write("Create interactive flashcards for effective memorization.")
    
    flashcard_input = st.text_area(
        "Enter topic or paste text for flashcard generation:",
        placeholder="Enter a topic or paste your study material...",
        height=150
    )
    
    num_cards = st.slider("Number of flashcards:", 3, 20, 8)
    
    if st.button("🎴 Generate Flashcards", key="flashcard_btn"):
        if flashcard_input:
            with st.spinner("🤖 AI is generating your flashcards..."):
                try:
                    prompt = f"""Create {num_cards} flashcards based on: {flashcard_input}
                    
                    Format: Each flashcard should have a clear front (question/keyword) and back (answer/definition).
                    Return in this exact JSON format:
                    {{
                        "flashcards": [
                            {{
                                "front": "Question or keyword",
                                "back": "Answer or definition"
                            }}
                        ]
                    }}"""
                    
                    response = model.generate_content(prompt)
                    
                    try:
                        match = re.search(r'\{[\s\S]*\}', response.text)
                        if match:
                            json_str = match.group(0)
                            flashcard_data = json.loads(json_str)
                            st.session_state["flashcards_data"] = flashcard_data.get("flashcards", [])
                            st.session_state["flashcards_source"] = flashcard_input
                        else:
                            st.error("Failed to find JSON in the response. Please try again.")
                            st.text(response.text)
                    except Exception as e:
                        st.error(f"Failed to parse flashcard response: {str(e)}")
                        st.text(response.text)
                except Exception as e:
                    st.error(f"Error generating flashcards: {str(e)}")
        else:
            st.warning("Please enter a topic or text for flashcard generation.")
    
    # Persisted rendering of flashcards so toggles don't clear data on rerun
    if "flashcards_data" in st.session_state and st.session_state["flashcards_data"]:
        flashcards = st.session_state["flashcards_data"]
        flashcard_input_source = st.session_state.get("flashcards_source", "")

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("### 🎴 Interactive Flashcards")
        st.write("Use the toggles to flip cards. Your cards persist when the app reruns.")

        cols = st.columns(2)
        for i, card in enumerate(flashcards):
            col = cols[i % 2]
            with col:
                card_state_key = f"flip_{i}"
                flipped = st.toggle(f"Flip Card {i+1}", key=card_state_key)
                flip_class = "flipped" if flipped else ""

                if stylable_container:
                    with stylable_container(key=f"stylable_card_{i}", css_styles="border-radius: 14px; padding: 0; border: 0;"):
                        st.markdown(f"""
                        <div class=\"flashcard\">
                            <div class=\"flashcard-inner {flip_class}\">
                                <div class=\"flashcard-front\">
                                    <h3>{card['front']}</h3>
                                </div>
                                <div class=\"flashcard-back\">
                                    <h3>{card['back']}</h3>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class=\"flashcard\">
                        <div class=\"flashcard-inner {flip_class}\">
                            <div class=\"flashcard-front\">
                                <h3>{card['front']}</h3>
                            </div>
                            <div class=\"flashcard-back\">
                                <h3>{card['back']}</h3>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Downloads
        flashcard_text = f"Flashcards Generated from: {flashcard_input_source}\n\n"
        for i, card in enumerate(flashcards, 1):
            flashcard_text += f"Card {i}:\n"
            flashcard_text += f"Front: {card['front']}\n"
            flashcard_text += f"Back: {card['back']}\n\n"

        st.download_button(
            label="📥 Download Flashcards as Text",
            data=flashcard_text,
            file_name="flashcards.txt",
            mime="text/plain"
        )

        df = pd.DataFrame(flashcards)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Flashcards as CSV",
            data=csv,
            file_name="flashcards.csv",
            mime="text/csv"
        )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666; margin-top: 3rem;">
    <p>🤖 Powered by Google Gemini AI | Built with Streamlit</p>
    <p>Made with ❤️ for students everywhere</p>
</div>
""", unsafe_allow_html=True)
