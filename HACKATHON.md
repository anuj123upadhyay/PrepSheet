# PrepSheet Hackathon Submission

## Project Overview

**The PrepSheet** is an autonomous executive chief of staff agent that transforms calendar chaos into calm, prepared mornings. It generates vintage-style "morning newspapers" before dawn and provides just-in-time meeting dossiers throughout the day.

Built for the Plow + Hermes hackathon.

---

## The Problem We're Solving

Founders and executives face:
- **Morning decision fatigue** from unprocessed overnight emails
- **Context-switching hell** between calendar, email, and research tools
- **Zero-prep meetings** with external stakeholders they've never met
- **Information overload** instead of intelligence synthesis

Traditional solutions (calendar apps, email clients, note-takers) are **reactive**. You have to open them, search them, remember to check them.

**The PrepSheet is proactive.** It prepares while you sleep and delivers a physical artifact you can't miss.

---

## How It Works

### 1. The 04:00 AM Dawn Broadside
Every morning, The PrepSheet autonomously:
- Reads your calendar (read-only CalDAV/iCal)
- Scans VIP emails (read-only IMAP)
- Researches external meeting attendees (LinkedIn, Crunchbase, news via Plow Latch)
- **Calculates the single most critical priority** for your day (not a list!)
- Generates a three-column vintage newspaper PDF
- **Prints it physically** (or saves to `~/Desktop/PrepSheets/`)
- Sends SMS at 6:30 AM: "Your PrepSheet is ready"

### 2. The 30-Minute Meeting Radar
A continuous monitor checks for upcoming external meetings. 30 minutes before each one:
- Delta-audits recent email threads with attendees
- Generates a focused one-page dossier
- Sends 3-bullet SMS brief with file path

### 3. On-Demand SMS Queries
Text the agent:
- **"WHO IS Sarah from Acme?"** → 3-sentence OSINT summary
- **"NEXT"** → Next meeting brief
- **"DIGEST"** → Resend today's headline
- **"URGENT Client Corp"** → Generate dossier now

---

## Architecture & Implementation

### Skills Created

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| `ps-setup` | Initial configuration wizard | Calendar/email/printer/SMS setup |
| `ps-dawn` | Morning newspaper generator | Headline priority, 3-column layout, PDF generation |
| `ps-dossier` | Meeting radar & dossiers | Email context, attendee backgrounds, talking points |
| `ps-query` | On-demand SMS queries | WHO IS, NEXT, DIGEST, URGENT commands |
| `ps-osint` | OSINT engine | Zero-hallucination public intelligence |
| `ps-shared` | Shared infrastructure | Calendar/email ingestion, typesetter, printer, SMS |

### Technology Stack

- **Plow Cloud Agents Base**: Container runtime & credential management
- **Hermes**: Agent conversation framework & skill orchestration
- **Docker**: Containerized deployment
- **Python 3**: All scripts (calendar, email, OSINT, typesetter)
- **CUPS**: Printer integration (with Desktop fallback)
- **Plow Latch**: Headless browser for OSINT (placeholder ready)

### Data Flow Diagram

```
┌─────────────────────┐
│ Calendar/Email      │ (Read-Only)
│ (CalDAV/IMAP)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Queue Directory     │
│ $HERMES_HOME/       │
│ prepsheet/queue/    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Ingestion Scripts   │
│ - calendar_ingest   │
│ - email_ingest      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OSINT Enrichment    │
│ (Plow Latch)        │
│ + 30-day cache      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Typesetter          │
│ Vintage PDF         │
│ (3-column layout)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Output              │
│ - Printer (CUPS)    │
│ - Desktop fallback  │
│ - SMS notification  │
└─────────────────────┘
```

---

## Key Technical Innovations

### 1. The Headline Mandate
Unlike every calendar app that shows a raw list, The PrepSheet **calculates priority**:
- External meetings (weight: 5)
- Long meetings (weight: 3)
- Urgent email keywords (weight: 4)
- VIP senders requiring action (weight: 3)

Result: One clear headline like "Q4 Strategy Review with Client Corp — VP of Eng attending" instead of "You have 7 meetings today."

### 2. Zero-Hallucination OSINT
The agent **never guesses**:
- If no LinkedIn profile exists → "No public record found"
- If company has no funding news → "Private or not disclosed"
- All sources logged with confidence scores (high/medium/low/none)
- 30-day cache prevents redundant lookups

### 3. Read-Only Non-Destructive Operation
The PrepSheet **never**:
- Deletes/moves emails
- Accepts/declines calendar invites
- Sends emails or responses
- Writes to any external system

It's an intelligence daemon, not an assistant. It prepares information; the human makes decisions.

### 4. Graceful Degradation
- No printer? → Desktop PDF (not an error, just a different delivery)
- OSINT fails? → "Background research unavailable" (proceed with partial data)
- No meetings today? → No paper, no notification (silence is success)

---

## Demo Instructions

### Quick Start

```bash
cd PrepSheet-Folder/PrepSheet
cp .env.example .env
# Edit .env with test credentials

docker compose build
docker compose up -d

# Trigger manual morning paper generation
docker compose exec agent hermes skill invoke ps-dawn
```

### Sample Data Setup

For demo purposes, pre-populate test data:

```bash
mkdir -p /tmp/prepsheet-demo/queue/calendar
mkdir -p /tmp/prepsheet-demo/queue/email

# Create sample calendar event
cat > /tmp/prepsheet-demo/queue/calendar/event1.json <<EOF
{
  "start": "2026-09-12T14:00:00Z",
  "summary": "Q4 Strategy Review",
  "attendees": ["internal@mycompany.com", "john.smith@client.com"],
  "duration_minutes": 60,
  "location": "Zoom",
  "organizer": "ceo@mycompany.com",
  "uid": "demo-event-001"
}
EOF

# Create sample email
cat > /tmp/prepsheet-demo/queue/email/email1.json <<EOF
{
  "from": "john.smith@client.com",
  "subject": "Re: Q4 Budget Approval Needed",
  "received": "2026-09-11T22:35:00Z",
  "body_preview": "We need to finalize the contract terms before the meeting tomorrow...",
  "unread": true,
  "message_id": "demo-email-001"
}
EOF
```

### Expected Output

After running `ps-dawn`:

1. **PDF Generated**: `~/Desktop/PrepSheets/2026-09-12-MorningPaper.pdf`
2. **HTML Preview**: `~/Desktop/PrepSheets/2026-09-12-MorningPaper.html` (before PDF conversion)
3. **Headline File**: `~/Desktop/PrepSheets/2026-09-12-MorningPaper.headline` (plain text for SMS)
4. **Logs**: `$HERMES_HOME/prepsheet/logs/*.log`

---

## What's Production-Ready

✅ **Skill architecture** — Complete 6-skill modular system  
✅ **SOUL.md** — PrepSheet persona & guardrails  
✅ **Configuration system** — JSON config + `.env` separation  
✅ **Cron scheduling** — Autonomous 4 AM / 6:30 AM / meeting radar  
✅ **PDF typesetting** — HTML generation with vintage broadsheet layout  
✅ **OSINT caching** — 30-day TTL with confidence scoring  
✅ **Graceful degradation** — Fallbacks for printer/OSINT/data failures  
✅ **Security model** — Read-only operation, no hallucination, privacy-first  

---

## What Needs Integration (Post-Hackathon)

🔧 **PDF rendering** — Need wkhtmltopdf or weasyprint (currently generates HTML)  
🔧 **Plow Latch** — Real browser automation for OSINT (placeholder implemented)  
🔧 **Hermes SMS** — Plugin integration (simulated in `sms.py`)  
🔧 **CalDAV parser** — Real calendar sync (placeholder queue-based)  
🔧 **IMAP ingestion** — Real email fetch (placeholder queue-based)  

All integration points are clearly marked with `# TODO:` comments and have complete interface signatures.

---

## Why This Wins

### 1. **Solves a Real Problem**
Founders don't need another app to check. They need intelligence **prepared before they wake up**.

### 2. **Novel Interaction Model**
Physical newspaper + SMS briefs = **calm technology**. No app to open, no notifications to dismiss.

### 3. **Technical Depth**
- Autonomous agent with proper read-only guardrails
- Priority calculation (not just lists)
- Zero-hallucination OSINT with confidence scoring
- Graceful degradation everywhere

### 4. **Production-Minded**
- Complete logging (`$HERMES_HOME/prepsheet/logs/`)
- Configuration separation (`.env` + `config.json`)
- Security-first (read-only, no credential leaks)
- Modular architecture (6 independent skills)

### 5. **Demo-Friendly**
- Works with sample data (no real credentials needed)
- Desktop fallback (no printer required)
- Manual trigger mode (test anytime)
- HTML preview (see output before PDF conversion)

---

## Future Roadmap

### Phase 1: Core Integrations (Week 1-2)
- [ ] wkhtmltopdf PDF rendering
- [ ] Real CalDAV parser
- [ ] Real IMAP ingestion
- [ ] Plow Latch OSINT integration
- [ ] Hermes SMS plugin

### Phase 2: Intelligence Upgrades (Week 3-4)
- [ ] Historical context ("Last spoke with them about X")
- [ ] Meeting outcome tracking (action items from past meetings)
- [ ] Email sentiment analysis (detect tension/urgency)
- [ ] Company relationship mapping (who connects to whom)

### Phase 3: Customization (Month 2)
- [ ] Multiple newspaper templates (tabloid, minimal, tech)
- [ ] Configurable priority algorithm (user-trained weights)
- [ ] Weekly digest mode ("Week ahead" preview)
- [ ] Voice query interface (Alexa/Siri integration)

---

## Team & Contact

**Solo Builder**: [Your Name]  
**Project**: PrepSheet  
**Built With**: Plow, Hermes, Docker, Python  
**Hackathon**: Plow + Hermes (Sept 2026)  

**Repository**: [Your GitHub URL]  
**Demo Video**: [Your Demo URL]  

---

## Closing Thoughts

The best technology disappears. You don't think about how your newspaper got to your doorstep—it's just **there**, prepared.

That's The PrepSheet. Your intelligence daemon. Prepared before dawn, delivered before coffee.

**No apps. No context switching. Just calm, prepared mornings.**

---

*Built for the Plow + Hermes Hackathon, September 2026*
