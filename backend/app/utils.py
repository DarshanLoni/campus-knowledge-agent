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
