#!/usr/bin/env python3
"""
Download Bebas Neue font from Google Fonts CDN.
Run this once before starting the bot, or let bot.py call it on startup.
"""
import os
import urllib.request

FONT_DIR  = "fonts"
FONT_FILE = os.path.join(FONT_DIR, "BebasNeue-Regular.ttf")
FONT_URL  = (
    "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf"
)

def download_font():
    if os.path.exists(FONT_FILE):
        print(f"[font] Already exists: {FONT_FILE}")
        return

    os.makedirs(FONT_DIR, exist_ok=True)
    print(f"[font] Downloading Bebas Neue → {FONT_FILE}")
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_FILE)
        print("[font] ✅ Download complete!")
    except Exception as e:
        print(f"[font] ⚠️  Could not download font: {e}")
        print("[font]    Falling back to DejaVu Sans Bold (system font).")

if __name__ == "__main__":
    download_font()
