import streamlit as st
from services.auth import guard


# Authenticate user
st.set_page_config(page_title="Multi-Utility App", layout="wide",page_icon="🛠️" )
guard()


st.markdown("""
    <style>
    .card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        margin: 20px;    
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .icon {
        font-size: 50px;
        margin-bottom: 10px;
        color: #198754;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👋 Welcome to Multi-Utility Dashboard")
st.caption(f"Hello, {st.session_state.name or 'User'}! Choose from the tools below.")

# Utility Cards
utilities = [
    {
        "title": "Product Tracker",
        "desc": "Track product prices over time from online stores.",
        "icon": "📦",
        "url": "/Products"
    },
    {
        "title": "Music Downloader",
        "desc": "Download music from YouTube links.",
        "icon": "🎵",
        "url": "/Music_downloader"
    },
    {
        "title": "Return Calculator",
        "desc": "Calculate your investment returns using XIRR.",
        "icon": "📈",
        "url": "/Return_calculator"
    },
    {
        "title": "More Utilities Coming Soon",
        "desc": "Stay tuned for more tools!",
        "icon": "🛠️",
        "url": "#"
    }
]

cols = st.columns(2)
for i, util in enumerate(utilities):
    with cols[i % 2]:
        st.markdown(f"""
            <div class="card">
                <div class="icon">{util['icon']}</div>
                <h3>{util['title']}</h3>
                <p>{util['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
