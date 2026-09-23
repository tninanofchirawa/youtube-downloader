#!/usr/bin/env python3
"""
Safe YouTube & Media Downloader - Main Application Entry Point
"""

import sys
import tkinter as tk
from tkinter import messagebox

from app.ui.main_window import MainWindow


def main():
    """Launches the Safe Media Downloader application."""
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror(
            "Fatal Application Error",
            f"An unexpected error occurred while running the application:\n\n{e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
