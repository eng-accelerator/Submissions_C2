"""
Chatbot UI Component for Streamlit
Provides chat interface with model selection and web search
"""

import streamlit as st
from chatbot import chat_with_llm, get_available_models, format_search_results_html


def render_chatbot_tab():
    """Render the chatbot interface in Streamlit"""

    st.markdown("### 💬 AI Assistant with Web Search")
    st.markdown("Chat with AI models and optionally search the web for real-time information.")

    # Model selection
    col1, col2 = st.columns([2, 1])

    with col1:
        available_models = get_available_models()
        selected_model_name = st.selectbox(
            "Select AI Model",
            options=list(available_models.keys()),
            index=2  # Default to GPT-3.5 Turbo
        )
        selected_model = available_models[selected_model_name]

    with col2:
        use_web_search = st.checkbox("🌐 Enable Web Search", value=False)
        if st.button("🗑️ Clear Chat"):
            st.session_state["chat_messages"] = []
            st.session_state["chat_history"] = []
            st.rerun()

    st.markdown("---")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.get("chat_messages", []):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("search_results"):
                    with st.expander("🔍 View Search Results"):
                        st.markdown(format_search_results_html(msg["search_results"]), unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask me anything...")

    if user_input:
        # Add user message to chat
        st.session_state["chat_messages"].append({
            "role": "user",
            "content": user_input
        })

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # Get AI response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response, search_results = chat_with_llm(
                        message=user_input,
                        model=selected_model,
                        conversation_history=st.session_state.get("chat_history", []),
                        use_web_search=use_web_search
                    )

                st.markdown(response)

                # Show search results if available
                if search_results:
                    with st.expander("🔍 View Search Results"):
                        st.markdown(format_search_results_html(search_results), unsafe_allow_html=True)

        # Save to conversation history
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        st.session_state["chat_history"].append({"role": "assistant", "content": response})

        # Save to messages for display
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": response,
            "search_results": search_results
        })

        st.rerun()

    # Show example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **General Questions:**
        - Explain how neural networks work
        - What are the differences between Python 2 and 3?

        **With Web Search** (enable "Enable Web Search"):
        - What are the latest news about AI?
        - What's the weather forecast for tomorrow?
        - Tell me about recent tech announcements
        - What are the current cryptocurrency prices?
        """)
