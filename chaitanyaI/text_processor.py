import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Interactive Text Processor", page_icon="📝")

# ---------- MAIN INTERFACE ----------
st.title("📝 Interactive Text Processor")
st.subheader("A simple app to analyze and transform text interactively.")

st.write(
    """
    This app lets you input any text and process it in different ways — 
    such as counting words, reversing text, or changing the case.  
    Use the **sidebar** to configure how you want the text processed.
    """
)

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Configuration Options")
st.sidebar.write("You’ll add interactive controls here in the next tasks.")
