from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS,FUNCTION_NAME_TO_FUNCTION_MAP
import os
import json

load_dotenv()
client =OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
messages=[]
messages.append(
    {
        "role":"system",
        "content":"Act live very Humble agent"
    })
messages.append({
        "role":"system",
        "content":"Give Answer as short as possible"
    }
    )
MAX_STEPS= 5
while True:
    userInput=input("\nYou:")
    if(userInput.lower().strip() in ["exit","bye","quit","goodbye"]):
        break
    messages.append({
        "role":"user",
        "content":userInput
    })

    for steps in range(MAX_STEPS):
        response=client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )

        msg=response.choices[0].message
        if not msg.tool_calls:
            break
        messages.append(msg)
        for tool_call in msg.tool_calls:
            fun_name=tool_call.function.name
            function={}
            try:
                fun_args=json.loads(tool_call.function.arguments or "{}")
                fn=FUNCTION_NAME_TO_FUNCTION_MAP[fun_name]
                result=fn(**fun_args)
            except Exception as e:
                result = f"Error while running {fun_name} : {e}"

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

    print("AI: "+msg.content)
