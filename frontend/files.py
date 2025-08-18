import streamlit as st
import requests

def show():
    st.title("📄 Uploaded Files")
    token = st.session_state.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("http://localhost:8000/files", headers=headers)
        if response.status_code == 200:
            files = response.json().get("files", [])
            if not files:
                st.info("No files uploaded yet.")
            else:
                for f in files:
                    st.write(f"Filename: {f['filename']}, Uploaded At: {f['uploaded_at']}")
                    if st.button(f"Delete {f['filename']}"):
                        del_resp = requests.delete(
                            "http://localhost:8000/files",
                            json={"file_ids": [f['file_id']]},
                            headers=headers
                        )
                        if del_resp.status_code == 200:
                            st.success(f"Deleted {f['filename']}")
                        else:
                            st.error(f"Delete failed: {del_resp.text}")
        else:
            st.error("Failed to fetch files.")
    except Exception as e:
        st.error(f"Error: {e}")
