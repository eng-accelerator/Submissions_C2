# 🔬 Multi-Agent AI Researcher - Streamlit UI

A web-based interface for the Multi-Agent AI Researcher system that uses multiple AI agents to conduct comprehensive research on any topic.

## Features

- 🔍 **Multi-Agent Research**: Uses 5 specialized AI agents for context retrieval, analysis, insight generation, report building, and validation
- 🤖 **Multiple Model Support**: Choose from Claude Sonnet 4, GPT-4o, or Llama 3.1 70B
- 📚 **Document Support**: Upload, paste, or use sample documents for context
- 🎨 **Beautiful UI**: Modern Streamlit interface with real-time progress tracking
- 💾 **Export Results**: Download research reports as text files
- ⚡ **Performance Metrics**: Track processing times for each agent

### Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. The app will open in your browser (usually at `http://localhost:8501`)

3. Configure your settings:
   - Enter your OpenRouter API key (get one from https://openrouter.ai/keys)
   - Select a model
   - Adjust temperature and max iterations if needed
   - Load documents (optional)

4. Enter your research question and click "Start Research"

5. Wait for the research to complete (typically 30-60 seconds)

6. Review the results and download if needed

## API Key

You need an OpenRouter API key to use this application. Get one from:
https://openrouter.ai/keys

Make sure you have credits available at:
https://openrouter.ai/credits

## Configuration

- **Temperature**: Controls creativity (0.0 = focused, 2.0 = creative)
- **Max Iterations**: Maximum number of validation iterations (1-5)
- **Documents**: Optional context documents for research

## Research Workflow

The system uses 5 agents in sequence:

1. **Contextual Retriever**: Retrieves relevant context from documents
2. **Critical Analysis**: Analyzes information quality and relevance
3. **Insight Generation**: Generates key insights
4. **Report Builder**: Creates comprehensive research report
5. **Validation**: Validates report quality (may iterate if needed)

## File Structure

- `researcher.py`: Core researcher class and logic
- `streamlit_app.py`: Streamlit user interface
- `requirements.txt`: Python dependencies
- `README.md`: This file

## Troubleshooting

- **API Key Error**: Make sure your API key is valid and has credits
- **Model Error**: Try a different model if one fails
- **Slow Performance**: Research typically takes 30-60 seconds
- **Import Error**: Make sure all dependencies are installed

## License

This project is provided as-is for research and educational purposes.
