import os
import traceback

import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

# Load environment variables (for local development)
load_dotenv()

# Determine if the app is running in Streamlit or locally
try:
    if st.secrets:
        if "firebase" not in st.secrets:
            st.error("Firebase configuration is missing from Streamlit secrets.")
            raise ValueError("Firebase configuration is missing")
        # Streamlit deployments
        firebase_config = st.secrets["firebase"]
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": firebase_config["project_id"],
            "private_key_id": firebase_config["private_key_id"],
            "private_key": firebase_config["private_key"].replace('\\n', '\n'),
            "client_email": firebase_config["client_email"],
            "client_id": firebase_config["client_id"],
            "auth_uri": firebase_config["auth_uri"],
            "token_uri": firebase_config["token_uri"],
            "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_config["client_x509_cert_url"]
        })
except StreamlitSecretNotFoundError:
    # Local development
    firebase_config_path = os.getenv('FIREBASE_CONFIG_PATH')
    cred = credentials.Certificate(firebase_config_path)
except:
    traceback.print_exc()

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
