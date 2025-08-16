import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from .db import supabase

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Load embedding model
print("Loading embedding model for retrieval...")
model = SentenceTransformer(
    'sentence-transformers/all-MiniLM-L6-v2',
    use_auth_token=HF_TOKEN
)

def retrieve_chunks(query: str, top_k: int = 3):
    query_embedding = model.encode(query).tolist()

    resp = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_count": top_k}
    ).execute()

    if not resp.data:
        return [], ""

    chunks = []
    for c in resp.data:
        chunks.append({
            "content": c["content"],
            "source": c.get("source"),
            "page": c.get("metadata", {}).get("page_number") if c.get("metadata") else None,
            "similarity": c.get("similarity")
        })

    raw_context = "\n\n".join([c["content"] for c in chunks])
    return chunks, raw_context
