import os
import random
import traceback
from pathlib import Path

import streamlit as st
from pydub import AudioSegment
from moviepy.editor import ImageClip, AudioFileClip

# ===================== CONFIG =====================
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent

UPLOAD_ROOT = BASE_DIR / "uploaded"
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO_EXT = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")


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

    description += "\n💽 Download/Listen links:\nYou can find these tracks online.\n\n"
    description += "🎧 Follow for more mixes!\n\n"
    description += "#Mixtape #DJMix #HouseMusic #MusicMix"

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
    video = (
        ImageClip(str(image_path))
        .set_duration(audio.duration)
        .set_audio(audio)
    )

    video.write_videofile(
        str(output_path),
        fps=1
    )

    video.close()
    audio.close()

    return output_path


# ===================== STREAMLIT UI =====================
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
                st.write(f"Saved: {f}")
    except Exception as e:
        st.error(f"Upload failed: {e}")
        st.code(traceback.format_exc())

existing_tracks = get_audio_files(job_prefix)
if existing_tracks:
    st.subheader("Current tracks in this job")
    for track in existing_tracks:
        st.write(track.name)

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

            with open(mp3_path, "rb") as f:
                st.download_button(
                    label="Download mixtape MP3",
                    data=f,
                    file_name=mp3_path.name,
                    mime="audio/mpeg"
                )

            st.session_state["latest_mp3_path"] = str(mp3_path)

    except Exception as e:
        st.error(f"Mixtape creation failed: {e}")
        st.code(traceback.format_exc())

# ---------------- GENERATE DESCRIPTION ----------------
st.header("3. Generate YouTube description")
mixtape_name = st.text_input("Mixtape name", value="Afro House Mix")
genre = st.text_input("Genre", value="Afro House")

if st.button("Generate description"):
    try:
        files = get_audio_files(job_prefix)

        if not files:
            st.error("No tracks found for this job.")
        else:
            description = generate_youtube_description_with_timestamps(
                files,
                mixtape_name=mixtape_name,
                genre=genre
            )

            st.text_area("Generated Description", value=description, height=300)
            st.session_state["latest_description"] = description

    except Exception as e:
        st.error(f"Description generation failed: {e}")
        st.code(traceback.format_exc())

# ---------------- MAKE VIDEO ----------------
st.header("4. Make video from mixtape")

image_file = st.file_uploader(
    "Upload background image",
    type=["jpg", "jpeg", "png"],
    key="video_image_uploader"
)

default_audio_path = st.session_state.get("latest_mp3_path", str(OUTPUT_DIR / "mixtape.mp3"))
audio_file_name = st.text_input("Audio path", value=default_audio_path)
video_name = st.text_input("Output video filename", value="mixtape_vid.mp4")

if st.button("Create video"):
    try:
        if not image_file:
            st.error("Please upload a background image first.")
        else:
            image_path = IMAGES_DIR / image_file.name
            with open(image_path, "wb") as f:
                f.write(image_file.getbuffer())

            st.success(f"Image saved: {image_path}")

            with st.spinner("Creating video... this can take a bit depending on file size"):
                video_path = make_video_from_audio(
                    image_path=image_path,
                    audio_path=audio_file_name,
                    output_filename=video_name
                )

            st.success("Video created successfully!")
            st.video(str(video_path))

            with open(video_path, "rb") as f:
                st.download_button(
                    label="Download video",
                    data=f,
                    file_name=video_path.name,
                    mime="video/mp4"
                )

            st.session_state["latest_video_path"] = str(video_path)

    except Exception as e:
        st.error(f"Video creation failed: {e}")
        st.code(traceback.format_exc())

# ---------------- OUTPUT FILES ----------------
st.header("5. Existing output files")

output_files = sorted(OUTPUT_DIR.glob("*"))
if output_files:
    for file_path in output_files:
        st.write(file_path.name)
else:
    st.info("No output files yet.")