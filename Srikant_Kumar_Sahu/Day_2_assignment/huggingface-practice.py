import gradio as gr
from transformers import pipeline
from huggingface_hub import whoami
import torch
import csv
import io
from datetime import datetime
from google.colab import userdata

# hf_token = userdata.get('HF_TOKEN')d

# Verify the token by checking your identity
try:
    user_info = whoami(token=hf_token)
    print(f"Logged in as: {user_info['name']}")
except Exception as e:
    print(f"Could not log in: {e}")
    print("Please make sure you have added your Hugging Face token to Colab Secrets with the name 'HF_TOKEN'")


# Load the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def generate_summary(text, summary_type):
    if not text.strip():
        return "Please enter some text to summarize."
    
    # Set parameters based on summary type
    if summary_type == "Short":
        max_length = 50
        min_length = 25
    elif summary_type == "Medium":
        max_length = 100
        min_length = 40
    else:  # Long
        max_length = 150
        min_length = 60
    
    try:
        # Generate summary using the Hugging Face model
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def create_csv_export(original_text, summary_text, summary_type):
    """
    Create a CSV file with the original text, summary, and metadata
    
    Args:
        original_text (str): The original input text
        summary_text (str): The generated summary
        summary_type (str): The type of summary (Short, Medium, Long)
    
    Returns:
        tuple: (filename, status_message)
    """
    if not summary_text or summary_text.startswith("Please enter") or summary_text.startswith("Error"):
        return None, "❌ No valid summary to export. Please generate a summary first."
    
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_export_{timestamp}.csv"
        
        # Create CSV content
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Timestamp', 'Summary Type', 'Original Text Length', 'Summary Length', 'Original Text', 'Summary'])
            
            # Write data
            export_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            original_length = len(original_text.split()) if original_text else 0
            summary_length = len(summary_text.split()) if summary_text else 0
            
            writer.writerow([
                export_timestamp,
                summary_type,
                original_length,
                summary_length,
                original_text[:500] + "..." if len(original_text) > 500 else original_text,  # Truncate if too long
                summary_text
            ])
        
        return filename, f"✅ CSV exported successfully as {filename}"
    except Exception as e:
        return None, f"❌ Error creating CSV: {str(e)}"

with gr.Blocks(title="Text Summarizer") as demo:
    gr.Markdown("# 📝 Text Summarizer")
    gr.Markdown("Enter your text and select a summary type to generate a summary.")
    
    with gr.Row():
        with gr.Column():
            # Input textbox for the text to summarize
            input_text = gr.Textbox(
                label="Text to Summarize",
                placeholder="Enter your text here...",
                lines=8,
                max_lines=15
            )
            
            # Dropdown for summary type
            summary_type = gr.Dropdown(
                choices=["Short", "Medium", "Long"],
                value="Medium",
                label="Summary Length"
            )
            
            # Generate button
            generate_btn = gr.Button("Generate Summary", variant="primary")
        
        with gr.Column():
            # Output textbox for the summary
            output_text = gr.Textbox(
                label="Generated Summary",
                lines=8,
                max_lines=15,
                interactive=False
            )
            
            # Status message
            status_msg = gr.Markdown("💡 Generate a summary first, then click 'Export as CSV' to download", visible=True)
            
            # Button row for actions
            with gr.Row():
                # Export button
                export_btn = gr.Button("📥 Export as CSV", variant="secondary", size="lg")
            
            # File download component
            csv_file = gr.File(
                label="📁 Download CSV File",
                visible=True
            )
    
    # Connect the generate button to the function
    generate_btn.click(
        fn=generate_summary,
        inputs=[input_text, summary_type],
        outputs=output_text
    )
    
    # Connect the export button to create CSV
    export_btn.click(
        fn=create_csv_export,
        inputs=[input_text, output_text, summary_type],
        outputs=[csv_file, status_msg]
    )

# Add some examples
    gr.Examples(
        examples=[
            ["Hugging Face is a company and open-source platform that provides tools and models for natural language processing (NLP). It has become a central hub for the ML community, offering a wide range of pre-trained models that can be easily used or fine-tuned for specific applications. Key aspects of Hugging Face include the Transformers library, Model Hub, Datasets library, and Tokenizers library. Hugging Face democratizes access to powerful ML models, making it easier for developers and researchers to build and deploy applications.", "Medium"],
            ["Artificial Intelligence (AI) is transforming the way we live and work. From virtual assistants to autonomous vehicles, AI technologies are becoming increasingly integrated into our daily lives. Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed. Deep learning, which uses neural networks with multiple layers, has revolutionized fields like computer vision and natural language processing.", "Short"],
            ["Climate change is one of the most pressing challenges of our time. Rising global temperatures, melting ice caps, and extreme weather events are clear indicators of the environmental changes occurring worldwide. The primary cause is the increased concentration of greenhouse gases in the atmosphere, largely due to human activities such as burning fossil fuels, deforestation, and industrial processes. Addressing climate change requires immediate action from governments, businesses, and individuals to reduce carbon emissions and transition to sustainable practices.", "Long"]
        ],
        inputs=[input_text, summary_type],
        outputs=output_text
    )
    
# Launch the interface
if __name__ == "__main__":
    demo.launch()