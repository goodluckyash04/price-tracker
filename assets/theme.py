"""
Shared theme module for the Multi-Utility Streamlit App.
Call inject_global_css() at the top of every page (after set_page_config).
"""
import streamlit as st


# ── Design tokens ──────────────────────────────────────────────────────────
BG          = "#0a0f1e"
SURFACE     = "#111827"
SURFACE_ALT = "#1a2234"
BORDER      = "#1f2d44"
ACCENT      = "#4a9eff"
ACCENT2     = "#a855f7"
ACCENT3     = "#f472b6"
GOLD        = "#f59e0b"
TEXT        = "#e2eaff"
MUTED       = "#64748b"
SUCCESS     = "#22c55e"
ERROR       = "#ef4444"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background-color: #0a0f1e !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1424 !important;
    border-right: 1px solid #1f2d44 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    color: #94a3b8 !important;
    border-radius: 8px;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #1e2d47 !important;
    color: #4a9eff !important;
}
[data-testid="stSidebarNavItems"] {
    padding-top: 8px;
}

/* ── Headings ── */
h1 { color: #e2eaff !important; font-weight: 800 !important; letter-spacing: -0.5px; }
h2, h3 { color: #e2eaff !important; font-weight: 700 !important; }
p, li, label { color: #94a3b8 !important; }

/* ── Inputs & text areas ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #111827 !important;
    border: 1px solid #1f2d44 !important;
    border-radius: 10px !important;
    color: #e2eaff !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #4a9eff !important;
    box-shadow: 0 0 0 3px #4a9eff22 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #111827 !important;
    border: 1px solid #1f2d44 !important;
    border-radius: 10px !important;
    color: #e2eaff !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4a9eff, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.4rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background: #1e2d47 !important;
    color: #94a3b8 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #1e2d47 !important;
    border: 1px solid #1f2d44 !important;
    color: #4a9eff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #111827 !important;
    border: 1px dashed #1f2d44 !important;
    border-radius: 12px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1f2d44 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #4a9eff !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: #64748b !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #4a9eff !important;
    border-bottom-color: #4a9eff !important;
}

/* ── Shared card surface ── */
.card-surface {
    background: linear-gradient(145deg, #111827, #1a2234);
    border: 1px solid #1f2d44;
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.card-surface:hover {
    transform: translateY(-2px);
    border-color: #4a9eff44;
}
.card-surface::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4a9eff, #a855f7, #f472b6);
    opacity: 0.6;
}

/* ── Section header ── */
.section-header {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4a9eff !important;
    margin: 28px 0 14px 0;
    padding: 0 0 0 12px;
    border-left: 3px solid #4a9eff;
}

/* ── Metric box ── */
.metric-box {
    background: linear-gradient(145deg, #111827, #1a2234);
    border: 1px solid #1f2d44;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
}
.metric-box .m-val {
    font-size: 28px;
    font-weight: 800;
    color: #e2eaff;
    line-height: 1.1;
}
.metric-box .m-lbl {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* ── Page hero header ── */
.page-hero {
    padding: 4px 0 24px 0;
}
.page-hero h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #e2eaff !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.page-hero p {
    color: #64748b !important;
    margin: 6px 0 0 0 !important;
    font-size: 14px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
"""


def inject_global_css():
    """Inject the shared dark theme CSS into the current page."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def page_hero(icon: str, title: str, subtitle: str = ""):
    """Render a styled page header."""
    sub_html = f'<p>{subtitle}</p>' if subtitle else ''
    st.markdown(
        f'<div class="page-hero"><h1>{icon} {title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]):
    """
    Render a row of metric boxes.
    Each dict: { "label": str, "value": str }
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="m-val">{m["value"]}</div>'
                f'<div class="m-lbl">{m["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def section_header(text: str):
    """Render a styled section sub-header."""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)
