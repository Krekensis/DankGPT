import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pinecone import Pinecone
from groq import Groq

app = FastAPI(title="DankGPT Serverless API")

# Setup Environment Variables (Vercel will inject these)
PINECONE_KEY = os.environ.get("PINECONE_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
GROQ_KEY = os.environ.get("GROQ_KEY")

# Initialize Pinecone and Groq
pc = None
index = None
if PINECONE_KEY:
    pc = Pinecone(api_key=PINECONE_KEY)
    index = pc.Index("dankgpt")

if GROQ_KEY:
    groq_client = Groq(api_key=GROQ_KEY)

# Hugging Face Inference API details
HF_API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"

class ChatRequest(BaseModel):
    question: str

def get_hf_embedding(text: str):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": text}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Hugging Face API Error: {response.text}")
    return response.json()

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not (PINECONE_KEY and HF_TOKEN and GROQ_KEY):
        raise HTTPException(status_code=500, detail="Missing API Keys on Vercel Server.")
    
    user_question = req.question

    try:
        # 1. Get Embedding from Hugging Face
        embedding_data = get_hf_embedding(user_question)
        # HF Inference API returns [[float, ...]] for a single string input
        query_vector = embedding_data[0] if isinstance(embedding_data[0], list) else embedding_data
        
        # 2. Search Pinecone Official Namespace
        off_res = index.query(
            namespace="official",
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )
        
        # 3. Search Pinecone Community Namespace
        com_res = index.query(
            namespace="community",
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )
        
        # Format Context
        official_context = ""
        for match in off_res.get('matches', []):
            official_context += match['metadata'].get('raw_data', '') + "\n\n"
            
        community_context = ""
        for match in com_res.get('matches', []):
            community_context += match['metadata'].get('raw_data', '') + "\n\n"

        # 4. Generate LLM Response with Groq
        prompt = f"""You are DankGPT, an expert AI assistant for the Dank Memer Discord Bot.
Your goal is to answer the user's question accurately, concisely, and with a friendly tone.

You will be provided with two sources of context to answer the question:
1. [OFFICIAL FACTS]: This is data extracted directly from the game's API and official guides. This information is 100% accurate. You MUST prioritize this information above all else.
2. [COMMUNITY RUMORS]: These are messages extracted from the community Discord server. This information might be outdated, subjective, or factually incorrect. ONLY use this information if the Official Facts do not fully answer the question. If you use Community Rumors, you MUST warn the user that the information is based on community speculation.

CRITICAL INSTRUCTIONS:
- NEVER hallucinate or make up information. If the answer cannot be deduced from the provided context, explicitly state "I don't have enough information to answer that."
- FORMATTING: Use Discord-flavored Markdown (bolding, italics, bullet points) to make your response easy to read.
- Be concise and directly address the user's question.
- PROVIDE EXACT DETAILS: Never give vague or obvious answers. You MUST extract and provide specific quantities, exact amounts, drop rates, and exact command syntaxes if they are present in the Context. Be highly analytical.

[OFFICIAL FACTS]
{official_context}

[COMMUNITY RUMORS]
{community_context}

[USER QUESTION]
{user_question}
"""
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return {"response": completion.choices[0].message.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
