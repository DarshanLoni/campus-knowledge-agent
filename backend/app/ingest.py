# app/ingest.py
import os
from dotenv import load_dotenv
from .db import supabase
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from os.path import basename
import google.generativeai as genai
import google.auth

load_dotenv()

# Authenticate with Service Account instead of API key
credentials, project = google.auth.load_credentials_from_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
genai.configure(credentials=credentials)

print("Using Google GenAI embeddings with Service Account...")

def process_document(file_path: str, user_id: str, file_id: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    filename_only = basename(file_path)

    for idx, chunk in enumerate(chunks):
        page = chunk.metadata.get("page", None)

        # Generate embedding using Google GenAI
        embedding_resp = genai.embed_content(
            model="models/embedding-001",
            content=chunk.page_content
        )
        embedding = embedding_resp["embedding"]

        supabase.table("chunks").insert({
            "content": chunk.page_content,
            "embedding": embedding,
            "user_id": user_id,
            "file_id": file_id,
            "metadata": {
                "source": filename_only,
                "page_number": page,
                "chunk_index": idx
            }
        }).execute()

    print(f"Inserted {len(chunks)} chunks from {file_path} for user {user_id}, file_id={file_id}.")
