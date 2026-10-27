# standard library imports
import os

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv




load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

response = client.embeddings.create(
    model=os.getenv("EMBED_MODEL"),
    input="I am a Ashura"
)

print(response, end="",flush=True)