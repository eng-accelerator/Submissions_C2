"""
AI Chatbot with Web Search Integration
Supports multiple OpenAI models and web search capabilities
"""

import os
import requests
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Available OpenAI models
OPENAI_MODELS = {
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "GPT-4": "openai/gpt-4",
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo"
}


def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web using Google Custom Search API

    Args:
        query: Search query
        num_results: Number of results to return (max 10 per request)

    Returns:
        List of search results with title, snippet, and link
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return [{
            'title': 'Google Search not configured',
            'snippet': 'Please add GOOGLE_API_KEY and GOOGLE_CSE_ID to your .env file. Get them from: https://console.cloud.google.com/',
            'link': ''
        }]

    try:
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': min(num_results, 10)  # Google API max is 10 per request
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                })
        else:
            return [{
                'title': 'No results found',
                'snippet': 'Try a different search query',
                'link': ''
            }]

        return results

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return [{
                'title': 'Search error',
                'snippet': 'Invalid Google API configuration. Check your GOOGLE_API_KEY and GOOGLE_CSE_ID.',
                'link': ''
            }]
        elif e.response.status_code == 403:
            return [{
                'title': 'Search quota exceeded',
                'snippet': 'Google API daily quota reached. Try again tomorrow or upgrade your quota.',
                'link': ''
            }]
        else:
            return [{
                'title': 'Search error',
                'snippet': f'HTTP {e.response.status_code}: {str(e)}',
                'link': ''
            }]
    except requests.exceptions.RequestException as e:
        return [{
            'title': 'Search error',
            'snippet': f'Error connecting to Google Search API: {str(e)}',
            'link': ''
        }]
    except Exception as e:
        return [{
            'title': 'Search error',
            'snippet': f'Unexpected error performing search: {str(e)}',
            'link': ''
        }]


def chat_with_llm(
    message: str,
    model: str = "openai/gpt-3.5-turbo",
    conversation_history: Optional[List[Dict[str, str]]] = None,
    use_web_search: bool = False,
    max_tokens: int = 2000
) -> Tuple[str, Optional[List[Dict[str, str]]]]:
    """
    Chat with LLM using OpenRouter API

    Args:
        message: User message
        model: Model to use (from OPENAI_MODELS)
        conversation_history: Previous conversation messages
        use_web_search: Whether to perform web search and include results
        max_tokens: Maximum tokens in response

    Returns:
        Tuple of (response_text, search_results if web_search enabled)
    """
    if not OPENROUTER_API_KEY:
        return "⚠️ OPENROUTER_API_KEY not set. Please configure it in the .env file.", None

    # Perform web search if requested
    search_results = None
    search_context = ""
    if use_web_search:
        search_results = search_web(message)
        if search_results and search_results[0].get('title') != 'Web search unavailable':
            search_context = "\n\n📚 Web Search Results:\n"
            for idx, result in enumerate(search_results, 1):
                search_context += f"\n{idx}. {result['title']}\n"
                search_context += f"   {result['snippet']}\n"
                search_context += f"   Source: {result['link']}\n"

            message = f"{message}\n\n{search_context}\n\nPlease provide an answer using the above search results as context."

    # Build conversation messages
    messages = conversation_history or []
    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()

        # Try to parse JSON response
        try:
            data = response.json()
        except ValueError as json_err:
            return f"❌ Invalid API response. Check your OPENROUTER_API_KEY in .env file. Error: {json_err}", search_results

        assistant_message = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not assistant_message:
            # Check if there's an error message from the API
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                return f"⚠️ API Error: {error_msg}", search_results
            return "⚠️ No response from the model. Please try again.", search_results

        return assistant_message, search_results

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "❌ Invalid API key. Please check your OPENROUTER_API_KEY in the .env file.", search_results
        elif e.response.status_code == 402:
            return "❌ Insufficient credits. Please add credits to your OpenRouter account.", search_results
        else:
            return f"❌ HTTP Error {e.response.status_code}: {str(e)}", search_results
    except requests.exceptions.RequestException as e:
        return f"❌ Error connecting to OpenRouter API: {str(e)}", search_results
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}", search_results


def get_available_models() -> Dict[str, str]:
    """
    Get list of available OpenAI models

    Returns:
        Dictionary of model names and their identifiers
    """
    return OPENAI_MODELS


def format_search_results_html(results: List[Dict[str, str]]) -> str:
    """
    Format search results as HTML for display

    Args:
        results: List of search results

    Returns:
        HTML formatted string
    """
    if not results or results[0].get('title') == 'Web search unavailable':
        return ""

    html = '<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px;">'
    html += '<h4 style="margin-top: 0;">🔍 Web Search Results</h4>'

    for idx, result in enumerate(results, 1):
        html += f'<div style="background-color: white; padding: 10px; margin-bottom: 10px; border-radius: 5px;">'
        html += f'<strong>{idx}. {result["title"]}</strong><br>'
        html += f'<small>{result["snippet"]}</small><br>'
        if result.get('link'):
            html += f'<a href="{result["link"]}" target="_blank" style="color: #0066cc; text-decoration: none;">🔗 Visit source</a>'
        html += '</div>'

    html += '</div>'
    return html


# Example usage and testing
if __name__ == "__main__":
    print("Testing Chatbot Module...")
    print("=" * 60)

    # Test 1: Basic chat without web search
    print("\n1. Testing basic chat...")
    response, _ = chat_with_llm("What is Python?", model="openai/gpt-3.5-turbo")
    print(f"Response: {response[:100]}...")

    # Test 2: Chat with web search
    print("\n2. Testing chat with web search...")
    response, results = chat_with_llm(
        "What are the latest AI developments?",
        model="openai/gpt-3.5-turbo",
        use_web_search=True
    )
    print(f"Response: {response[:100]}...")
    if results:
        print(f"Found {len(results)} search results")

    # Test 3: Get available models
    print("\n3. Available models:")
    for name, model_id in get_available_models().items():
        print(f"   - {name}: {model_id}")

    print("\n" + "=" * 60)
    print("✓ Chatbot module ready!")
