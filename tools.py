import json
import requests
from datetime import datetime

from utilities.utilities import log
from rag import search

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response = requests.get(url,timeout=10)
    response.raise_for_status()
    return response.text

def get_current_city():
    return "Vijayawada"

def search_knowledgebase(query):
    results=search(query)
    log(f"search_knowledgebase({query})")
    for  r in results:
        log(f"  ->{r['source']}: {r['text']} #{r['chunk_id']}")
    blocks=[]
    for r in results:
        sourceFileName=r['source']
        chunkId=r['chunk_id']
        chunkText=r['text']
        header=f"[{sourceFileName} #{chunkId}]"
        block=f"{header}\n{chunkText}"
        blocks.append(block)
        
    return "\n".join(blocks)

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
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledgebase",
            "description": "Searches the NIMBUS DYNAMICS PVT. LTD. company knowledge base: leave, medical, HR, rc, tech, travel expense, and other company policies. Returns the most relevant passages to the query with their source. Use it for any question related to company policies, procedures, and guidelines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question, rewritten as short, self-contained search query."
                    }
                },
                "required": ["query"],
            }
        }
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP={
    "get_current_time":get_current_time,
    "get_current_city":get_current_city,
    "get_city_weather":get_city_weather,
    "search_knowledgebase":search_knowledgebase
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
    return result