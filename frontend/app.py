
import streamlit as st
import requests
import os
from utils import get_auth_headers


st.set_page_config(page_title="Campus Knowledge Agent", page_icon="🎓", layout="wide")

# Load BACKEND_URL from .env or Streamlit secrets
BACKEND_URL = os.environ.get("BACKEND_URL") or st.secrets.get("BACKEND_URL") or "http://localhost:8000"

# ------------------ Token Handling ------------------
query_params = st.experimental_get_query_params()
token = query_params.get("token", [None])[0]

if token:
    st.session_state["jwt_token"] = token
    st.experimental_set_query_params()  # remove token from URL

# ------------------ Login Check ------------------
if "jwt_token" not in st.session_state:
    st.markdown("""
        <div style="display:flex; justify-content:center; align-items:center; height:80vh; flex-direction:column;">
            <h1 style="font-family:sans-serif; color:#4B8BBE;">Campus Knowledge Agent</h1>
            <a href="{BACKEND_URL}/auth/google/login" style="
                background-color:#4285F4; color:white; padding:12px 24px; 
                text-decoration:none; border-radius:8px; font-weight:bold; font-size:18px;">
                Continue with Google
            </a>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ------------------ Sidebar Navigation ------------------
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Ask", "Upload", "Files"])

headers = get_auth_headers()

# ------------------ Theme Colors ------------------
if st.get_option("theme.base") == "dark":
    USER_BUBBLE = "rgba(30,144,255,0.9)"      # blueish for user
    BOT_BUBBLE = "rgba(25,25,25,0.95)"        # even darker for bot
    CARD_BG = "rgba(50,50,50,0.3)"
    CARD_BORDER = "rgba(100,100,100,0.5)"
    AI_THINKING = "#FFFFFF"
    CHAT_TEXT_COLOR = "#FFFFFF"
else:
    USER_BUBBLE = "rgba(220,248,198,0.9)"
    BOT_BUBBLE = "rgb(22, 38, 51)"
    CARD_BG = "rgba(255,255,255,0.05)"
    CARD_BORDER = "rgba(224,224,224,0.5)"
    AI_THINKING = "#555555"
    CHAT_TEXT_COLOR = "#222222"

# ----- Home Page -----
if page == "Home":
    st.markdown("<h1 style='color:#4B8BBE;'>🎓 EduAssist AI</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="padding:15px; border-radius:10px; background-color: #4B8BBE;">
            <h3 style="color:#4B8BBE;">About EduAssist AI</h3>
            <p>
            EduAssist AI is your personal AI-powered knowledge assistant for academic and campus-related content.
            It allows you to upload PDF documents, ask questions, and get instant AI-generated answers  
            with references from your uploaded materials.
            </p>
            <ul>
                <li>🔹 Upload your PDF documents (lecture notes, reports, research papers).</li>
                <li>🔹 Ask questions in natural language and get precise answers from your files.</li>
                <li>🔹 AI-powered summarization and source referencing for better understanding.</li>
                <li>🔹 Manage and organize uploaded files efficiently.</li>
                <li>🔹 Secure login with Google authentication for personalized access.</li>
            </ul>
            <p>Start by uploading your files and exploring the Ask page to interact with EduAssist AI!</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        resp = requests.get(f"{BACKEND_URL}/files", headers=headers)
        if resp.status_code == 200:
            files = resp.json().get("files", [])
            if files:
                st.markdown(f"<h3 style='color:#4B8BBE;'>📂 Your Uploaded Files ({len(files)})</h3>", unsafe_allow_html=True)
                for f in files:
                    st.markdown(f"""
                        <div style='border:1px solid {CARD_BORDER}; padding:10px; border-radius:10px; margin-bottom:10px; background-color:{CARD_BG};'>
                            <b>Filename:</b> {f['filename']} <br>
                            <b>Uploaded At:</b> {f.get('uploaded_at', 'N/A')}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("You haven't uploaded any files yet. Go to the Upload page to get started!")
        else:
            st.error("Failed to fetch files. Please login again.")
    except Exception as e:
        st.error(f"Error: {e}")


# ----- Upload Page -----
elif page == "Upload":
    st.markdown("<h1 style='color:#4B8BBE;'>📤 Upload PDF</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getbuffer(), "application/pdf")}
        try:
            resp = requests.post(
                f"{BACKEND_URL}/upload",
                files=files,
                headers=headers
            )
            if resp.status_code == 200:
                st.success(f"Uploaded: {uploaded_file.name}")
                st.json(resp.json())
            else:
                st.error(f"Upload failed: {resp.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# ----- Files Page -----
elif page == "Files":
    st.markdown("<h1 style='color:#4B8BBE;'>📄 Uploaded Files</h1>", unsafe_allow_html=True)
    try:
        resp = requests.get(f"{BACKEND_URL}/files", headers=headers)
        if resp.status_code == 200:
            files = resp.json().get("files", [])
            if not files:
                st.info("No files uploaded yet.")
            for f in files:
                st.markdown(f"""
                    <div style='border:1px solid {CARD_BORDER}; padding:10px; border-radius:10px; margin-bottom:10px; background-color:{CARD_BG};'>
                        <b>Filename:</b> {f['filename']} <br>
                        <b>Uploaded At:</b> {f.get('uploaded_at', 'N/A')}
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Delete {f['filename']}"):
                    del_resp = requests.delete(
                        f"{BACKEND_URL}/files",
                        json={"file_ids": [f['file_id']]},
                        headers=headers
                    )
                    if del_resp.status_code == 200:
                        st.success(f"Deleted {f['filename']}")
                        st.rerun()
                    else:
                        st.error(f"Delete failed: {del_resp.text}")
        else:
            st.error("Failed to fetch files.")
    except Exception as e:
        st.error(f"Error: {e}")
