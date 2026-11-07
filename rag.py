# standard library imports
import json
import os
from pathlib import Path

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv
import numpy
from utilities.utilities import log

load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
EMBEDING_MODEL=os.getenv("EMBED_MODEL")
KNOWLEDGE_BASE_FOLDER = os.getenv("KB_FOLDER")
VECTOR_STORE_FILE = os.getenv("VECTOR_STORE_FILE")

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

def save_vector_store(chunks):
    with open(VECTOR_STORE_FILE,"w",encoding="utf-8") as f:
        json.dump(chunks,f,indent=4)

def load_vector_store():
    with open(VECTOR_STORE_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def load_chunks():
    if os.path.exists(VECTOR_STORE_FILE):
        log("Loading chunks from vector store...")
        chunks=load_vector_store()
    else:
        log("Creating chunks from documents...")
        chunks=create_chunks()
        chunks=add_embeddings(chunks)
        save_vector_store(chunks)
    return chunks

chunks=load_chunks()

def search(query,top_k=3):
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
