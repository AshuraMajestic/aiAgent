# standard library imports
import json
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
VECTOR_STORE_FILE = Path(__file__).resolve().parent.parent / os.getenv("VECTOR_STORE_FILE")

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


def add_embeddings(chunks):
    for chunk in chunks:
        vector=generate_embedding(chunk["text"])
        chunk["vector"]=vector
    return chunks


def search(query,chunks,top_k=3):
    query_vector=generate_embedding(query)
    
    results=[]
    
    for chunk in chunks:
        score =cosine_similarity(query_vector,chunk["vector"])
        results.append({
            "score":float(score),
            "chunk_id":chunk["id"],
            "source":chunk["source"],
            "text":chunk["text"],
            "size":len(chunk["text"])
        })
    
    results.sort(key=lambda rec:rec["score"],reverse=True)
    
    return results[:top_k]

def chunk_documents(document):
    chunks=[]
    chunk_id=0
    for part in document["text"].split("\n\n"):
        if len(part.strip())==0:
            continue
        chunks.append({
            "id":chunk_id,
            "source":document["source"],
            "text":part.strip()
        })
        chunk_id += 1
    return chunks

    
def create_chunks():
    documents=load_documents()
    chunks=[]
    
    for document in documents:
        chunks.extend(chunk_documents(document))
        
    return chunks

def test(user_query,chunks,top_k=3):
    print(f"\nUser Query: {user_query}")
    
    results=search(user_query,chunks,top_k)
    
    for r in results:
        print(f"{r['score']:.2f} - {r['source']} - {r['size']} characters")
        print(f"{r['text']}\n")

def save_vector_store(chunks):
    with open(VECTOR_STORE_FILE,"w",encoding="utf-8") as f:
        json.dump(chunks,f,indent=4)

def load_vector_store():
    with open(VECTOR_STORE_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

chunks=[]
if os.path.exists(VECTOR_STORE_FILE):
    chunks=load_vector_store()
    print(f"Loaded {len(chunks)} chunks from {VECTOR_STORE_FILE}")
else:
    chunks=create_chunks()
    chunks=add_embeddings(chunks)
    save_vector_store(chunks)
    print(f"Created and saved {len(chunks)} chunks to {VECTOR_STORE_FILE}")
    


print(f"We have embedded {len(chunks)} chunks")

user_query="What are the benefits of the maternity leave?"

test(user_query,chunks,3)