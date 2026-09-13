---
name: ps-query
description: On-demand SMS queries and commands. WHO IS, NEXT, DIGEST, URGENT.
---

# Executive queries via SMS

This skill handles incoming text messages from the owner. Four command types:

## 1. WHO IS [name/company]

"Who is Sarah from Acme?"

Search the OSINT cache and dossier log for the attendee:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --search "Sarah" \
  --domain "acme.com" \
  --cache-only
```

If found in cache (meeting dossier from today or recent lookup):

**Response (3 sentences max):**
```
Sarah Chen, VP of Product at Acme Corp. Last interaction: Q3 Roadmap Review on 2026-09-10. Acme raised Series A ($20M) in July, focusing on enterprise SaaS.
```

If not in cache, trigger a live lookup:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --search "Sarah" \
  --domain "acme.com"
```

If no public record exists:

```
No public record found for Sarah at acme.com—internal contact or private profile. No recent meetings in your calendar.
```

Never hallucinate. If you don't have data, say so explicitly.

## 2. NEXT

"What's next?"

Retrieve the next meeting on today's calendar:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/calendar_ingest.py" \
  --date today \
  --next-only
```

Output:
```json
{
  "time": "15:30",
  "title": "Product Demo with Acme",
  "attendees": ["sarah.chen@acme.com"],
  "duration_min": 30
}
```

Check if a dossier exists for this meeting:

```bash
ls "$HOME/Desktop/PrepSheets/$(date +%Y-%m-%d)-ProductDemoWithAcme.pdf"
```

**Response:**
```
Next: 3:30 PM - Product Demo with Acme (30min)
Sarah Chen (VP of Product) attending
Dossier: ~/Desktop/PrepSheets/2026-09-12-ProductDemoWithAcme.pdf
```

If no dossier exists yet (meeting is >30min away):

```
Next: 3:30 PM - Product Demo with Acme (30min)
Sarah Chen attending. Dossier will be ready 30min before the meeting.
```

If no more meetings today:

```
No more meetings today. Clear runway.
```

## 3. DIGEST

"Send me today's headline again"

Retrieve today's morning paper:

```bash
cat "$HOME/Desktop/PrepSheets/$(date +%Y-%m-%d)-MorningPaper.pdf.headline"
```

The typesetter saves a plain-text `.headline` file alongside every PDF for quick SMS retrieval.

**Response:**
```
Today's priority: Q4 Strategy Review with Client Corp — VP of Eng attending

Full paper: ~/Desktop/PrepSheets/2026-09-12-MorningPaper.pdf
```

If no paper was generated today (no meetings/emails):

```
No morning paper today—clear runway. No external meetings or urgent emails.
```

## 4. URGENT [name/company]

"URGENT Client Corp"

Generate an immediate dossier for the next scheduled meeting with that attendee, bypassing the 30-minute window:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/calendar_ingest.py" \
  --search-attendee "client.com" \
  --next-only
```

If a meeting is found (today or future):

```json
{
  "time": "16:00",
  "title": "Q4 Contract Finalization",
  "attendees": ["john.smith@client.com"],
  "date": "2026-09-12"
}
```

Immediately trigger `ps-dossier` for this meeting (same flow as the 30-min radar, but on-demand):

```bash
hermes skill invoke ps-dossier --meeting-id "2026-09-12-160000-q4-contract-finalization"
```

**Response after dossier generation:**
```
📋 Urgent dossier generated for 4:00 PM meeting with Client Corp

• John Smith, VP of Eng (Series B $50M raised in Aug)
• Latest email: Contract terms discussion, pricing finalization pending
• Talking points: Deployment timeline, SLA requirements, support model

Full dossier: ~/Desktop/PrepSheets/2026-09-12-Q4ContractFinalization.pdf
```

If no upcoming meeting with that attendee:

```
No upcoming meetings found with Client Corp. Want me to search past dossiers or calendar history?
```

## Free-form queries

Any SMS that doesn't match the four commands above gets interpreted as a natural language query.

**Examples:**
- "When is my next meeting with Acme?" → Parse as calendar search
- "What did Sarah say about pricing?" → Search email archives for "pricing" in threads with Sarah
- "Show me all meetings this week" → Calendar summary for the week

For each:
1. Parse intent (calendar, email, OSINT, or file search)
2. Run the appropriate script from `ps-shared`
3. Respond with a 3-sentence summary + file path if applicable

**Never say "I can't help with that."** Always attempt to interpret the query, and if truly ambiguous, offer 2-3 specific alternatives:

```
Not sure if you meant:
1. Next meeting with Acme (calendar search)
2. Recent emails from Acme (email search)
3. Background on Acme attendees (OSINT lookup)

Reply with 1, 2, or 3.
```

## Error handling

- **SMS service unavailable**: Log the query to `$HERMES_HOME/prepsheet/sms_queue.json` for retry when service returns.
- **Ambiguous attendee name**: Ask for clarification with specific options (e.g., "Did you mean Sarah Chen from Acme or Sarah Lee from Beta Corp?")
- **No data available**: Be explicit: "No calendar events found with that attendee" or "No OSINT data available for that domain."

Never hallucinate. If you don't know, say so and offer to look it up.

## Rate limiting

If the owner sends >5 queries in 10 minutes, gently suggest:

```
Getting a lot of queries—want me to generate a full briefing document instead of individual lookups?
```

This prevents SMS spam and offers a better UX for rapid-fire questions (compile into one PDF).
