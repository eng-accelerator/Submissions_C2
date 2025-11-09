import streamlit as st
from datetime import datetime
from openai import OpenAI
import os
import json

st.set_page_config(
	page_title="Translation Assistant",
	page_icon="🌐",
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
	else:
		st.error("⚠️ OPENAI_API_KEY not found. Please set it in Streamlit secrets or environment variables.")
		return None
	
	if not api_key:
		st.error("⚠️ OPENAI_API_KEY is empty.")
		return None
	
	return OpenAI(api_key=api_key)
client = get_openai_client()

# Supported languages with common names
LANGUAGES = {
	"English": "en",
	"Spanish": "es",
	"French": "fr",
	"German": "de",
	"Italian": "it",
	"Portuguese": "pt",
	"Chinese (Simplified)": "zh",
	"Japanese": "ja",
	"Korean": "ko",
	"Russian": "ru",
	"Arabic": "ar",
	"Hindi": "hi",
	"Dutch": "nl",
	"Polish": "pl",
	"Turkish": "tr",
	"Greek": "el",
	"Swedish": "sv",
	"Norwegian": "no",
	"Danish": "da",
	"Finnish": "fi",
	"Czech": "cs",
	"Romanian": "ro",
	"Thai": "th",
	"Vietnamese": "vi",
}

MAX_MESSAGES = 75

def init_state():
	if "messages" not in st.session_state:
		st.session_state.messages = []
	if not st.session_state.messages:
		st.session_state.messages.append({
			"role": "assistant",
			"content": "🌐 Hello! I'm your translation assistant. Type text in any language and I'll detect it and translate it for you!",
			"time": datetime.utcnow(),
		})
	
	if "target_language" not in st.session_state:
		st.session_state.target_language = "English"
	
	if "translation_history" not in st.session_state:
		st.session_state.translation_history = []
	
	if "show_cultural_context" not in st.session_state:
		st.session_state.show_cultural_context = True
	
	if "show_alternatives" not in st.session_state:
		st.session_state.show_alternatives = True
	
	if "show_confidence" not in st.session_state:
		st.session_state.show_confidence = True
	
	if "session_started_at" not in st.session_state:
		st.session_state.session_started_at = None
	
	if "app_opened_at" not in st.session_state:
		st.session_state.app_opened_at = datetime.utcnow()
	
	if "history_limit" not in st.session_state:
		st.session_state.history_limit = 40
	
	if "show_timestamps" not in st.session_state:
		st.session_state.show_timestamps = True

def detect_language(text: str) -> dict:
	"""Detect the language of input text using OpenAI."""
	if not client:
		return {"language": "Unknown", "code": "unknown", "confidence": 0.0}
	
	system_prompt = """You are a language detection expert. Analyze the text and determine its language.
Return your response in this exact JSON format:
{
  "language": "Language Name in English",
  "code": "ISO 639-1 code (e.g., 'en', 'es', 'fr')",
  "confidence": 0.95
}
Be precise and accurate. Confidence should be between 0.0 and 1.0."""
	
	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": f"Detect the language of this text: {text}"}
			],
			response_format={"type": "json_object"},
			temperature=0.3,
		)
		result = json.loads(response.choices[0].message.content)
		return result
	except Exception as e:
		st.error(f"Error detecting language: {e}")
		return {"language": "Unknown", "code": "unknown", "confidence": 0.0}

def translate_text(text: str, source_lang: str, target_lang: str, source_lang_code: str, target_lang_code: str) -> dict:
	"""Translate text with cultural context and alternatives."""
	if not client:
		return {
			"translation": "Translation unavailable (API key missing)",
			"alternatives": [],
			"cultural_notes": "",
			"confidence": 0.0
		}
	
	system_prompt = f"""You are an expert translator specializing in {source_lang} to {target_lang} translations.
Your task is to provide:
1. A high-quality, natural translation
2. Alternative translation options (2-3 variants if appropriate)
3. Cultural context and notes about idiomatic expressions, regional variations, or usage notes

Return your response in this exact JSON format:
{{
  "translation": "Main translation text",
  "alternatives": ["Alternative 1", "Alternative 2"],
  "cultural_notes": "Cultural context, usage notes, or regional variations (or empty string if not needed)",
  "confidence": 0.95
}}

If the text is already in {target_lang}, still provide the translation and mark it as such.
Confidence should reflect translation quality (0.0 to 1.0)."""
	
	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": f"Translate this {source_lang} text to {target_lang}:\n\n{text}"}
			],
			response_format={"type": "json_object"},
			temperature=0.7,
		)
		result = json.loads(response.choices[0].message.content)
		return result
	except Exception as e:
		st.error(f"Error translating: {e}")
		return {
			"translation": f"Translation error: {str(e)}",
			"alternatives": [],
			"cultural_notes": "",
			"confidence": 0.0
		}

def format_translation_response(detection: dict, translation: dict, source_text: str, target_lang: str):
	"""Format the translation response with all details."""
	response_parts = []
	
	# Detection info
	response_parts.append(f"🔍 **Detected Language:** {detection.get('language', 'Unknown')}")
	if st.session_state.show_confidence:
		confidence_percent = int(detection.get('confidence', 0) * 100)
		response_parts.append(f"   _(Confidence: {confidence_percent}%)_")
	
	response_parts.append("")  # Blank line
	
	# Translation
	response_parts.append(f"🎯 **Translation ({target_lang}):** {translation.get('translation', 'N/A')}")
	if st.session_state.show_confidence:
		trans_confidence = int(translation.get('confidence', 0) * 100)
		response_parts.append(f"   _(Confidence: {trans_confidence}%)_")
	
	# Alternatives
	alternatives = translation.get('alternatives', [])
	if alternatives and st.session_state.show_alternatives:
		response_parts.append("")
		response_parts.append("🌟 **Alternative Translations:**")
		for i, alt in enumerate(alternatives[:3], 1):
			response_parts.append(f"   {i}. {alt}")
	
	# Cultural notes
	cultural_notes = translation.get('cultural_notes', '').strip()
	if cultural_notes and st.session_state.show_cultural_context:
		response_parts.append("")
		response_parts.append(f"💡 **Cultural Context:**")
		response_parts.append(f"   {cultural_notes}")
	
	return "\n".join(response_parts)

init_state()

# Sidebar configuration
with st.sidebar:
	st.header("🌐 Configuration")
	
	st.subheader("Translation Settings")
	st.session_state.target_language = st.selectbox(
		"Target Language",
		options=list(LANGUAGES.keys()),
		index=list(LANGUAGES.keys()).index(st.session_state.target_language),
	)
	
	st.subheader("Display Options")
	st.session_state.show_cultural_context = st.checkbox("Show Cultural Context", value=st.session_state.show_cultural_context)
	st.session_state.show_alternatives = st.checkbox("Show Alternative Translations", value=st.session_state.show_alternatives)
	st.session_state.show_confidence = st.checkbox("Show Confidence Scores", value=st.session_state.show_confidence)
	st.session_state.show_timestamps = st.checkbox("Show Timestamps", value=st.session_state.show_timestamps)
	st.session_state.history_limit = st.slider("Max Chat History", 1, MAX_MESSAGES, min(st.session_state.history_limit, MAX_MESSAGES))
	
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
	st.metric("Translations Done", len(st.session_state.translation_history))
	
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
		file_name=f"translation-chat-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.txt",
		mime="text/plain",
		use_container_width=True,
	)
	
	if st.button("🗑️ Clear Chat", use_container_width=True):
		st.session_state.messages = []
		st.session_state.session_started_at = None
		st.session_state.translation_history = []
		st.session_state.messages.append({
			"role": "assistant",
			"content": "🌐 Chat cleared! I'm ready to translate for you.",
			"time": datetime.utcnow(),
		})
		st.rerun()
	
	# Translation History
	if st.session_state.translation_history:
		with st.expander("📚 Translation History", expanded=False):
			for i, hist in enumerate(reversed(st.session_state.translation_history[-10:]), 1):
				st.write(f"**{i}.** {hist['source']} → {hist['target']}")
				st.caption(f"From {hist['source_lang']} to {hist['target_lang']}")

# Main interface
st.title("🌐 Translation Assistant")
st.caption(f"Target Language: **{st.session_state.target_language}** | Type text in any language to translate")

# Chat transcript
for msg in st.session_state.messages[-st.session_state.history_limit:]:
	with st.chat_message(msg["role"]):
		if st.session_state.show_timestamps and isinstance(msg.get("time"), datetime):
			st.caption(msg["time"].strftime("%H:%M:%S"))
		st.markdown(msg["content"])

# User input
prompt = st.chat_input(f"Type text to translate to {st.session_state.target_language}...")
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
	
	# Process translation
	with st.spinner("🔍 Detecting language and translating..."):
		# Step 1: Detect language
		detection = detect_language(prompt)
		
		# Step 2: Translate
		target_lang_code = LANGUAGES[st.session_state.target_language]
		source_lang = detection.get('language', 'Unknown')
		source_lang_code = detection.get('code', 'unknown')
		
		translation = translate_text(prompt, source_lang, st.session_state.target_language, source_lang_code, target_lang_code)
		
		# Format response
		response = format_translation_response(detection, translation, prompt, st.session_state.target_language)
		
		# Save to history
		st.session_state.translation_history.append({
			"source": prompt,
			"target": translation.get('translation', ''),
			"source_lang": source_lang,
			"target_lang": st.session_state.target_language,
			"time": now,
		})
		
		# Add to messages
		assistant_time = datetime.utcnow()
		st.session_state.messages.append({"role": "assistant", "content": response, "time": assistant_time})
		
		# Trim if exceeding cache
		if len(st.session_state.messages) > MAX_MESSAGES:
			st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
	
	with st.chat_message("assistant"):
		if st.session_state.show_timestamps:
			st.caption(assistant_time.strftime("%H:%M:%S"))
		st.markdown(response)
	
	st.rerun()

# Footer
st.divider()

with st.expander("📘 About This Translation Assistant", expanded=False):
	st.markdown("""
	**Features:**
	- 🔍 Automatic language detection
	- 🎯 High-quality translation to your target language
	- 🌟 Alternative translation options
	- 💡 Cultural context and usage notes
	- 📊 Confidence scoring
	- 📚 Translation history tracking
	""")

with st.expander("🧑‍🏫 How to Use", expanded=False):
	st.markdown("""
	1. Select your target language from the sidebar
	2. Type or paste text in any language
	3. The assistant will automatically detect the source language
	4. Get translation with cultural context and alternatives
	5. Check translation history in the sidebar
	""")


