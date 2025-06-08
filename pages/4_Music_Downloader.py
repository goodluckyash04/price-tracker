import tempfile
import os
import streamlit as st
import yt_dlp
from mutagen import File as MutagenFile

from services.auth import guard

st.set_page_config(page_title="Audio Downloader", layout="wide", page_icon="🎵")
guard()

def download_audio(url: str, doc_type: str = "WEBM"):
    ext = "mp3" if doc_type.upper() == "MP3" else "webm"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, f"temp.{ext}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': []  # Skip conversion
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                st.error("Download failed or file is empty.")
                return None, None

            audio = MutagenFile(output_path) if ext == "webm" else None
            audio_info = audio.info if audio else None

            metadata = {
                "Bitrate (kbps)": round(audio_info.bitrate / 1000, 2) if hasattr(audio_info, 'bitrate') else 'N/A',
                "Sample Rate": audio_info.sample_rate if hasattr(audio_info, 'sample_rate') else 'N/A',
                "Channels": audio_info.channels if hasattr(audio_info, 'channels') else 'N/A',
                "Length (sec)": round(audio_info.length, 2) if hasattr(audio_info, 'length') else 'N/A',
                "Codec": type(audio_info).__name__ if audio_info else 'Unknown',
            }

            with open(output_path, 'rb') as f:
                file_data = f.read()

            title = info.get("title", "audio")
            filename = f"{title}.{ext}"

            return file_data, filename, metadata

        except Exception as e:
            st.error(f"Failed to download audio: {str(e)}")
            return None, None, None


st.title("🎵 Audio Downloader")

with st.form("yt_form"):
    url = st.text_input("Enter YouTube URL")
    doc_type = st.selectbox("Audio Format", ["WEBM", "MP3"])
    submitted = st.form_submit_button("Download")

if submitted and url:
    file_data, filename, metadata = download_audio(url, doc_type)

    if file_data:
        st.success("Download successful!")
        st.download_button(label=f"⬇️ Download {filename}",
                            data=file_data,
                            file_name=filename,
                            mime=f"audio/{filename.split('.')[-1]}")

        st.subheader("🔍 Audio Metadata")
        for key, value in metadata.items():
            st.write(f"**{key}:** {value}")