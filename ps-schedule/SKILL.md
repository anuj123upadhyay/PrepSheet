---
name: ps-schedule
description: Schedule meetings on Mac Calendar or Google Calendar via Plow Latch.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, scheduling, calendar, meetings]
    related_skills: [ps-shared]
---

# Meeting Scheduling

Schedule meetings when the user requests. Uses Plow Latch to create events on Google Calendar
or Mac Calendar for direct API access.

## Parse the request

Extract from user message:
- **Title**: Meeting subject
- **Date/Time**: When to schedule
- **Duration**: How long (default: 60 minutes)
- **Attendees**: Email addresses
- **Location**: Optional (Zoom, Google Meet, etc.)

If critical info missing (title, date/time, or attendees), ask one short question.

## Confirm before creating

Show parsed details:

```
I'll schedule:
• Title: Q4 Strategy Review
• Date/Time: Friday, September 15 at 3:00 PM
• Duration: 60 minutes
• Attendees: john@acme.com, sarah@acme.com
• Location: Zoom

Create this event?
```

Wait for explicit confirmation ("yes", "go ahead", "schedule it").

## Create via Plow Latch (Google Calendar)

Use Plow's Google Calendar access (already authenticated in browser):

```bash
# Method 1: If google-calendar adapter exists
rote adapter call google-calendar create-event \
  --title "Q4 Strategy Review" \
  --start "2026-09-15T15:00:00" \
  --duration 60 \
  --attendees "john@acme.com,sarah@acme.com" \
  --location "Zoom"

# Method 2: Browser automation fallback
rote browser navigate "https://calendar.google.com/calendar/u/0/r/eventedit"
rote browser fill "[name='title']" "Q4 Strategy Review"
# ... fill other fields ...
rote browser click "button[name='save']"
```

## Create via Mac Calendar (direct API)

If config specifies Mac Calendar as primary:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" \
  --action create \
  --title "Q4 Strategy Review" \
  --start "2026-09-15 15:00" \
  --duration 60 \
  --attendees "john@acme.com,sarah@acme.com" \
  --location "Zoom"
```

## Confirm creation

If successful:

```
✓ Meeting scheduled successfully!

Q4 Strategy Review
Friday, September 15 at 3:00 PM (60 min)
Attendees: john@acme.com, sarah@acme.com

A dossier will be generated 30 minutes before the meeting.
```

If failed, explain error and suggest alternatives (check permissions, try different calendar).

## Natural language patterns

Common date/time formats:
- "tomorrow at 2pm" → next day, 14:00
- "next Monday at 10am" → following Monday, 10:00
- "Friday at 3" → this/next Friday, 15:00
- "in 2 hours" → current time + 2 hours

Duration patterns:
- "for 1 hour" → 60 min
- "30 minute meeting" → 30 min
- Default if unspecified: 60 min

## Never

- Never schedule without explicit confirmation
- Never modify existing events (this skill only creates new ones)
- Never auto-add attendees user didn't mention
