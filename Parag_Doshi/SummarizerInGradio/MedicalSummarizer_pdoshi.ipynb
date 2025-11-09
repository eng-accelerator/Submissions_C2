import gradio as gr
from transformers import pipeline
import os

# Step 1: Load model from Hugging Face (replace with your own)
# Example: "facebook/bart-large-cnn" or "t5-small"
MODEL_NAME = "Falconsai/medical_summarization"

# Step 2: Use your Hugging Face token (you can set as environment variable)
# HF_TOKEN = os.getenv("HF_TOKEN")  # or paste your token directly here (not recommended for public repos)

from google.colab import userdata
# userdata.get('HF_TOKEN')


# Step 3: Define summarization function
# Load summarization pipeline
summarizer = pipeline("summarization", model=MODEL_NAME)

def summarize_text(text):
    if not text.strip():
        return "⚠️ Please provide a medical document to summarize."
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]["summary_text"]

# Step 4: Define export functionality
def export_summary(summary):
    with open("medical_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    return "medical_summary.txt"

# Step 4.1:  Generate an image from text
#TTS = pipeline("text-to-image", model="SDXL LoRA Fine-tuning - ZB-Tech/Text-To-Image") # Corrected model name
#def generate_image(text):
#    if not text.strip():
#        return "⚠️ Please provide a medical document to generate an image from."

#   image = TTS(text)[0] # Access the image from the output list
#    return image

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="auto",
    token=userdata.get('HF_TOKEN'),)

# output is a PIL.Image object
#image = client.text_to_image(
#    "Astronaut riding a horse",
#    model="Mridulmadhok/Mridul_flux",
#)



# Step 5: Build Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 📝 Medical Report Summarizer ")
    gr.Markdown("Enter your medical report below and click **Summarize**.")

    with gr.Row():
        text_input = gr.Textbox(
            label="Input Text",
            placeholder="Paste a medical report here...",
            lines=10
        )
    with gr.Row():
        summarize_button = gr.Button("🔍 Summarize")
        clear_button = gr.Button("🧹 Clear")
    with gr.Row():
        output_box = gr.Textbox(label="Summary Output", lines=10)

    with gr.Row():
        gr.Markdown("## 🖼️ Generate Image from Summary") # Added new section title
        genimage_button = gr.Button("🎨 Generate Image - Not working")
    #    image_output = gr.Image(label="Generated Image") # Added image output component

    with gr.Row():
        export_button = gr.Button("💾 Export Summary")
        gr.Markdown("---") # Added separator

    # Actions
    summarize_button.click(fn=summarize_text, inputs=text_input, outputs=output_box)
    clear_button.click(fn=lambda: "", inputs=None, outputs=[text_input, output_box])
    export_button.click(fn=export_summary, inputs=output_box, outputs=gr.File())
    # genimage_button.click(fn=generate_image, inputs=output_box, outputs=image_output) # Changed input to output_box




    # Optional: Toggle light/dark theme
    gr.Markdown("---")
    gr.Markdown("🌗 Switch between light and dark themes using the toggle button in the top-right corner.")

# Launch app
if __name__ == "__main__":
    demo.launch(share=False)
