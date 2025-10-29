# neelay_mehta


---

# 🧠 AI Text Summarizer using Gradio

This project is a **web-based text summarization app** built with **Gradio** and **Hugging Face Transformers**.
It uses the **Falconsai/text_summarization** model to generate concise summaries of long text passages,
and includes **dark/light theme toggle** and **summary export functionality**.

---

## 🚀 Features

* 🧩 **Automatic Summarization** — powered by the pre-trained `facebook/bart-large-cnn` model
* 🌗 **Theme Toggle** — switch between *Light (gradio/soft)* and *Dark (gradio/dracula)* modes
* 📄 **Export Option** — download the generated summary as a `.txt` file
* ⚡ **Interactive UI** — built using Gradio’s `Blocks()` API for flexibility and a modern layout
* 🪶 **Clean Design** — simple Markdown titles, button-based flow, and responsive layout

---

## 🧰 Requirements

Install the required Python libraries:

```bash
pip install gradio transformers torch
```

---

## 🧾 Usage

### ▶️ Run the App

Save the code in a file named `app.py` and run:

```bash
python app.py
```

The app will launch locally (by default on `http://127.0.0.1:7860`).

---

## 💻 Code Overview

### 1. **Model Loading**

```python
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
```

Uses the **Hugging Face Transformers** pipeline to load the BART model for summarization.

---

### 2. **Core Functions**

#### `summarize_text(text)`

* Takes a long paragraph as input
* Returns a concise summary (120 words max, 30 words min)

#### `export_summary(summary)`

* Saves the generated summary as `summary.txt`
* Returns a downloadable file path for Gradio

---

### 3. **UI with Gradio Blocks**

The app is structured with `gr.Blocks()` for layout flexibility:

* Text input box for the paragraph
* “Summarize” button to trigger the model
* Output box for the summary
* “Export Summary” button for download
* Theme toggle (Light/Dark)

```python
with gr.Blocks(theme=theme) as demo:
    gr.Markdown("## 🧠 AI Text Summarizer")
    ...
```

---

### 4. **Theme Toggle**

The app provides a simple **Light ↔ Dark** theme switcher:

```python
theme_toggle = gr.Radio(
    ["gradio/soft", "gradio/dracula"],
    value=theme,
    label="🌓 Theme"
)
```

---

## 🧩 App Flow

1. User enters a long text.
2. Clicks **“Summarize”** → The BART model generates a summary.
3. Clicks **“Export Summary”** → Downloads the summary as a `.txt` file.
4. Toggles between **Light/Dark mode** anytime.

---

## 🖼️ Example

**Input:**

> The industrial revolution began in the 18th century, transforming manufacturing processes and leading to rapid urbanization...

**Output:**

> The 18th-century industrial revolution revolutionized production, driving technological growth and urbanization.

---

## 🎨 Themes Used

| Theme            | Description                              |
| ---------------- | ---------------------------------------- |
| `gradio/soft`    | Default light theme with soft colors     |
| `gradio/dracula` | Dark theme for comfortable nighttime use |

---





---

## 👨‍💻 Author

**Neelay Mehta**

---


