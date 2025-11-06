# 🤖 Agentic RAG System

An intelligent Retrieval-Augmented Generation (RAG) system that automatically searches multiple sources to answer your questions. The agent intelligently decides which source to query based on availability and relevance.

## 🌟 Features

- **Intelligent Multi-Source Search**: Automatically searches PDF documents, Wikipedia, and the web in order of priority
- **Agentic Decision Making**: Uses a ReAct agent that thinks through which tools to use
- **PDF Processing**: Upload and search through your own PDF documents
- **Vector Search**: Uses FAISS for semantic similarity search within PDFs
- **Interactive Chat Interface**: Beautiful Streamlit UI with chat history
- **Transparent Reasoning**: See the agent's decision-making process in real-time

## 🔄 How It Works

The system follows an intelligent search hierarchy:

1. **Primary Source - Your PDF**: Always checks uploaded PDF first
2. **Secondary Source - Wikipedia**: Falls back to Wikipedia for general knowledge
3. **Tertiary Source - Web Search**: Uses DuckDuckGo as last resort for current information

The agent automatically decides when to move to the next source based on whether the current source has relevant information.

## 📋 Prerequisites

- Python 3.8 or higher
- OpenRouter API key (for LLM access)
- OpenAI API key (for embeddings)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd agentic-rag-system
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install streamlit langchain langchain-openai langchain-community faiss-cpu pypdf python-dotenv wikipedia duckduckgo-search
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Getting API Keys:**
- OpenRouter: Sign up at [openrouter.ai](https://openrouter.ai/)
- OpenAI: Get your key from [platform.openai.com](https://platform.openai.com/)

## 💻 Usage

1. **Start the application**
```bash
streamlit run app.py
```

2. **Upload a PDF**
   - Use the sidebar to upload your PDF document
   - Wait for the system to process and create the vector database

3. **Ask questions**
   - Type your question in the chat input
   - The agent will automatically search the best sources
   - View the agent's reasoning process in the expandable section

## 📚 Sample PDFs for Testing

Try these sample PDFs to test the system:

- **AI Research**: [Attention is All You Need](https://arxiv.org/pdf/1706.03762.pdf) - Original Transformer paper
- **Climate Science**: [IPCC Climate Report](https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_SPM.pdf)
- **Programming**: Any Python documentation PDF

## 🛠️ Technical Architecture

### Components

- **LLM**: GPT-4 via OpenRouter for agent reasoning
- **Embeddings**: OpenAI embeddings for vector search
- **Vector Store**: FAISS for similarity search
- **Agent Framework**: LangChain ReAct agent
- **Tools**:
  - `SearchPDF`: Queries uploaded PDF using vector similarity
  - `SearchWikipedia`: Searches Wikipedia for factual information
  - `SearchWeb`: DuckDuckGo search for current/web information

### Agent Decision Flow

```
User Question
    ↓
[Agent Analyzes Question]
    ↓
Try SearchPDF
    ↓
Found? → Return Answer
    ↓ No
Try SearchWikipedia
    ↓
Found? → Return Answer
    ↓ No
Try SearchWeb
    ↓
Return Answer
```

## 🎯 Example Queries

**Questions for PDF:**
- "What is the main topic of this document?"
- "Summarize the key findings"
- "What methodology was used?"

**Questions triggering Wikipedia:**
- "Who is Albert Einstein?" (if not in PDF)
- "What is quantum mechanics?"

**Questions triggering Web Search:**
- "What are the latest developments in AI?"
- "Current news about [topic]"

## 🔧 Configuration

### Adjust Chunk Size
In `PDFRetriever.setup_vectorstore()`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Increase for more context
    chunk_overlap=200      # Increase for better continuity
)
```

### Change LLM Model
In `create_agentic_rag()`:
```python
llm = ChatOpenAI(
    model="openai/gpt-4o",  # Try gpt-3.5-turbo for faster/cheaper
    temperature=0            # Increase for more creative responses
)
```

### Adjust Agent Iterations
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,  # Increase if agent needs more steps
    verbose=True
)
```

## 📊 Cost Optimization

- Use `gpt-3.5-turbo` instead of `gpt-4o` for lower costs
- Reduce `chunk_size` to decrease embedding costs
- Limit `max_iterations` to prevent excessive API calls
- Cache frequently asked questions

## 🐛 Troubleshooting

### "No PDF loaded" error
- Ensure you've uploaded a PDF before asking questions
- Check that the PDF uploaded successfully (green checkmark)

### "API Key not found" error
- Verify your `.env` file exists and contains valid keys
- Restart the Streamlit app after adding keys

### Slow responses
- Try reducing `chunk_size` to 500
- Use a faster model like `gpt-3.5-turbo`
- Check your internet connection

### PDF processing fails
- Ensure PDF is not password-protected
- Try with a smaller PDF first
- Check if PDF contains readable text (not just images)

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Keep your API keys secure and rotate them regularly
