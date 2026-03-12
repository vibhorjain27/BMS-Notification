#!/usr/bin/env python3
"""
BookMyShow Ticket Watcher — Dhurandhar: The Revenge (Hindi)
Checks multiple API date windows to catch March 19 going live.
Sends Gmail alert when tickets are available.
"""

import requests
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ── Injected from GitHub Secrets ──────────────────────────────────────────
GMAIL_USER     = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
NOTIFY_EMAIL   = os.environ["GMAIL_USER"]
TEST_MODE      = os.environ.get("TEST_MODE", "false").lower() == "true"
# ──────────────────────────────────────────────────────────────────────────

TARGET_DATE_CODE = "20260319"
MOVIE_NAME = "Dhurandhar: The Revenge (Hindi)"
MOVIE_URL  = "https://in.bookmyshow.com/buytickets/dhurandhar-the-revenge-hindi/movie-mumbai-ET00478890-MT/20260319"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
    "Referer": "https://in.bookmyshow.com/",
}


def build_api_url(from_date: str) -> str:
    """Build BMS API URL — the window shifts based on bmsId timestamp."""
    # bmsId encodes the date window start; we pass a timestamp for the target week
    ts = int(datetime.strptime(from_date, "%Y%m%d").timestamp() * 1000)
    return (
        f"https://in.bookmyshow.com/api/movies-data/showtimes-by-event"
        f"?appCode=MOBAND2&appVersion=14304&language=en"
        f"&eventCode=ET00478890&regionCode=MUMBAI&subRegion=MUMBAI"
        f"&bmsId=1.21145812.{ts}"
        f"&token=67x1xa33b4x422b361ba"
        f"&lat=19.0760&lon=72.8777&favCount=0&device=ANDROID"
    )


def check_availability():
    """
    Check multiple date windows to find March 19.
    The API only shows 7 days at a time, so we try windows
    starting from today AND from a week ahead.
    """
    # Try 3 different date windows to find March 19
    check_dates = [
        datetime.today().strftime("%Y%m%d"),           # today's window
        (datetime.today() + timedelta(days=7)).strftime("%Y%m%d"),   # next week
        (datetime.today() + timedelta(days=5)).strftime("%Y%m%d"),   # +5 days
    ]

    for from_date in check_dates:
        try:
            url = build_api_url(from_date)
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            dates = data.get("ShowDatesArray", [])
            march19 = next((d for d in dates if d.get("DateCode") == TARGET_DATE_CODE), None)

            if march19:
                is_disabled = march19.get("isDisabled", True)
                shows = data.get("ShowDetails", [])
                print(f"  Found March 19 in window starting {from_date}: disabled={is_disabled}, shows={len(shows)}")
                if not is_disabled:
                    return True, f"{len(shows)} shows available"
            else:
                print(f"  Window {from_date}: March 19 not visible (last date: {dates[-1].get('DateCode') if dates else 'none'})")

        except Exception as e:
            print(f"  Window {from_date} error: {e}")

    return False, "March 19 not yet available in any date window"


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
    if TEST_MODE:
        print("🧪 TEST MODE — sending test email...")
        try:
            send_gmail(
                subject="✅ BMS Watcher is working!",
                html_body=f"""
                <div style="font-family:Arial,sans-serif;max-width:500px;">
                    <h2 style="color:#2a9d8f;">✅ Your BMS Watcher is active!</h2>
                    <p>GitHub Actions is running correctly and your Gmail connection works.</p>
                    <p>You will receive another email the moment <strong>{MOVIE_NAME}</strong>
                    tickets open for <strong>Thursday, 19 March 2026</strong>.</p>
                    <p style="color:#888;font-size:12px;">Checking every 5 minutes automatically.</p>
                </div>
                """
            )
            print(f"📧 Test email sent to {NOTIFY_EMAIL}!")
        except Exception as e:
            print(f"❌ Email failed: {e}")
        sys.exit(0)

    print(f"Checking BookMyShow: {MOVIE_NAME} — 19 March 2026")

    available, info = check_availability()

    if available:
        print(f"✅ TICKETS ARE LIVE! {info} — Sending Gmail alert...")
        try:
            send_gmail(
                subject="🎬 BOOK NOW — Dhurandhar Tickets Live on March 19!",
                html_body=f"""
                <div style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;">
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
            print(f"📧 Alert email sent to {NOTIFY_EMAIL}!")
        except Exception as e:
            print(f"⚠️ Email failed: {e}")
    else:
        print(f"⏳ {info}")

    sys.exit(0)


if __name__ == "__main__":
    main()
