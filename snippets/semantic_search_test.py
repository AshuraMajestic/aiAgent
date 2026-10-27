# standard library imports
import os

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv
import numpy




load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def generate_embedding(text):
    response = client.embeddings.create(
        model=os.getenv("EMBED_MODEL"),
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(A,B):
    dot_product=numpy.dot(A,B)
    normal_A=numpy.linalg.norm(A)
    normal_B=numpy.linalg.norm(B)
    return dot_product/(normal_A*normal_B)

text1="I am a Good Boy"
text2="People tell about me that he is a Good Boy"
text3="I love eating apples"


embedding1=generate_embedding(text1)
embedding2=generate_embedding(text2)
embedding3=generate_embedding(text3)

cosineAB=cosine_similarity(embedding1,embedding2)
cosineAC=cosine_similarity(embedding1,embedding3)
cosineBC=cosine_similarity(embedding2,embedding3)

print("text 1 and text 2: ",cosineAB)
print("text 1 and text 3: ",cosineAC)
print("text 2 and text 3: ",cosineBC)

