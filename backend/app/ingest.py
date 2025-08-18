# app/ingest.py
# CHECKPOINT FIXED
import os
from dotenv import load_dotenv
from .db import supabase
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from os.path import basename

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

print("Loading embedding model...")
# use_auth_token deprecated → use token
model = SentenceTransformer(
    'sentence-transformers/paraphrase-MiniLM-L3-v2',
    token=HF_TOKEN
)

def process_document(file_path: str, user_id: str, file_id: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    filename_only = basename(file_path)

    for idx, chunk in enumerate(chunks):
        page = chunk.metadata.get("page", None)
        embedding = model.encode(chunk.page_content).tolist()

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
