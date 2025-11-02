import streamlit as st
from datetime import datetime
import time
import io

st.set_page_config(page_title="Demo Assistant", layout="wide")

# -------- Initialize State --------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "messages_sent" not in st.session_state:
    st.session_state.messages_sent = 0
if "show_dev_info" not in st.session_state:
    st.session_state.show_dev_info = False

# -------- Sidebar Configuration --------
with st.sidebar:
    st.title("🛠️ Configuration")
    st.header("Assistant Settings")
    assistant_name = st.text_input("Assistant Name", value="Demo Assistant")
    response_style = st.selectbox("Response Style", options=["Friendly", "Formal", "Concise"])
    st.header("Chat Settings")
    max_history = st.slider("Max Chat History", 10, 100, 40)
    show_timestamps = st.checkbox("Show Timestamps", value=True)

    st.header("Session Stats")
    duration = int(time.time() - st.session_state.start_time)
    minutes, seconds = divmod(duration, 60)
    st.markdown(f"**Session Duration**: {minutes}m {seconds}s")
    st.markdown(f"**Messages Sent**: {st.session_state.messages_sent}")
    st.markdown(f"**Total Messages**: {len(st.session_state.chat_history)}")

    st.header("Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.messages_sent = 0
            st.session_state.start_time = time.time()
    with col2:
        chat_txt = "\n".join(
            [f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}" for msg in st.session_state.chat_history]
        )
        st.download_button("Export Chat", data=chat_txt, file_name="chat_history.txt")
        

# -------- Main Chat UI --------
st.markdown(
    f"<h1 style='text-align: left;'>🚀 {assistant_name}</h1>"
    f"Response Style: <b>{response_style}</b> | History Limit: <b>{max_history} messages</b>",
    unsafe_allow_html=True,
)
st.info("Hello! I'm your demo assistant. How can I help you today?")

# -------- Chat History Cards --------
for msg in st.session_state.chat_history[-max_history:]:
    icon = "🧑" if msg["sender"] == "You" else "🤖"
    bg_col = "#222" if msg["sender"] == "You" else "#353a47"
    text_col = "#fff"
    sender_str = f"<span style='font-weight:bold'>{icon} {msg['sender']}</span>"
    time_str = f"<span style='float:right; color:#bbb'>{msg['timestamp']}</span>" if show_timestamps else ""
    st.markdown(
        f"""
        <div style="
            background: {bg_col}; 
            color: {text_col}; 
            padding: 0.75em; 
            border-radius: 0.5em; 
            margin: 0.5em 0;
            font-size:1.15em">
            {sender_str} {time_str}<br>{msg['message']}
        </div>
        """, unsafe_allow_html=True
    )

# -------- Expanders and Dev Info --------
with st.expander("About This Demo"):
    st.write("This is a sample Streamlit Chat Assistant inspired by your frontend screenshot.")

with st.expander("Instructor Notes"):
    st.write("You can extend this code to include actual AI/model integration.")

st.session_state.show_dev_info = st.checkbox("Show Development Info", value=st.session_state.show_dev_info)
if st.session_state.show_dev_info:
    st.write(" ---- Development Info ---- ")

# -------- Chat Input and Sending --------
with st.form(key="chat_form", clear_on_submit=True):
    message = st.text_input("Message", placeholder=f"Message {assistant_name}...")
    submitted = st.form_submit_button("Send")
    if submitted and message.strip():
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Add user message
        st.session_state.chat_history.append({
            "sender": "You",
            "message": message,
            "timestamp": timestamp
        })
        st.session_state.messages_sent += 1
        # Bot reply (demo logic)
        bot_reply = (
            f"Hey, great question about '{message}'! "
            f"I'm happy to help you with that. Here's what I'm thinking..."
        )
        st.session_state.chat_history.append({
            "sender": assistant_name,
            "message": bot_reply,
            "timestamp": timestamp
        })

