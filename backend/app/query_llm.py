# app/query_llm.py
def generate_clarification(query: str, context: str) -> str:
    """
    Calls Gemini to generate a clarifying question for ambiguous queries.
    """
    prompt = f"""
    The user asked an ambiguous question: "{query}"
    Based on the following context:
    "{context}"
    Generate a concise clarifying question to ask the user.
    """
    return ask_gemini(prompt)
# app/query_llm.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def ask_gemini(prompt: str) -> str:
    """
    Calls Gemini with a raw text prompt and returns text.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        # You can pass safety settings/params here if needed:
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 400
        }
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        return f"Error: {resp.text}"
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return str(data)
