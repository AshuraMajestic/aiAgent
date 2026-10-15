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
while True:
    userInput=input("\nYou:")
    if(userInput.lower().strip() in ["exit","bye","quit","goodbye"]):
        break
    messages.append({
        "role":"user",
        "content":userInput
    })

    response=client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS
    )

    msg=response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)
        for tool_call in msg.tool_calls:
            fun_name=tool_call.function.name
            fun_args=json.loads(tool_call.function.arguments or "{}")

            fn=FUNCTION_NAME_TO_FUNCTION_MAP[fun_name]
            result=fn(**fun_args)
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
    messages.append({
        "role":"assistant",
        "content":msg.content
    })

    print("AI: "+msg.content)
