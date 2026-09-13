---
name: ps-dossier
description: Generate meeting dossiers 30 minutes before external meetings.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, meetings, dossier, research]
    related_skills: [ps-shared, ps-osint]
---

# Meeting Dossier (30 Min Before Meetings)

Monitor calendar for upcoming external meetings. Generate focused one-page dossiers
with attendee backgrounds, email context, and talking points.

## Trigger

Runs automatically 30 minutes before any meeting with external attendees (emails not in `internal_domains`).

Can also be triggered manually: "Give me a dossier for my next meeting"

## Step 1: Identify the meeting

When triggered, receive meeting context:
- Title, time, duration
- Attendees (internal and external)
- Location/link

## Step 2: Search email history via Plow

Use Plow Latch to search Gmail for recent exchanges with attendees:

```bash
# For each external attendee
rote browser navigate "https://mail.google.com/mail/u/0/#search/from:john@acme.com+OR+to:john@acme.com+newer_than:7d"
rote browser wait 2000
# Extract thread summaries
```

Group by thread. Identify unresolved topics, pending decisions, last message preview.

## Step 3: Research attendees

Use `ps-osint` to gather:
- Name and title (LinkedIn via Plow)
- Company background (website)
- Recent company news (Google News via Plow)
- Funding/metrics (Crunchbase via Plow)

See `ps-osint` skill for research workflow.

## Step 4: Generate dossier PDF

Call the typesetter in dossier mode:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --mode dossier \
  --meeting meeting.json \
  --emails email_context.json \
  --osint osint.json \
  --output ~/Desktop/PrepSheet/$(date +%Y-%m-%d)-<Company>-meeting-dossier.pdf
```

The dossier contains:
- Meeting header (title, time, attendees, duration)
- Attendee backgrounds with company context
- Recent email exchanges (thread summaries)
- Strategic talking points (auto-generated from context)

Output: `~/Desktop/PrepSheet/YYYY-MM-DD-CompanyName-meeting-dossier.pdf`

## If internal-only meeting

If all attendees are in `internal_domains`, output `quiet` and skip dossier.
No need for intelligence on your own team.
