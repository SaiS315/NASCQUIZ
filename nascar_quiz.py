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
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'all'

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

def filter_questions_by_difficulty(questions, difficulty_level):
    """Filter questions based on selected difficulty"""
    if difficulty_level == 'mixed':
        return questions
    
    filtered_questions = [
        q for q in questions 
        if q.get('difficulty', '').lower() == difficulty_level.lower()
    ]
    
    return filtered_questions

def filter_questions_by_category(questions, category):
    """Filter questions based on selected category"""
    if category == 'all':
        return questions
    
    filtered_questions = [
        q for q in questions 
        if q.get('category', '').lower() == category.lower()
    ]
    
    return filtered_questions

def get_available_categories():
    """Get list of available categories"""
    if not st.session_state.all_questions:
        return []
    
    categories = set()
    for question in st.session_state.all_questions:
        category = question.get('category', 'Unknown')
        if category:
            categories.add(category)
    
    return sorted(list(categories))

def get_difficulty_stats():
    """Get statistics about questions by difficulty"""
    if not st.session_state.all_questions:
        return {}
    
    stats = {}
    for question in st.session_state.all_questions:
        difficulty = question.get('difficulty', 'unknown').lower()
        stats[difficulty] = stats.get(difficulty, 0) + 1
    
    return stats

def get_category_stats():
    """Get statistics about questions by category"""
    if not st.session_state.all_questions:
        return {}
    
    stats = {}
    for question in st.session_state.all_questions:
        category = question.get('category', 'Unknown')
        stats[category] = stats.get(category, 0) + 1
    
    return stats

def get_filtered_question_count(difficulty, category):
    """Get count of questions matching both difficulty and category filters"""
    questions = st.session_state.all_questions
    
    # Apply category filter
    if category != 'all':
        questions = [q for q in questions if q.get('category', '').lower() == category.lower()]
    
    # Apply difficulty filter
    if difficulty != 'mixed':
        questions = [q for q in questions if q.get('difficulty', '').lower() == difficulty.lower()]
    
    return len(questions)

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

def start_quiz(difficulty_level='mixed', category='all'):
    """Initialize a new quiz session with difficulty and category selection"""
    if not st.session_state.all_questions:
        st.error("Cannot start quiz: No questions available.")
        return False
    
    # Filter questions by category first, then difficulty
    available_questions = filter_questions_by_category(st.session_state.all_questions, category)
    available_questions = filter_questions_by_difficulty(available_questions, difficulty_level)
    
    if not available_questions:
        st.error(f"No questions available for {difficulty_level} difficulty in {category} category.")
        return False
    
    if len(available_questions) < 5:
        st.warning(f"Only {len(available_questions)} questions available for {difficulty_level} difficulty in {category} category.")
        
    st.session_state.quiz_started = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.selected_difficulty = difficulty_level
    st.session_state.selected_category = category
    
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
        "difficulty": current_q.get("difficulty", "medium"),
        "category": current_q.get("category", "Unknown")
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

def get_category_emoji(category):
    """Get emoji for category"""
    category_emojis = {
        'history': '📚',
        'drivers': '👤',
        'tracks': '🏁',
        'cars': '🏎️',
        'records': '🏆',
        'rules': '📋',
        'teams': '👥',
        'general': '🎯',
        'unknown': '❓'
    }
    return category_emojis.get(category.lower(), '🎯')

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

# Get available categories and stats
available_categories = get_available_categories()
difficulty_stats = get_difficulty_stats()
category_stats = get_category_stats()

# Display question statistics
if st.session_state.all_questions:
    total_questions = len(st.session_state.all_questions)

# Quiz not started - Welcome screen with difficulty and category selection
if not st.session_state.quiz_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Welcome to NASCQUIZ! 🏎️
        
        **How does it work?:**
        - 5 multiple choice questions, try and get them all right!
        - You'll get your score at the end, and if you got a question wrong, you'll see the correct answer as well and the reason.
        
        **Customize your quiz:**
        """)
        
        # Category selection
        st.markdown("**Choose your category:**")
        category_options = {'all': f"🎯 All Categories ({total_questions} questions)"}
        for category in available_categories:
            emoji = get_category_emoji(category)
            count = category_stats.get(category, 0)
            category_options[category] = f"{emoji} {category.title()} ({count} questions)"
        
        selected_category = st.selectbox(
            "Select category:",
            options=list(category_options.keys()),
            format_func=lambda x: category_options[x],
            index=0,
            key="category_select"
        )
        
        # Difficulty selection (updated based on category)
        st.markdown("**Choose your difficulty:**")
        available_count = get_filtered_question_count('mixed', selected_category)
        difficulty_options = {
            'mixed': f"🎲 Mixed Difficulty ({available_count} questions)"
        }
        
        for difficulty in ['easy', 'medium', 'hard']:
            count = get_filtered_question_count(difficulty, selected_category)
            if count > 0:
                emoji = get_difficulty_emoji(difficulty)
                difficulty_options[difficulty] = f"{emoji} {difficulty.title()} ({count} questions)"
        
        selected_difficulty = st.selectbox(
            "Select difficulty:",
            options=list(difficulty_options.keys()),
            format_func=lambda x: difficulty_options[x],
            index=0,
            key="difficulty_select"
        )
        
        # Display information about selections
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            if selected_category != 'all':
                category_emoji = get_category_emoji(selected_category)
                st.info(f"{category_emoji} **{selected_category.title()}**: Questions focused on this specific NASCAR topic!")
            else:
                st.info("🎯 **All Categories**: Questions from all NASCAR topics - comprehensive challenge!")
        
        with col_info2:
            if selected_difficulty == 'easy':
                st.info("🟢 **Easy**: Basic NASCAR knowledge - great for beginners!")
            elif selected_difficulty == 'medium':
                st.info("🟡 **Medium**: Moderate NASCAR knowledge - for casual fans!")
            elif selected_difficulty == 'hard':
                st.info("🔴 **Hard**: Advanced NASCAR knowledge - for true experts!")
            else:
                st.info("🎲 **Mixed**: Questions from all difficulty levels - balanced challenge!")
        
        # Show final question count
        final_count = get_filtered_question_count(selected_difficulty, selected_category)
        if final_count < 5:
            st.warning(f"⚠️ Only {final_count} questions available with current selections. Consider broadening your criteria.")
        else:
            st.success(f"✅ {min(5, final_count)} questions ready for your quiz!")
        
        st.markdown("Ready to put your NASCAR knowledge to the test?")
        
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True, disabled=final_count == 0):
            if start_quiz(selected_difficulty, selected_category):
                st.rerun()

# Quiz in progress
elif st.session_state.current_question < len(st.session_state.quiz_questions):
    current_q = st.session_state.quiz_questions[st.session_state.current_question]
    current_difficulty = current_q.get('difficulty', 'medium')
    current_category = current_q.get('category', 'Unknown')
    
    # Progress bar
    progress = (st.session_state.current_question) / len(st.session_state.quiz_questions)
    st.progress(progress, text=f"Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}")
    
    # Centered current score
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric("Current Score", f"{st.session_state.score}/{st.session_state.current_question}")
    
    # Centered question with bigger text
    st.markdown("<br>", unsafe_allow_html=True)  # Add some space
    
    # Center the question number, difficulty, and category indicators
    category_emoji = get_category_emoji(current_category)
    difficulty_emoji = get_difficulty_emoji(current_difficulty)
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2>Question {st.session_state.current_question + 1} {difficulty_emoji} {category_emoji}</h2>
        <p style='color: #888; font-size: 0.9rem;'>{current_difficulty.title()} • {current_category.title()}</p>
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

# Quiz completed - Results screen with difficulty and category analysis
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
        
        # Show quiz settings
        category_emoji = get_category_emoji(st.session_state.selected_category)
        difficulty_emoji = get_difficulty_emoji(st.session_state.selected_difficulty) if st.session_state.selected_difficulty != 'mixed' else '🎲'
        
        st.markdown(f"**Quiz Type:** {category_emoji} {st.session_state.selected_category.title()} • {difficulty_emoji} {st.session_state.selected_difficulty.title()}")
        
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
    
    # Category and difficulty breakdown
    st.markdown("---")
    
    # Category breakdown (if mixed categories)
    if st.session_state.selected_category == 'all':
        st.markdown("### 📊 Performance by Category")
        
        category_breakdown = {}
        for answer in st.session_state.answers:
            cat = answer.get('category', 'Unknown')
            if cat not in category_breakdown:
                category_breakdown[cat] = [0, 0]  # [correct, total]
            category_breakdown[cat][1] += 1  # total
            if answer['is_correct']:
                category_breakdown[cat][0] += 1  # correct
        
        cols = st.columns(min(len(category_breakdown), 4))
        for i, (cat, (correct, total)) in enumerate(category_breakdown.items()):
            with cols[i % len(cols)]:
                pct = (correct / total) * 100
                cat_emoji = get_category_emoji(cat)
                st.metric(
                    f"{cat_emoji} {cat.title()}", 
                    f"{correct}/{total} ({pct:.0f}%)"
                )
    
    # Difficulty breakdown (if mixed difficulty)
    if st.session_state.selected_difficulty == 'mixed':
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
        question_category = answer.get('category', 'Unknown')
        difficulty_emoji = get_difficulty_emoji(question_difficulty)
        category_emoji = get_category_emoji(question_category)
        
        with st.expander(f"Question {i}: {'✅' if answer['is_correct'] else '❌'} {difficulty_emoji} {category_emoji} {question_category.title()}"):
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

# Sidebar with additional info including difficulty stats only
with st.sidebar:
    st.markdown("### 🏁 About This Quiz")
    
    if st.session_state.all_questions:
        st.markdown(f"""
        **Question Database:**
        - Total Questions: {total_questions}
        
        **Difficulty Breakdown:**
        """)
        
        # Show difficulty stats with emojis
        for difficulty, count in difficulty_stats.items():
            emoji = get_difficulty_emoji(difficulty)
            st.markdown(f"- {emoji} {difficulty.title()}: {count} questions")
        
        st.markdown(f"""
        **Quiz Format:**
        - Up to 5 random questions per quiz
        - Multiple choice format with instant feedback and explanations
        - Choose your preferred difficulty level and category!
        """)
    
    st.markdown("""
    This NASCAR quiz tests your knowledge across different categories:
    - **History**: NASCAR's past and milestones
    - **Drivers**: Famous racers and their achievements
    - **Tracks**: Racing venues and their characteristics  
    - **Cars**: Vehicle specs and technology
    - **Records**: Racing achievements and statistics
    - **Rules**: NASCAR regulations and procedures
    
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
        current_category = st.session_state.selected_category
        difficulty_emoji = get_difficulty_emoji(current_difficulty) if current_difficulty != 'mixed' else '🎲'
        category_emoji = get_category_emoji(current_category)
        
        st.markdown(f"**Current Quiz:**")
        st.markdown(f"- {category_emoji} Category: {current_category.title()}")
        st.markdown(f"- {difficulty_emoji} Difficulty: {current_difficulty.title()}")
        
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