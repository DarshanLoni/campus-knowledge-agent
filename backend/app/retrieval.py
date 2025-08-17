# app/retrieval.py
#  CHECKPOINT WORKING
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from .db import supabase

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

print("Loading embedding model for retrieval...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', use_auth_token=HF_TOKEN)

def retrieve_chunks(query: str, user_id: str, top_k: int = 3):
    query_embedding = model.encode(query).tolist()

    resp = supabase.rpc(
        "match_documents_user",
        {"query_embedding": query_embedding, "match_count": top_k, "p_user_id": user_id}
    ).execute()

    if not resp.data:
        return [], ""

    chunks = []
    for c in resp.data:
        md = c.get("metadata") or {}
        chunks.append({
            "content": c["content"],
            "source": c.get("source"),
            "page": md.get("page_number"),
            "similarity": c.get("similarity"),
            "metadata": md
        })

    raw_context = "\n\n".join([c["content"] for c in chunks])
    return chunks, raw_context
