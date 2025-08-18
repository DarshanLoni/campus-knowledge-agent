import streamlit as st
import requests

def show():
    st.title("📤 Upload PDF")
    token = st.session_state.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getbuffer(), "application/pdf")}
        try:
            response = requests.post(
                "http://localhost:8000/upload",
                files=files,
                headers=headers
            )
            if response.status_code == 200:
                st.success(f"Uploaded: {uploaded_file.name}")
                st.json(response.json())
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
