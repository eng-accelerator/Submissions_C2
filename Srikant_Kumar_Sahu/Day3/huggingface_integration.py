"""
OpenRoute API Integration Module
Provides integration with OpenRoute API for the Streamlit chat app with local JSON chat history
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

class OpenRouteChat:
    """OpenRoute API integration with local JSON chat history"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTE_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model_name = "meta-llama/llama-3.1-8b-instruct:free"
        self.chat_history_file = "chat_history.json"
        self.conversation_history = []
        self.load_chat_history()
        
    def set_api_key(self, api_key):
        """Set the OpenRoute API key"""
        self.api_key = api_key
        return True
    
    def set_model(self, model_name):
        """Set the model to use"""
        self.model_name = model_name
        return True
    
    def load_chat_history(self):
        """Load chat history from JSON file"""
        try:
            if os.path.exists(self.chat_history_file):
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversations', [])
            else:
                self.conversation_history = []
        except Exception as e:
            st.warning(f"Could not load chat history: {str(e)}")
            self.conversation_history = []
    
    def save_chat_history(self):
        """Save chat history to JSON file"""
        try:
            data = {
                'conversations': self.conversation_history,
                'last_updated': datetime.now().isoformat(),
                'total_messages': len(self.conversation_history)
            }
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.warning(f"Could not save chat history: {str(e)}")
    
    def get_available_models(self):
        """Get list of available OpenRoute models"""
        return {
            "meta-llama/llama-3.1-8b-instruct:free": {
                "name": "Llama 3.1 8B (Free)",
                "description": "Meta's Llama 3.1 8B model - free tier",
                "size": "8B",
                "type": "conversational"
            },
            "meta-llama/llama-3.1-70b-instruct:nitro": {
                "name": "Llama 3.1 70B (Nitro)",
                "description": "Meta's Llama 3.1 70B model - nitro tier",
                "size": "70B",
                "type": "conversational"
            },
            "google/gemini-pro-1.5": {
                "name": "Gemini Pro 1.5",
                "description": "Google's Gemini Pro 1.5 model",
                "size": "Large",
                "type": "conversational"
            },
            "openai/gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "description": "OpenAI's GPT-3.5 Turbo model",
                "size": "Medium",
                "type": "conversational"
            }
        }
    
    def generate_response(self, user_input, max_length=150, temperature=0.7, top_p=0.9):
        """Generate response using OpenRoute API"""
        try:
            if not self.api_key:
                return "No API key provided. Please set your OpenRoute API key."
            
            # Prepare messages for API
            messages = []
            
            # Add conversation history (last 6 messages for context)
            recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_length,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result['choices'][0]['message']['content'].strip()
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": assistant_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Save to file
                self.save_chat_history()
                
                return assistant_response
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                st.error(error_msg)
                return f"Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        self.save_chat_history()
    
    def get_model_info(self):
        """Get information about the current setup"""
        info = {
            "api_provider": "OpenRoute",
            "model_name": self.model_name,
            "conversation_length": len(self.conversation_history),
            "has_api_key": bool(self.api_key),
            "chat_history_file": self.chat_history_file
        }
        return info
    
    def export_chat_history(self, filename=None):
        """Export chat history to a specific file"""
        if not filename:
            filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = {
                'conversations': self.conversation_history,
                'exported_at': datetime.now().isoformat(),
                'total_messages': len(self.conversation_history),
                'model_used': self.model_name
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            st.error(f"Could not export chat history: {str(e)}")
            return None

# Available OpenRoute models
AVAILABLE_MODELS = {
    "conversational": {
        "meta-llama/llama-3.1-8b-instruct:free": {
            "name": "Llama 3.1 8B (Free)",
            "description": "Meta's Llama 3.1 8B model - free tier",
            "size": "8B",
            "type": "conversational"
        },
        "meta-llama/llama-3.1-70b-instruct:nitro": {
            "name": "Llama 3.1 70B (Nitro)",
            "description": "Meta's Llama 3.1 70B model - nitro tier",
            "size": "70B",
            "type": "conversational"
        },
        "google/gemini-pro-1.5": {
            "name": "Gemini Pro 1.5",
            "description": "Google's Gemini Pro 1.5 model",
            "size": "Large",
            "type": "conversational"
        },
        "openai/gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "description": "OpenAI's GPT-3.5 Turbo model",
            "size": "Medium",
            "type": "conversational"
        }
    }
}

def get_model_list():
    """Get a flattened list of all available models"""
    all_models = {}
    for category, models in AVAILABLE_MODELS.items():
        all_models.update(models)
    return all_models

def get_model_by_category(category):
    """Get models by category"""
    return AVAILABLE_MODELS.get(category, {})

def initialize_openroute_chat(api_key=None):
    """Initialize OpenRoute chat instance in session state"""
    if "openroute_chat" not in st.session_state:
        st.session_state.openroute_chat = OpenRouteChat(api_key)
    
    return st.session_state.openroute_chat

def set_openroute_api_key(api_key):
    """Set OpenRoute API key"""
    openroute_chat = initialize_openroute_chat()
    return openroute_chat.set_api_key(api_key)

def set_openroute_model(model_name):
    """Set OpenRoute model"""
    openroute_chat = initialize_openroute_chat()
    return openroute_chat.set_model(model_name)

def generate_openroute_response(user_input, max_length=150, temperature=0.7, top_p=0.9):
    """Generate response using OpenRoute API"""
    openroute_chat = initialize_openroute_chat()
    return openroute_chat.generate_response(user_input, max_length, temperature, top_p)

def reset_openroute_conversation():
    """Reset OpenRoute conversation"""
    openroute_chat = initialize_openroute_chat()
    openroute_chat.reset_conversation()

def get_openroute_model_info():
    """Get OpenRoute model information"""
    openroute_chat = initialize_openroute_chat()
    return openroute_chat.get_model_info()

def export_chat_history(filename=None):
    """Export chat history to file"""
    openroute_chat = initialize_openroute_chat()
    return openroute_chat.export_chat_history(filename)

# Backward compatibility aliases
def initialize_hf_chat(api_key=None):
    """Backward compatibility - initialize OpenRoute chat"""
    return initialize_openroute_chat(api_key)

def generate_hf_response(user_input, max_length=150, temperature=0.7, top_p=0.9):
    """Backward compatibility - generate OpenRoute response"""
    return generate_openroute_response(user_input, max_length, temperature, top_p)

def reset_hf_conversation():
    """Backward compatibility - reset OpenRoute conversation"""
    return reset_openroute_conversation()

def get_hf_model_info():
    """Backward compatibility - get OpenRoute model info"""
    return get_openroute_model_info()
