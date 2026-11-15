# Media Toolkit

A lightweight, locally-hosted web application for media processing — no login required, no cloud dependency.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![Vue 3](https://img.shields.io/badge/Vue-3-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Tool | Description |
|---|---|
| **Universal Converter** | Convert images (PNG, JPG, WEBP, GIF, ICO) and videos to different formats |
| **Basic Editor** | Rotate, flip, crop, draw, and add text to images in-browser |
| **Frame Extractor** | Extract video frames at 1 fps and download them as a ZIP archive |
| **Downloader** | Download videos from YouTube, Facebook, TikTok, Instagram, Twitter, and 1000+ sites via yt-dlp |
| **AI Studio** | Remove image backgrounds (AI) and upscale images 2× with Lanczos |
| **Compressor** | Compress images to JPEG quality 40 or videos with H.264 CRF 28 |
| **Audio Extractor** | Extract audio from any video and save it as MP3 |

---

## Requirements

- Python **3.10** or higher
- `ffmpeg` is bundled automatically via [`static-ffmpeg`](https://pypi.org/project/static-ffmpeg/) — no manual install needed

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/media-toolkit.git
cd media-toolkit

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Copy .env.example and set your secret key
cp .env.example .env
# Edit .env and set SECRET_KEY=<your-long-random-string>

# 5. Run the app
python app.py
```

The app will be available at **http://localhost:5000**

---

## Usage

1. Open your browser and go to `http://localhost:5000`
2. Select a tool from the left sidebar
3. Upload a file or paste a video URL
4. Click the action button — the processed file downloads automatically

No login or account required.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-me` | Flask session secret — change this for any non-local deployment |

Set via `.env` file or environment variable:

```bash
export SECRET_KEY=my-super-secret-key   # Linux / macOS
set SECRET_KEY=my-super-secret-key      # Windows CMD
```

---

## Project Structure

```
media-toolkit/
├── app.py               # Flask backend — all processing logic
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Files excluded from version control
├── README.md            # This file
├── run.bat              # Windows launcher
├── run.sh               # Linux / macOS launcher
└── templates/
    └── index.html       # Vue 3 + Vuetify 3 frontend
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | [Flask 3](https://flask.palletsprojects.com/) |
| Frontend | [Vue 3](https://vuejs.org/) + [Vuetify 3](https://vuetifyjs.com/) |
| Video Download | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Background Removal | [rembg](https://github.com/danielgatis/rembg) (ONNX) |
| Image Processing | [Pillow](https://python-pillow.org/) |
| FFmpeg | [static-ffmpeg](https://pypi.org/project/static-ffmpeg/) |
| Cropping UI | [Cropper.js](https://github.com/fengyuanchen/cropperjs) |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Disclaimer

This tool is intended for personal, local use only.  
Please respect platform terms of service when downloading media content.
