"""Modern Theme with Deep Black, Purple, Emerald Green, White, and Yellow Palette."""

import tkinter as tk
from tkinter import ttk


class Theme:
    """Color palette and styling matching modern web downloader UI."""

    # Backgrounds
    BG_DARK = "#090a0f"          # Deep space black
    BG_CARD = "#12141c"          # Modern card background
    BG_CARD_ALT = "#191c28"      # Elevated container
    BG_INPUT = "#0d0f15"         # Input box
    BG_HOVER = "#212534"         # Hover state

    # Borders
    BORDER = "#252938"           # Clean divider borders
    BORDER_FOCUS = "#8b5cf6"     # Purple glow on focus

    # Brand Colors (Purple, Emerald Green, Yellow, Red)
    PURPLE = "#8b5cf6"           # Primary Purple Accent
    PURPLE_HOVER = "#7c3aed"
    PURPLE_DARK = "#4c1d95"
    PURPLE_BADGE_BG = "#2e1065"

    GREEN = "#10b981"            # Success Emerald Green
    GREEN_HOVER = "#059669"
    GREEN_DARK = "#064e3b"

    YELLOW = "#f59e0b"           # Warning / Notice Amber
    YELLOW_DARK = "#78350f"

    RED = "#ef4444"              # Danger Red
    RED_DARK = "#7f1d1d"

    # Text
    TEXT_PRIMARY = "#ffffff"     # Pure white
    TEXT_SECONDARY = "#94a3b8"   # Slate gray
    TEXT_MUTED = "#64748b"       # Muted subtext
    TEXT_PURPLE = "#a78bfa"      # Light purple text
    TEXT_GREEN = "#34d399"       # Light green text
    TEXT_YELLOW = "#fbbf24"      # Warning yellow text

    # Typography
    FONT_HERO = ("Segoe UI", 18, "bold")
    FONT_TITLE = ("Segoe UI", 13, "bold")
    FONT_SUBTITLE = ("Segoe UI", 10, "bold")
    FONT_BODY = ("Segoe UI", 9)
    FONT_BODY_BOLD = ("Segoe UI", 9, "bold")
    FONT_SMALL = ("Segoe UI", 8)
    FONT_MONO = ("Consolas", 9)
    FONT_BUTTON = ("Segoe UI", 9, "bold")
    FONT_BUTTON_LARGE = ("Segoe UI", 10, "bold")


def apply_modern_theme(root: tk.Tk) -> ttk.Style:
    """Applies clean dark theme styling to Tkinter and TTK widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=Theme.BG_DARK)

    # Frames
    style.configure("TFrame", background=Theme.BG_DARK)
    style.configure("Card.TFrame", background=Theme.BG_CARD, relief="flat")
    style.configure("CardAlt.TFrame", background=Theme.BG_CARD_ALT, relief="flat")

    # Labels
    style.configure("TLabel", background=Theme.BG_DARK, foreground=Theme.TEXT_PRIMARY, font=Theme.FONT_BODY)
    style.configure("Card.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_PRIMARY, font=Theme.FONT_BODY)
    style.configure("CardSecondary.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_SECONDARY, font=Theme.FONT_BODY)

    # Notebook Tabs
    style.configure(
        "TNotebook",
        background=Theme.BG_DARK,
        borderwidth=0,
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=Theme.BG_CARD,
        foreground=Theme.TEXT_SECONDARY,
        padding=[20, 9],
        font=Theme.FONT_BUTTON,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", Theme.PURPLE), ("active", Theme.BG_HOVER)],
        foreground=[("selected", "#ffffff"), ("active", Theme.TEXT_PRIMARY)],
    )

    # Progressbar
    style.configure(
        "Horizontal.TProgressbar",
        background=Theme.PURPLE,
        troughcolor=Theme.BG_INPUT,
        bordercolor=Theme.BORDER,
        lightcolor=Theme.PURPLE,
        darkcolor=Theme.PURPLE_DARK,
        thickness=10,
    )

    # Combobox
    style.configure(
        "TCombobox",
        background=Theme.BG_INPUT,
        foreground=Theme.TEXT_PRIMARY,
        fieldbackground=Theme.BG_INPUT,
        darkcolor=Theme.BORDER,
        lightcolor=Theme.BORDER,
        arrowcolor=Theme.TEXT_PRIMARY,
        bordercolor=Theme.BORDER,
        padding=6,
        font=Theme.FONT_BODY,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", Theme.BG_INPUT)],
        foreground=[("readonly", Theme.TEXT_PRIMARY)],
        selectbackground=[("readonly", Theme.PURPLE)],
        selectforeground=[("readonly", "#ffffff")],
    )

    return style
