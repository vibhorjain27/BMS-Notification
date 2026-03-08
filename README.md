# BMS Ticket Watcher 🎬

Monitors BookMyShow for **Dhurandhar: The Revenge (Hindi)** — 19 March 2026 (Mumbai).
Sends a **Gmail email** the moment tickets go live. Checks every 5 minutes via GitHub Actions.

## GitHub Secrets Required

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name | Value |
|---|---|
| `GMAIL_USER` | `vibhorjain27@gmail.com` |
| `GMAIL_PASSWORD` | Your 16-character Gmail App Password |

## Manual Test
Go to **Actions tab → BMS Ticket Watcher → Run workflow** to trigger a test run anytime.
