import os
import time
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"  # run uvicorn locally

# PROJECT ROOT (one level above frontend/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

st.set_page_config(page_title="YouTube Mixtape Automation", layout="centered")
st.title("YouTube Mixtape Automation")

job_prefix = st.text_input("Job prefix (folder name)", value="job1")

# ---------------- UPLOAD AUDIO ----------------
st.header("Upload audio tracks")
uploaded = st.file_uploader(
    "Choose audio files",
    accept_multiple_files=True,
    type=["mp3", "wav", "m4a", "aac", "ogg", "flac"]
)

if st.button("Upload tracks"):
    if not uploaded:
        st.error("Please choose at least one audio file.")
    else:
        for f in uploaded:
            files = {"file": (f.name, f.getvalue())}
            data = {"job_prefix": job_prefix}

            r = requests.post(f"{API_BASE}/upload-track/", files=files, data=data)
            try:
                st.write(r.json())
            except Exception:
                st.error(f"Upload failed for {f.name}: {r.text}")

# ---------------- CREATE MIXTAPE ----------------
st.header("Create mixtape")
transition_ms = st.number_input("Transition ms", value=6000)
output_name = st.text_input("Output MP3 filename", value="mixtape.mp3")

if st.button("Start mixtape"):
    data = {
        "job_prefix": job_prefix,
        "transition_ms": str(transition_ms),
        "output_name": output_name
    }

    r = requests.post(f"{API_BASE}/create-mixtape/", data=data)

    try:
        resp = r.json()
        st.write(resp)
    except Exception:
        st.error(f"Could not read server response: {r.text}")
        resp = {}

    job_id = resp.get("job_id")
    if job_id:
        st.write("Polling job status...")
        status_box = st.empty()
        final_status = None

        for _ in range(60):
            s = requests.get(f"{API_BASE}/job/{job_id}").json()
            final_status = s
            status_box.json(s)

            if s.get("status") in ("completed", "failed"):
                break

            time.sleep(1)

        if final_status:
            if final_status.get("status") == "completed":
                mp3_path = final_status.get("result")

                if mp3_path and os.path.exists(mp3_path):
                    st.success("Mixtape created successfully!")

                    with open(mp3_path, "rb") as f:
                        st.download_button(
                            label="Download mixtape MP3",
                            data=f,
                            file_name=os.path.basename(mp3_path),
                            mime="audio/mpeg"
                        )
                else:
                    st.error("Mixtape completed but output file was not found.")

            elif final_status.get("status") == "failed":
                st.error(final_status.get("error", "Mixtape job failed"))

# ---------------- GENERATE DESCRIPTION ----------------
st.header("Generate YouTube description")
mixtape_name = st.text_input("Mixtape name", value="Afro House Mix")

if st.button("Generate description"):
    r = requests.post(
        f"{API_BASE}/generate-description/",
        data={
            "job_prefix": job_prefix,
            "mixtape_name": mixtape_name,
            "genre": "Afro House"
        }
    )

    try:
        resp = r.json()
        st.text_area("Description", value=resp.get("description", ""), height=300)
    except Exception:
        st.error(f"Could not generate description: {r.text}")

# ---------------- MAKE VIDEO ----------------
st.header("Make video from mixtape")

image_file = st.file_uploader(
    "Background image",
    type=["jpg", "jpeg", "png"],
    key="video_image_uploader"
)

audio_file_name = st.text_input(
    "Audio path (use output/mixtape.mp3)",
    value="output/mixtape.mp3"
)

video_name = st.text_input(
    "Output video filename",
    value="mixtape_vid.mp4"
)

if st.button("Create video"):
    if not image_file:
        st.error("Please upload an image first.")
    else:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        img_path = os.path.join(IMAGES_DIR, image_file.name)

        with open(img_path, "wb") as f:
            f.write(image_file.getvalue())

        st.success(f"Image saved at: {img_path}")

        r = requests.post(
            f"{API_BASE}/make-video/",
            data={
                "image_path": img_path,
                "audio_path": audio_file_name,
                "output_name": video_name
            }
        )

        try:
            resp = r.json()
            st.write(resp)
        except Exception:
            st.error(f"Could not read server response: {r.text}")
            resp = {}

        job_id = resp.get("job_id")
        if job_id:
            st.write("Polling video job...")
            status_box = st.empty()
            final_status = None

            for _ in range(120):
                s = requests.get(f"{API_BASE}/job/{job_id}").json()
                final_status = s
                status_box.json(s)

                if s.get("status") in ("completed", "failed"):
                    break

                time.sleep(1)

            if final_status:
                if final_status.get("status") == "completed":
                    video_path = final_status.get("result")

                    if video_path and os.path.exists(video_path):
                        st.success("Video created successfully!")

                        with open(video_path, "rb") as f:
                            st.download_button(
                                label="Download video",
                                data=f,
                                file_name=os.path.basename(video_path),
                                mime="video/mp4"
                            )

                        st.video(video_path)
                    else:
                        st.error("Video completed but file was not found.")

                elif final_status.get("status") == "failed":
                    st.error(final_status.get("error", "Video job failed"))