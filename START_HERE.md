# PrepSheet - Start Here

**Since you have Plow Latch MCP connected, setup is 3 steps:**

## 1. Install Dependencies

```bash
pip3 install weasyprint pyobjc-framework-EventKit
```

## 2. Create Config

File: `~/.hermes/prepsheet/config.json`

```json
{
  "internal_domains": ["yourcompany.com"],
  "vip_senders": [],
  "calendar_sources": ["mac", "plow-google"],
  "use_plow_latch": true
}
```

**Replace `yourcompany.com` with your actual email domain!**

This is critical - PrepSheet uses this to identify "external" attendees who need research.

## 3. Create Directory

```bash
mkdir -p ~/Desktop/PrepSheet
```

## That's It!

No Google API credentials needed. No .env file. Plow Latch uses your browser sessions.

---

## How It Works

### Morning PrepSheet (6:00 AM Daily)

Automatically:
1. Reads your Mac Calendar + Google Calendar (via Plow)
2. Scans unread Gmail (via Plow)
3. Researches external attendees (LinkedIn, company sites, news via Plow)
4. Generates vintage newspaper PDF
5. Saves to `~/Desktop/PrepSheet/YYYY-MM-DD-MorningPrepsheet.pdf`

**Three columns:**
- Left: Today's agenda
- Center: Meeting intelligence
- Right: Urgent emails

### Meeting Dossier (30 Min Before Meetings)

Automatically for external meetings:
1. Searches Gmail for recent exchanges
2. Researches attendees
3. Generates one-page dossier
4. Saves to `~/Desktop/PrepSheet/YYYY-MM-DD-Company-meeting-dossier.pdf`

### Meeting Scheduling (On-Demand)

Just ask:
- "Schedule a meeting with john@acme.com tomorrow at 2pm"
- "Create a 30-minute call with Sarah on Monday at 10am"

PrepSheet confirms details, then creates the event via Plow Latch.

---

## Test It

### Test Calendar Access
```bash
python3 ps-shared/scripts/mac_calendar_simple.py --date today
```

Should show your today's events in JSON.

### Generate Morning PrepSheet
Ask the agent: **"Generate my morning PrepSheet"**

It will read your calendar/email and create a PDF in `~/Desktop/PrepSheet/`.

### Schedule a Test Meeting
Ask: **"Schedule a test meeting with myself tomorrow at 10am"**

It will confirm, then create the event.

---

## Config Options

### Minimum (what you need)
```json
{
  "internal_domains": ["mycompany.com"]
}
```

### Full Config
```json
{
  "internal_domains": ["mycompany.com", "startup.io"],
  "vip_senders": ["client.com", "investor@vc.com"],
  "calendar_sources": ["mac", "plow-google"],
  "dawn_hour": 6,
  "meeting_radar_minutes": 30,
  "pdf_archive_path": "~/Desktop/PrepSheet",
  "use_plow_latch": true
}
```

**Important**: `internal_domains` = your organization's email domains
- Everyone else = "external" → triggers research & dossiers
- Your teammates = "internal" → no dossiers needed

---

## Skills Overview

- **ps-dawn** - Morning PrepSheet generator
- **ps-dossier** - Meeting dossier generator
- **ps-schedule** - Meeting scheduler
- **ps-osint** - OSINT research (via Plow)
- **ps-shared** - Common utilities

All skills delegate to Plow Latch for calendar/email/web access.

---

## Troubleshooting

**"No events found"**
- Check you have events in calendar today
- Verify `calendar_sources` in config

**"PDF generation failed"**
```bash
pip3 install weasyprint
```

**"Calendar access denied (macOS)"**
- System Preferences > Privacy > Calendar
- Grant access to Terminal/Python

**"rote command not found"**
- Plow CLI should be in PATH
- Check: `which rote`

---

## What's Different from Complex Setup

**Traditional approach:**
- Install Google API libraries ❌
- Create Google Cloud project ❌
- Enable APIs ❌
- Download OAuth credentials ❌
- Authenticate ❌

**With Plow Latch:**
- You're already logged into Google in browser ✅
- PrepSheet uses those sessions ✅
- Done! ✅

---

## Next Steps

1. Run PrepSheet for one week to build intelligence
2. Add VIP senders to config for email prioritization
3. Customize internal_domains for your organization
4. Let it run autonomously

**The PrepSheet** - Prepared before dawn, delivered before coffee. ☕
