#  CHECKPOINT WORKING Fully functional
def process_pdf_into_chunks(file_path: str, chunk_size: int = 500):
    """
    Reads a PDF and splits it into text chunks.
    """
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    # Split into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return [{"content": chunk} for chunk in chunks]
# app/utils.py
from typing import List, Dict

def unique_sources(chunks: List[Dict]) -> List[Dict]:
    """
    Extract unique sources from retrieved chunks.
    Keeps highest similarity chunk per source.
    """
    seen = {}
    for chunk in chunks:
        src = chunk.get("source")
        sim = chunk.get("similarity", 0)
        if src:
            # Keep the chunk with highest similarity
            if src not in seen or sim > seen[src]["similarity"]:
                seen[src] = {"source": src, "similarity": sim}
    return list(seen.values())
