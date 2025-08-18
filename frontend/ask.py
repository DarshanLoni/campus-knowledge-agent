import streamlit as st
import requests

def show():
    st.title("❓ Ask a Question")
    token = st.session_state.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    question = st.text_input("Enter your question:")
    top_k = st.number_input("Top K chunks", value=4, min_value=1, max_value=10)
    
    if st.button("Ask"):
        if not question:
            st.warning("Enter a question first.")
            return
        
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={"question": question, "top_k": top_k},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer:")
                st.write(data.get("answer", "No answer found"))
                
                st.subheader("Sources Used:")
                for src in data.get("sources", []):
                    st.write(f"Source: {src.get('source')}, Page: {src.get('page')}")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
