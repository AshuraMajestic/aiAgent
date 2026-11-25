import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
CHAT_FOLDER = os.getenv("CHAT_FOLDER", "chats")


def save_chat(path, messages):
    os.makedirs(CHAT_FOLDER, exist_ok=True)

    if path is None:
        file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        path = os.path.join(CHAT_FOLDER, file_name)

    first_user = next((m["content"] for m in messages if m["role"] == "user"), "(untitled)")

    data = {
        "title": first_user[:40],
        "updated": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "messages": messages,
    }

    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)
    return path


def load_chat(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def list_chats():
    if not os.path.exists(CHAT_FOLDER):
        return []

    chats = []
    for name in os.listdir(CHAT_FOLDER):
        if not name.endswith(".json"):
            continue
        path = os.path.join(CHAT_FOLDER, name)
        data = load_chat(path)
        if data is None:
            print(f"Skipped unreadable chat file: {name}")
            continue
        chats.append({
            "path": path,
            "title": data.get("title", "(untitled)"),
            "updated": data.get("updated", ""),
            "count": len(data.get("messages", [])),
        })

    chats.sort(key=lambda c: c["updated"], reverse=True)
    return chats