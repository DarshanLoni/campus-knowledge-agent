# app/retrieval.py
import os
from dotenv import load_dotenv
from .db import supabase
import google.generativeai as genai
import google.auth

load_dotenv()

# Authenticate with Service Account instead of API key
credentials, project = google.auth.load_credentials_from_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
genai.configure(credentials=credentials)

print("Using Google GenAI embeddings with Service Account for retrieval...")

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
