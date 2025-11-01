

import gradio as gr
from transformers import pipeline
from gtts import gTTS
import tempfile
import json
import os
import requests
from typing import List

# -----------------------
# Summarization pipeline or API
# -----------------------
PIPELINE_CACHE = {}

def summarize_via_api(model_id: str, text: str, min_length: int, max_length: int):
    token = os.getenv("HF_API_KEY")
    if not token:
        return None
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": text, "parameters": {"min_length": min_length, "max_length": max_length}}
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0 and "summary_text" in data[0]:
            return data[0]["summary_text"]
        return str(data)
    except Exception as e:
        return f"API error: {e}"

def get_summarizer(model_id: str):
    if model_id in PIPELINE_CACHE:
        return PIPELINE_CACHE[model_id]
    summarizer = pipeline("summarization", model=model_id, tokenizer=model_id, device=-1)
    PIPELINE_CACHE[model_id] = summarizer
    return summarizer

def summarize_text(model_id: str, text: str, min_length: int, max_length: int):
    if not text or text.strip() == "":
        return "Please provide input text.", ""

    # Try Hugging Face Inference API if token exists
    if os.getenv("HF_API_KEY"):
        summary = summarize_via_api(model_id, text, min_length, max_length)
        return summary, "(via Hugging Face API)"

    # Otherwise use local pipeline
    summarizer = get_summarizer(model_id)
    try:
        outputs = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return outputs[0]["summary_text"].strip(), "(local)"
    except Exception as e:
        return f"Error during summarization: {e}", ""

# -----------------------
# Chat and exports
# -----------------------
CHAT_HISTORY: List[dict] = []

def add_to_history(user_text: str, summary_text: str, model: str):
    CHAT_HISTORY.append({"user_text": user_text, "summary": summary_text, "model": model})

def export_chat_json():
    if not CHAT_HISTORY:
        return None
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(CHAT_HISTORY, f, ensure_ascii=False, indent=2)
    return path

def export_chat_txt():
    if not CHAT_HISTORY:
        return None
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for i, e in enumerate(CHAT_HISTORY, 1):
            f.write(f"--- Entry {i} ---\nUser:\n{e['user_text']}\n\nSummary:\n{e['summary']}\n\n")
    return path

# -----------------------
# Text-to-Speech
# -----------------------
def tts_generate(text: str, lang: str = "en"):
    if not text:
        return None
    try:
        t = gTTS(text=text, lang=lang)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        t.save(path)
        return path
    except Exception:
        return None

# -----------------------
# Theme CSS
# -----------------------
LIGHT_CSS = ":root{--bg:#fff;--fg:#0f172a;}body{background:var(--bg);color:var(--fg);}" 
DARK_CSS = ":root{--bg:#0b1220;--fg:#e6eef8;}body{background:var(--bg);color:var(--fg);}" 

MODEL_CHOICES = ["facebook/bart-large-cnn", "sshleifer/distilbart-cnn-12-6", "google/pegasus-xsum"]
TTS_LANGS = {"English": "en"}

with gr.Blocks(css=LIGHT_CSS) as demo:
    gr.Markdown("# 📚 Summarizer + TTS (Hugging Face + Gradio)")

    with gr.Row():
        with gr.Column(scale=3):
            text_in = gr.Textbox(lines=8, label="Paste text")
            model_dd = gr.Dropdown(MODEL_CHOICES, value=MODEL_CHOICES[0], label="Model")
            min_len = gr.Slider(10, 100, value=20, label="Min length")
            max_len = gr.Slider(20, 400, value=120, label="Max length")
            summarize_btn = gr.Button("Summarize")

            export_json_btn = gr.Button("Export JSON")
            export_txt_btn = gr.Button("Export TXT")
            clear_btn = gr.Button("Clear history")

        with gr.Column(scale=2):
            summary_out = gr.Textbox(lines=10, label="Summary")
            source_lbl = gr.Markdown(visible=False)
            lang_dd = gr.Dropdown(list(TTS_LANGS.keys()), value="English", label="TTS language")
            tts_btn = gr.Button("Play TTS")
            tts_dl = gr.Button("Download TTS")
            theme_toggle = gr.Radio(["Light", "Dark"], value="Light", label="Theme")
            css_html = gr.HTML(visible=False)

    def do_summarize(text, model, minl, maxl):
        summary, src = summarize_text(model, text, int(minl), int(maxl))
        add_to_history(text, summary, model)
        return summary, gr.update(value=f"Source: {src}", visible=True)

    summarize_btn.click(do_summarize, [text_in, model_dd, min_len, max_len], [summary_out, source_lbl])

    def do_tts(summary, lang_name):
        path = tts_generate(summary, lang=TTS_LANGS[lang_name])
        return path

    tts_btn.click(do_tts, [summary_out, lang_dd], outputs=[gr.Audio(label="Audio")])

    export_json_btn.click(lambda: export_chat_json(), outputs=[gr.File(label="Download JSON")])
    export_txt_btn.click(lambda: export_chat_txt(), outputs=[gr.File(label="Download TXT")])
    clear_btn.click(lambda: CHAT_HISTORY.clear() or gr.update(value=""), outputs=[summary_out])

    def apply_theme(choice):
        return f"<style>{DARK_CSS if choice=='Dark' else LIGHT_CSS}</style>"

    theme_toggle.change(apply_theme, [theme_toggle], [css_html])

    gr.Markdown("--- If you set HF_TOKEN in your environment, the app will use the Hugging Face Inference API instead of local model downloads.")


demo.queue().launch(share=False)
