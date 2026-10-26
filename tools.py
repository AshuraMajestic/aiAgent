import json
import requests
from datetime import datetime

from utilities.utilities import log


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response = requests.get(url,timeout=10)
    response.raise_for_status()
    return response.text

def get_current_city():
    return "Vijayawada"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_city",
            "description": "Returns the user's home city or current city when asked.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Returns the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city whose weather is requested."
                    }
                },
                "required": ["city"],
            }
        }
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP={
    "get_current_time":get_current_time,
    "get_current_city":get_current_city,
    "get_city_weather":get_city_weather
}

def run_tool(tool_call):
    fun_name=tool_call.function.name
    function={}
    try:
        fun_args=json.loads(tool_call.function.arguments or "{}")
        log(f"{fun_name} ({fun_args})")
    
        fn=FUNCTION_NAME_TO_FUNCTION_MAP[fun_name]
        result=fn(**fun_args)
    except Exception as e:
        result = f"Error while running {fun_name} : {e}"
    
    log(f"  ->{result}")