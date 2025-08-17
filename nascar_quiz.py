import streamlit as st
import random
import json
import os
from datetime import datetime

# Basic Page Configuration
st.set_page_config(
    page_title="NASQUIZ",
    page_icon="🏁",
    layout="wide"
)

# Initialize session state
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'questions_loaded' not in st.session_state:
    st.session_state.questions_loaded = False
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'selected_difficulty' not in st.session_state:
    st.session_state.selected_difficulty = 'mixed'

@st.cache_data
def load_questions_from_json(file_path="questions.json"):
    """Load questions from JSON file with caching"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        else:
            st.error(f"Questions file '{file_path}' not found. Please make sure the file exists in the same directory as this script.")
            return []
    except json.JSONDecodeError as e:
        st.error(f"Error reading JSON file: {e}")
        return []
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return []

def initialize_questions():
    """Initialize questions from JSON file"""
    if not st.session_state.questions_loaded:
        st.session_state.all_questions = load_questions_from_json()
        st.session_state.questions_loaded = True
        
        if not st.session_state.all_questions:
            st.warning("No questions loaded. Please check your questions file.")
            return False
    return True

def filter_questions_by_difficulty(difficulty_level):
    """Filter questions based on selected difficulty"""
    if difficulty_level == 'mixed':
        return st.session_state.all_questions
    
    filtered_questions = [
        q for q in st.session_state.all_questions 
        if q.get('difficulty', '').lower() == difficulty_level.lower()
    ]
    
    return filtered_questions

def get_difficulty_stats():
    """Get statistics about questions by difficulty"""
    if not st.session_state.all_questions:
        return {}
    
    stats = {}
    for question in st.session_state.all_questions:
        difficulty = question.get('difficulty', 'unknown').lower()
        stats[difficulty] = stats.get(difficulty, 0) + 1
    
    return stats

def calculate_difficulty_score(answers):
    """Calculate score with difficulty weighting"""
    total_weighted_score = 0
    max_possible_score = 0
    
    difficulty_weights = {'easy': 1, 'medium': 2, 'hard': 3}
    
    for i, answer in enumerate(answers):
        question = st.session_state.quiz_questions[i]
        difficulty = question.get('difficulty', 'medium').lower()
        weight = difficulty_weights.get(difficulty, 2)
        
        max_possible_score += weight
        if answer['is_correct']:
            total_weighted_score += weight
    
    return total_weighted_score, max_possible_score

def start_quiz(difficulty_level='mixed'):
    """Initialize a new quiz session with difficulty selection"""
    if not st.session_state.all_questions:
        st.error("Cannot start quiz: No questions available.")
        return False
    
    # Filter questions by difficulty
    available_questions = filter_questions_by_difficulty(difficulty_level)
    
    if not available_questions:
        st.error(f"No questions available for {difficulty_level} difficulty level.")
        return False
    
    if len(available_questions) < 5:
        st.warning(f"Only {len(available_questions)} questions available for {difficulty_level} difficulty.")
        
    st.session_state.quiz_started = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.selected_difficulty = difficulty_level
    
    # Randomize questions for each quiz
    num_questions = min(5, len(available_questions))
    st.session_state.quiz_questions = random.sample(available_questions, num_questions)
    return True

def submit_answer(selected_option):
    """Process the submitted answer"""
    current_q = st.session_state.quiz_questions[st.session_state.current_question]
    is_correct = selected_option == current_q["correct"]
    
    if is_correct:
        st.session_state.score += 1
    
    st.session_state.answers.append({
        "question": current_q["question"],
        "selected": selected_option,
        "correct": current_q["correct"],
        "is_correct": is_correct,
        "explanation": current_q["explanation"],
        "difficulty": current_q.get("difficulty", "medium")
    })
    
    st.session_state.current_question += 1

def reset_quiz():
    """Reset the quiz to start over"""
    st.session_state.quiz_started = False
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.quiz_questions = []

def get_difficulty_emoji(difficulty):
    """Get emoji for difficulty level"""
    difficulty_emojis = {
        'easy': '🟢',
        'medium': '🟡', 
        'hard': '🔴'
    }
    return difficulty_emojis.get(difficulty.lower(), '⚪')

def get_difficulty_color(difficulty):
    """Get color for difficulty level"""
    difficulty_colors = {
        'easy': 'green',
        'medium': 'orange',
        'hard': 'red'
    }
    return difficulty_colors.get(difficulty.lower(), 'gray')

# Main App Layout
st.title("🏁 NASCQUIZ")
st.markdown("---")

# Initialize questions from JSON file
if not initialize_questions():
    st.stop()

# Display question statistics in sidebar
if st.session_state.all_questions:
    total_questions = len(st.session_state.all_questions)
    categories = list(set(q.get('category', 'Unknown') for q in st.session_state.all_questions))
    difficulties = list(set(q.get('difficulty', 'Unknown') for q in st.session_state.all_questions))
    difficulty_stats = get_difficulty_stats()

# Quiz not started - Welcome screen with difficulty selection
if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Welcome to NASCQUIZ! 🏎️
        
        **How does it work?:**
        - 5 multiple choice questions, try and get them all right!
        - You'll get your score at the end, and if you got a question wrong, you'll see the correct answer as well and the reason.
        
        **Choose your difficulty level:**
        """)
        
        # Difficulty selection
        difficulty_options = {
            'mixed': f"🎲 Mixed Difficulty ({total_questions} questions)",
            'easy': f"🟢 Easy ({difficulty_stats.get('easy', 0)} questions)",
            'medium': f"🟡 Medium ({difficulty_stats.get('medium', 0)} questions)",
            'hard': f"🔴 Hard ({difficulty_stats.get('hard', 0)} questions)"
        }
        
        selected_difficulty = st.selectbox(
            "Select difficulty:",
            options=list(difficulty_options.keys()),
            format_func=lambda x: difficulty_options[x],
            index=0
        )
        
        # Difficulty descriptions
        if selected_difficulty == 'easy':
            st.info("🟢 **Easy**: Basic NASCAR knowledge - great for beginners!")
        elif selected_difficulty == 'medium':
            st.info("🟡 **Medium**: Moderate NASCAR knowledge - for casual fans!")
        elif selected_difficulty == 'hard':
            st.info("🔴 **Hard**: Advanced NASCAR knowledge - for true experts!")
        else:
            st.info("🎲 **Mixed**: Questions from all difficulty levels - balanced challenge!")
        
        st.markdown("Ready to put your NASCAR knowledge to the test?")
        
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
            if start_quiz(selected_difficulty):
                st.rerun()

# Quiz in progress
elif st.session_state.current_question < len(st.session_state.quiz_questions):
    current_q = st.session_state.quiz_questions[st.session_state.current_question]
    current_difficulty = current_q.get('difficulty', 'medium')
    
    # Progress bar
    progress = (st.session_state.current_question) / len(st.session_state.quiz_questions)
    st.progress(progress, text=f"Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}")
    
    # Centered current score
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric("Current Score", f"{st.session_state.score}/{st.session_state.current_question}")
    
    # Centered question with bigger text
    st.markdown("<br>", unsafe_allow_html=True)  # Add some space
    
    # Center the question number and difficulty indicator
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2>Question {st.session_state.current_question + 1} {get_difficulty_emoji(current_difficulty)}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the question text with bigger font
    st.markdown(f"""
    <div style='text-align: center; margin: 30px 0; padding: 20px;'>
        <h3 style='color: #ffffff; font-size: 1.5rem; line-height: 1.4;'>{current_q['question']}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add space before options
    
    # Answer options with bigger text, centered, and no preselection
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        # Style the radio button labels with bigger text and center them
        st.markdown("""
        <style>
        .stRadio > div {
            font-size: 1.2rem !important;
            line-height: 1.5 !important;
            text-align: center !important;
        }
        .stRadio > div > label {
            font-size: 1.2rem !important;
            padding: 8px 0 !important;
            justify-content: center !important;
            text-align: center !important;
        }
        .stRadio > div > label > div {
            font-size: 1.2rem !important;
            text-align: center !important;
        }
        .stRadio > div > label > div:first-child {
            margin-right: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        selected_option = st.radio(
            "Choose your answer:",
            options=range(len(current_q["options"])),
            format_func=lambda x: current_q["options"][x],
            key=f"q_{st.session_state.current_question}",
            index=None  # This prevents any option from being preselected
        )
    
    # Submit button with validation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if selected_option is not None:
            if st.button("Submit Answer", type="primary", use_container_width=True):
                submit_answer(selected_option)
                st.rerun()
        else:
            st.button("Submit Answer", type="primary", use_container_width=True, disabled=True)
            st.caption("Please select an answer first")

# Quiz completed - Results screen with difficulty analysis
else:
    st.balloons()
    
    final_score = st.session_state.score
    total_questions = len(st.session_state.quiz_questions)
    percentage = (final_score / total_questions) * 100
    
    # Calculate weighted score if using mixed difficulty
    if st.session_state.selected_difficulty == 'mixed':
        weighted_score, max_weighted = calculate_difficulty_score(st.session_state.answers)
        weighted_percentage = (weighted_score / max_weighted) * 100 if max_weighted > 0 else 0
    
    # Results header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🏁 Quiz Complete!")
        
        # Score display with different messages based on performance
        if percentage >= 80:
            st.success(f"🏆 Excellent! You scored {final_score}/{total_questions} ({percentage:.0f}%)")
            st.markdown("You're a NASCAR expert! 🏎️")
        elif percentage >= 60:
            st.info(f"👍 Good job! You scored {final_score}/{total_questions} ({percentage:.0f}%)")
            st.markdown("You know your NASCAR facts pretty well!")
        else:
            st.warning(f"📚 You scored {final_score}/{total_questions} ({percentage:.0f}%)")
            st.markdown("Everyone starts somewhere! Keep at it!")
        
        # Show weighted score for mixed difficulty
        if st.session_state.selected_difficulty == 'mixed':
            st.markdown(f"**Weighted Score:** {weighted_score}/{max_weighted} ({weighted_percentage:.0f}%)")
            st.caption("*Weighted score accounts for question difficulty (Easy=1pt, Medium=2pts, Hard=3pts)*")
    
    # Difficulty breakdown
    if st.session_state.selected_difficulty == 'mixed':
        st.markdown("---")
        st.markdown("### 📈 Performance by Difficulty")
        
        difficulty_breakdown = {'easy': [0, 0], 'medium': [0, 0], 'hard': [0, 0]}
        for answer in st.session_state.answers:
            diff = answer.get('difficulty', 'medium').lower()
            if diff in difficulty_breakdown:
                difficulty_breakdown[diff][1] += 1  # total
                if answer['is_correct']:
                    difficulty_breakdown[diff][0] += 1  # correct
        
        cols = st.columns(3)
        for i, (diff, (correct, total)) in enumerate(difficulty_breakdown.items()):
            if total > 0:
                with cols[i]:
                    pct = (correct / total) * 100
                    st.metric(
                        f"{get_difficulty_emoji(diff)} {diff.title()}", 
                        f"{correct}/{total} ({pct:.0f}%)"
                    )
    
    # Detailed results
    st.markdown("---")
    st.markdown("### 📊 Detailed Results")
    
    for i, answer in enumerate(st.session_state.answers, 1):
        question_difficulty = answer.get('difficulty', 'medium')
        difficulty_emoji = get_difficulty_emoji(question_difficulty)
        
        with st.expander(f"Question {i}: {'✅' if answer['is_correct'] else '❌'} {difficulty_emoji} {question_difficulty.title()}"):
            st.markdown(f"**{answer['question']}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Your Answer:**")
                if answer['is_correct']:
                    st.success(st.session_state.quiz_questions[i-1]['options'][answer['selected']])
                else:
                    st.error(st.session_state.quiz_questions[i-1]['options'][answer['selected']])
            
            with col2:
                st.markdown("**Correct Answer:**")
                st.success(st.session_state.quiz_questions[i-1]['options'][answer['correct']])
            
            st.info(f"**Explanation:** {answer['explanation']}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Take Quiz Again", use_container_width=True):
            reset_quiz()
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            reset_quiz()
            st.rerun()

# Sidebar with additional info including difficulty stats
with st.sidebar:
    st.markdown("### 🏁 About This Quiz")
    
    if st.session_state.all_questions:
        st.markdown(f"""
        **Question Database:**
        - Total Questions: {total_questions}
        - Categories: {', '.join(sorted(categories))}
        
        **Difficulty Breakdown:**
        """)
        
        # Show difficulty stats with emojis
        for difficulty, count in difficulty_stats.items():
            emoji = get_difficulty_emoji(difficulty)
            st.markdown(f"- {emoji} {difficulty.title()}: {count} questions")
        
        st.markdown(f"""
        **Quiz Format:**
        - {min(5, total_questions)} random questions per quiz
        - Multiple choice format with instant feedback and explanations
        - Choose your preferred difficulty level!
        """)
    
    st.markdown("""
    This NASCAR quiz tests your knowledge of:
    - NASCAR history and records
    - Famous drivers and nicknames  
    - Iconic tracks and races
    - Racing terminology and facts
    
    **Difficulty Levels:**
    - 🟢 Easy: Basic NASCAR knowledge
    - 🟡 Medium: Moderate NASCAR facts  
    - 🔴 Hard: Advanced NASCAR trivia
    - 🎲 Mixed: All difficulty levels
    
    **Have fun!**
    """)
    
    st.markdown("---")
    st.markdown("### 🏎️ Fun NASCAR Facts")
    st.markdown("""
    - NASCAR was founded in 1948
    - The first race was held on Daytona Beach
    - The NASCAR Hall of Fame is in Charlotte, NC
    - The fastest qualifying speed ever recorded was 212.809 mph
    """)
    
    if st.session_state.quiz_started:
        st.markdown("---")
        current_difficulty = st.session_state.selected_difficulty
        difficulty_emoji = get_difficulty_emoji(current_difficulty) if current_difficulty != 'mixed' else '🎲'
        st.markdown(f"**Current Mode:** {difficulty_emoji} {current_difficulty.title()}")
        
        if st.button("🏠 Quit Quiz", type="secondary"):
            reset_quiz()
            st.rerun()
    
    # File management section
    st.markdown("---")
    st.markdown("### 📁 Question File Info")
    if st.session_state.all_questions:
        st.success(f"✅ Questions loaded successfully")
        if st.button("🔄 Reload Questions"):
            st.session_state.questions_loaded = False
            st.rerun()
    else:
        st.error("❌ Questions file not found")
        st.markdown("Make sure `questions.json` is in the same directory.")