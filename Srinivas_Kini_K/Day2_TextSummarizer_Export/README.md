# 🧠 Text Summarization & Export Tool

## 🔍 Overview
This project is a simple yet powerful **text summarization web app** built with **Gradio** and a **transformer-based summarization model** (`Falconsai/text_summarization`).  
It allows users to input long text, generate an AI-powered summary, and **download the summarized text** as a timestamped `.txt` file.

---

## 🚀 Features
- 🧩 **AI Summarization:** Uses a pre-trained transformer model to condense lengthy text into concise summaries.  
- 💾 **Export to File:** Automatically saves the summary as `summary_YYYY-MM-DD_HH-MM-SS.txt`.  
- 🖥️ **Simple Web UI:** Powered by [Gradio](https://www.gradio.app/), so you can run it locally or deploy it easily.  
- 🕒 **Timestamped Downloads:** Each summary file is uniquely named to avoid overwrites.  

---

## 🧰 Tech Stack
| Component | Description |
|------------|-------------|
| **Python 3.x** | Programming language |
| **Gradio** | For interactive web UI |
| **Transformers (Hugging Face)** | For the summarization model |
| **Datetime** | For timestamp-based file naming |

---

## ⚙️ Installation

### 1️⃣ Clone the repository

git clone https://github.com/<your-username>/text-summarization-export-tool.git
cd text-summarization-export-tool 

### 2. Create and activate a virtual environment

For **macOS/Linux**:
```bash
python -m venv venv
source venv/bin/activate
