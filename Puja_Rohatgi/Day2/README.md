"""
Gradio + Hugging Face Text Summarization app
Features:
- Summarize text using a selectable Hugging Face model (local or from AutoModel)
- Store a simple chat history (user inputs + summaries)
- Export chat as JSON or plain TXT
- Text-to-speech playback & download using gTTS (multi-language)
- Simple theme toggles (light / dark) via injected CSS

Requirements:
pip install gradio transformers sentencepiece gTTS==2.3.0

Run:
python gradio_hf_summarizer_app.py

Notes:
- If you don't want to download large HF models locally, set up the HF_TOKEN env var and use the Inference API or pick a small model.
- The app caches model pipelines per model id to avoid repeated reloading.


Gradio + Hugging Face Text Summarization app (API-ready)
Features:
- Summarize text using a Hugging Face model (local or via Inference API if HF_TOKEN is set)
- Store chat history and export as JSON/TXT
- Text-to-speech playback & download (multi-language)
- Theme toggle (light/dark)

Requirements:
pip install gradio transformers sentencepiece gTTS==2.3.0 requests

Run:
python gradio_hf_summarizer_app.py
"""
