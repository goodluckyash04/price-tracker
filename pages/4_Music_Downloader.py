import tempfile
import os

import streamlit as st
import yt_dlp
from mutagen import File as MutagenFile

from services.auth import guard
from assets.theme import inject_global_css, page_hero, section_header

st.set_page_config(page_title="Audio Downloader", layout="wide", page_icon="🎵")
inject_global_css()
guard()

page_hero("🎵", "Music Downloader", "Download audio from any YouTube link in WEBM or MP3 format.")


def download_audio(url: str, doc_type: str = "WEBM"):
    ext = "mp3" if doc_type.upper() == "MP3" else "webm"
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, f"temp.{ext}")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            "postprocessors": [],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                st.error("Download failed or file is empty.")
                return None, None, None

            audio = MutagenFile(output_path) if ext == "webm" else None
            audio_info = audio.info if audio else None

            metadata = {
                "Bitrate (kbps)": round(audio_info.bitrate / 1000, 2) if hasattr(audio_info, "bitrate") else "N/A",
                "Sample Rate (Hz)": audio_info.sample_rate if hasattr(audio_info, "sample_rate") else "N/A",
                "Channels": audio_info.channels if hasattr(audio_info, "channels") else "N/A",
                "Length (sec)": round(audio_info.length, 2) if hasattr(audio_info, "length") else "N/A",
                "Codec": type(audio_info).__name__ if audio_info else "Unknown",
            }

            with open(output_path, "rb") as f:
                file_data = f.read()

            title = info.get("title", "audio")
            filename = f"{title}.{ext}"
            return file_data, filename, metadata

        except Exception as e:
            st.error(f"❌ Failed to download: {str(e)}")
            return None, None, None


# ── Input form ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.form("yt_form"):
    url_col, fmt_col, btn_col = st.columns([5, 2, 1])
    with url_col:
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    with fmt_col:
        doc_type = st.selectbox("Format", ["WEBM", "MP3"], label_visibility="collapsed")
    with btn_col:
        submitted = st.form_submit_button("⬇️ Get", type="primary", use_container_width=True)

if submitted and url:
    with st.spinner("Downloading audio… this may take a moment."):
        file_data, filename, metadata = download_audio(url, doc_type)

    if file_data:
        st.success(f"✅ Download ready — **{filename}**")

        dl_col, _ = st.columns([2, 5])
        with dl_col:
            st.download_button(
                label=f"⬇️ Save {filename}",
                data=file_data,
                file_name=filename,
                mime=f"audio/{filename.split('.')[-1]}",
                use_container_width=True,
            )

        section_header("Audio Metadata")
        meta_cols = st.columns(len(metadata))
        for col, (key, val) in zip(meta_cols, metadata.items()):
            with col:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<div class="m-val" style="font-size:1.3rem;">{val}</div>'
                    f'<div class="m-lbl">{key}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
elif submitted and not url:
    st.warning("⚠️ Please enter a YouTube URL first.")