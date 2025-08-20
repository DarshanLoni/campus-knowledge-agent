import streamlit as st
#  CHECKPOINT WORKING Fully functional
def get_auth_headers() -> dict:
    """
    Returns Authorization headers with JWT token from session_state.
    Raises an exception if user is not logged in.
    """
    if "jwt_token" not in st.session_state:
        raise Exception("User not authenticated. Please login first.")
    return {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
