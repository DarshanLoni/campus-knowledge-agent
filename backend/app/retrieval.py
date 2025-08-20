import os
from dotenv import load_dotenv
from .db import supabase
import google.generativeai as genai
#  CHECKPOINT WORKING Fully functional
load_dotenv()

# ✅ Use API key for Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

print("Using Google GenAI embeddings with API key for retrieval...")

def retrieve_chunks(query: str, user_id: str, top_k: int = 3):
    # Generate embedding for query
    embedding_resp = genai.embed_content(
        model="models/embedding-001",
        content=query
    )
    query_embedding = embedding_resp["embedding"]

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
