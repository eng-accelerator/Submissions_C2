import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="centered")

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ Configurations")

# Load API Key
assitant_name = st.sidebar.text_input("Assitant Name", type="default")

# Model selection
res_style = st.sidebar.selectbox(
    "Response Style",
    ["Friendly", "Casual", "Professional"],
    index=0
)

# Temperature control
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.5, 0.7, 0.1)

# System Prompt
system_prompt = st.sidebar.text_area(
    "🧠 System Prompt",
    "You are a helpful assistant that provides clear and concise answers."
)

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")


# --- Title ---
st.title("💬 Simple Chatbot Interface")

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Display chat history ---
for chat in st.session_state["messages"]:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# --- User Input ---
user_input = st.chat_input("Type your message...")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # --- Dummy Bot Response (Replace with your model or API call) ---
    bot_response = f"You said: **{user_input}**"
    
    # Display bot message
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    
    st.session_state["messages"].append({"role": "assistant", "content": bot_response})
