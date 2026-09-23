"""Main Application Window Controller with enlarged modern canvas."""

import tkinter as tk
from tkinter import ttk

from ..core.ffmpeg_handler import is_ffmpeg_available
from .tab_batch import BatchVideoTab
from .tab_single import SingleVideoTab
from .theme import Theme, apply_modern_theme


class MainWindow:
    """Top-level modern window controller."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YouTube Video & Audio Downloader (Pro Edition)")
        
        # Generous modern screen size
        width = 880
        height = 760
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(820, 680)

        self._center_window(width, height)
        self.style = apply_modern_theme(self.root)

        self._build_header()
        self._build_notebook()
        self._build_footer()

    def _center_window(self, width: int, height: int):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=Theme.BG_DARK)
        header_frame.pack(fill="x", padx=24, pady=(12, 4))

        # Brand / Logo Left
        brand_box = tk.Frame(header_frame, bg=Theme.BG_DARK)
        brand_box.pack(side="left")

        tk.Label(
            brand_box,
            text="🎬 Safe Downloader Pro",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_TITLE,
        ).pack(anchor="w")

        # Badges Right
        badge_box = tk.Frame(header_frame, bg=Theme.BG_DARK)
        badge_box.pack(side="right")

        # Zero-Trust Security Pill
        sec_badge = tk.Label(
            badge_box,
            text="🛡️ ZERO-TRUST PROTECTED",
            bg=Theme.GREEN_DARK,
            fg=Theme.TEXT_GREEN,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=4,
        )
        sec_badge.pack(side="right", padx=(8, 0))

        # FFmpeg Status Pill
        ffmpeg_ok = is_ffmpeg_available()
        ffmpeg_bg = Theme.PURPLE_DARK if ffmpeg_ok else Theme.YELLOW_DARK
        ffmpeg_fg = Theme.TEXT_PURPLE if ffmpeg_ok else Theme.TEXT_YELLOW
        ffmpeg_text = "⚡ FFMPEG READY" if ffmpeg_ok else "⚠️ FFMPEG MISSING"

        ffmpeg_badge = tk.Label(
            badge_box,
            text=ffmpeg_text,
            bg=ffmpeg_bg,
            fg=ffmpeg_fg,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=4,
        )
        ffmpeg_badge.pack(side="right")

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(4, 6))

        self.single_tab = SingleVideoTab(self.notebook)
        self.batch_tab = BatchVideoTab(self.notebook)

        self.notebook.add(self.single_tab, text="  Single Video Mode  ")
        self.notebook.add(self.batch_tab, text="  Batch Queue Mode  ")

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=Theme.BG_CARD_ALT, height=28)
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="Encrypted Safe Core Engine • 1080p, 720p, 480p, MP3 Audio",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
        ).pack(side="left", padx=16, pady=4)

        tk.Label(
            footer,
            text="v2.5.0",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
        ).pack(side="right", padx=16, pady=4)
