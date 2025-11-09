# Tavily Integration Guide

## Why Tavily?

Tavily Search API is specifically designed for AI agents and LLM-based research systems. It provides several advantages over traditional search APIs:

### Key Benefits

1. **AI-Optimized Results**
   - Pre-ranked and deduplicated results
   - Relevance scores for each result
   - Structured data format (not just links)

2. **Parsed Content**
   - Returns actual content, not just snippets
   - No need to scrape websites
   - Content is already cleaned and formatted

3. **AI-Generated Answers**
   - Provides synthesized answers from multiple sources
   - Perfect for quick summaries
   - Reduces need for additional processing

4. **Better for Agents**
   - Designed specifically for LLM workflows
   - Faster response times
   - More reliable than web scraping

## Setup

### 1. Get Tavily API Key

1. Visit https://tavily.com/
2. Sign up for an account
3. Get your API key from the dashboard

### 2. Configure Environment

Add to your `.env` file:

```env
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Install Dependencies

```bash
pip install tavily-python
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The retriever agent automatically uses Tavily when the API key is configured:

```python
from agents.retriever import ContextualRetrieverAgent

retriever = ContextualRetrieverAgent()
results = retriever.retrieve("Latest developments in quantum computing 2024")
```

## Response Format

Tavily returns structured results:

```python
{
    "title": "Article Title",
    "url": "https://example.com/article",
    "content": "Parsed article content...",
    "score": 0.95,  # Relevance score (0-1)
    "published_date": "2024-01-15",
    "raw_content": "Full page content..."  # Optional
}
```

## Features Used

### Search Depth
- `"basic"` - Fast, surface-level search
- `"advanced"` - Deeper search with more sources (default)

### Include Answer
- `include_answer=True` - Get AI-generated summary
- Automatically included in results

### Max Results
- Configurable per query
- Default: 5 results per source type

## Comparison: Tavily vs DuckDuckGo

| Feature | Tavily | DuckDuckGo |
|---------|--------|------------|
| Structured Results | ✅ Yes | ❌ String only |
| Parsed Content | ✅ Yes | ❌ No |
| Relevance Scores | ✅ Yes | ❌ No |
| AI-Generated Answers | ✅ Yes | ❌ No |
| Designed for AI | ✅ Yes | ❌ No |
| Rate Limits | ✅ Generous | ⚠️ Strict |
| Reliability | ✅ High | ⚠️ Variable |

## Troubleshooting

### API Key Not Working
- Verify key is correct in `.env` file
- Check key is active at https://tavily.com/
- Ensure no extra spaces in key

### No Results Returned
- Check query is clear and specific
- Try increasing `max_results`
- Verify API key has credits

### Rate Limit Errors
- Tavily has generous rate limits
- Check your plan at https://tavily.com/
- Consider caching results for demos

## Migration from DuckDuckGo

The system automatically uses Tavily when configured. If Tavily is not available, it falls back gracefully:

1. **With Tavily API Key**: Uses Tavily for all web searches
2. **Without Tavily API Key**: Logs warning, continues with ArXiv only

## Best Practices

1. **Use Specific Queries**
   - Better results with clear, specific queries
   - Include timeframes: "2024", "recent", etc.

2. **Leverage AI Answers**
   - Tavily's AI-generated answers are great for summaries
   - Use for quick overviews before deep analysis

3. **Combine with ArXiv**
   - Tavily for web/news
   - ArXiv for research papers
   - Best of both worlds

4. **Cache Results**
   - For demo mode, cache Tavily results
   - Reduces API calls during presentations

---

**Tavily makes research retrieval much better for AI agents!** 🚀

