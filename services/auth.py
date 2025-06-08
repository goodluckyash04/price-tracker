import os
import streamlit as st
import requests
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError
from datetime import datetime, timedelta
import streamlit.components.v1 as components    


load_dotenv()

def _revalidate_needed():
    """Returns True if revalidation time has passed."""
    expiry_time = st.session_state.get("auth_expiry")
    if not expiry_time:
        return True
    return datetime.now() > expiry_time

def _perform_validation():
    try:
        if st.secrets:
            VALIDATE_URL = st.secrets["myhelperbuddy"]["AUTHENTICATE_URL"]
            SESSION_DURATION_MINUTES = st.secrets["myhelperbuddy"]["TIMEOUT"]
    except StreamlitSecretNotFoundError:
        # Local development
        VALIDATE_URL = os.getenv('AUTHENTICATE_URL')
        SESSION_DURATION_MINUTES = 60 # minutes
        
    session_key = st.query_params.get("_id")
    if session_key:
        try:
            response = requests.get(VALIDATE_URL, params={'session_key': session_key})
            data = response.json()
            if data.get("validate"):
                st.session_state.authenticated = True
                st.session_state.username = data.get("username", "")
                st.session_state.name = data.get("name", "")
                st.session_state.email = data.get("email", "")
                st.session_state.auth_expiry = datetime.now() + timedelta(minutes=SESSION_DURATION_MINUTES)
                return
        except:
            pass
    st.session_state.authenticated = False
    st.session_state.auth_expiry = None

def authenticate_once():
    """Checks if user should be (re)authenticated."""
    if _revalidate_needed():
        _perform_validation()

def guard():
    
    """Use at the top of every Streamlit page."""
    authenticate_once()
    if not st.session_state.get("authenticated"):
        try:
            if st.secrets:
                REDIRECT_URL = st.secrets["myhelperbuddy"]["REDIRECT_URL"]
        except StreamlitSecretNotFoundError:
            # Local development
            REDIRECT_URL = os.getenv('REDIRECT_URL')

        components.html(f"""
            <script>
                window.location.replace("{REDIRECT_URL}");
            </script>
            <p>If you're not redirected, <a href="{REDIRECT_URL}">click here</a>.</p>
        """, height=0)
        st.stop()