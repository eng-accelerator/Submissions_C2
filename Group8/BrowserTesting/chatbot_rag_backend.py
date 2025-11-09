"""
RAG Chatbot Backend with LangGraph
Supports multimodal input (text, images, documents) and web search
"""

import os
import json
import base64
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from pathlib import Path
from dotenv import load_dotenv
import requests

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Model configurations
CHAT_MODEL = "anthropic/claude-3.5-sonnet"
VISION_MODEL = "anthropic/claude-3.5-sonnet"  # Claude 3.5 Sonnet supports vision


class ChatbotState(TypedDict):
    """State for the chatbot graph"""
    messages: Annotated[List[Dict[str, Any]], add_messages]
    context: str
    web_search_results: List[Dict[str, str]]
    uploaded_files: List[Dict[str, Any]]
    agent_features: Optional[Dict[str, Any]]
    current_query: str
    response: str


class RAGChatbot:
    """RAG-based chatbot with multimodal support and web search"""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.chat_model = CHAT_MODEL
        self.vision_model = VISION_MODEL
        self.google_api_key = GOOGLE_API_KEY
        self.google_cse_id = GOOGLE_CSE_ID
        self.agent_features = self._load_agent_features()
        self.graph = self._create_graph()

    def _load_agent_features(self) -> Dict[str, Any]:
        """Load and analyze agent features from the agents folder"""
        agents_dir = Path(__file__).parent / "agents"
        features = {
            "available_agents": [],
            "capabilities": {},
            "usage_guide": {}
        }

        if not agents_dir.exists():
            return features

        agent_descriptions = {
            "flow_discovery": {
                "name": "Flow Discovery Agent",
                "purpose": "Discovers and maps user journey steps from natural language goals",
                "usage": "Analyzes your testing goal and creates a step-by-step flow",
                "example": "Used when you describe 'Test login flow' - it breaks it down into concrete steps"
            },
            "script_generator": {
                "name": "Script Generator Agent",
                "purpose": "Converts flow steps into executable Playwright test scripts",
                "usage": "Generates Python code with proper selectors and assertions",
                "example": "Takes flow steps and creates runnable test code"
            },
            "execution": {
                "name": "Execution Agent",
                "purpose": "Runs generated test scripts and captures results",
                "usage": "Executes scripts in browser, captures logs and screenshots",
                "example": "Runs your test and shows you what happened"
            },
            "error_diagnosis": {
                "name": "Error Diagnosis Agent",
                "purpose": "Analyzes test failures and identifies root causes",
                "usage": "When tests fail, it explains why in human-readable terms",
                "example": "Tells you 'Login button not found' instead of cryptic error"
            },
            "adaptive_repair": {
                "name": "Adaptive Repair Agent",
                "purpose": "Self-healing - automatically fixes broken tests",
                "usage": "Suggests and applies fixes when tests break due to UI changes",
                "example": "Updates selectors when buttons change from #btn to .button-class"
            },
            "regression_monitor": {
                "name": "Visual Regression Monitor",
                "purpose": "Tracks visual changes and detects UI regressions",
                "usage": "Compares screenshots to baseline, detects unwanted changes",
                "example": "Alerts when product page layout changes unexpectedly"
            }
        }

        for agent_file in agents_dir.glob("*.py"):
            if agent_file.name.startswith("_"):
                continue

            agent_name = agent_file.stem
            if agent_name in agent_descriptions:
                features["available_agents"].append(agent_name)
                features["capabilities"][agent_name] = agent_descriptions[agent_name]

        features["usage_guide"]["workflow"] = [
            "1. Describe your testing goal in plain English",
            "2. Flow Discovery creates step-by-step plan",
            "3. Script Generator writes Playwright code",
            "4. Execution Agent runs the test",
            "5. If failed: Error Diagnosis + Adaptive Repair fix it",
            "6. Visual Regression checks for UI changes"
        ]

        return features

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = Path(filename).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        elif ext in ['.pdf']:
            return 'pdf'
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
            return 'text'
        else:
            return 'unknown'

    def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web using Google Custom Search API"""
        if not self.google_api_key or not self.google_cse_id:
            return [{
                'title': 'Web search not configured',
                'snippet': 'Please configure GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file',
                'link': ''
            }]

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': min(num_results, 10)
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

            return results if results else [{'title': 'No results', 'snippet': 'Try different keywords', 'link': ''}]

        except Exception as e:
            return [{'title': 'Search error', 'snippet': str(e), 'link': ''}]

    def _call_llm(self, messages: List[Dict[str, Any]], model: str = None) -> str:
        """Call OpenRouter LLM API"""
        if not self.api_key:
            return "Error: OPENROUTER_API_KEY not configured. Please add it to your .env file."

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or self.chat_model,
                    "messages": messages,
                    "max_tokens": 4000,
                },
                timeout=60,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from model")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key. Please check your OPENROUTER_API_KEY."
            elif e.response.status_code == 402:
                return "Error: Insufficient credits. Please add credits to your OpenRouter account."
            else:
                return f"HTTP Error {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def _analyze_query(self, state: ChatbotState) -> ChatbotState:
        """Analyze user query and determine actions needed"""
        query = state["current_query"]

        # Check if query is about agent features
        agent_keywords = ["agent", "feature", "capability", "what can", "how does", "flow discovery",
                         "script generator", "execution", "diagnosis", "repair", "visual", "regression"]
        is_agent_query = any(keyword in query.lower() for keyword in agent_keywords)

        # Check if query needs web search
        search_keywords = ["latest", "current", "recent", "news", "today", "2024", "2025", "search for"]
        needs_search = any(keyword in query.lower() for keyword in search_keywords)

        state["agent_features"] = self.agent_features if is_agent_query else None

        return state

    def _perform_web_search(self, state: ChatbotState) -> ChatbotState:
        """Perform web search if needed"""
        query = state["current_query"]

        # Simple heuristic: search if query seems to need current information
        search_keywords = ["latest", "current", "recent", "news", "today", "search"]
        if any(keyword in query.lower() for keyword in search_keywords):
            results = self.web_search(query, num_results=5)
            state["web_search_results"] = results

        return state

    def _process_documents(self, state: ChatbotState) -> ChatbotState:
        """Process uploaded documents and images"""
        if not state.get("uploaded_files"):
            return state

        context_parts = []

        for file_info in state["uploaded_files"]:
            file_type = file_info.get("type")
            file_path = file_info.get("path")
            file_name = file_info.get("name")

            if file_type == "text":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context_parts.append(f"File: {file_name}\n```\n{content}\n```\n")
                except Exception as e:
                    context_parts.append(f"File: {file_name} (error reading: {e})\n")

            elif file_type == "image":
                context_parts.append(f"Image: {file_name} (will be processed by vision model)\n")

        state["context"] = "\n".join(context_parts)
        return state

    def _generate_response(self, state: ChatbotState) -> ChatbotState:
        """Generate final response using LLM"""
        messages = []

        # System message with context
        system_parts = [
            "You are an intelligent assistant for the AI Browser Automation Lab.",
            "You help users understand and use the browser testing automation features."
        ]

        # Add agent features context if relevant
        if state.get("agent_features"):
            features_text = json.dumps(state["agent_features"], indent=2)
            system_parts.append(f"\n\nAvailable Agent Features:\n{features_text}")
            system_parts.append("\nWhen users ask about features, explain them clearly with examples.")

        # Add document context
        if state.get("context"):
            system_parts.append(f"\n\nUploaded Documents:\n{state['context']}")

        # Add web search results
        if state.get("web_search_results"):
            search_text = "\n\nWeb Search Results:\n"
            for i, result in enumerate(state["web_search_results"][:5], 1):
                search_text += f"{i}. {result['title']}\n   {result['snippet']}\n   {result['link']}\n\n"
            system_parts.append(search_text)

        system_message = "".join(system_parts)

        # Build messages for API
        messages.append({"role": "system", "content": system_message})

        # Add conversation history
        for msg in state.get("messages", []):
            if isinstance(msg, dict):
                messages.append(msg)

        # Add current query
        messages.append({"role": "user", "content": state["current_query"]})

        # Check if we have images to process
        has_images = any(f.get("type") == "image" for f in state.get("uploaded_files", []))
        model = self.vision_model if has_images else self.chat_model

        # If we have images, format messages for vision model
        if has_images:
            content_parts = [{"type": "text", "text": state["current_query"]}]

            for file_info in state.get("uploaded_files", []):
                if file_info.get("type") == "image":
                    try:
                        image_data = self._encode_image(file_info["path"])
                        image_ext = Path(file_info["path"]).suffix.lower()
                        media_type = "image/jpeg" if image_ext in ['.jpg', '.jpeg'] else "image/png"

                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        })
                    except Exception as e:
                        content_parts.append({"type": "text", "text": f"Error loading image {file_info['name']}: {e}"})

            # Replace last message with multimodal content
            messages[-1] = {"role": "user", "content": content_parts}

        # Call LLM
        response = self._call_llm(messages, model=model)
        state["response"] = response

        # Add to conversation history
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "user", "content": state["current_query"]})
        state["messages"].append({"role": "assistant", "content": response})

        return state

    def _create_graph(self) -> StateGraph:
        """Create LangGraph workflow"""
        workflow = StateGraph(ChatbotState)

        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("web_search", self._perform_web_search)
        workflow.add_node("process_documents", self._process_documents)
        workflow.add_node("generate_response", self._generate_response)

        # Define edges
        workflow.add_edge("analyze_query", "web_search")
        workflow.add_edge("web_search", "process_documents")
        workflow.add_edge("process_documents", "generate_response")
        workflow.add_edge("generate_response", END)

        # Set entry point
        workflow.set_entry_point("analyze_query")

        return workflow.compile()

    def chat(
        self,
        query: str,
        uploaded_files: List[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main chat function

        Args:
            query: User's question/query
            uploaded_files: List of uploaded file info [{"name": str, "path": str, "type": str}]
            conversation_history: Previous conversation messages

        Returns:
            Dict with response and metadata
        """
        initial_state = {
            "messages": conversation_history or [],
            "context": "",
            "web_search_results": [],
            "uploaded_files": uploaded_files or [],
            "agent_features": None,
            "current_query": query,
            "response": ""
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        return {
            "response": final_state["response"],
            "web_search_results": final_state.get("web_search_results", []),
            "agent_features_used": final_state.get("agent_features") is not None,
            "messages": final_state.get("messages", [])
        }


def get_agent_features_summary() -> str:
    """Get a summary of available agent features"""
    chatbot = RAGChatbot()
    features = chatbot.agent_features

    summary = "## Available Features:\n\n"
    for agent_name in features["available_agents"]:
        info = features["capabilities"].get(agent_name, {})
        summary += f"**{info.get('name', agent_name)}**\n"
        summary += f"- {info.get('purpose', 'N/A')}\n"
        summary += f"- Example: {info.get('example', 'N/A')}\n\n"

    return summary


if __name__ == "__main__":
    # Test the chatbot
    chatbot = RAGChatbot()

    # Test 1: Simple query
    print("Test 1: Simple query")
    result = chatbot.chat("What is this application for?")
    print(result["response"])
    print("\n" + "="*80 + "\n")

    # Test 2: Agent features query
    print("Test 2: Agent features query")
    result = chatbot.chat("What agents are available and what do they do?")
    print(result["response"])
    print("\n" + "="*80 + "\n")

    # Test 3: Web search query (if configured)
    print("Test 3: Web search query")
    result = chatbot.chat("What is the latest news about Playwright testing?")
    print(result["response"])
    if result["web_search_results"]:
        print("\nSources:")
        for r in result["web_search_results"][:3]:
            print(f"- {r['title']}: {r['link']}")
