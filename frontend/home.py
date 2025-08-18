import streamlit as st
import requests

def show():
    st.title("🏠 Home Page")
    token = st.session_state.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("http://localhost:8000/files", headers=headers)
        if response.status_code == 200:
            files = response.json().get("files", [])
            st.write(f"You are logged in! You have {len(files)} uploaded file(s).")
        else:
            st.error("Failed to fetch files. Please login again.")
    except Exception as e:
        st.error(f"Error: {e}")
