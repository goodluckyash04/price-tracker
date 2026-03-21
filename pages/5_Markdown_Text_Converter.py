import streamlit as st

st.set_page_config(page_title="Markdown Text converter", layout="wide", page_icon="📝")

# Initialize toggle state
if "show_input" not in st.session_state:
    st.session_state.show_input = True

# Button to toggle visibility
toggle_label = "🔽" if st.session_state.show_input else "🔼"
if st.button(toggle_label):
    st.session_state.show_input = not st.session_state.show_input

# Show both columns if input is visible; else show preview full width
if st.session_state.show_input:
    col1, col2 = st.columns([1, 2])
else:
    col2 = st.container()

if st.session_state.show_input:
    with col1:
        uploaded_file = st.file_uploader("Upload Markdown file", type=["md", "markdown", "txt"])

        if uploaded_file is not None:
            # Read file and update session state immediately
            st.session_state.md_text = uploaded_file.read().decode("utf-8")
        else:
            # Initialize if not set
            if "md_text" not in st.session_state:
                st.session_state.md_text = ""

        # Text area with session state binding
        md_text = st.text_area("Enter your markdown text here:", value=st.session_state.md_text, height=400)

        # Update session state only if text area content changes
        if md_text != st.session_state.md_text:
            st.session_state.md_text = md_text

with col2:
    st.markdown(st.session_state.md_text, unsafe_allow_html=True)
