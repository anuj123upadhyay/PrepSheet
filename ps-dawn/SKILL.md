---
name: ps-dawn
description: Generate the morning PrepSheet at 6 AM with calendar, email, and OSINT intelligence.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, morning, intelligence, calendar, email]
    related_skills: [ps-shared, ps-osint]
---

# Morning PrepSheet (6:00 AM)

Generate the daily intelligence briefing. Read today's calendar events via Plow Latch,
scan unread emails, research external attendees, and produce a vintage newspaper PDF.

Read `ps-shared` for the PDF generation workflow.

## Step 1: Get today's events via Plow

Use Plow Latch to read Google Calendar (already authenticated in browser):

```bash
rote browser navigate "https://calendar.google.com/calendar/u/0/r/day/$(date +%Y/%m/%d)"
rote browser wait 2000
rote browser eval 'JSON.stringify(Array.from(document.querySelectorAll("[data-eventid]")).map(e => ({
  title: e.querySelector("[data-draggable-id]")?.textContent || "Untitled",
  time: e.getAttribute("data-start-time"),
  attendees: e.getAttribute("data-attendees")?.split(",") || []
})))'
```

Also read Mac Calendar if configured:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" --date today
```

Combine both sources. Identify external attendees (emails not matching `internal_domains` from config).

## Step 2: Scan unread emails via Plow

Use Plow Latch to read Gmail:

```bash
rote browser navigate "https://mail.google.com/mail/u/0/#search/is:unread+newer_than:1d"
rote browser wait 2000
# Extract email summaries
```

Filter by VIP senders from config. Extract: sender, subject, preview, urgency keywords.

## Step 3: Research external attendees

For each unique external domain, use `ps-osint` to research:
- Company background (website, about page)
- Recent news (Google News search via Plow)
- LinkedIn profiles (if logged in via Plow)

See `ps-osint` skill for the research workflow.

## Step 4: Calculate headline priority

Score each event/email:
- External meetings: weight 5
- Long meetings (>60min): weight 3
- Urgent email keywords: weight 4
- VIP senders: weight 3

Select highest score as headline. If all internal/routine: "Clear Runway — Internal Syncs Only"

## Step 5: Generate PDF

Call the typesetter:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --mode paper \
  --events events.json \
  --emails emails.json \
  --osint osint.json \
  --headline "<calculated headline>" \
  --output ~/Desktop/PrepSheet/$(date +%Y-%m-%d)-MorningPrepsheet.pdf
```

The typesetter renders a three-column vintage newspaper:
- Left: Today's agenda (chronological)
- Center: Meeting intelligence (attendee backgrounds)
- Right: Urgent email triage

Output is saved to `~/Desktop/PrepSheet/YYYY-MM-DD-MorningPrepsheet.pdf`

## When to run

Automatically at 6:00 AM via cron (configured in `ps-setup`).

Can also be triggered manually: "Generate my morning PrepSheet"

## If nothing to report

If zero external meetings and zero urgent emails, output `quiet` and skip PDF generation.
Most days don't need a printed briefing.
