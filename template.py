import os
from pathlib import Path
import logging

# ----------------------------
# Logging configuration
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s]: %(message)s'
)

# ----------------------------
# Project name
# ----------------------------
project_name = "youtube_mixtape"

# ----------------------------
# List of files & folders
# ----------------------------
list_of_files = [
    f"{project_name}/app/__init__.py",
    f"{project_name}/app/main.py",          # FastAPI app
    f"{project_name}/app/audio.py",         # mixtape generator functions
    f"{project_name}/app/video.py",         # ffmpeg wrapper
    f"{project_name}/app/description.py",   # description generator
    f"{project_name}/app/utils.py",         # helpers
    f"{project_name}/app/config.py",        # constants

    f"{project_name}/frontend/streamlit_app.py",

    f"{project_name}/mixtape/.gitkeep",     # example input tracks
    f"{project_name}/images/.gitkeep",      # example bg images
    f"{project_name}/output/.gitkeep",      # generated files

    f"{project_name}/requirements.txt",
    f"{project_name}/README.md",
]

# ----------------------------
# Create directories and files
# ----------------------------
for filepath in list_of_files:
    filepath = Path(filepath)
    filedir = filepath.parent

    if filedir != Path('.'):
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Directory ensured: {filedir}")

    if not filepath.exists():
        filepath.touch()
        logging.info(f"Created file: {filepath.name}")
    else:
        logging.info(f"File already exists: {filepath.name}")
