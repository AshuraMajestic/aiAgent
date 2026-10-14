from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client =OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
while True:
    userInput=input("\nYou:")
    if(userInput.lower().strip() in ["exit","bye","quit","goodbye"]):
        break
    response=client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role":"user",
                "content":userInput
            }
        ]
    )
    print("AI: "+response.choices[0].message.content)