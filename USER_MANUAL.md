# 📖 Safe Media Downloader — User Manual & Quickstart Guide

Welcome to the **Safe Media Downloader (Pro Edition)**. This guide provides simple, step-by-step instructions so anyone (friends, family, and colleagues) can run and use the application effortlessly and safely.

---

## ⚡ 1-Minute Quick Start (Easiest Method for Windows)

If you are on Windows, you don't even need to open a terminal:

1. **Step 1**: Open the project folder.
2. **Step 2**: Double-click **`Start_Downloader.bat`**.
3. **Step 3**: The app will launch in modern dark mode automatically!

---

## 💻 Standard Installation & Terminal Launch

If you prefer launching via terminal or are running on macOS / Linux:

### 1. Install Requirements (Only needed the first time)
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run.py
```

---

## 🎯 How to Use the Features

### 1. Single Video Mode (Hero Layout)
- **Paste Link**: Paste any YouTube link into the large search bar (or click **Paste**).
- **Download / Inspect**: Click **Download Now**. The app fetches the video thumbnail, creator, duration, and displays clean format options:
  - 🎬 **1080p Full HD (MP4)** $\rightarrow$ Click `⬇️ Download 1080p`
  - 📺 **720p HD (MP4)** $\rightarrow$ Click `⬇️ Download 720p`
  - 📱 **480p SD (MP4)** $\rightarrow$ Click `⬇️ Download 480p`
  - 📱 **360p / 240p (MP4)** $\rightarrow$ Click `⬇️ Download 360p`
  - 🎵 **MP3 Audio (320 kbps)** $\rightarrow$ Click `⬇️ Download MP3`
  - 🎧 **M4A Audio (Fastest)** $\rightarrow$ Click `⬇️ Download M4A`
- **Progress**: A live progress bar inside the card updates in real-time with download speed (MB/s) and ETA countdown.

---

### 2. Batch / Group Queue Mode
- **Paste Multiple Links**: Paste a list of YouTube links into the text box.
- **Select Quality Preset**: Choose 1080p, 720p, 480p, or MP3.
- **Start Batch**: Click **🚀 Download Entire Batch Queue**.

---

## 🛡️ Security & Privacy Assurance

You can run and share this software with complete peace of mind:

- **100% Encrypted Connections**: All downloads connect strictly over secure **HTTPS / TLS 1.3** encryption directly to official YouTube media servers.
- **Zero Local Probing (SSRF Immunity)**: The app blocks access to local IP addresses, private subnets, and local file schemes (`file://`, `127.0.0.1`, `localhost`).
- **Path Traversal Immunity**: Filenames are sanitized against directory traversal attacks (`../`) and Windows system-reserved names (`CON`, `PRN`, `AUX`, `NUL`).
- **Sandboxed Execution**: Runs purely in memory with sandboxed yt-dlp Python APIs (no arbitrary shell command execution).
- **Zero Tracking**: No user data, history, credentials, or cookies are stored or shared.

---

## 🧪 Verifying System Health & Running Tests

To verify that all 43 security and performance tests pass on your machine:
```bash
python -m unittest discover -s tests -v
```
*(All 43 tests should report `OK`)*.
