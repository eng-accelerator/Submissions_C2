# Medical Report Summarizer

This project implements an interactive medical report summarization tool using state-of-the-art NLP models and a user-friendly web interface.

## Overview

The application provides a complete workflow for:
- Summarizing medical reports using the Falconsai/medical_summarization model
- Converting summaries to speech using the Suno/Bark text-to-speech model
- Exporting summaries to text files
- Interactive web interface built with Gradio

## Key Features

1. **Medical Report Summarization**
   - Uses specialized medical summarization model
   - Configurable summary length (75-300 tokens)
   - Handles formatting and preprocessing automatically

2. **Text-to-Speech Generation**
   - High-quality voice synthesis using Suno/Bark model
   - GPU acceleration when available
   - Natural-sounding medical terminology pronunciation

3. **User Interface**
   - Clean, intuitive Gradio interface
   - Light/dark theme support
   - Sample medical report included
   - Real-time component state management

## Technical Implementation

- **Model Architecture**: Uses Hugging Face Transformers pipeline
- **Dependencies**:
  - transformers
  - gradio
  - soundfile
  - torch
  - os, time (standard libraries)

## Security Features

- Secure token management using Colab userdata secrets
- No hardcoded API tokens or sensitive information

## Usage Notes

1. Connect to a T4 GPU runtime in Google Colab for optimal performance
2. Audio generation takes approximately 4-6 minutes
3. Summary length is optimized for readability (75-300 tokens)
4. Supports both light and dark themes

## Implementation Details

The application is structured in several key components:

1. **Configuration and Setup**
   - Model initialization
   - Pipeline configuration
   - Environment checks

2. **Core Functions**
   - `summarize_text`: Handles text summarization
   - `export_summary`: Manages file exports
   - `generate_voice`: Handles text-to-speech conversion
   - `update_component_states`: Manages UI state

3. **User Interface**
   - Input text area with sample data
   - Control buttons for main actions
   - Dynamic output components
   - Progress indicators

## Performance Considerations

- GPU acceleration for text-to-speech
- Optimized model loading
- Efficient state management
- Responsive UI updates

This implementation demonstrates the practical application of AI in medical documentation, combining NLP and speech synthesis in a user-friendly interface.
