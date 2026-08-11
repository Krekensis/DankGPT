"""
DankGPT Debug Script
Run: python debug_test.py
Reads keys from .env file in the parent directory.
"""
import os
import sys
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

PINECONE_KEY = os.environ.get("PINECONE_KEY", "").strip('"').strip("'")
HF_TOKEN     = os.environ.get("HF_TOKEN", "").strip('"').strip("'")
GROQ_KEY     = os.environ.get("GROQ_KEY", "").strip('"').strip("'")

TEST_QUESTION = "How do I get coins in Dank Memer?"
HF_API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"

def sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ─── Step 0: Check Keys ───────────────────────────────────────
sep("STEP 0: Environment Variables")
for name, val in [("PINECONE_KEY", PINECONE_KEY), ("HF_TOKEN", HF_TOKEN), ("GROQ_KEY", GROQ_KEY)]:
    if val:
        print(f"  ✅ {name} = {val[:8]}...{val[-4:]}")
    else:
        print(f"  ❌ {name} = MISSING")

if not all([PINECONE_KEY, HF_TOKEN, GROQ_KEY]):
    print("\n  FATAL: Missing keys. Check your .env file.")
    sys.exit(1)

# ─── Step 1: Hugging Face Embedding ──────────────────────────
sep("STEP 1: HuggingFace Inference API (Embedding)")
print(f"  Model: BAAI/bge-large-en-v1.5")
print(f"  Input: '{TEST_QUESTION}'")
try:
    client = InferenceClient(api_key=HF_TOKEN)
    vector = client.feature_extraction(text=TEST_QUESTION, model="BAAI/bge-large-en-v1.5")
    query_vector = vector.tolist() if hasattr(vector, 'tolist') else vector
    
    print(f"  ✅ Got embedding. Dimension: {len(query_vector)}")
    print(f"  First 5 values: {query_vector[:5]}")
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")
    print("  >> Continuing with dummy zero-vector to still test Pinecone/Groq...")
    query_vector = [0.0] * 1024

# ─── Step 2: Pinecone Connection ─────────────────────────────
sep("STEP 2: Pinecone Connection")
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=PINECONE_KEY)
    indexes = [i.name for i in pc.list_indexes()]
    print(f"  Available indexes: {indexes}")
    if "dankgpt" not in indexes:
        print("  ❌ Index 'dankgpt' NOT FOUND. Did the upload notebook finish?")
        sys.exit(1)
    print("  ✅ Index 'dankgpt' exists.")
    index = pc.Index("dankgpt")
    stats = index.describe_index_stats()
    print(f"  Index stats: {stats}")
    namespaces = stats.get("namespaces", {})
    for ns in ["official", "community"]:
        count = namespaces.get(ns, {}).get("vector_count", 0)
        status = "✅" if count > 0 else "❌ EMPTY"
        print(f"  {status} namespace='{ns}' → {count} vectors")
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")
    sys.exit(1)

# ─── Step 3: Pinecone Query ───────────────────────────────────
sep("STEP 3: Pinecone Query")
try:
    for ns in ["official", "community"]:
        res = index.query(namespace=ns, vector=query_vector, top_k=2, include_metadata=True)
        print(f"\n  namespace='{ns}': {len(res.matches)} results")
        for i, m in enumerate(res.matches):
            print(f"    [{i}] score={m.score:.4f}, metadata keys={list(m.metadata.keys())}")
            raw_data = m.metadata.get("raw_data", "")
            print(f"         raw_data preview: {str(raw_data)[:120]}")
    print("\n  ✅ Pinecone query successful.")
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# ─── Step 4: Groq ─────────────────────────────────────────────
sep("STEP 4: Groq API")
try:
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        temperature=0.0,
    )
    reply = completion.choices[0].message.content
    print(f"  ✅ Groq responded: '{reply}'")
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")
    sys.exit(1)

# ─── All Clear ────────────────────────────────────────────────
sep("ALL STEPS PASSED ✅")
print("  The backend pipeline is fully functional.")
print("  If you still get 500s on Vercel, the issue is environment variables not set there.\n")
