"""Modern Hero-Style Single Video Downloader Tab matching modern web UI."""

import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional
from PIL import Image, ImageTk
import requests

from ..core.downloader import SafeDownloader
from ..core.extractor import MediaExtractor, MediaFormat, VideoMetadata
from ..core.security import SecurityValidationError, sanitize_filename
from .theme import Theme


class SingleVideoTab(ttk.Frame):
    """Sleek hero-style YouTube downloader tab matching modern web layout."""

    def __init__(self, parent: ttk.Notebook):
        super().__init__(parent, style="TFrame")
        self.parent = parent
        self.metadata: Optional[VideoMetadata] = None
        self.downloader: Optional[SafeDownloader] = None
        self.thumbnail_img: Optional[ImageTk.PhotoImage] = None

        self.save_dir = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        self.status_msg = tk.StringVar(value="")
        self.speed_msg = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        # -------------------------------------------------------------
        # 1. HERO HEADER SECTION (Matching Reference Screenshot 1)
        # -------------------------------------------------------------
        hero_frame = tk.Frame(container, bg=Theme.BG_DARK)
        hero_frame.pack(fill="x", pady=(10, 16))

        # Pill Badge
        badge_frame = tk.Frame(hero_frame, bg=Theme.BG_DARK)
        badge_frame.pack(anchor="center", pady=(0, 6))

        pill = tk.Label(
            badge_frame,
            text="• Pro Tool",
            bg=Theme.PURPLE_BADGE_BG,
            fg=Theme.TEXT_PURPLE,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=3,
        )
        pill.pack()

        # Headline
        tk.Label(
            hero_frame,
            text="YouTube Video Downloader",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_HERO,
        ).pack(anchor="center", pady=(0, 4))

        # Subtitle
        tk.Label(
            hero_frame,
            text="Download any YouTube video in 1080p, 720p, 480p, or MP3. Fast, instant, safe.",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY,
        ).pack(anchor="center")

        # -------------------------------------------------------------
        # 2. LARGE SEARCH / URL BAR (Matching Reference Screenshot 1)
        # -------------------------------------------------------------
        search_card = tk.Frame(
            container,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=6,
            pady=6,
        )
        search_card.pack(fill="x", pady=(0, 16))

        # Icon Label
        tk.Label(
            search_card,
            text="🔗",
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(10, 6))

        # URL Entry Field
        self.url_entry = tk.Entry(
            search_card,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            relief="flat",
            font=("Segoe UI", 11),
        )
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self.on_fetch_clicked())

        # Paste Quick Button
        self.paste_btn = tk.Button(
            search_card,
            text="Paste",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_SECONDARY,
            activebackground=Theme.BG_HOVER,
            activeforeground=Theme.TEXT_PRIMARY,
            relief="flat",
            font=Theme.FONT_BUTTON,
            command=self._paste_clipboard,
            cursor="hand2",
            padx=12,
            pady=6,
        )
        self.paste_btn.pack(side="left", padx=(0, 8))

        # Big Download / Inspect Action Button
        self.fetch_btn = tk.Button(
            search_card,
            text="Download Now",
            bg=Theme.RED,
            fg="#ffffff",
            activebackground=Theme.RED_DARK,
            activeforeground="#ffffff",
            font=Theme.FONT_BUTTON_LARGE,
            relief="flat",
            command=self.on_fetch_clicked,
            cursor="hand2",
            padx=20,
            pady=8,
        )
        self.fetch_btn.pack(side="right")

        # -------------------------------------------------------------
        # 3. DESTINATION FOLDER BAR (Subtle & Clean)
        # -------------------------------------------------------------
        dest_bar = tk.Frame(container, bg=Theme.BG_DARK)
        dest_bar.pack(fill="x", pady=(0, 12))

        tk.Label(
            dest_bar,
            text="📁 Save Location:",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
        ).pack(side="left", padx=(4, 6))

        self.folder_label = tk.Label(
            dest_bar,
            textvariable=self.save_dir,
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        self.folder_label.pack(side="left", fill="x", expand=True)

        tk.Button(
            dest_bar,
            text="Change Folder",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_PURPLE,
            activebackground=Theme.BG_DARK,
            activeforeground=Theme.TEXT_PRIMARY,
            relief="flat",
            font=Theme.FONT_SMALL,
            command=self._browse_folder,
            cursor="hand2",
        ).pack(side="right")

        # -------------------------------------------------------------
        # 4. RESULT CARD (Matching Reference Screenshot 2)
        # -------------------------------------------------------------
        self.result_card = tk.Frame(
            container,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        # Hidden initially until URL is fetched
        self.result_card.pack_forget()

        # Top Section: Thumbnail + Info
        top_info = tk.Frame(self.result_card, bg=Theme.BG_CARD)
        top_info.pack(fill="x", pady=(0, 12))

        self.thumb_label = tk.Label(
            top_info,
            text="🖼️ Preview",
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            width=20,
            height=6,
            relief="flat",
        )
        self.thumb_label.pack(side="left", padx=(0, 16))

        meta_col = tk.Frame(top_info, bg=Theme.BG_CARD)
        meta_col.pack(side="left", fill="both", expand=True)

        self.title_label = tk.Label(
            meta_col,
            text="Video Title",
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_TITLE,
            anchor="w",
            justify="left",
            wraplength=540,
        )
        self.title_label.pack(anchor="w", pady=(0, 4))

        self.meta_subtext = tk.Label(
            meta_col,
            text="Creator • Duration",
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED,
            font=Theme.FONT_BODY,
            anchor="w",
        )
        self.meta_subtext.pack(anchor="w", pady=(0, 8))

        # Progress bar container inside Result Card
        self.progress_container = tk.Frame(meta_col, bg=Theme.BG_CARD)
        self.progress_container.pack(fill="x", pady=(4, 0))

        self.progress = ttk.Progressbar(
            self.progress_container,
            style="Horizontal.TProgressbar",
            mode="determinate",
        )
        self.progress.pack(fill="x", pady=(0, 4))

        prog_status_row = tk.Frame(self.progress_container, bg=Theme.BG_CARD)
        prog_status_row.pack(fill="x")

        self.status_lbl = tk.Label(
            prog_status_row,
            textvariable=self.status_msg,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_GREEN,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        self.status_lbl.pack(side="left")

        self.speed_lbl = tk.Label(
            prog_status_row,
            textvariable=self.speed_msg,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="e",
        )
        self.speed_lbl.pack(side="right")

        # Divider line
        tk.Frame(self.result_card, bg=Theme.BORDER, height=1).pack(fill="x", pady=(8, 12))

        # Bottom Section: Format Rows container
        self.formats_container = tk.Frame(self.result_card, bg=Theme.BG_CARD)
        self.formats_container.pack(fill="x")

    def _paste_clipboard(self):
        try:
            clip = self.clipboard_get().strip()
            if clip:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clip)
                self.on_fetch_clicked()
        except Exception:
            pass

    def _browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.save_dir.get())
        if chosen:
            self.save_dir.set(chosen)

    def on_fetch_clicked(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please paste a YouTube URL to download.")
            return

        self.fetch_btn.config(state="disabled", text="Loading...", bg=Theme.RED_DARK)
        self.status_msg.set("Verifying link & fetching available formats...")
        self.speed_msg.set("")
        self.progress["value"] = 0

        threading.Thread(target=self._worker_fetch, args=(url,), daemon=True).start()

    def _worker_fetch(self, url: str):
        try:
            meta = MediaExtractor.fetch_metadata(url)
            self.after(0, self._render_results, meta)
        except SecurityValidationError as sve:
            self.after(0, self._on_fetch_error, f"Security Block: {sve}")
        except Exception as err:
            self.after(0, self._on_fetch_error, f"Error: {err}")

    def _render_results(self, meta: VideoMetadata):
        self.metadata = meta
        self.fetch_btn.config(state="normal", text="Download Now", bg=Theme.RED)
        self.status_msg.set("Select your preferred quality below:")

        # Show result card
        self.result_card.pack(fill="x", pady=(0, 10))

        # Title & Meta info
        display_title = meta.title if len(meta.title) <= 70 else meta.title[:67] + "..."
        self.title_label.config(text=display_title)
        self.meta_subtext.config(
            text=f"📺 {meta.uploader}   •   ⏱️ {meta.duration_display}   •   👁️ {meta.view_count:,} views"
        )

        # Clear old format rows
        for child in self.formats_container.winfo_children():
            child.destroy()

        # Build clean format rows (Matching Screenshot 2)
        all_formats: List[MediaFormat] = meta.video_formats + meta.audio_formats

        for fmt in all_formats:
            row = tk.Frame(
                self.formats_container,
                bg=Theme.BG_CARD_ALT,
                highlightbackground=Theme.BORDER,
                highlightthickness=1,
                padx=12,
                pady=8,
            )
            row.pack(fill="x", pady=4)

            # Format label & info left
            label_col = tk.Frame(row, bg=Theme.BG_CARD_ALT)
            label_col.pack(side="left", fill="x", expand=True)

            tk.Label(
                label_col,
                text=fmt.label,
                bg=Theme.BG_CARD_ALT,
                fg=Theme.TEXT_PRIMARY,
                font=Theme.FONT_SUBTITLE,
                anchor="w",
            ).pack(anchor="w")

            # Download button right
            btn_bg = Theme.GREEN if fmt.is_audio_only else Theme.PURPLE
            btn_hover = Theme.GREEN_HOVER if fmt.is_audio_only else Theme.PURPLE_HOVER
            btn_text = "⬇️ Download MP3" if fmt.is_audio_only else f"⬇️ Download {fmt.resolution}"

            dl_btn = tk.Button(
                row,
                text=btn_text,
                bg=btn_bg,
                fg="#ffffff",
                activebackground=btn_hover,
                activeforeground="#ffffff",
                font=Theme.FONT_BUTTON,
                relief="flat",
                cursor="hand2",
                command=lambda f=fmt: self.trigger_download(f),
                padx=14,
                pady=6,
            )
            dl_btn.pack(side="right")

        # Fetch Thumbnail in background
        if meta.thumbnail_url:
            threading.Thread(target=self._load_thumbnail, args=(meta.thumbnail_url,), daemon=True).start()

    def _load_thumbnail(self, thumb_url: str):
        try:
            resp = requests.get(thumb_url, timeout=8)
            if resp.status_code == 200:
                img_data = Image.open(io.BytesIO(resp.content))
                img_data.thumbnail((160, 95), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_data)
                self.after(0, self._set_thumbnail_image, photo)
        except Exception:
            pass

    def _set_thumbnail_image(self, photo: ImageTk.PhotoImage):
        self.thumbnail_img = photo
        self.thumb_label.config(image=self.thumbnail_img, text="", width=160, height=95)

    def _on_fetch_error(self, err_text: str):
        self.fetch_btn.config(state="normal", text="Download Now", bg=Theme.RED)
        messagebox.showerror("Download Error", err_text)

    def trigger_download(self, selected_format: MediaFormat):
        url = self.url_entry.get().strip()
        save_folder = self.save_dir.get()

        self.status_msg.set(f"Starting download ({selected_format.resolution})...")
        self.speed_msg.set("")
        self.progress["value"] = 0

        self.downloader = SafeDownloader(
            progress_callback=lambda p: self.after(0, self._on_download_progress, p),
            status_callback=lambda s: self.after(0, self._on_download_status, s),
        )

        threading.Thread(
            target=self._worker_download,
            args=(url, selected_format, save_folder),
            daemon=True,
        ).start()

    def _worker_download(self, url: str, fmt: MediaFormat, save_folder: str):
        try:
            output_dir = self.downloader.download(
                raw_url=url,
                media_format=fmt,
                save_dir=save_folder,
            )
            self.after(0, self._on_download_success, output_dir)
        except Exception as e:
            self.after(0, self._on_download_error, str(e))

    def _on_download_progress(self, p: dict):
        percent = p.get("percent", 0.0)
        self.progress["value"] = percent
        speed = p.get("speed_str", "")
        eta = p.get("eta_str", "")
        self.status_msg.set(f"Downloading: {percent:.1f}%")
        self.speed_msg.set(f"Speed: {speed}  •  ETA: {eta}")

    def _on_download_status(self, msg: str):
        self.status_msg.set(msg)

    def _on_download_success(self, out_dir: str):
        self.progress["value"] = 100
        self.status_msg.set("✔ Download Completed Successfully!")
        self.speed_msg.set("")
        messagebox.showinfo("Success", f"File saved securely to:\n{out_dir}")

    def _on_download_error(self, err_msg: str):
        self.status_msg.set("Download failed.")
        messagebox.showerror("Download Error", f"Operation failed:\n{err_msg}")
