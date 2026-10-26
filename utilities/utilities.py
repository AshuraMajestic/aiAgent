import os 
from dotenv import load_dotenv

load_dotenv()
START_SEQUENCE="\033[91m"
END_SEQUENCE="\033[0m"

def log(text):
    if os.getenv("DEBUG", "").lower() == "true":
        print(f"  {START_SEQUENCE}{text}{END_SEQUENCE}")


def build_tool_calls_payload(tool_calls):
    payload=[]
    for tool_call in tool_calls:
        tool_call_dict={
            "id":tool_call.id,
            "type":"function",
            "functions":{
                "name":tool_call.function.name,
                "arguments":tool_call.function.arguments
            }
        }
        payload.append(tool_call_dict)
    return payload
