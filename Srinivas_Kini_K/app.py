import gradio as gr
from datetime import datetime



def export_text_to_file(summary_text):
    """
    Writes the given summary text to a timestamped file and returns the file path.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"summary_{timestamp}.txt"
    with open(file_path, "w") as f:
        f.write(summary_text)
    return file_path

def text_summarizer(text):
  summarizer = pipeline("summarization", model="Falconsai/text_summarization")

  ARTICLE = text
  response=summarizer(ARTICLE, max_length=1000, min_length=30, do_sample=False)
  response=response[0]["summary_text"]
  return response

def process_and_generate_text(description_text):
    """
    Example function that processes the description and generates summarized text.
    """
    processed_text = text_summarizer(description_text)
    return processed_text

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Text Summarization & Export Tool")

    # Renamed and labeled textboxes
    description_input = gr.TextArea(
        label="✏️ Enter Description",
        placeholder="Write a paragraph or text to summarize...",
        max_lines=10
    )

    summary_output = gr.TextArea(
        label="🧾 Generated Summary",
        placeholder="Your summary will appear here...",
        max_lines=10
    )

    with gr.Row():
        summarize_button = gr.Button("✨ Generate Summary")
        download_button = gr.DownloadButton("⬇️ Download Summary", visible=True)

    # Step 1: Process text
    summarize_button.click(
        fn=process_and_generate_text,
        inputs=description_input,
        outputs=summary_output,
    )

    # Step 2: Export processed text when user clicks download
    download_button.click(
        fn=export_text_to_file,
        inputs=summary_output,
        outputs=download_button
    )

demo.launch(show_api=True)
