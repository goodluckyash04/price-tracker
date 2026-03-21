import os
from datetime import datetime, timedelta

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

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
        VALIDATE_URL = os.getenv("AUTHENTICATE_URL")
        SESSION_DURATION_MINUTES = 60

    session_key = st.query_params.get("_id")
    if session_key:
        try:
            response = requests.get(VALIDATE_URL, params={"session_key": session_key})
            data = response.json()
            if data.get("validate"):
                st.session_state.authenticated = True
                st.session_state.username = data.get("username", "")
                st.session_state.name = data.get("name", "")
                st.session_state.email = data.get("email", "")
                st.session_state.auth_expiry = datetime.now() + timedelta(
                    minutes=SESSION_DURATION_MINUTES
                )
                return
        except Exception:
            pass
    st.session_state.authenticated = False
    st.session_state.auth_expiry = None


def authenticate_once():
    """Checks if user should be (re)authenticated."""
    if _revalidate_needed():
        _perform_validation()


def guard():
    """Use at the top of every Streamlit page."""
    # Local dev bypass
    try:
        if os.getenv("ENVIRONMENT") == "Local":
            st.session_state.authenticated = True
            st.session_state.username = "Dev"
            st.session_state.name = "Developer"
            st.session_state.email = ""
            st.session_state.auth_expiry = datetime.now() + timedelta(minutes=60)
            return
    except Exception:
        pass

    authenticate_once()
    if not st.session_state.get("authenticated"):
        try:
            if st.secrets:
                REDIRECT_URL = st.secrets["myhelperbuddy"]["REDIRECT_URL"]
        except StreamlitSecretNotFoundError:
            REDIRECT_URL = os.getenv("REDIRECT_URL")

        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        html,body,[class*="css"]{ font-family:'Inter',sans-serif !important; }
        .stApp { background: #0a0f1e !important; }
        .auth-wrap {
            display: flex; align-items: center; justify-content: center;
            min-height: 80vh;
        }
        .auth-card {
            background: linear-gradient(145deg, #111827, #1a2234);
            border: 1px solid #1f2d44;
            border-radius: 24px;
            padding: 48px 40px;
            text-align: center;
            max-width: 420px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        .auth-card::before {
            content:'';
            position:absolute; top:0; left:0; right:0; height:3px;
            background: linear-gradient(90deg,#4a9eff,#a855f7,#f472b6);
        }
        .auth-icon { font-size: 56px; margin-bottom: 16px; display: block; }
        .auth-title {
            font-size: 1.6rem; font-weight: 800;
            color: #e2eaff; margin: 0 0 8px 0;
        }
        .auth-sub { font-size: 14px; color: #64748b; margin-bottom: 32px; }
        .auth-btn {
            display: inline-block;
            background: linear-gradient(135deg, #4a9eff, #a855f7);
            color: white !important;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 15px;
            transition: opacity 0.2s, transform 0.15s;
            letter-spacing: 0.3px;
        }
        .auth-btn:hover { opacity: 0.85; transform: translateY(-1px); }
        .auth-note { font-size: 12px; color: #334155; margin-top: 20px; }
        #MainMenu, footer { visibility: hidden; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="auth-wrap">
            <div class="auth-card">
                <span class="auth-icon">🛠️</span>
                <div class="auth-title">Multi-Utility Dashboard</div>
                <div class="auth-sub">Your session has expired or you need to sign in to access this page.</div>
                <a class="auth-btn" href="{REDIRECT_URL}" target="_blank">🔐 Sign In with myHelperBuddy</a>
                <div class="auth-note">
                    Visit <a href="https://myhelperbuddy.pythonanywhere.com" style="color:#4a9eff;text-decoration:none;">myHelperBuddy</a> to manage your account.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
