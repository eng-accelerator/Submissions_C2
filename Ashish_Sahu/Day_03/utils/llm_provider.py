import requests
import json
from typing import List, Dict, Any, Generator

class LLMProvider:
    def __init__(self, provider: str, config: Dict[str, Any], settings: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.settings = settings

    def chat_completion(self, messages: List[Dict[str, str]], model: str, stream: bool = True) -> Generator[str, None, None]:
        if self.provider == 'openrouter':
            return self._openrouter_completion(messages, model, stream)
        elif self.provider == 'ollama':
            return self._ollama_completion(messages, model, stream)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _openrouter_completion(self, messages: List[Dict[str, Any]], model: str, stream: bool = True) -> Generator[str, None, None]:
        url = f"{self.config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": self.settings.get('temperature', 0.7),
            "max_tokens": self.settings.get('max_tokens', 2000),
            "stream": stream
        }

        try:
            response = requests.post(url, headers=headers, json=payload, stream=stream, timeout=60)
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            yield f"\n\n**Error:** {str(e)}"
        except Exception as e:
            yield f"\n\n**Error:** {str(e)}"

    def _ollama_completion(self, messages: List[Dict[str, Any]], model: str, stream: bool = True) -> Generator[str, None, None]:
        url = f"{self.config['endpoint']}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.settings.get('temperature', 0.7),
                "num_predict": self.settings.get('max_tokens', 2000)
            }
        }

        try:
            response = requests.post(url, json=payload, stream=stream, timeout=60)
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'message' in chunk and 'content' in chunk['message']:
                                yield chunk['message']['content']
                            if chunk.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    yield result['message']['content']

        except requests.exceptions.RequestException as e:
            yield f"\n\n**Error:** {str(e)}"
        except Exception as e:
            yield f"\n\n**Error:** {str(e)}"

    def test_connection(self) -> tuple[bool, str]:
        try:
            if self.provider == 'openrouter':
                url = f"{self.config['base_url']}/models"
                headers = {
                    "Authorization": f"Bearer {self.config['api_key']}",
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return True, "Connection successful"
            elif self.provider == 'ollama':
                url = f"{self.config['endpoint']}/api/tags"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return True, "Connection successful"
        except requests.exceptions.RequestException as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

def get_translation_prompt(target_language: str) -> str:
    return f"""You are a professional translator and cultural advisor. Your task is to:

1. **Detect the language** of the user's input text
2. **Translate** it to {target_language}
3. **Provide cultural context** and alternative translations when relevant

Format your response EXACTLY as follows:

🔍 Detected Language: [Language Name]
🎯 Translation ({target_language}): "[translated text]"

💡 Cultural Note: [Provide cultural context, usage notes, or formality level if relevant]
🌟 Alternative: [Provide alternative translations if applicable]
💡 Regional Note: [Mention regional variations if applicable]

Guidelines:
- Always detect the source language first
- Provide accurate, natural translations
- Include cultural context when the translation involves idioms, formal/informal distinctions, or cultural-specific concepts
- Mention alternative translations when multiple valid options exist
- Note regional variations when they're significant
- Keep translations natural and contextually appropriate
- If the input is already in {target_language}, detect it and provide a brief acknowledgment

Example 1:
Input: "Bonjour, comment allez-vous?"
Output:
🔍 Detected Language: French
🎯 Translation ({target_language}): "Hello, how are you?"

💡 Cultural Note: This is a formal greeting in French. In casual settings, you might hear "Salut, ça va?" instead.

Example 2:
Input: "I love this weather"
Output:
🔍 Detected Language: English
🎯 Translation (Spanish): "Me encanta este clima"

🌟 Alternative: "Adoro este tiempo" (more emphatic)
💡 Regional Note: In Mexico, you might also hear "está padrísimo el clima"
"""

def prepare_messages_with_files(messages: List[Dict[str, str]], files: List[Dict[str, Any]], custom_instructions: str, provider: str, translation_mode: bool = False, target_language: str = "English", personality_mode: str = "Professional", custom_personality: str = "") -> List[Dict[str, Any]]:
    from utils.personality_prompts import get_personality_prompt

    prepared_messages = []

    system_prompt = ""

    if translation_mode:
        system_prompt = get_translation_prompt(target_language)
    elif personality_mode and personality_mode != "Professional" or personality_mode == "Professional":
        personality_info = get_personality_prompt(personality_mode, custom_personality)
        system_prompt = personality_info['prompt']
    elif custom_instructions.strip():
        system_prompt = custom_instructions.strip()

    if system_prompt:
        prepared_messages.append({
            "role": "system",
            "content": system_prompt
        })

    has_images = any(f.get('type') == 'image' and not f.get('error') for f in files)

    if has_images and provider == 'openrouter':
        for msg in messages:
            if msg['role'] == 'user':
                content = []
                content.append({"type": "text", "text": msg['content']})

                for file in files:
                    if file.get('type') == 'image' and not file.get('error'):
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file['mime_type']};base64,{file['content']}"
                            }
                        })

                prepared_messages.append({
                    "role": msg['role'],
                    "content": content
                })
            else:
                prepared_messages.append(msg)
    else:
        text_context_parts = []
        for file in files:
            if file.get('format') == 'text' and not file.get('error'):
                text_context_parts.append(f"File: {file['name']}\n{file['content']}")

        if text_context_parts and messages:
            file_context = "\n\n---\n\n".join(text_context_parts)
            first_user_msg = messages[0]
            enhanced_content = f"{file_context}\n\n---\n\nUser message: {first_user_msg['content']}"

            prepared_messages.append({
                "role": "user",
                "content": enhanced_content
            })

            for msg in messages[1:]:
                prepared_messages.append(msg)
        else:
            prepared_messages.extend(messages)

    return prepared_messages
