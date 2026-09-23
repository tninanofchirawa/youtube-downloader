"""Modern Batch Video Downloader Tab matching hero web UI."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from ..core.downloader import SafeDownloader
from ..core.extractor import MediaFormat
from ..core.security import SecurityValidationError, validate_media_url
from .theme import Theme


class BatchVideoTab(ttk.Frame):
    """Sleek batch downloader tab for downloading multiple links in bulk."""

    def __init__(self, parent: ttk.Notebook):
        super().__init__(parent, style="TFrame")
        self.parent = parent
        self.downloader: Optional[SafeDownloader] = None
        self._is_running = False

        self.save_dir = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        self.status_msg = tk.StringVar(value="")
        self.item_status_msg = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        # -------------------------------------------------------------
        # 1. HERO HEADER SECTION
        # -------------------------------------------------------------
        hero_frame = tk.Frame(container, bg=Theme.BG_DARK)
        hero_frame.pack(fill="x", pady=(10, 16))

        badge_frame = tk.Frame(hero_frame, bg=Theme.BG_DARK)
        badge_frame.pack(anchor="center", pady=(0, 6))

        pill = tk.Label(
            badge_frame,
            text="• Bulk Queue Tool",
            bg=Theme.PURPLE_BADGE_BG,
            fg=Theme.TEXT_PURPLE,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=3,
        )
        pill.pack()

        tk.Label(
            hero_frame,
            text="Batch Video & Playlist Downloader",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_HERO,
        ).pack(anchor="center", pady=(0, 4))

        tk.Label(
            hero_frame,
            text="Paste multiple links to download an entire queue in high definition automatically.",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY,
        ).pack(anchor="center")

        # -------------------------------------------------------------
        # 2. BATCH TEXT AREA CARD
        # -------------------------------------------------------------
        text_card = tk.Frame(
            container,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        text_card.pack(fill="x", pady=(0, 14))

        top_bar = tk.Frame(text_card, bg=Theme.BG_CARD)
        top_bar.pack(fill="x", pady=(0, 6))

        tk.Label(
            top_bar,
            text="Paste Video URLs (one link per line):",
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            font=Theme.FONT_SUBTITLE,
        ).pack(side="left")

        btn_box = tk.Frame(top_bar, bg=Theme.BG_CARD)
        btn_box.pack(side="right")

        tk.Button(
            btn_box,
            text="📋 Paste All",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_SECONDARY,
            activebackground=Theme.BG_HOVER,
            activeforeground=Theme.TEXT_PRIMARY,
            relief="flat",
            font=Theme.FONT_SMALL,
            command=self._paste_clipboard,
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_box,
            text="🗑️ Clear",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_SECONDARY,
            activebackground=Theme.BG_HOVER,
            activeforeground=Theme.TEXT_PRIMARY,
            relief="flat",
            font=Theme.FONT_SMALL,
            command=self._clear_text,
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left")

        self.url_text = tk.Text(
            text_card,
            height=5,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            relief="flat",
            highlightbackground=Theme.BORDER,
            highlightcolor=Theme.BORDER_FOCUS,
            highlightthickness=1,
            font=Theme.FONT_MONO,
            wrap="none",
        )
        self.url_text.pack(fill="x", pady=(0, 6))

        # -------------------------------------------------------------
        # 3. PRESETS & DESTINATION
        # -------------------------------------------------------------
        opts_row = tk.Frame(container, bg=Theme.BG_DARK)
        opts_row.pack(fill="x", pady=(0, 14))

        # Preset Quality Dropdown Left
        preset_col = tk.Frame(opts_row, bg=Theme.BG_DARK)
        preset_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Label(
            preset_col,
            text="Quality Preset:",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
        ).pack(anchor="w", pady=(0, 4))

        self.quality_presets = {
            "🎬 1080p Full HD (MP4)": MediaFormat(
                format_id="1080p_batch",
                label="1080p Max (MP4)",
                extension="mp4",
                resolution="1080p",
                format_selector="bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            ),
            "📺 720p HD (MP4)": MediaFormat(
                format_id="720p_batch",
                label="720p Max (MP4)",
                extension="mp4",
                resolution="720p",
                format_selector="bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            ),
            "📱 480p SD (MP4)": MediaFormat(
                format_id="480p_batch",
                label="480p Max (MP4)",
                extension="mp4",
                resolution="480p",
                format_selector="bestvideo[height<=480]+bestaudio/best[height<=480]/best",
            ),
            "🎵 MP3 Audio (320 kbps)": MediaFormat(
                format_id="mp3_320_batch",
                label="MP3 320k",
                extension="mp3",
                resolution="Audio",
                is_audio_only=True,
                format_selector="bestaudio/best",
                audio_bitrate_kbps=320,
                target_codec="mp3",
            ),
        }

        self.preset_combobox = ttk.Combobox(
            preset_col,
            state="readonly",
            values=list(self.quality_presets.keys()),
            font=Theme.FONT_BODY,
        )
        self.preset_combobox.set("🎬 1080p Full HD (MP4)")
        self.preset_combobox.pack(fill="x")

        # Destination Folder Right
        dest_col = tk.Frame(opts_row, bg=Theme.BG_DARK)
        dest_col.pack(side="right", fill="x", expand=True)

        tk.Label(
            dest_col,
            text="Save Destination:",
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_BODY_BOLD,
        ).pack(anchor="w", pady=(0, 4))

        dest_inner = tk.Frame(dest_col, bg=Theme.BG_DARK)
        dest_inner.pack(fill="x")

        self.folder_entry = tk.Entry(
            dest_inner,
            textvariable=self.save_dir,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            relief="flat",
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            state="readonly",
            font=Theme.FONT_BODY,
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 6))

        tk.Button(
            dest_inner,
            text="📁 Browse",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_PRIMARY,
            relief="flat",
            font=Theme.FONT_SMALL,
            command=self._browse_folder,
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="right")

        # -------------------------------------------------------------
        # 4. ACTION CONTROLS & PROGRESS
        # -------------------------------------------------------------
        action_card = tk.Frame(
            container,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        action_card.pack(fill="x")

        self.progress = ttk.Progressbar(action_card, style="Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 6))

        status_row = tk.Frame(action_card, bg=Theme.BG_CARD)
        status_row.pack(fill="x", pady=(0, 8))

        self.status_label = tk.Label(
            status_row,
            textvariable=self.status_msg,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_GREEN,
            font=Theme.FONT_SMALL,
            anchor="w",
        )
        self.status_label.pack(side="left")

        self.item_label = tk.Label(
            status_row,
            textvariable=self.item_status_msg,
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_SMALL,
            anchor="e",
        )
        self.item_label.pack(side="right")

        btn_row = tk.Frame(action_card, bg=Theme.BG_CARD)
        btn_row.pack(fill="x")

        self.start_btn = tk.Button(
            btn_row,
            text="🚀  Download Entire Batch Queue",
            bg=Theme.GREEN,
            fg="#ffffff",
            activebackground=Theme.GREEN_HOVER,
            activeforeground="#ffffff",
            font=Theme.FONT_BUTTON_LARGE,
            relief="flat",
            cursor="hand2",
            command=self.on_start_batch,
            pady=8,
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.cancel_btn = tk.Button(
            btn_row,
            text="✖ Stop Queue",
            bg=Theme.BG_CARD_ALT,
            fg=Theme.TEXT_SECONDARY,
            activebackground=Theme.RED,
            activeforeground="#ffffff",
            font=Theme.FONT_BUTTON,
            relief="flat",
            cursor="hand2",
            command=self.on_stop_batch,
            state="disabled",
            padx=16,
            pady=8,
        )
        self.cancel_btn.pack(side="right")

    def _paste_clipboard(self):
        try:
            clip = self.clipboard_get().strip()
            if clip:
                self.url_text.insert(tk.END, ("\n" if self.url_text.get("1.0", tk.END).strip() else "") + clip)
        except Exception:
            pass

    def _clear_text(self):
        self.url_text.delete("1.0", tk.END)

    def _browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.save_dir.get())
        if chosen:
            self.save_dir.set(chosen)

    def on_start_batch(self):
        raw_text = self.url_text.get("1.0", tk.END).strip()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not lines:
            messagebox.showwarning("Empty Batch", "Please enter at least one YouTube link.")
            return

        valid_urls: List[str] = []
        invalid_entries: List[str] = []

        for line in lines:
            try:
                clean = validate_media_url(line)
                valid_urls.append(clean)
            except SecurityValidationError:
                invalid_entries.append(line)

        if invalid_entries:
            msg = f"Filtered out {len(invalid_entries)} invalid/unauthorized URL(s)."
            if not valid_urls:
                messagebox.showerror("Validation Error", msg)
                return

        selected_preset = self.preset_combobox.get()
        media_fmt = self.quality_presets.get(selected_preset, list(self.quality_presets.values())[0])
        save_folder = self.save_dir.get()

        self._is_running = True
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress["value"] = 0

        threading.Thread(
            target=self._worker_batch_loop,
            args=(valid_urls, media_fmt, save_folder),
            daemon=True,
        ).start()

    def _worker_batch_loop(self, urls: List[str], media_fmt: MediaFormat, save_folder: str):
        total = len(urls)
        completed = 0
        failed = 0

        self.downloader = SafeDownloader(
            progress_callback=lambda p: self.after(0, self._on_item_progress, p),
            status_callback=lambda s: self.after(0, self._on_status_update, s),
        )

        for idx, url in enumerate(urls, start=1):
            if not self._is_running:
                break

            self.after(0, self._update_queue_header, idx, total)

            try:
                self.downloader.download(
                    raw_url=url,
                    media_format=media_fmt,
                    save_dir=save_folder,
                )
                completed += 1
            except Exception:
                failed += 1

            overall_pct = (idx / total) * 100.0
            self.after(0, self._set_progress, overall_pct)

        self.after(0, self._on_batch_finished, completed, failed, total, save_folder)

    def _update_queue_header(self, current: int, total: int):
        self.status_msg.set(f"Processing item [{current}/{total}]...")
        self.item_status_msg.set(f"Queue: {current}/{total}")

    def _on_item_progress(self, p: dict):
        percent = p.get("percent", 0.0)
        speed = p.get("speed_str", "")
        eta = p.get("eta_str", "")
        self.item_status_msg.set(f"Item: {percent:.0f}%  •  {speed}  •  ETA: {eta}")

    def _on_status_update(self, msg: str):
        self.status_msg.set(msg)

    def _set_progress(self, val: float):
        self.progress["value"] = val

    def _on_batch_finished(self, completed: int, failed: int, total: int, save_folder: str):
        self._is_running = False
        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.progress["value"] = 100
        self.status_msg.set(f"✔ Completed {completed} of {total} items.")
        self.item_status_msg.set("")

        messagebox.showinfo(
            "Batch Complete",
            f"Finished batch queue:\n✔ Successful: {completed}/{total}\n❌ Failed: {failed}\n\nSaved to:\n{save_folder}",
        )

    def on_stop_batch(self):
        self._is_running = False
        if self.downloader:
            self.downloader.cancel()
        self.status_msg.set("Stopping queue...")
        self.cancel_btn.config(state="disabled")
