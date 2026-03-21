import streamlit as st
from services.auth import guard
from assets.theme import inject_global_css, page_hero

st.set_page_config(page_title="Multi-Utility App", layout="wide", page_icon="🛠️")
inject_global_css()
guard()

# ── Extra Home-page styles ──────────────────────────────────────────────────
st.markdown("""
<style>
.utility-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 8px;
}
.utility-card {
    background: linear-gradient(145deg, #111827, #1a2234);
    border: 1px solid #1f2d44;
    border-radius: 18px;
    padding: 28px 24px;
    text-align: center;
    text-decoration: none;
    display: block;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.utility-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4a9eff, #a855f7, #f472b6);
    opacity: 0.5;
    transition: opacity 0.2s;
}
.utility-card:hover {
    transform: translateY(-4px);
    border-color: #4a9eff55;
    box-shadow: 0 12px 32px rgba(74,158,255,0.12);
}
.utility-card:hover::before { opacity: 1; }
.utility-icon { font-size: 48px; margin-bottom: 12px; display: block; }
.utility-title {
    font-size: 18px;
    font-weight: 700;
    color: #e2eaff;
    margin-bottom: 8px;
}
.utility-desc { font-size: 13px; color: #64748b; line-height: 1.5; }
.tagline-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4a9eff22, #a855f722);
    border: 1px solid #4a9eff44;
    border-radius: 100px;
    padding: 4px 16px;
    font-size: 12px;
    color: #4a9eff;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Welcome banner ──────────────────────────────────────────────────────────
name = st.session_state.get("name") or "there"
st.markdown(f"""
<div style="padding: 8px 0 4px 0;">
    <div class="tagline-badge">🛠️ Multi-Utility Dashboard</div>
    <h1 style="font-size:2.4rem; font-weight:800; color:#e2eaff; margin:0; letter-spacing:-1px;">
        Welcome back, {name}! 👋
    </h1>
    <p style="color:#64748b; margin:8px 0 28px 0; font-size:15px;">
        Pick a tool below to get started.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Utility cards ───────────────────────────────────────────────────────────
utilities = [
    {"title": "Product Tracker",       "desc": "Track Amazon product prices over time and get price history charts.", "icon": "📦", "url": "/Product_Tracker"},
    {"title": "My Products",            "desc": "View all tracked products with price stats and refresh data.",         "icon": "🗂️", "url": "/My_Products"},
    {"title": "Return Calculator",      "desc": "Calculate your investment returns using the XIRR method.",            "icon": "📈", "url": "/Return_Calculator"},
    {"title": "Music Downloader",       "desc": "Download audio from YouTube links in WEBM or MP3 format.",            "icon": "🎵", "url": "/Music_Downloader"},
    {"title": "Markdown Converter",     "desc": "Write or upload markdown and preview the rendered output live.",       "icon": "📝", "url": "/Markdown_Text_Converter"},
    {"title": "Jio Plans",              "desc": "Browse and filter Jio prepaid recharge plans with live data.",         "icon": "📶", "url": "/Jio_Plans"},
]

cards_html = '<div class="utility-grid">'
for u in utilities:
    cards_html += (
        f'<a class="utility-card" href="{u["url"]}">'
        f'<span class="utility-icon">{u["icon"]}</span>'
        f'<div class="utility-title">{u["title"]}</div>'
        f'<div class="utility-desc">{u["desc"]}</div>'
        f'</a>'
    )
cards_html += '</div>'

st.markdown(cards_html, unsafe_allow_html=True)
