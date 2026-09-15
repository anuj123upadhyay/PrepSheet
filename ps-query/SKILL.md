---
name: ps-query
description: On-demand conversational queries and commands. WHO IS, NEXT, DIGEST, URGENT, and natural language executive Q&A.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, query, sms, executive, conversational]
    related_skills: [ps-shared, ps-osint, ps-dossier, ps-schedule]
---

# Executive Conversational Queries

This skill handles incoming chat and SMS queries from the executive. Responses must be **2 to 3 sentences maximum**, crisp, and immediately actionable.

---

## 1. WHO IS [name/company]

*Example: "Who is Sarah from Acme?"*

1. Query the OSINT cache first via `ps-shared`:
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --search "Sarah" \
  --domain "acme.com" \
  --cache-only
```

2. If found in cache (from a recent meeting dossier or lookup):
```
Sarah Chen, VP of Product at Acme Corp. Last interaction: Q3 Roadmap Review on Sept 10. Acme raised a $20M Series A in July focusing on enterprise workflows.
```

3. If not in cache, trigger a live lookup via `ps-osint` (using Plow Latch to inspect LinkedIn/Crunchbase):
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --attendee "sarah@acme.com" \
  --domain "acme.com"
```

4. If no public record exists, state explicitly:
```
No public record found for Sarah at acme.com—internal contact or private profile. No past meetings found in your calendar.
```

*Never hallucinate or guess credentials.*

---

## 2. NEXT

*Example: "What's next?"*

Retrieve the next upcoming meeting on today's calendar:
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" \
  --action read \
  --date today \
  --next-only
```

Check if a dossier PDF exists for this meeting:
```bash
ls "$HOME/Desktop/PrepSheets/"*"-meeting-dossier.pdf" 2>/dev/null
```

**Response Format:**
```
Next: 3:30 PM — Product Demo with Acme Corp (30 min).
Sarah Chen (VP of Product) attending.
Dossier: ~/Desktop/PrepSheets/2026-09-15-AcmeCorp-meeting-dossier.pdf
```

If the meeting is more than 30 minutes away and no dossier exists yet:
```
Next: 3:30 PM — Product Demo with Acme Corp (30 min).
Sarah Chen attending. Dossier will be generated automatically at 3:00 PM.
```

If the calendar is clear for the remainder of the day:
```
Clear runway—no more meetings scheduled for today.
```

---

## 3. DIGEST

*Example: "Send me today's headline again" or "Give me my morning digest"*

Retrieve today's morning paper headline:
```bash
cat "$HOME/Desktop/PrepSheets/$(date +%Y-%m-%d)-MorningPrepsheet.headline" 2>/dev/null
```

**Response Format:**
```
Today's Priority: Q4 Strategy Review with Acme Corp — Series B expansion on agenda.
Full broadsheet: ~/Desktop/PrepSheets/2026-09-15-MorningPrepsheet.pdf
```

If no paper was generated (routine internal syncs only):
```
No morning paper generated today—clear runway with internal syncs only.
```

---

## 4. URGENT [name/company]

*Example: "URGENT Acme Corp"*

Locate the upcoming meeting with that attendee or domain:
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" \
  --action read \
  --search-attendee "acme.com"
```

Immediately trigger `ps-dossier` for this meeting, bypassing the normal 30-minute radar wait.

**Response Format:**
```
📋 Urgent dossier generated for 3:30 PM meeting with Acme Corp:
• Sarah Chen, VP of Product (Series A $20M closed July).
• Latest email: Final pricing and SLA terms pending review.
Dossier: ~/Desktop/PrepSheets/2026-09-15-AcmeCorp-meeting-dossier.pdf
```

---

## 5. Free-Form Conversational Inquiries

Any message not matching the four primary keywords is interpreted as an executive query:
- *"When is my next meeting with Stripe?"* → Search calendar for Stripe.
- *"What did Alex email about yesterday?"* → Scan recent VIP emails via Plow Latch.
- *"Summarize my morning"* → Synthesize today's morning meetings.

**Rules for Natural Language Responses:**
1. Keep replies strictly under 3 sentences unless asked for an in-depth breakdown.
2. If ambiguous, provide 2 to 3 numbered choices rather than generic apologies.
3. If information is missing, clearly state what was searched and offer next steps.
