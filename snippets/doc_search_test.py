# standard library imports
import os
from pathlib import Path

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv
import numpy


load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
EMBEDING_MODEL=os.getenv("EMBED_MODEL")
KNOWLEDGE_BASE_FOLDER = Path(__file__).resolve().parent.parent / os.getenv("KB_FOLDER")


def generate_embedding(text):
    response = client.embeddings.create(
        model=EMBEDING_MODEL,
        input=text
    )

    return response.data[0].embedding

def cosine_similarity(A,B):
    dot_product=numpy.dot(A,B)
    normal_A=numpy.linalg.norm(A)
    normal_B=numpy.linalg.norm(B)
    return dot_product/(normal_A*normal_B)


def load_documents(folder=KNOWLEDGE_BASE_FOLDER):
    documents=[]
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        
        path =os.path.join(folder,filename)
        with open(path,"r",encoding="utf-8") as f:
            documents.append({
                "source":filename,
                "text":f.read()
            })
    return documents

def add_embeddings(documents):
    for document in documents:
        vector=generate_embedding(document["text"])
        document["vector"]=vector
    return documents


def search(query,documents,top_k=3):
    query_vector=generate_embedding(query)
    
    results=[]
    
    for document in documents:
        score =cosine_similarity(query_vector,document["vector"])
        results.append({
            "score":score,
            "source":document["source"],
            "text":document["text"],
            "size":len(document["text"])
        })
    
    results.sort(key=lambda rec:rec["score"],reverse=True)
    
    return results[:top_k]


def test(user_query,documents,top_k=3):
    print(f"\nUser Query: {user_query}")
    
    results=search(user_query,documents,top_k)
    
    for r in results:
        print(f"{r['score']:.2f} - {r['source']} - {r['size']} characters")
        

documents=load_documents()
documents=add_embeddings(documents)

print(f"We have embedded {len(documents)} documents")

user_query="How many days will i get for maternity leave?"

test(user_query,documents,3)