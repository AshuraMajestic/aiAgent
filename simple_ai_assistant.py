from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client =OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
messages=[]
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
        messages=messages
    )
    print("\nAI: "+response.choices[0].message.content)
    messages.append({
            "role":"assistant",
            "content":response.choices[0].message.content
        })