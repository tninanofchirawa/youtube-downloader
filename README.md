# 🎬 Safe Media Downloader (Pro Edition)

A high-performance, secure, and modern desktop application for downloading YouTube videos and extracting ultra-high-definition audio (4K UHD, 2K, 1080p60, 720p, MP3 320kbps, M4A, and WAV).

---

## 🛡️ Zero-Tolerance Security Architecture

This application is built from the ground up with defensive security best practices to protect your machine and make it 100% safe to share with friends and family without risk:

1. **SSRF & Loopback Probing Immunity**:
   - Whitelists only genuine YouTube domains (`youtube.com`, `m.youtube.com`, `music.youtube.com`, `youtu.be`).
   - Blocks private IP ranges (`127.0.0.1`, `localhost`, `10.x.x.x`, `192.168.x.x`, `169.254.x.x`, `::1`).
   - Blocks arbitrary protocol schemes (`file://`, `ftp://`, `gopher://`, `data:`, `javascript:`).
2. **Zero-Trust Filename Sanitization & Path Traversal Defense**:
   - Strips directory traversal sequences (`..`, `/`, `\`), null bytes (`\0`), and illegal Windows characters (`< > : " / \ | ? *`).
   - Immunizes against Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`).
   - Validates destination directories using canonical path resolution (`os.path.realpath`) to prevent writes to system directories (`Windows`, `System32`, `Program Files`).
3. **No Shell Invocations**:
   - Executes all operations directly through sandboxed Python APIs without passing unsanitized commands to `os.system` or shell interpreters.
4. **Thread-Safe UI Operations**:
   - All network and processing operations run asynchronously in background worker threads and dispatch updates safely to the GUI event loop.

---

## ✨ Key Features

- **📺 Video Formats**: 4K UHD (2160p), 1440p (2K), 1080p 60fps, 1080p, 720p 60fps, 720p, 480p, 360p (with automatic H.264/AVC compatibility merging into MP4).
- **🎵 Audio Extraction**: Ultra Quality MP3 (320 kbps CBR), High Quality (192 kbps), Standard (128 kbps), Original M4A/AAC (No Transcoding), and Lossless WAV PCM.
- **🖼️ Video Metadata Preview**: Live thumbnail preview, creator channel name, video duration, and total view count.
- **📦 Batch / Group Mode**: Download entire lists of video links concurrently with unified quality presets.
- **⚡ Real-Time Progress**: Live download speed in MB/s, estimated completion time (ETA), and animated progress indicators.
- **🎨 Modern Dark Interface**: Clean, minimalist card design built with dark ttk styling.

---

## 🚀 How to Use (For Friends & Family)

### 1-Click Launch on Windows:
Simply double-click **`Start_Downloader.bat`** to start the application!

### Or Launch via Terminal:
```bash
# 1. Install dependencies (only required once)
pip install -r requirements.txt

# 2. Start the downloader
python run.py
```

### How to Download Videos & Audio:
1. **Single Video Mode**:
   - Copy any YouTube link and click **📋 Paste** (or press Enter).
   - Click **⚡ Inspect & Fetch** to load available resolutions and audio bitrates.
   - Choose your preferred quality (e.g. `1080p60 (H.264, mp4)` or `🎵 MP3 320 kbps`).
   - Choose your save folder and click **⬇️ Download Now**.
2. **Batch / Group Mode**:
   - Paste multiple YouTube links (one per line) into the text box.
   - Select a batch quality preset (e.g. `⭐ Best Available Quality (MP4)` or `🎵 MP3 Audio 320 kbps`).
   - Click **🚀 Download Entire Batch Queue**.

---

## 🧪 Comprehensive 43-Test Verification Suite

The codebase includes an extensive suite of **43 automated tests** covering heavy stress testing, security bug vectors, and edge cases:
- **10 Heavy Stress Tests** (50 concurrent threads, 2,000 URL batch stress, petabyte sizes, 10,000 progress events).
- **10 Heavy Security Bug Tests** (IPv6 SSRF bypasses, DNS rebinding, deep directory traversal, Windows reserved names, null-bytes, sandbox integrity).
- **10 Minute Bug & Edge-Case Tests** (Duration extremes, byte boundaries, illegal filenames, trailing spaces, cancellation safety).
- **13 Core Security & Extractor Tests**.

To run all tests:
```bash
python -m unittest discover -s tests -v
```

---

## 📦 Pushing to Your GitHub Account

Follow these quick steps to push this clean, secured repository to your GitHub profile:

### Step 1: Create a new repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Name your repository (e.g. `youtube-downloader` or `safe-media-downloader`).
3. Set visibility to **Public** or **Private**.
4. Leave "Add a README file" **unchecked** (we already have a complete one).
5. Click **Create repository**.

### Step 2: Push your local code from your terminal
Open your terminal in this folder and run:

```bash
# 1. Stage all clean project files (.gitignore ensures large binaries & cache are ignored)
git add .

# 2. Create your initial commit
git commit -m "Initial commit: Safe Media Downloader v2.0 (Hardened & Modular)"

# 3. Set branch name to main
git branch -M main

# 4. Link your remote GitHub repository (replace with your actual GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# 5. Push your code to GitHub
git push -u origin main
```

---

## 📁 Clean Project Layout

```
Youtube Downloader/
├── app/
│   ├── core/                    # Core engine & security
│   │   ├── downloader.py        # Safe download execution & progress hooks
│   │   ├── extractor.py         # Deep format & metadata inspection
│   │   ├── ffmpeg_handler.py    # Auto-detection for bundled or system FFmpeg
│   │   └── security.py          # Strict URL validation & filename sanitizer
│   ├── ui/                      # Modern GUI presentation layer
│   │   ├── main_window.py       # Main Application Window & Navigation
│   │   ├── theme.py             # Modern Dark palette & TTK styling
│   │   ├── tab_single.py        # Single video tab (Specs, Thumbnail, Progress)
│   │   └── tab_batch.py         # Batch video tab (Queue list, Batch presets)
│   └── utils/
│       └── helpers.py           # Byte formatting, duration & string helpers
├── tests/                       # 43 automated unit & stress tests
│   ├── test_stress.py           # Concurrency, massive batch, and memory stress tests
│   ├── test_security_heavy.py   # SSRF, DNS rebinding, traversal & sandbox tests
│   ├── test_edge_cases.py       # Minute bugs & format boundary tests
│   ├── test_security.py         # Core security validation tests
│   └── test_extractor.py        # Extractor parser tests
├── .gitignore                   # Safe Git ignore rules (blocks huge binaries & cache)
├── Start_Downloader.bat         # 1-Click launcher for Windows
├── requirements.txt             # Python dependencies
├── run.py                       # Safe application entry point
├── LICENSE                      # MIT Open Source License
└── README.md                    # Documentation & User Guide
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
