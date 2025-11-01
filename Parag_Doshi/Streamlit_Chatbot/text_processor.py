import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# Task 1: Setup and Basic Interface
st.set_page_config(
    page_title="Interactive Text Processor",
    page_icon="📝",
    layout="wide"
)

# Initialize theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS for dark mode
dark_mode_css = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #1E1E1E; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #2D2D2D; }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] { color: #FFFFFF !important; }
    .stButton button { background-color: #4A4A4A; color: #FFFFFF; }
    .stTextArea textarea { background-color: #2D2D2D; color: #FFFFFF; caret-color: #FFFFFF !important; }
    div[data-baseweb="select"] > div { background-color: #2D2D2D; color: #FFFFFF; }
    div[data-baseweb="select"] svg { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .success { background-color: #1E4620 !important; color: #9CFF9C !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    [data-testid="stExpander"] { background-color: #2D2D2D !important; }
    [data-testid="stExpander"] [data-testid="stMarkdown"] p { color: #FFFFFF !important; }
    button[data-testid="baseButton-secondary"] { color: #FFFFFF !important; }
    .stNumberInput input { color: #FFFFFF !important; background-color: #2D2D2D !important; }

    /* Input field labels */
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label {
        color: #FFFFFF !important;
    }
    
    /* Processing History Styling */
    [data-testid="stExpander"] {
        background-color: #2D2D2D !important;
        border: 1px solid #404040 !important;
    }
    [data-testid="stExpander"] [data-testid="stMarkdown"] {
        color: #FFFFFF !important;
    }
    
    /* Numbers in configuration */
    .stNumberInput input {
        color: #FFFFFF !important;
        background-color: #2D2D2D !important;
    }
    
    /* Dark mode toggle and text */
    [data-testid="baseButton-secondary"] {
        color: #FFFFFF !important;
    }
    
    /* Processing History Numbers */
    [data-testid="stExpander"] [data-testid="stText"] {
        color: #FFFFFF !important;
    }
    
    /* Expander headers */
    button[kind="expanderHeader"] {
        background-color: #383838 !important;
        color: #FFFFFF !important;
        border: 1px solid #404040 !important;
    }
    
    /* Toggle button in dark mode */
    .toggleButton-knob {
        background-color: #FFFFFF !important;
    }
    .toggleButton-slider {
        background-color: #4A4A4A !important;
    }
    .toggleButton-slider[aria-checked="true"] {
        background-color: #4CAF50 !important;
    }
</style>
"""

# Light mode CSS
light_mode_css = """
<style>
    .operation-card {
        background-color: #FFFFFF !important;
    }
    /* Ensure good contrast in light mode */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #31333F !important;
    }
    label {
        color: #31333F !important;
    }
</style>
"""

st.markdown(dark_mode_css if st.session_state.dark_mode else light_mode_css, unsafe_allow_html=True)

st.title("Interactive Text Processor")
st.subheader("A versatile tool for processing and analyzing text in various ways")

# Initialize session states
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processing_type' not in st.session_state:
    st.session_state.processing_type = "AI Chat"

# Initialize AI model
@st.cache_resource
def load_model():
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=2048,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
        repetition_penalty=1.15
    )

# Function to generate AI response
def generate_ai_response(prompt, history):
    conversation = ""
    for msg in history:
        conversation += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
    conversation += f"User: {prompt}\nAssistant:"
    
    response = generator(
        conversation,
        max_new_tokens=512,
        num_return_sequences=1,
        pad_token_id=generator.tokenizer.eos_token_id
    )
    
    full_response = response[0]['generated_text']
    return full_response.split("Assistant:")[-1].strip()

try:
    generator = load_model()
    st.sidebar.success("AI Chat Model loaded successfully!")
except Exception as e:
    st.error(f"Error loading AI model: {str(e)}")
    st.stop()

# st.title("Interactive Text Processor")
# st.subheader("A versatile tool for processing and analyzing text in various ways")

# Task 2: Input Components
# Sidebar Options
with st.sidebar:
    st.header("Configuration")
    
    # Dark mode toggle at the top of sidebar
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.toggle("Dark Mode 🌙", value=st.session_state.dark_mode, key="dark_mode_toggle"):
            if not st.session_state.dark_mode:  # Only rerun if mode actually changed
                st.session_state.dark_mode = True
                st.rerun()
        else:
            if st.session_state.dark_mode:  # Only rerun if mode actually changed
                st.session_state.dark_mode = False
                st.rerun()
    
    st.divider()
    
    st.session_state.processing_type = st.selectbox(
        "Select Processing Type",
        ["AI Chat", "Word Count", "Character Count", "Reverse Text", "Uppercase", "Title Case"]
    )
    
    if st.session_state.processing_type == "AI Chat":
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.subheader("Text Processing Settings")
        char_limit = st.number_input(
            "Character Limit",
            min_value=10,
            max_value=500,
            value=100
        )
        show_steps = st.checkbox("Show processing steps")
        
        # History settings
        st.subheader("History Settings")
        history_limit = st.number_input(
            "Number of operations to remember",
            min_value=1,
            max_value=10,
            value=5,
            help="How many recent operations to show in the history"
        )
        if st.button("Clear History"):
            st.session_state.processing_history = []
            st.rerun()

# Task 3: Text Processing Logic
def process_text(text, process_type):
    """Process text based on selected type"""
    if not text:
        return None, {}
    
    steps = {}
    result = None
    
    if process_type == "Word Count":
        # Show detailed word counting process
        words = text.split()
        result = len(words)
        steps = {
            "1. Input Text": text,
            "2. Split into Words": words,
            "3. Words Identified": [f"'{word}'" for word in words],
            "4. Count Words": f"{result} words",
            "Python Code": "len(text.split())"
        }
    
    elif process_type == "Character Count":
        # Show character counting process
        with_spaces = len(text)
        text_no_spaces = text.replace(" ", "")
        without_spaces = len(text_no_spaces)
        spaces_count = with_spaces - without_spaces
        result = f"With spaces: {with_spaces}\nWithout spaces: {without_spaces}"
        steps = {
            "1. Input Text": text,
            "2. Total Characters (with spaces)": f"{with_spaces} characters",
            "3. Space Characters Found": f"{spaces_count} spaces",
            "4. Text without Spaces": text_no_spaces,
            "5. Characters (without spaces)": f"{without_spaces} characters",
            "Python Code": "len(text) for total, len(text.replace(' ', '')) for no spaces"
        }
    
    elif process_type == "Reverse Text":
        # Show step-by-step process
        char_list = list(text)
        reversed_list = char_list[::-1]
        result = ''.join(reversed_list)
        steps = {
            "1. Input Text": text,
            "2. Convert to Character List": char_list,
            "3. Reverse the List": reversed_list,
            "4. Join Characters": result,
            "Python One-liner": "text[::-1]"
        }
    
    elif process_type == "Uppercase":
        # Show uppercase conversion process
        result = text.upper()
        changed_chars = [(c, c.upper()) for c in text if c.upper() != c]
        steps = {
            "1. Input Text": text,
            "2. Characters to Convert": changed_chars if changed_chars else "No characters need conversion",
            "3. Final Result": result,
            "Python Code": "text.upper()"
        }
    
    elif process_type == "Title Case":
        # Show title case conversion process
        words = text.split()
        titled_words = [word.title() for word in words]
        result = ' '.join(titled_words)
        steps = {
            "1. Input Text": text,
            "2. Split into Words": words,
            "3. Convert Each Word": [f"{word} → {word.title()}" for word in words],
            "4. Join Words": result,
            "Python Code": "text.title() or ' '.join(word.title() for word in text.split())"
        }
    
    return result, steps

# Different layouts for AI Chat vs Text Processing
if st.session_state.processing_type == "AI Chat":
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(message["user"])
        with st.chat_message("assistant"):
            st.write(message["assistant"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_ai_response(prompt, st.session_state.chat_history)
                st.write(response)
                
        # Append to chat history
        st.session_state.chat_history.append({
            "user": prompt,
            "assistant": response
        })
else:
    # Regular text processing interface
    text_input = st.text_area(
        "Enter your text here:",
        height=150,
        max_chars=char_limit,
        help=f"Maximum {char_limit} characters allowed"
    )
    process_button = st.button("Process Text", type="primary")

# Initialize processing history in session state if not exists
if 'processing_history' not in st.session_state:
    st.session_state.processing_history = []

# Process text when the button is clicked (for non-chat features)
if st.session_state.processing_type != "AI Chat" and 'process_button' in locals() and process_button and text_input:
    MIN_LENGTH = 5  # Minimum text length requirement
    
    # Input validation
    if len(text_input.strip()) < MIN_LENGTH:
        st.error(f"Please enter at least {MIN_LENGTH} characters. Current length: {len(text_input.strip())}")
    else:
        result, steps = process_text(text_input, st.session_state.processing_type)
        
        # Display results in a container
        with st.container():
            # Define colors for different processing types based on theme
            type_colors = {
                "Word Count": "#00B4D8" if st.session_state.dark_mode else "#1f77b4",      # Blue
                "Character Count": "#2ECC71" if st.session_state.dark_mode else "#2ca02c",  # Green
                "Reverse Text": "#BD93F9" if st.session_state.dark_mode else "#9467bd",     # Purple
                "Uppercase": "#FF6B6B" if st.session_state.dark_mode else "#d62728",        # Red
                "Title Case": "#FFB86C" if st.session_state.dark_mode else "#ff7f0e"        # Orange
            }
            
            # Get color for current processing type
            color = type_colors.get(st.session_state.processing_type, "#000000")
            
            # Display result with custom styling
            st.markdown(f"""
                <div style='padding: 20px; border-radius: 10px; background-color: {color}20;'>
                    <h3 style='color: {color};'>Result</h3>
                    <p style='font-size: 18px;'>{result}</p>
                </div>
            """, unsafe_allow_html=True)
                
            # Show processing steps if enabled
            if show_steps:
                st.markdown(f"<h3 style='color: {color};'>Processing Steps</h3>", unsafe_allow_html=True)
                for step, value in steps.items():
                    st.write(f"**{step}:** {value}")
            
            # Success message
            st.success("Processing complete!")
            
            # Download button
            download_text = str(result)
            st.download_button(
                label="Download Result",
                data=download_text,
                file_name="processed_text.txt",
                mime="text/plain"
            )
            
            # Text length warning
            if len(text_input) > char_limit * 0.9:
                st.warning(f"Getting close to the {char_limit} character limit!")
            
            # Add to processing history with configurations
            history_entry = {
                'type': st.session_state.processing_type,
                'input': text_input[:50] + '...' if len(text_input) > 50 else text_input,
                'result': str(result)[:50] + '...' if len(str(result)) > 50 else str(result),
                'timestamp': st.session_state.get('current_time', 'Now'),
                'configs': {
                    'character_limit': char_limit,
                    'show_steps': show_steps,
                }
            }
            st.session_state.processing_history.insert(0, history_entry)
            # Keep only last N entries based on user configuration
            st.session_state.processing_history = st.session_state.processing_history[:history_limit]
            
            # Display processing history
            if st.session_state.processing_history:
                st.markdown(f"""
                    <h3 style='margin-top: 30px;'>Processing History</h3>
                    <p style='color: #666;'>(Last {history_limit} operations)</p>
                """, unsafe_allow_html=True)
                
                for i, entry in enumerate(st.session_state.processing_history, 1):
                    with st.expander(
                        f"Operation {i}: {entry['type']} - {entry['timestamp']}", 
                        expanded=(i == 1)  # Auto-expand most recent operation
                    ):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write("**Input:**", entry['input'])
                            st.write("**Result:**", entry['result'])
                        
                        with col2:
                            st.write("**Configurations:**")
                            st.write("- Character limit:", entry['configs']['character_limit'])
                            st.write("- Show steps:", "Yes" if entry['configs']['show_steps'] else "No")