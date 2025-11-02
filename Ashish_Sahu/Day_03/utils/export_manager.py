import json
import csv
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any

def calculate_statistics(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calculate conversation statistics"""
    if not messages:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "total_characters": 0,
            "average_message_length": 0,
            "total_words": 0,
            "average_words_per_message": 0
        }

    user_messages = [m for m in messages if m.get('role') == 'user']
    assistant_messages = [m for m in messages if m.get('role') == 'assistant']

    total_chars = sum(len(m.get('content', '')) for m in messages)
    total_words = sum(len(m.get('content', '').split()) for m in messages)

    return {
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "total_characters": total_chars,
        "average_message_length": round(total_chars / len(messages)) if messages else 0,
        "total_words": total_words,
        "average_words_per_message": round(total_words / len(messages)) if messages else 0
    }

def export_to_txt(messages: List[Dict[str, str]], chat_title: str = "New Chat",
                  personality_mode: str = None, translation_mode: bool = False,
                  target_language: str = None) -> str:
    """Export conversation to TXT format"""
    export_time = datetime.now()
    stats = calculate_statistics(messages)

    output = []
    output.append(f"Chat Export - {chat_title}")
    output.append("=" * 60)
    output.append("")

    output.append("Session Information:")
    output.append(f"- Total Messages: {stats['total_messages']}")
    output.append(f"- User Messages: {stats['user_messages']}")
    output.append(f"- Assistant Messages: {stats['assistant_messages']}")
    output.append(f"- Total Characters: {stats['total_characters']}")
    output.append(f"- Total Words: {stats['total_words']}")

    if personality_mode:
        output.append(f"- AI Personality: {personality_mode}")

    if translation_mode and target_language:
        output.append(f"- Translation Mode: Enabled ({target_language})")

    output.append(f"- Export Date: {export_time.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")

    output.append("Conversation:")
    output.append("-" * 60)
    output.append("")

    for idx, message in enumerate(messages, 1):
        role = message.get('role', 'unknown')
        content = message.get('content', '')

        role_display = "You" if role == "user" else "Assistant"
        output.append(f"[Message {idx}] {role_display}:")
        output.append(content)
        output.append("")
        output.append("-" * 60)
        output.append("")

    output.append("")
    output.append("End of Conversation")
    output.append("=" * 60)

    return "\n".join(output)

def export_to_json(messages: List[Dict[str, str]], chat_title: str = "New Chat",
                   personality_mode: str = None, translation_mode: bool = False,
                   target_language: str = None) -> str:
    """Export conversation to JSON format"""
    export_time = datetime.now()
    stats = calculate_statistics(messages)

    export_data = {
        "export_metadata": {
            "export_timestamp": export_time.isoformat(),
            "format_version": "1.0",
            "chat_title": chat_title,
            "total_messages": stats['total_messages'],
            "personality_mode": personality_mode,
            "translation_mode": translation_mode,
            "target_language": target_language if translation_mode else None
        },
        "conversation": [],
        "statistics": stats
    }

    for idx, message in enumerate(messages, 1):
        content = message.get('content', '')
        message_data = {
            "message_id": idx,
            "role": message.get('role', 'unknown'),
            "content": content,
            "character_count": len(content),
            "word_count": len(content.split())
        }
        export_data["conversation"].append(message_data)

    return json.dumps(export_data, indent=2, ensure_ascii=False)

def export_to_csv(messages: List[Dict[str, str]], chat_title: str = "New Chat") -> str:
    """Export conversation to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Message_ID', 'Role', 'Content', 'Character_Count', 'Word_Count'])

    for idx, message in enumerate(messages, 1):
        role = message.get('role', 'unknown')
        content = message.get('content', '')
        char_count = len(content)
        word_count = len(content.split())

        content_escaped = content.replace('"', '""')

        writer.writerow([idx, role, content_escaped, char_count, word_count])

    return output.getvalue()

def generate_filename(chat_title: str, format_ext: str) -> str:
    """Generate a filename for the export"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    safe_title = "".join(c for c in chat_title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:50]

    if not safe_title:
        safe_title = "chat_export"

    return f"{safe_title}_{timestamp}.{format_ext}"
