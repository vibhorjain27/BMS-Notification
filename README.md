# BMS Ticket Watcher 🎬

Monitors BookMyShow for **Dhurandhar: The Revenge (Hindi)** — 19 March 2026 (Mumbai).
Sends a **WhatsApp notification** the moment tickets go live.

## How it works
- GitHub Actions runs the check every **5 minutes** automatically
- Uses BookMyShow's internal API (no scraping, very reliable)
- Sends WhatsApp message via **CallMeBot** (free)

## Setup — GitHub Secrets required

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Value |
|---|---|
| `WHATSAPP_PHONE` | Your number without `+` (e.g. `919876543210`) |
| `CALLMEBOT_APIKEY` | API key received from CallMeBot on WhatsApp |

## Activate CallMeBot
1. Save `+34 644 95 73 56` in your contacts
2. Send `I allow callmebot to send me messages` on WhatsApp to that number
3. You'll receive your API key in reply — add it as the `CALLMEBOT_APIKEY` secret above

## Manual trigger
Go to **Actions tab → BMS Ticket Watcher → Run workflow** to test anytime.
