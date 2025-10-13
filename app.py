import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
from config import GEMINI_API_KEY, APP_TITLE, APP_ICON
import os
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "2"  # Hide INFO/ERROR from absl


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# New custom CSS for a dark, professional theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: #1b1e23;
        color: #f0f4f8;
    }
    
    .stApp {
        background-color: #1b1e23;
    }

    [data-testid="stAppViewContainer"] > .main {
        background-color: #1b1e23;
    }

    .hero-section {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFD166 100%);
        padding: 4rem 3rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        animation: hero-appear 1s ease-out;
        color: white;
    }

    @keyframes hero-appear {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        letter-spacing: -2px;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.6rem;
        font-style: italic;
        margin-top: 0.5rem;
    }
    
    /* Style for the mode selector container */
    .mode-selector {
        background: #2b2e35;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
    }

    /* Customizing the Streamlit Radio button labels and colors */
    .st-emotion-cache-1xw2e8g label {
        color: #f0f4f8 !important;
        font-weight: 600;
    }

    .st-emotion-cache-1xw2e8g div[role="radiogroup"] {
        background-color: transparent !important;
    }
    
    .st-emotion-cache-1xw2e8g > div > div > label > div > div {
        background-color: #555 !important;
        border: 2px solid #555 !important;
    }
    
    .st-emotion-cache-1xw2e8g > div > div > label > div > div[aria-checked="true"] {
        background-color: #FF5722 !important; /* A bright orange */
        border-color: #FF5722 !important;
    }
    
    .st-emotion-cache-1f87n4w {
        width: 100%;
    }
    
    .st-emotion-cache-1j43d3s {
        background-color: transparent;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: none;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-box {
        background: #2b2e35;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        border-left: 5px solid #00BCD4; /* A bright teal */
    }
    
    .feature-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        background: #3c4048;
    }
    
    .chat-container {
        background: #2b2e35;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .message-bubble {
        padding: 1rem 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    .user-message {
        background: #00BCD4;
        color: white;
        margin-left: 20%;
        border-top-right-radius: 5px;
    }
    
    .ai-message {
        background: #f0f4f8;
        border-left: 4px solid #FF5722;
        margin-right: 20%;
        border-top-left-radius: 5px;
        color: #1a202c;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FF5722 0%, #FF9800 100%);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 87, 34, 0.4);
    }
    
    .topic-tag {
        display: inline-block;
        background: #00BCD4;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .timeline-item {
        border-left: 3px solid #FF5722;
        padding-left: 1.5rem;
        margin: 1rem 0;
        position: relative;
    }
    
    .timeline-item:before {
        content: '';
        position: absolute;
        left: -8px;
        top: 0;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        background: #FF5722;
        border: 3px solid #ffffff;
    }
    
    .st-emotion-cache-163j0c0 {
        color: #f0f4f8;
    }
    
</style>
""", unsafe_allow_html=True)

# Initialize Gemini
@st.cache_resource
def initialize_gemini():
    if not GEMINI_API_KEY:
        st.error("⚠️ Please set your GEMINI_API_KEY in the config file")
        st.stop()
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

model = initialize_gemini()

# Initialize session state
if "study_sessions" not in st.session_state:
    st.session_state.study_sessions = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "study_plan" not in st.session_state:
    st.session_state.study_plan = None
if "learning_progress" not in st.session_state:
    st.session_state.learning_progress = {}

# Hero Section
st.markdown(f"""
<div class="hero-section">
    <div class="hero-title">{APP_ICON} {APP_TITLE}</div>
    <div class="hero-subtitle">Your Personal AI Study Buddy</div>
</div>
""", unsafe_allow_html=True)

# Mode Selector at the top
st.markdown("### 🎓 Select a learning mode to begin:")
mode = st.radio(
    "Learning Mode Selector",
    ["🎯 Smart Study Planner", "💬 AI Tutor Chat", "📊 Practice & Test", "🧠 Mind Map Generator", "📚 Topic Research"],
    horizontal=True,
    label_visibility="hidden"
)

# Main Content Based on Mode
if mode == "🎯 Smart Study Planner":
    st.markdown("## 🎯 Smart Study Planner")
    st.write("Create a personalized study plan tailored to your goals and schedule.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.text_input("📒 What subject/topic do you want to study?", placeholder="e.g., Python Programming, Biology, Calculus")
        goal = st.text_area("🎯 What's your learning goal?", placeholder="e.g., Pass the exam, Build a project, Understand concepts", height=100)
    
    with col2:
        duration = st.selectbox("⏰ Study Duration", ["1 Week", "2 Weeks", "1 Month", "3 Months"])
        daily_time = st.slider("📅 Daily Study Time (hours)", 1, 8, 2)
        difficulty = st.select_slider("🎚️ Current Level", ["Beginner", "Intermediate", "Advanced"])
    
    if st.button("🚀 Generate My Study Plan"):
        if subject and goal:
            with st.spinner("🤖 AI is crafting your personalized study plan..."):
                try:
                    prompt = f"""Create a detailed, structured study plan for:
                    Subject: {subject}
                    Goal: {goal}
                    Duration: {duration}
                    Daily Time: {daily_time} hours
                    Current Level: {difficulty}
                    
                    Return a JSON with this structure:
                    {{
                        "title": "Study Plan for {subject}",
                        "overview": "Brief overview of the plan.",
                        "weeks": [
                            {{
                                "week_number": 1,
                                "focus": "Main focus area",
                                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                                "daily_tasks": ["Task 1", "Task 2"],
                                "milestones": ["Milestone 1"]
                            }}
                        ],
                        "resources": ["Resource 1", "Resource 2"],
                        "tips": ["Tip 1", "Tip 2"]
                    }}"""
                    
                    response = model.generate_content(prompt)
                    match = re.search(r'\{[\s\S]*\}', response.text)
                    
                    if match:
                        plan_data = json.loads(match.group(0))
                        st.session_state.study_plan = plan_data
                        
                        st.success("✅ Your study plan is ready!")
                        
                        # Display Plan
                        st.markdown(f"### 📋 {plan_data['title']}")
                        st.info(plan_data['overview'])
                        
                        # Timeline
                        st.markdown("### 📅 Study Timeline")
                        for week in plan_data['weeks']:
                            with st.expander(f"Week {week['week_number']}: {week['focus']}", expanded=True):
                                st.markdown(f"**📒 Topics to Cover:**")
                                for topic in week['topics']:
                                    st.markdown(f"- {topic}")
                                
                                st.markdown(f"**✅ Daily Tasks:**")
                                for task in week['daily_tasks']:
                                    st.checkbox(task, key=f"task_{week['week_number']}_{task}")
                                
                                st.markdown(f"**🏆 Milestones:**")
                                for milestone in week['milestones']:
                                    st.markdown(f"- {milestone}")
                        
                        # Resources
                        st.markdown("### 📒 Recommended Resources")
                        for resource in plan_data['resources']:
                            st.markdown(f"- {resource}")
                        
                        # Tips
                        st.markdown("### 💡 Study Tips")
                        for tip in plan_data['tips']:
                            st.success(tip)
                        
                        # Download
                        plan_text = json.dumps(plan_data, indent=2)
                        st.download_button("📥 Download Study Plan", plan_text, "study_plan.json", "application/json")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill in subject and goal.")

elif mode == "💬 AI Tutor Chat":
    st.markdown("## 💬 AI Tutor Chat")
    st.write("Ask me anything! I'm here to help you understand any concept.")
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="message-bubble user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-bubble ai-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    user_input = st.text_input("Ask your question:", placeholder="e.g., Explain quantum mechanics in simple terms", key="chat_input")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Send 📤"):
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                with st.spinner("🤖 Thinking..."):
                    try:
                        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-5:]])
                        prompt = f"""You are a friendly, knowledgeable tutor. Previous context: {context}
                        
                        Student question: {user_input}
                        
                        Provide a clear, helpful explanation. Use examples and analogies when appropriate."""
                        
                        response = model.generate_content(prompt)
                        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("Clear Chat 🗑️"):
            st.session_state.chat_history = []
            st.rerun()

elif mode == "📊 Practice & Test":
    st.markdown("## 📊 Practice & Test Your Knowledge")
    st.write("Generate practice problems and test yourself.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("📒 Topic:", placeholder="e.g., Algebra, Python Functions")
        problem_type = st.selectbox("📝 Problem Type:", ["Multiple Choice", "Short Answer", "True/False", "Fill in the Blank"])
    
    with col2:
        difficulty = st.select_slider("🎚️ Difficulty:", ["Easy", "Medium", "Hard"])
        num_problems = st.slider("🔢 Number of Problems:", 1, 10, 5)
    
    # Store problems in session state
    if "problems" not in st.session_state:
        st.session_state.problems = None

    if st.button("🎯 Generate Practice Problems"):
        if topic:
            with st.spinner("🤖 Creating practice problems..."):
                try:
                    prompt = f"""Generate {num_problems} {difficulty} {problem_type} problems about {topic}.
                    
                    Return in JSON format:
                    {{
                        "problems": [
                            {{
                                "question": "Problem text",
                                "answer": "Correct answer",
                                "explanation": "Why this is correct",
                                "hints": ["Hint 1", "Hint 2"]
                            }}
                        ]
                    }}"""
                    
                    response = model.generate_content(prompt)
                    match = re.search(r'\{[\s\S]*\}', response.text)
                    
                    if match:
                        problems_data = json.loads(match.group(0))
                        # Store problems in session state to persist them
                        st.session_state.problems = problems_data['problems']
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a topic.")
    
    # Display problems from session state
    if st.session_state.problems:
        for i, prob in enumerate(st.session_state.problems, 1):
            with st.expander(f"Problem {i}", expanded=True):
                st.markdown(f"**Question:** {prob['question']}")
                
                user_answer = st.text_input(f"Your answer:", key=f"answer_{i}")
                
                # Use a separate session state variable for each hint to control visibility
                if f"show_hint_{i}" not in st.session_state:
                    st.session_state[f"show_hint_{i}"] = False
                
                if st.button(f"Show Hints 💡", key=f"hints_{i}"):
                    st.session_state[f"show_hint_{i}"] = True
                
                if st.session_state[f"show_hint_{i}"]:
                    for hint in prob['hints']:
                        st.info(hint)

                if st.button(f"Check Answer ✅", key=f"check_{i}"):
                    user_answer_value = st.session_state.get(f"answer_{i}", "").strip()
                    if user_answer_value:
                        st.success(f"**Correct Answer:** {prob['answer']}")
                        st.markdown(f"**Explanation:** {prob['explanation']}")
                    else:
                        st.warning("Please enter your answer before checking.")

elif mode == "🧠 Mind Map Generator":
    st.markdown("## 🧠 Mind Map Generator")
    st.write("Visualize concepts and their relationships.")
    
    topic = st.text_input("🎯 Main Topic:", placeholder="e.g., Machine Learning, World War II")
    
    if st.button("🗺️ Generate Mind Map"):
        if topic:
            with st.spinner("🤖 Creating your mind map..."):
                try:
                    prompt = f"""Create a comprehensive mind map structure for: {topic}
                    
                    Return JSON with this structure:
                    {{
                        "central_topic": "{topic}",
                        "branches": [
                            {{
                                "name": "Branch name",
                                "subtopics": ["Subtopic 1", "Subtopic 2"],
                                "key_concepts": ["Concept 1", "Concept 2"]
                            }}
                        ]
                    }}"""
                    
                    response = model.generate_content(prompt)
                    match = re.search(r'\{[\s\S]*\}', response.text)
                    
                    if match:
                        mindmap_data = json.loads(match.group(0))
                        
                        # Central topic
                        st.markdown(f"### 🎯 {mindmap_data['central_topic']}")
                        
                        # Branches
                        cols = st.columns(len(mindmap_data['branches']))
                        for idx, branch in enumerate(mindmap_data['branches']):
                            with cols[idx]:
                                st.markdown(f"#### {branch['name']}")
                                st.markdown("**Subtopics:**")
                                for subtopic in branch['subtopics']:
                                    st.markdown(f"- {subtopic}")
                                st.markdown("**Key Concepts:**")
                                for concept in branch['key_concepts']:
                                    st.markdown(f'<span class="topic-tag">{concept}</span>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a topic.")

elif mode == "📚 Topic Research":
    st.markdown("## 📚 Topic Research Assistant")
    st.write("Get comprehensive research summaries on any topic.")
    
    research_topic = st.text_input("🔍 Research Topic:", placeholder="e.g., Renewable Energy, Ancient Rome")
    research_depth = st.selectbox("📊 Depth of Research:", ["Overview", "Detailed", "Comprehensive"])
    
    if st.button("🔬 Start Research"):
        if research_topic:
            with st.spinner("🤖 Researching and compiling information..."):
                try:
                    prompt = f"""Conduct a {research_depth} research on: {research_topic}
                    
                    Return JSON:
                    {{
                        "summary": "Brief summary",
                        "key_points": ["Point 1", "Point 2"],
                        "historical_context": "Context information",
                        "current_developments": "Recent developments",
                        "related_topics": ["Topic 1", "Topic 2"],
                        "further_reading": ["Source 1", "Source 2"]
                    }}"""
                    
                    response = model.generate_content(prompt)
                    match = re.search(r'\{[\s\S]*\}', response.text)
                    
                    if match:
                        research_data = json.loads(match.group(0))
                        
                        # Display the generated content
                        st.markdown(f"### 📊 Research Summary: {research_topic}")
                        st.info(research_data['summary'])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🔑 Key Points")
                            for point in research_data['key_points']:
                                st.markdown(f"- {point}")
                            
                            st.markdown("#### 📜 Historical Context")
                            st.write(research_data['historical_context'])
                        
                        with col2:
                            st.markdown("#### 🆕 Current Developments")
                            st.write(research_data['current_developments'])
                            
                            st.markdown("#### 🔗 Related Topics")
                            for rt in research_data['related_topics']:
                                st.markdown(f'<span class="topic-tag">{rt}</span>', unsafe_allow_html=True)
                        
                        st.markdown("#### 📖 Further Reading")
                        for source in research_data['further_reading']:
                            st.markdown(f"- {source}")
                        
                        # Save to session
                        st.session_state.study_sessions.append({
                            "topic": research_topic,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a research topic.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p style="font-size: 1.1rem;">🚀 Powered by Google Gemini AI</p>
    <p>Transform your learning journey today!</p>
</div>
""", unsafe_allow_html=True)