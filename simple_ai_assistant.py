import os

from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS,FUNCTION_NAME_TO_FUNCTION_MAP,run_tool
from utilities.utilities import log

load_dotenv()
client =OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
messages=[]
messages.append(
    {
        "role":"system",
        "content":"Act like very Flirty agent"
    })

MAX_STEPS= 5
while True:
    userInput=input("\nYou:")
    if(userInput.lower().strip() in ["exit","bye","quit","goodbye"]):
        break
    messages.append({
        "role":"user",
        "content":userInput
    })

    for step in range(MAX_STEPS):
        response=client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )

        msg=response.choices[0].message
        
        if not msg.tool_calls:
            break

        log(f"Step {step+1} : Model Requested {len(msg.tool_calls)} tool calls")

        messages.append(msg)
        for tool_call in msg.tool_calls:
            result=run_tool(tool_call)

            messages.append({
                "role":"tool",
                "tool_id":tool_call.id,
                "content":str(result)
            })
        response=client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
        )

        msg=response.choices[0].message

    else:
        fallback = "Sorry, The Task cannot be finished within the given resource limit"
        messages.append({
            "role":"assistant",
            "content":fallback
        })
        print("AI: "+fallback)
        continue

    messages.append({
        "role":"assistant",
        "content":msg.content
    })

    print("AI: "+(msg.content or ""))
