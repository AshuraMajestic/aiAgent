import json
import os 
from dotenv import load_dotenv

load_dotenv()
START_SEQUENCE="\033[91m"
END_SEQUENCE="\033[0m"

def log(text):
    if os.getenv("DEBUG", "").lower() == "true":
        print(f"  {START_SEQUENCE}{text}{END_SEQUENCE}")


def build_tool_calls_payload(tool_calls):
    payload = []
    for tc in tool_calls:
        args = tc.function.arguments
        if isinstance(args, dict):          # dict -> JSON string
            args = json.dumps(args)
        args = (args or "").strip() or "{}"  # empty -> "{}"
        json.loads(args)                     # raises early if invalid

        payload.append({
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": args,
            },
        })
    return payload
