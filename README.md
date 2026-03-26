https://automated-youtube-mixtape-creation.streamlit.app/


# 🎧 Automated YouTube Mixtape Creation

### Full-Stack Audio → Video Automation System

A production-style, modular application that automates the creation of YouTube-ready mixtapes from multiple audio tracks.

Built with:

* FastAPI – Backend API
* Streamlit – Interactive Frontend
* MoviePy – Video Processing Engine
* Uvicorn – ASGI Server

---

# 🚀 Overview

This project transforms a simple audio workflow into a complete full-stack automation system capable of:

✔ Uploading multiple audio tracks
✔ Creating smooth DJ-style fade transitions
✔ Generating timestamped YouTube descriptions
✔ Converting static image + audio → MP4 video
✔ Managing background processing jobs
✔ Running with one-tap locally

This is not just a script — it is a deployable full-stack system.

---

# 🧩 System Architecture

```
Streamlit (Frontend UI)
        ↓
FastAPI (REST API Layer)
        ↓
Audio Processing (Transitions + Merge)
        ↓
MoviePy (Image + Audio → MP4)
        ↓
Final Downloadable Assets
```

---
<img width="600" height="776" alt="image" src="https://github.com/user-attachments/assets/897cb6a4-fb1c-49a3-949c-96beed100d2f" />


---

# 🎶 Core Features

## 1️⃣ Mixtape Generator

* Concatenates multiple tracks
* Applies fade-in / fade-out transitions
* Preserves audio quality
* Outputs: `mixtape.mp3`

---

## 2️⃣ YouTube Description Generator

* Reads track durations
* Automatically calculates timestamps
* Generates formatted YouTube-ready description

Example:

```
00:00 - Intro
03:45 - Track 1
07:32 - Track 2
```

---

## 3️⃣ Video Renderer

Powered by MoviePy:

* Combines static background image + audio
* Generates high-quality MP4
* Optimized for long audio files

Output:

```
mixtape_video.mp4
```

---

## 4️⃣ Streamlit Frontend

The UI allows users to:

* Upload audio files
* Generate mixtape
* Create YouTube description
* Render video
* Download final assets

Access locally:

```
http://localhost:8501
```

---

## 5️⃣ FastAPI Backend

REST endpoints:

| Endpoint                 | Method | Description          |
| ------------------------ | ------ | -------------------- |
| `/upload-track/`         | POST   | Upload audio file    |
| `/create-mixtape/`       | POST   | Start background job |
| `/job/{job_id}`          | GET    | Check job status     |
| `/generate-description/` | POST   | Generate timestamps  |
| `/make-video/`           | POST   | Create MP4           |
| `/download/`             | GET    | Download outputs     |

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Shivanshvyas1729/Automated-YouTube-Mixtape-Creation.git
cd Automated-YouTube-Mixtape-Creation
```

---

## 2️⃣ Create Environment

```bash
conda create -n song python=3.10
conda activate song
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Optional (faster installs):

```bash
pip install uv
uv pip install -r requirements.txt
```

---

# ▶️ Running the Application

## Option 1 — Manual Start

### Start Backend

```bash
uvicorn app.main:app --reload
```

### Start Frontend (new terminal)

```bash
streamlit run frontend/streamlit_app.py
```

---

## Option 2 — One-Click Run (Windows)

Inside `youtube_mixtape`:

```
run_project.bat
```

This launches both:

* Backend (Port 8000)
* Frontend (Port 8501)

---



# 🧠 Technical Highlights

✔ RESTful API architecture
✔ Background job processing
✔ Modular service separation
✔ Media processing pipeline
✔ Clean scalable folder structure
✔ Deployment-ready configuration



---

# 👨‍💻 Author

## Shivansh Vyas

Machine Learning & Backend Systems Enthusiast
Building scalable automation systems & AI-powered applications.

GitHub:
[https://github.com/Shivanshvyas1729](https://github.com/Shivanshvyas1729)

---


