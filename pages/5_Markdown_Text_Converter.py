import streamlit as st
from assets.theme import inject_global_css, page_hero

st.set_page_config(page_title="Markdown Converter", layout="wide", page_icon="📝")
inject_global_css()

# ── Extra styles for the editor/preview panes ───────────────────────────────
st.markdown("""
<style>
.pane-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4a9eff;
    margin-bottom: 6px;
    padding-left: 2px;
}
.preview-pane {
    background: #111827;
    border: 1px solid #1f2d44;
    border-radius: 12px;
    padding: 20px 24px;
    min-height: 460px;
    color: #e2eaff;
    line-height: 1.7;
}
.preview-pane h1, .preview-pane h2, .preview-pane h3 {
    color: #e2eaff !important;
}
.preview-pane a { color: #4a9eff; }
.preview-pane code {
    background: #1a2234;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 13px;
    color: #f472b6;
}
.preview-pane pre {
    background: #1a2234;
    border-radius: 8px;
    padding: 14px;
    overflow-x: auto;
}
.preview-pane blockquote {
    border-left: 3px solid #4a9eff;
    margin-left: 0;
    padding-left: 16px;
    color: #64748b;
}
</style>
""", unsafe_allow_html=True)

page_hero("📝", "Markdown Converter", "Write or upload Markdown and see a live rendered preview.")

# ── Session init ────────────────────────────────────────────────────────────
if "md_text" not in st.session_state:
    st.session_state.md_text = ""
if "show_input" not in st.session_state:
    st.session_state.show_input = True

# ── Toggle button ───────────────────────────────────────────────────────────
tog_col, _ = st.columns([1, 8])
with tog_col:
    label = "◀ Hide Editor" if st.session_state.show_input else "▶ Show Editor"
    if st.button(label):
        st.session_state.show_input = not st.session_state.show_input

# ── Layout ──────────────────────────────────────────────────────────────────
if st.session_state.show_input:
    col1, col2 = st.columns([1, 2])
else:
    col1, col2 = None, st.container()

if st.session_state.show_input and col1 is not None:
    with col1:
        st.markdown('<div class="pane-label">✏️ Editor</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload .md / .txt file",
            type=["md", "markdown", "txt"],
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            st.session_state.md_text = uploaded_file.read().decode("utf-8")

        md_text = st.text_area(
            "Markdown input",
            value=st.session_state.md_text,
            height=440,
            placeholder="# Hello World\n\nStart typing your **Markdown** here...",
            label_visibility="collapsed",
        )
        if md_text != st.session_state.md_text:
            st.session_state.md_text = md_text

with col2:
    st.markdown('<div class="pane-label">👁️ Preview</div>', unsafe_allow_html=True)
    preview_content = st.session_state.md_text or "*Your rendered preview will appear here…*"
    st.markdown(
        f'<div class="preview-pane">{st.markdown(preview_content, unsafe_allow_html=True) or ""}</div>',
        unsafe_allow_html=True,
    )
