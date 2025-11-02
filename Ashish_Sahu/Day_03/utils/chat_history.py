import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

CHATS_DIR = "chats"

def ensure_chats_directory():
    if not os.path.exists(CHATS_DIR):
        os.makedirs(CHATS_DIR)

def generate_chat_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_chat_title(first_message: str, max_length: int = 50) -> str:
    title = first_message.strip()
    if len(title) > max_length:
        title = title[:max_length] + "..."
    return title or "New Chat"

def save_chat(messages: List[Dict[str, str]], chat_id: Optional[str] = None, title: Optional[str] = None) -> str:
    ensure_chats_directory()

    if not chat_id:
        chat_id = generate_chat_id()

    if not title and messages:
        first_user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), "New Chat")
        title = generate_chat_title(first_user_message)

    chat_data = {
        "id": chat_id,
        "title": title or "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": messages
    }

    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")

    try:
        with open(file_path, 'w') as f:
            json.dump(chat_data, f, indent=2)
        return chat_id
    except Exception as e:
        print(f"Error saving chat: {e}")
        return None

def load_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading chat: {e}")
        return None

def list_chats() -> List[Dict[str, Any]]:
    ensure_chats_directory()

    chats = []

    for filename in os.listdir(CHATS_DIR):
        if filename.endswith('.json'):
            chat_id = filename[:-5]
            chat_data = load_chat(chat_id)
            if chat_data:
                chats.append({
                    "id": chat_data.get("id", chat_id),
                    "title": chat_data.get("title", "Untitled"),
                    "created_at": chat_data.get("created_at", ""),
                    "message_count": len(chat_data.get("messages", []))
                })

    chats.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return chats

def delete_chat(chat_id: str) -> bool:
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting chat: {e}")
            return False
    return False

def get_chat_summary(chat_id: str) -> Optional[str]:
    chat_data = load_chat(chat_id)
    if not chat_data:
        return None

    messages = chat_data.get("messages", [])
    message_count = len(messages)

    return f"{chat_data.get('title', 'Untitled')} ({message_count} messages)"
