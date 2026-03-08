#!/usr/bin/env python3
"""
BookMyShow Ticket Watcher — Dhurandhar: The Revenge (Hindi)
Runs via GitHub Actions every 5 minutes.
Sends Gmail alert when March 19 tickets go live.
"""

import requests
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Injected from GitHub Secrets ──────────────────────────────────────────
GMAIL_USER     = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
NOTIFY_EMAIL   = os.environ["GMAIL_USER"]
TEST_MODE      = os.environ.get("TEST_MODE", "false").lower() == "true"
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
    return not march19.get("isDisabled", True), march19


def send_gmail(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, NOTIFY_EMAIL, msg.as_string())


def main():
    # ── TEST MODE: just verify email works ──────────────────────────────
    if TEST_MODE:
        print("🧪 TEST MODE — sending test email...")
        try:
            send_gmail(
                subject="✅ BMS Watcher is working!",
                html_body=f"""
                <div style="font-family:Arial,sans-serif;max-width:500px;">
                    <h2 style="color:#2a9d8f;">✅ Your BMS Watcher is active!</h2>
                    <p>GitHub Actions is running correctly and your Gmail connection works.</p>
                    <p>You will receive another email like this one the moment
                    <strong>{MOVIE_NAME}</strong> tickets open for
                    <strong>Thursday, 19 March 2026</strong>.</p>
                    <p style="color:#888;font-size:12px;">Checking every 5 minutes automatically.</p>
                </div>
                """
            )
            print(f"📧 Test email sent to {NOTIFY_EMAIL}!")
        except Exception as e:
            print(f"❌ Email failed: {e}")
        sys.exit(0)

    # ── NORMAL MODE: check BMS ───────────────────────────────────────────
    print(f"Checking BookMyShow: {MOVIE_NAME} — 19 March 2026")

    try:
        available, info = check_availability()
    except Exception as e:
        print(f"❌ BMS API error: {e}")
        sys.exit(0)

    if available:
        print("✅ TICKETS ARE LIVE! Sending Gmail alert...")
        try:
            send_gmail(
                subject="🎬 BOOK NOW — Dhurandhar Tickets Live on March 19!",
                html_body=f"""
                <div style="font-family:Arial,sans-serif;max-width:500px;">
                    <h2 style="color:#e63946;">🎬 Tickets Are LIVE!</h2>
                    <p style="font-size:16px;">
                        <strong>{MOVIE_NAME}</strong> tickets for
                        <strong>Thursday, 19 March 2026</strong> are now open for booking!
                    </p>
                    <a href="{MOVIE_URL}"
                       style="display:inline-block;padding:12px 24px;background:#e63946;
                              color:white;text-decoration:none;border-radius:6px;
                              font-size:16px;font-weight:bold;margin-top:10px;">
                        Book Tickets Now →
                    </a>
                    <p style="color:#888;font-size:12px;margin-top:20px;">
                        Sent by your BMS Watcher on GitHub Actions
                    </p>
                </div>
                """
            )
            print(f"📧 Email sent to {NOTIFY_EMAIL}!")
        except Exception as e:
            print(f"⚠️ Email failed: {e}")
    else:
        print(f"⏳ Not yet available — {info}")

    sys.exit(0)


if __name__ == "__main__":
    main()
