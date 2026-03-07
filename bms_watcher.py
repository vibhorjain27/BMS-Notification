#!/usr/bin/env python3
"""
BookMyShow Ticket Watcher — Dhurandhar: The Revenge (Hindi)
Runs via GitHub Actions every 5 minutes.
Sends WhatsApp alert via CallMeBot when March 19 tickets go live.
"""

import requests
import json
import os
import sys
from urllib.parse import quote

# ── Injected from GitHub Secrets ──────────────────────────────────────────
PHONE   = os.environ["WHATSAPP_PHONE"]    # e.g. 919876543210 (no + sign)
API_KEY = os.environ["CALLMEBOT_APIKEY"]  # from CallMeBot WhatsApp activation
# ──────────────────────────────────────────────────────────────────────────

TARGET_DATE_CODE = "20260319"
MOVIE_NAME = "Dhurandhar: The Revenge (Hindi)"
MOVIE_URL  = "https://in.bookmyshow.com/movies/mumbai/dhurandhar-the-revenge-hindi/ET00478890"

BMS_API = (
    "https://in.bookmyshow.com/api/movies-data/showtimes-by-event"
    "?appCode=MOBAND2&appVersion=14304&language=en"
    "&eventCode=ET00478890&regionCode=MUMBAI&subRegion=MUMBAI"
    "&bmsId=1.21145812.1703001600000&token=67x1xa33b4x422b361ba"
    "&lat=19.0760&lon=72.8777&favCount=0&device=ANDROID"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
    "Referer": "https://in.bookmyshow.com/",
}


def check_availability():
    resp = requests.get(BMS_API, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    dates = data.get("ShowDatesArray", [])
    march19 = next((d for d in dates if d.get("DateCode") == TARGET_DATE_CODE), None)

    if march19 is None:
        return False, "March 19 not yet visible in BMS date picker"

    is_disabled = march19.get("isDisabled", True)
    return not is_disabled, march19


def send_whatsapp(message: str):
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={encoded}&apikey={API_KEY}"
    resp = requests.get(url, timeout=15)
    print(f"  CallMeBot response: {resp.status_code} — {resp.text[:100]}")
    return resp.status_code == 200


def main():
    print(f"Checking BookMyShow: {MOVIE_NAME} — 19 March 2026")

    try:
        available, info = check_availability()
    except Exception as e:
        print(f"❌ BMS API error: {e}")
        sys.exit(0)

    if available:
        print("✅ TICKETS ARE LIVE! Sending WhatsApp alert...")
        msg = (
            f"🎬 *{MOVIE_NAME}* tickets are LIVE!\n"
            f"📅 Thu, 19 March 2026 — Book NOW before they fill up!\n"
            f"👉 {MOVIE_URL}"
        )
        sent = send_whatsapp(msg)
        if sent:
            print("📱 WhatsApp alert sent successfully!")
        else:
            print("⚠️ WhatsApp send failed — check WHATSAPP_PHONE and CALLMEBOT_APIKEY secrets")
    else:
        print(f"⏳ Not yet available — {info}")

    sys.exit(0)


if __name__ == "__main__":
    main()
