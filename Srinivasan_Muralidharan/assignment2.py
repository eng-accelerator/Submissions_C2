import streamlit as st
from datetime import datetime
from openai import OpenAI
import os
import json

st.set_page_config(
	page_title="Personality Chatbot",
	page_icon="🎭",
	layout="wide",
)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
	# Try Streamlit secrets first (recommended)
	if "OPENAI_API_KEY" in st.secrets:
		api_key = st.secrets["OPENAI_API_KEY"]
	# Fallback to environment variable
	elif "OPENAI_API_KEY" in os.environ:
		api_key = os.environ["OPENAI_API_KEY"]
	# Fallback to hardcoded (for development - not recommended for production)
	elif not api_key or api_key.startswith("your-"):
		st.error("⚠️ OPENAI_API_KEY not found. Please set it in Streamlit secrets or environment variables.")
		return None
	
	if not api_key:
		st.error("⚠️ OPENAI_API_KEY is empty.")
		return None
	
	return OpenAI(api_key=api_key)

client = get_openai_client()

# Personality definitions with system prompts
PERSONALITIES = {
	"Professional Business Assistant": {
		"system_prompt": """You are a Professional Business Assistant. Your role is to provide formal, structured, and business-focused guidance.

Key characteristics:
- Formal and professional tone
- Structured responses with clear points (numbered lists, bullet points)
- Business strategy and professional communication expertise
- Results-oriented and efficient
- Polite and respectful

Always provide actionable, professional advice with concrete steps and clear outcomes.""",
		"description": "Formal, structured, business-focused. Perfect for professional communication and strategy.",
		"icon": "💼",
		"example": "How can I structure a quarterly business review meeting?"
	},
	"Creative Writing Helper": {
		"system_prompt": """You are a Creative Writing Helper. Your role is to inspire, encourage, and support creative expression.

Key characteristics:
- Imaginative and expressive language
- Enthusiastic and artistic tone
- Expertise in creative writing, storytelling, and artistic projects
- Encouraging and inspiring
- Uses metaphors and creative language when appropriate

Help users unlock their creativity, overcome writer's block, and craft compelling narratives.""",
		"description": "Imaginative, expressive, inspiring. Ideal for creative writing, storytelling, and artistic projects.",
		"icon": "✨",
		"example": "Help me write a compelling opening for my novel"
	},
	"Technical Expert": {
		"system_prompt": """You are a Technical Expert. Your role is to provide precise, detailed, and technically accurate guidance.

Key characteristics:
- Precise and analytical language
- Detailed explanations with code examples when relevant
- Programming, technology, and problem-solving expertise
- Methodical and educational approach
- Breaks down complex concepts into understandable parts

Always provide clear, accurate technical information with practical examples and best practices.""",
		"description": "Precise, detailed, code-focused. Perfect for programming, technology, and technical problem-solving.",
		"icon": "🔧",
		"example": "Explain how React hooks work with a code example"
	},
	"Friendly Companion": {
		"system_prompt": """You are a Friendly Companion. Your role is to be supportive, empathetic, and conversational.

Key characteristics:
- Casual and warm tone
- Supportive and empathetic approach
- General chat and emotional support expertise
- Encouraging and positive
- Conversational and relatable

Be a good listener, offer encouragement, and help users feel heard and supported.""",
		"description": "Casual, supportive, conversational. Great for general chat, emotional support, and friendly advice.",
		"icon": "🤗",
		"example": "I'm feeling stressed about an upcoming presentation. Any advice?"
	},
	"Custom Personality": {
		"system_prompt": """You are a helpful assistant with a customizable personality. Adapt your style based on user preferences.""",
		"description": "User-defined personality. Customize the style, expertise, and tone to your needs.",
		"icon": "🎨",
		"example": "You can customize this personality!"
	}
}

MAX_MESSAGES = 75

def init_state():
	if "messages" not in st.session_state:
		st.session_state.messages = []
	if not st.session_state.messages:
		st.session_state.messages.append({
			"role": "assistant",
			"content": "🎭 Hello! I'm your multi-personality assistant. Choose a personality from the sidebar to get started!",
			"time": datetime.utcnow(),
		})
	
	if "current_personality" not in st.session_state:
		st.session_state.current_personality = "Professional Business Assistant"
	
	if "personality_history" not in st.session_state:
		st.session_state.personality_history = []
	
	if "custom_prompt" not in st.session_state:
		st.session_state.custom_prompt = ""
	
	if "show_personality_indicators" not in st.session_state:
		st.session_state.show_personality_indicators = True
	
	if "session_started_at" not in st.session_state:
		st.session_state.session_started_at = None
	
	if "app_opened_at" not in st.session_state:
		st.session_state.app_opened_at = datetime.utcnow()
	
	if "history_limit" not in st.session_state:
		st.session_state.history_limit = 40
	
	if "show_timestamps" not in st.session_state:
		st.session_state.show_timestamps = True

def get_system_prompt() -> str:
	"""Get the system prompt for the current personality."""
	personality = st.session_state.current_personality
	
	if personality == "Custom Personality" and st.session_state.custom_prompt:
		return st.session_state.custom_prompt
	
	return PERSONALITIES[personality]["system_prompt"]

def generate_response(user_text: str) -> str:
	"""Generate a response using the current personality's system prompt."""
	if not client:
		return "I'm sorry, but I'm unable to respond right now. Please check your API key configuration."
	
	try:
		system_prompt = get_system_prompt()
		
		# Build conversation context (last 10 messages for context)
		messages = [{"role": "system", "content": system_prompt}]
		for msg in st.session_state.messages[-10:]:
			if msg["role"] in ["user", "assistant"]:
				messages.append({
					"role": msg["role"],
					"content": msg["content"]
				})
		
		# Add current user message
		messages.append({"role": "user", "content": user_text})
		
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=messages,
			temperature=0.7,
		)
		
		return response.choices[0].message.content
	except Exception as e:
		return f"I encountered an error: {str(e)}. Please try again."

init_state()

# Sidebar configuration
with st.sidebar:
	st.header("🎭 Personality Selector")
	
	# Personality selection
	st.subheader("Choose Personality")
	previous_personality = st.session_state.current_personality
	st.session_state.current_personality = st.selectbox(
		"Select Personality",
		options=list(PERSONALITIES.keys()),
		index=list(PERSONALITIES.keys()).index(st.session_state.current_personality),
	)
	
	# Track personality changes
	if previous_personality != st.session_state.current_personality:
		if st.session_state.messages and st.session_state.messages[-1]["role"] != "system":
			st.session_state.personality_history.append({
				"from": previous_personality,
				"to": st.session_state.current_personality,
				"time": datetime.utcnow(),
			})
	
	# Display current personality info
	current_personality_info = PERSONALITIES[st.session_state.current_personality]
	st.info(f"""
	**{current_personality_info['icon']} {st.session_state.current_personality}**
	
	{current_personality_info['description']}
	
	**Example:** {current_personality_info['example']}
	""")
	
	# Custom personality configuration
	if st.session_state.current_personality == "Custom Personality":
		with st.expander("⚙️ Customize Personality", expanded=True):
			st.session_state.custom_prompt = st.text_area(
				"Define Custom Personality",
				value=st.session_state.custom_prompt,
				placeholder="""You are a helpful assistant. Describe your personality, expertise area, and communication style here.

Example:
You are a motivational fitness coach. You're energetic, supportive, and knowledgeable about exercise and nutrition. Use an encouraging tone and provide practical workout tips.""",
				height=150,
			)
			if st.session_state.custom_prompt:
				st.success("✅ Custom personality configured!")
			else:
				st.warning("⚠️ Define your custom personality above")
	
	st.divider()
	
	# Display options
	st.subheader("Display Options")
	st.session_state.show_personality_indicators = st.checkbox(
		"Show Personality Indicators", 
		value=st.session_state.show_personality_indicators
	)
	st.session_state.show_timestamps = st.checkbox("Show Timestamps", value=st.session_state.show_timestamps)
	st.session_state.history_limit = st.slider(
		"Max Chat History", 
		1, 
		MAX_MESSAGES, 
		min(st.session_state.history_limit, MAX_MESSAGES)
	)
	
	st.divider()
	
	# Session stats
	st.subheader("Session Stats")
	session_start = st.session_state.session_started_at or st.session_state.app_opened_at
	duration = datetime.utcnow() - session_start
	total_seconds = int(duration.total_seconds())
	minutes = total_seconds // 60
	seconds = total_seconds % 60
	messages_sent = sum(1 for m in st.session_state.messages if m["role"] == "user")
	st.metric("Session Duration", f"{minutes}m {seconds}s")
	st.metric("Messages Sent", messages_sent)
	st.metric("Total Messages", len(st.session_state.messages))
	st.metric("Personality Switches", len(st.session_state.personality_history))
	
	# Personality history
	if st.session_state.personality_history:
		with st.expander("🔄 Personality History", expanded=False):
			for i, change in enumerate(reversed(st.session_state.personality_history[-5:]), 1):
				st.caption(f"{i}. {change['from']} → {change['to']}")
	
	st.divider()
	
	# Utilities
	def format_transcript():
		lines = []
		for m in st.session_state.messages:
			ts = m.get("time")
			when = ts.strftime("%Y-%m-%d %H:%M:%S") if isinstance(ts, datetime) else ""
			role = m.get("role", "")
			content = m.get("content", "")
			lines.append(f"[{when}] {role}: {content}" if when else f"{role}: {content}")
		return "\n".join(lines) + ("\n" if lines else "")
	
	st.download_button(
		label="📥 Download Chat (.txt)",
		data=format_transcript(),
		file_name=f"personality-chat-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.txt",
		mime="text/plain",
		use_container_width=True,
	)
	
	if st.button("🗑️ Clear Chat", use_container_width=True):
		st.session_state.messages = []
		st.session_state.session_started_at = None
		st.session_state.personality_history = []
		st.session_state.messages.append({
			"role": "assistant",
			"content": "🎭 Chat cleared! Choose a personality and let's start fresh!",
			"time": datetime.utcnow(),
		})
		st.rerun()

# Main interface
st.title(f"🎭 {PERSONALITIES[st.session_state.current_personality]['icon']} Personality Chatbot")
current_info = PERSONALITIES[st.session_state.current_personality]
st.caption(f"**Current Personality:** {st.session_state.current_personality} | {current_info['description']}")

# Personality indicator banner
if st.session_state.show_personality_indicators:
	st.info(f"🎭 You're chatting with **{st.session_state.current_personality}** {current_info['icon']}")

# Chat transcript
for msg in st.session_state.messages[-st.session_state.history_limit:]:
	with st.chat_message(msg["role"]):
		if st.session_state.show_timestamps and isinstance(msg.get("time"), datetime):
			st.caption(msg["time"].strftime("%H:%M:%S"))
		st.markdown(msg["content"])

# User input
prompt = st.chat_input(f"Message {st.session_state.current_personality}...")
if prompt:
	if not client:
		st.error("OpenAI client not initialized. Please check your API key.")
		st.stop()
	
	now = datetime.utcnow()
	if st.session_state.session_started_at is None:
		st.session_state.session_started_at = now
	
	# Add user message
	st.session_state.messages.append({"role": "user", "content": prompt, "time": now})
	with st.chat_message("user"):
		if st.session_state.show_timestamps:
			st.caption(now.strftime("%H:%M:%S"))
		st.write(prompt)
	
	# Generate response with current personality
	with st.spinner(f"💭 {st.session_state.current_personality} is thinking..."):
		response = generate_response(prompt)
	
	# Add to messages
	assistant_time = datetime.utcnow()
	st.session_state.messages.append({"role": "assistant", "content": response, "time": assistant_time})
	
	# Trim if exceeding cache
	if len(st.session_state.messages) > MAX_MESSAGES:
		st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
	
	with st.chat_message("assistant"):
		if st.session_state.show_personality_indicators:
			st.caption(f"{PERSONALITIES[st.session_state.current_personality]['icon']} {st.session_state.current_personality}")
		if st.session_state.show_timestamps:
			st.caption(assistant_time.strftime("%H:%M:%S"))
		st.markdown(response)
	
	st.rerun()

# Footer
st.divider()

with st.expander("📘 About This Chatbot", expanded=False):
	st.markdown("""
	**Personality Features:**
	- 🎭 **Multiple Personalities**: Switch between 5 different AI personalities
	- 💼 **Professional**: Formal, business-focused assistant
	- ✨ **Creative**: Imaginative writing and artistic helper
	- 🔧 **Technical**: Precise, code-focused expert
	- 🤗 **Friendly**: Casual, supportive companion
	- 🎨 **Custom**: Define your own personality
	
	Each personality has unique communication styles, expertise areas, and approaches!
	""")

with st.expander("🧑‍🏫 How to Use", expanded=False):
	st.markdown("""
	1. **Select a Personality** from the sidebar dropdown
	2. **Start chatting** - responses will match the selected personality
	3. **Switch personalities** anytime - the conversation continues with the new personality
	4. **Customize** - Use "Custom Personality" to define your own AI assistant style
	5. **Compare** - Try the same question with different personalities to see how they differ!
	""")

# Show all personalities
with st.expander("🎭 Explore All Personalities", expanded=False):
	cols = st.columns(3)
	for i, (name, info) in enumerate(PERSONALITIES.items()):
		col = cols[i % 3]
		with col:
			st.markdown(f"**{info['icon']} {name}**")
			st.caption(info['description'])
			st.write(f"*Example: {info['example']}*")
			if i < len(PERSONALITIES) - 1:
				st.divider()

