# app/retrieval.py
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
    """
    Retrieve top_k relevant chunks from Supabase for the given query.
    Returns:
        chunks: List of dicts with content, source, page_number, similarity
        raw_context: combined text of top_k chunks
    """
    # 1) Generate embedding for query
    query_embedding = model.encode(query).tolist()

    # 2) Call Supabase RPC function to get top_k matches
    resp = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_count": top_k}
    ).execute()

    if not resp.data:
        return [], ""

    # 3) Extract chunks with page_number and similarity
    chunks = []
    for c in resp.data:
        chunks.append({
            "content": c["content"],
            "source": c.get("source"),
            "page": c.get("metadata", {}).get("page_number") if c.get("metadata") else None,
            "similarity": c.get("similarity")
        })

    # 4) Combine raw context for LLM input
    raw_context = "\n\n".join([c["content"] for c in chunks])

    return chunks, raw_context
