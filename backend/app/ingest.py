import os
from dotenv import load_dotenv
from .db import supabase
# from app.ingest import process_document

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Load env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Load embedding model from Hugging Face
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', use_auth_token=HF_TOKEN)

def process_document(file_path: str):
    # Step 1 — Load document
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Step 2 — Chunk document
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    # Step 3 — Generate embeddings & store in Supabase
    # for chunk in chunks:
    #     embedding = model.encode(chunk.page_content).tolist()
    #     supabase.table("chunks").insert({
    #         "content": chunk.page_content,
    #         "embedding": embedding,
    #         "metadata": {"source": file_path}
    #     }).execute()
    # inside process_document loop (ingest.py)
    for idx, chunk in enumerate(chunks):
        # chunk.metadata may include 'page' if loader supports it; some loaders put in chunk.metadata["page"]
        page = chunk.metadata.get("page", None)
        embedding = model.encode(chunk.page_content).tolist()
        supabase.table("chunks").insert({
            "content": chunk.page_content,
            "embedding": embedding,
            "metadata": {"source": file_path, "page_number": page, "chunk_index": idx}
        }).execute()


        print(f"Inserted {len(chunks)} chunks from {file_path} into Supabase.")

if __name__ == "__main__":
    # Example run
    process_document("docs/campus_rules.pdf")
