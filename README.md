# 🎬 Downloader 1.0

A fast, modern, and secure desktop application for downloading YouTube videos and extracting high-definition audio (1080p, 720p, 480p, 360p, MP3 320kbps, and M4A).

---

## ✨ Features

- **⚡ Modern Hero UI**: Large search bar with 1-click clipboard paste and instant format discovery.
- **🎬 Streamlined Formats**:
  - 🎬 **1080p Full HD (MP4)**
  - 📺 **720p HD (MP4)**
  - 📱 **480p SD (MP4)**
  - 📱 **360p / 240p (MP4)**
  - 🎵 **MP3 Audio — Ultra Quality (320 kbps)**
  - 🎧 **M4A / AAC Audio — Fastest Direct Stream**
- **📦 Batch Queue Mode**: Download multiple videos concurrently with batch quality presets.
- **🛡️ Encrypted Zero-Trust Core**: Hardened security layer protecting against SSRF, directory traversal, and host spoofing.
- **⚡ Live Progress Tracker**: Real-time speed indicator (MB/s), ETA countdown, and smooth animated progress bar.

---

## 🚀 How to Run

### 1-Click Launch (Windows):
Double-click **`Start_Downloader.bat`** to start the application immediately!

### Or Launch via Terminal:
```bash
# 1. Install dependencies (only required once)
pip install -r requirements.txt

# 2. Run the application
python run.py
```

---

## 🧪 Comprehensive 43-Test Verification Suite

The application includes an extensive suite of **43 automated tests** verified across:
- **10 Heavy Stress Tests** (50 concurrent threads, 2,000 URL batch processing, petabyte bounds, 10,000 progress events).
- **10 Heavy Security Bug Tests** (IPv6 SSRF bypasses, DNS rebinding, deep directory traversal, Windows reserved DOS names, sandbox isolation).
- **10 Minute Bug & Edge-Case Tests** (Numerical extremes, byte boundary limits, illegal filename scrub, cancellation safety).
- **13 Core Extractor & Security Tests**.

To run all tests locally:
```bash
python -m unittest discover -s tests -v
```

---

## 📁 Clean Project Layout

```
Youtube Downloader/
├── app/
│   ├── core/                    # Sandboxed engine, downloader, and encrypted security layer
│   ├── ui/                      # Modern Hero UI, themes, and tabs
│   └── utils/                   # Byte formatting & duration helpers
├── tests/                       # 43 automated unit, security, and stress tests
├── .gitignore                   # Excludes binaries, cache, and private developer files
├── Start_Downloader.bat         # 1-Click launcher for Windows
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── USER_MANUAL.md               # User manual and quickstart guide
├── LICENSE                      # MIT Open Source License
└── README.md                    # Documentation
```

---

## ⚖️ Legal Disclaimer & Limitation of Liability

> **DISCLAIMER**: This software is provided "as-is" for personal, educational, and fair-use archiving purposes only.
>
> 1. **No Liability**: The original author and developer accept **NO LIABILITY**, legal accountability, or responsibility for any damages, data loss, misuse, copyright violations, or third-party platform terms of service violations arising from the use or distribution of this software.
> 2. **User Responsibility**: Users are solely responsible for ensuring that their downloads comply with all applicable local laws, copyright regulations, and platform terms.
> 3. **Modifications & Tampering**: If any person or third party edits, modifies, alters, decompiles, or redistributes this source code, they assume **100% of all risks and liabilities**. The original developer disclaims all warranties, express or implied.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
