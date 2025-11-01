🧠 Text Summarization & Export Tool
🔍 Overview

This project is a simple yet powerful text summarization web app built with Gradio and a transformer-based summarization model (Falconsai/text_summarization).
It allows users to input long text, generate an AI-powered summary, and download the summarized text as a timestamped .txt file.

🚀 Features

🧩 AI Summarization: Uses a pre-trained transformer model to condense lengthy text into concise summaries.

💾 Export to File: Automatically saves the summary as summary_YYYY-MM-DD_HH-MM-SS.txt.

🖥️ Simple Web UI: Powered by Gradio
, so you can run it locally or deploy it easily.

🕒 Timestamped Downloads: Each summary file is uniquely named to avoid overwrites.

🧰 Tech Stack
Component	Description
Python 3.x	Programming language
Gradio	For interactive web UI
Transformers (Hugging Face)	For the summarization model
Datetime	For timestamp-based file naming
⚙️ Installation

Clone the repository:

git clone https://github.com/<your-username>/text-summarization-export-tool.git
cd text-summarization-export-tool


Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate      # For macOS/Linux
venv\Scripts\activate         # For Windows


Install dependencies:

pip install gradio transformers torch

▶️ Usage

Run the Gradio app locally:

python app.py


This will launch a local Gradio server and display a link in your terminal (e.g., http://127.0.0.1:7860).

🧭 Steps:

Enter your text or paragraph in "✏️ Enter Description".

Click "✨ Generate Summary" to generate an AI summary.

Click "⬇️ Download Summary" to save the result as a .txt file.

📂 Project Structure
text-summarization-export-tool/
│
├── app.py                 # Main application file (Gradio UI + summarization logic)
├── README.md              # Project documentation
└── requirements.txt       # Optional: dependency list (can be generated via pip freeze)

🧪 Example Output

Input:

Artificial Intelligence (AI) is transforming industries by automating complex tasks and improving decision-making. From healthcare to finance, AI-powered systems are enabling smarter operations and insights.

Output Summary:

AI is revolutionizing industries with automation and data-driven insights, enhancing efficiency and decision-making across sectors.

Downloaded File:

summary_2025-11-01_10-45-23.txt

🛠️ Troubleshooting

If you see NameError: name 'pipeline' is not defined, install and import it:

from transformers import pipeline


If Gradio doesn’t open in your browser, manually visit http://127.0.0.1:7860.

🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests to improve the summarization flow, add model options, or enhance the UI.

📜 License

This project is licensed under the MIT License.
Feel free to use, modify, and share with attribution.

💡 Future Enhancements

 Add multiple summarization models for user selection

 Support for uploading text files or PDFs

 Add a character counter and word limit

 Deploy to Hugging Face Spaces or Streamlit Cloud

 💻 Installation Command

Once you have requirements.txt in your project folder, users can simply run:

pip install -r requirements.txt
