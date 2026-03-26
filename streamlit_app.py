import os
import random
import traceback
import time
from pathlib import Path

import streamlit as st
from pydub import AudioSegment
from moviepy.editor import ImageClip, AudioFileClip

# ===================== PATHS =====================
APP_DIR = Path(__file__).resolve().parent

UPLOAD_ROOT = APP_DIR / "uploaded"
IMAGES_DIR = APP_DIR / "images"
OUTPUT_DIR = APP_DIR / "output"

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO_EXT = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")


# ===================== AUTO CLEANUP =====================
def cleanup_old_files(folder_path, max_age_seconds=600):
    now = time.time()

    for file in Path(folder_path).glob("*"):
        if file.is_file():
            file_age = now - file.stat().st_mtime

            if file_age > max_age_seconds:
                try:
                    os.remove(file)
                    print(f"Deleted old file: {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")


# ✅ Run cleanup on every app start/rerun
cleanup_old_files(OUTPUT_DIR, 600)
cleanup_old_files(UPLOAD_ROOT, 600)
cleanup_old_files(IMAGES_DIR, 600)


# ===================== HELPERS =====================
def save_uploaded_audio_files(uploaded_files, job_prefix: str):
    job_dir = UPLOAD_ROOT / job_prefix
    job_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for f in uploaded_files:
        dest = job_dir / f.name
        with open(dest, "wb") as out:
            out.write(f.getbuffer())
        saved_files.append(dest)

    return saved_files


def get_audio_files(job_prefix: str):
    job_dir = UPLOAD_ROOT / job_prefix
    if not job_dir.exists():
        return []

    files = [
        job_dir / f
        for f in os.listdir(job_dir)
        if f.lower().endswith(ALLOWED_AUDIO_EXT)
    ]
    return sorted(files)


def smooth_fade_mixtape_from_files(file_paths, output_filename="mixtape.mp3", transition_ms=6000):
    if not file_paths:
        raise ValueError("No audio files found")

    file_paths = list(file_paths)
    random.shuffle(file_paths)

    mixtape = None
    for filepath in file_paths:
        song = AudioSegment.from_file(filepath)
        song = song.set_channels(2).set_frame_rate(44100)

        if mixtape is None:
            mixtape = song
        else:
            overlap = min(transition_ms, len(song), len(mixtape))
            outgoing = mixtape[-overlap:].fade_out(overlap).low_pass_filter(4000)
            incoming = song[:overlap].fade_in(overlap).low_pass_filter(4000)
            transition = outgoing.overlay(incoming)
            mixtape = mixtape[:-overlap] + transition + song[overlap:]

    out_path = OUTPUT_DIR / output_filename
    mixtape.export(out_path, format="mp3")
    return out_path


def generate_youtube_description_with_timestamps(
    track_paths,
    mixtape_name="Mixtape",
    genre="Mix",
    start_time_sec=0
):
    if not track_paths:
        raise ValueError("No tracks provided")

    description = f"🔥 {mixtape_name} 🔥\n"
    description += f"Genre: {genre}\n\n"
    description += "🎵 Tracklist:\n"

    current_time = start_time_sec
    for path in track_paths:
        audio = AudioSegment.from_file(path)
        duration_sec = len(audio) // 1000
        minutes = current_time // 60
        seconds = current_time % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        name = Path(path).stem
        description += f"{timestamp} - {name}\n"
        current_time += duration_sec

    description += "\n🎧 Follow for more mixes!\n"
    description += "\n#Mixtape #DJMix #HouseMusic #MusicMix"
    return description


def make_video_from_audio(image_path, audio_path, output_filename="mixtape_vid.mp4"):
    image_path = Path(image_path)
    audio_path = Path(audio_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    output_path = OUTPUT_DIR / output_filename

    audio = AudioFileClip(str(audio_path))
    video = ImageClip(str(image_path)).set_duration(audio.duration).set_audio(audio)

    video.write_videofile(
        str(output_path),
        fps=1,
        codec="libx264",
        audio_codec="aac"
    )

    video.close()
    audio.close()

    return output_path


# ===================== UI =====================
st.set_page_config(page_title="YouTube Mixtape Automation", layout="centered")
st.title("YouTube Mixtape Automation")

job_prefix = st.text_input("Job prefix (folder name)", value="job1")

# ---------------- UPLOAD AUDIO ----------------
st.header("1. Upload audio tracks")
uploaded_audio = st.file_uploader(
    "Choose audio files",
    accept_multiple_files=True,
    type=["mp3", "wav", "m4a", "aac", "ogg", "flac"]
)

if st.button("Upload tracks"):
    try:
        if not uploaded_audio:
            st.error("Please choose at least one audio file.")
        else:
            saved = save_uploaded_audio_files(uploaded_audio, job_prefix)
            st.success(f"Uploaded {len(saved)} file(s) successfully.")
            for f in saved:
                st.write(f"Saved: {f.name}")
    except Exception as e:
        st.error(f"Upload failed: {e}")
        st.code(traceback.format_exc())


# ---------------- CREATE MIXTAPE ----------------
st.header("2. Create mixtape")
transition_ms = st.number_input("Transition ms", min_value=0, value=6000, step=500)
output_name = st.text_input("Output MP3 filename", value="mixtape.mp3")

if st.button("Create mixtape"):
    try:
        files = get_audio_files(job_prefix)

        if not files:
            st.error("No audio files found for this job.")
        else:
            with st.spinner("Creating mixtape..."):
                mp3_path = smooth_fade_mixtape_from_files(
                    files,
                    output_filename=output_name,
                    transition_ms=transition_ms
                )

            st.success("Mixtape created successfully!")
            st.audio(str(mp3_path))

    except Exception as e:
        st.error(f"Mixtape creation failed: {e}")
        st.code(traceback.format_exc())


# ---------------- MAKE VIDEO ----------------
st.header("3. Make video from mixtape")

image_file = st.file_uploader("Upload background image", type=["jpg", "jpeg", "png"])
audio_file_name = st.text_input("Audio path", value=str(OUTPUT_DIR / "mixtape.mp3"))
video_name = st.text_input("Output video filename", value="mixtape_vid.mp4")

if st.button("Create video"):
    try:
        if not image_file:
            st.error("Please upload a background image first.")
        else:
            image_path = IMAGES_DIR / image_file.name
            with open(image_path, "wb") as f:
                f.write(image_file.getbuffer())

            with st.spinner("Creating video..."):
                video_path = make_video_from_audio(
                    image_path=image_path,
                    audio_path=audio_file_name,
                    output_filename=video_name
                )

            st.success("Video created successfully!")
            st.video(str(video_path))

    except Exception as e:
        st.error(f"Video creation failed: {e}")
        st.code(traceback.format_exc())