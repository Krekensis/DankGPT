import torch
import json
import os
from sentence_transformers import SentenceTransformer, util

# The user confirmed they are using the tiny model for free hosting!
MODEL_NAME = 'all-MiniLM-L6-v2'
MODELS_DIR = 'models'

# Load the embedding model (only takes a few seconds for the mini model)
print(f"Loading {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded successfully!")

def search(query, brain="official", top_k=5):
    """
    Takes a string query, converts it to a vector, and searches the specified brain.
    brain: "official" or "community"
    """
    embeddings_path = os.path.join(MODELS_DIR, f'embeddings_{brain}.pt')
    metadata_path = os.path.join(MODELS_DIR, f'metadata_{brain}.json')
    
    if not os.path.exists(embeddings_path) or not os.path.exists(metadata_path):
        return f"Error: Could not find databases for the '{brain}' brain in the {MODELS_DIR} folder."
    
    # 1. Load the database (we only do this on the fly for testing purposes. In production, keep this in memory!)
    db_embeddings = torch.load(embeddings_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        db_metadata = json.load(f)
        
    # 2. Convert the user's question into math
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # 3. Calculate Cosine Similarity (finds the vectors pointing in the exact same direction as our question)
    cosine_scores = util.cos_sim(query_embedding, db_embeddings)[0]
    
    # 4. Get the Top K highest scores
    top_results = torch.topk(cosine_scores, k=top_k)
    
    results = []
    for score, idx in zip(top_results[0], top_results[1]):
        item = db_metadata[idx]
        results.append({
            "score": f"{score:.4f}",
            "topic": item.get("topic", "Unknown"),
            "raw_data": item.get("raw_data", item.get("knowledge", ""))
        })
        
    return results

if __name__ == "__main__":
    # Test our brand new search engine!
    test_query = "How much does a Trash item sell for?"
    print(f"\n--- Searching the Official Brain for: '{test_query}' ---\n")
    
    results = search(test_query, brain="official", top_k=3)
    
    if isinstance(results, str):
        print(results)
    else:
        for i, res in enumerate(results):
            print(f"Result {i+1} (Score: {res['score']})")
            print(f"Topic: {res['topic']}")
            print(f"Content: {res['raw_data']}\n")
            print("-" * 40 + "\n")
