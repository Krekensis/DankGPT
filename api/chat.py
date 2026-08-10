import os
from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pinecone import Pinecone
from groq import Groq

app = FastAPI(title="DankGPT Serverless API")

PINECONE_KEY = os.environ.get("PINECONE_KEY", "").strip() or None
HF_TOKEN     = os.environ.get("HF_TOKEN", "").strip() or None
GROQ_KEY     = os.environ.get("GROQ_KEY", "").strip() or None

pc    = Pinecone(api_key=PINECONE_KEY) if PINECONE_KEY else None
index = pc.Index("dankgpt")            if pc           else None
groq_client = Groq(api_key=GROQ_KEY)  if GROQ_KEY     else None

HF_API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"

class ChatRequest(BaseModel):
    question: str

def get_hf_embedding(text: str, retries: int = 3) -> list:
    """Call HF Inference API. Returns a clear error if the model is still loading."""
    client = InferenceClient(api_key=HF_TOKEN)
    
    for attempt in range(retries):
        try:
            vector = client.feature_extraction(text=text, model="BAAI/bge-large-en-v1.5")
            # Usually returns a numpy array or list
            return vector.tolist() if hasattr(vector, 'tolist') else vector
        except Exception as e:
            if attempt == retries - 1:
                raise Exception(f"Error connecting to HuggingFace after {retries} attempts: {e}")
            import time
            time.sleep(1) # wait a second before retrying

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not (PINECONE_KEY and HF_TOKEN and GROQ_KEY):
        raise HTTPException(status_code=500, detail="Missing API Keys. Check Vercel Environment Variables.")

    try:
        # 1. Embed the question
        query_vector = get_hf_embedding(req.question)

        # 2. Search Pinecone — both namespaces
        # Pinecone SDK v3 returns QueryResponse objects, access via .matches (not .get())
        off_matches = index.query(namespace="official",  vector=query_vector, top_k=5, include_metadata=True).matches
        com_matches = index.query(namespace="community", vector=query_vector, top_k=5, include_metadata=True).matches

        # 3. Build context — each match is a ScoredVector, metadata is a plain dict
        official_context  = "\n\n".join(m.metadata.get("raw_data", "") for m in off_matches)
        community_context = "\n\n".join(m.metadata.get("raw_data", "") for m in com_matches)

        # 4. Ask Groq
        prompt = f"""You are DankGPT, an expert AI assistant for the Dank Memer Discord Bot.
Your goal is to answer the user's question accurately, concisely, and with a friendly tone.

You will be provided with two sources of context:
1. [GUIDE FACTS]: Extracted directly from guides. 100% accurate. Prioritize this above all else.
2. [COMMUNITY RUMORS]: Messages from the Discord community. May be outdated or wrong. Only use if GUIDE FACTS are insufficient, and warn the user.

CRITICAL INSTRUCTIONS:
- NEVER hallucinate. If the answer cannot be found in the context, say "I don't have enough information to answer that."
- FORMATTING: Use Markdown (bold, italics, bullet points) for readability.
- Be concise and directly address the question.
- PROVIDE EXACT DETAILS: Extract specific quantities, exact amounts, drop rates, and command syntaxes from the context.

[GUIDE FACTS]
{official_context or "No official data found."}

[COMMUNITY RUMORS]
{community_context or "No community data found."}

[USER QUESTION]
{req.question}
"""
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return {"response": completion.choices[0].message.content}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
