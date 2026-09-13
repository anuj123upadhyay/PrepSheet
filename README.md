# The PrepSheet

**An autonomous executive chief of staff and intelligence daemon**

The PrepSheet reclaims your morning focus by converting raw calendar invites, unread emails, and external web intelligence into a tangible, vintage-style physical "Morning Newspaper" delivered before dawn, supplemented by automated meeting dossiers throughout the day.

Built with **Plow** and **Hermes** for the hackathon.

---

## What It Does

### 1. The 04:00 AM Dawn Broadside (Daily Autonomous Run)

Every morning at 4 AM, The PrepSheet:

- **Ingests** today's calendar events and unread VIP emails (read-only)
- **Enriches** external attendees with public OSINT (LinkedIn, Crunchbase, recent news)
- **Calculates** the single most critical priority for your front-page headline
- **Generates** a vintage three-column broadsheet PDF:
  - **Left**: Daily chronological agenda
  - **Center**: Meeting intelligence & strategic talking points  
  - **Right**: Urgent email triage
- **Prints** the paper physically (or saves to `~/Desktop/PrepSheets/` if no printer)
- **Sends SMS** at 6:30 AM: *"Your PrepSheet is ready on your desk"*

### 2. The 30-Minute Meeting Radar (Just-In-Time Dossiers)

Continuously monitors your calendar. Exactly 30 minutes before external meetings:

- **Audits** recent email exchanges with attendees
- **Generates** a focused one-page dossier with attendee backgrounds
- **Saves** to `~/Desktop/PrepSheets/[Date]-[MeetingName].pdf`
- **Sends SMS** with a 3-bullet executive brief and file path

### 3. On-Demand Executive Queries (SMS Loop)

Respond to texts like:

- **"WHO IS Sarah from Acme?"** → 3-sentence OSINT summary
- **"NEXT"** → Next meeting brief with dossier link
- **"DIGEST"** → Resend today's headline
- **"URGENT Client Corp"** → Immediate dossier generation

---

## Installation & Setup

### Prerequisites

- Docker & Docker Compose
- Calendar access (CalDAV URL or local `.ics` export)
- Email access (IMAP credentials)
- *Optional:* Local printer (CUPS configured)
- *Optional:* Hermes SMS integration

### Quick Start

1. **Clone and configure:**

```bash
cd PrepSheet-Folder/PrepSheet
cp .env.example .env
# Edit .env with your calendar URL and email credentials
```

2. **Build and start:**

```bash
docker compose build
docker compose up -d
```

3. **Initial setup conversation:**

Send your first message to The PrepSheet agent via Hermes. It will guide you through:

- Calendar/email confirmation
- PDF archive path (default: `~/Desktop/PrepSheets/`)
- Printer setup (or Desktop-only fallback)
- SMS preferences
- VIP sender list

4. **Test the pipeline:**

```bash
# Manually trigger morning paper generation
docker compose exec agent hermes skill invoke ps-dawn
```

---

## Architecture

### Skills

- **`ps-setup`**: Initial configuration wizard
- **`ps-dawn`**: Morning newspaper generator (4 AM cron)
- **`ps-dossier`**: Meeting radar & dossier generation (30-min trigger)
- **`ps-query`**: On-demand SMS queries (WHO IS, NEXT, DIGEST, URGENT)
- **`ps-osint`**: Zero-hallucination OSINT engine (LinkedIn, Crunchbase, news)
- **`ps-shared`**: Shared scripts (calendar/email ingestion, typesetter, printer, SMS)

### Data Flow

```
Calendar/Email (Read-Only)
  ↓
Queue Directory ($HERMES_HOME/prepsheet/queue/)
  ↓
Ingestion Scripts (calendar_ingest.py, email_ingest.py)
  ↓
OSINT Enrichment (osint_lookup.py via Plow Latch)
  ↓
Typesetter (typesetter.py → Vintage PDF)
  ↓
Printer (printer.py → CUPS) OR Desktop  Folder PDF


```

### Autonomous Scheduling

The PrepSheet runs on these cron jobs (configured in `ps-setup`):

- `0 4 * * *` — Dawn broadside generation
- `30 6 * * *` — SMS notification (if paper was generated)
- `*/15 * * * *` — Meeting radar (checks for upcoming meetings)

---

## Configuration

Located at `$HERMES_HOME/prepsheet/config.json`:

```json
{
  "dawn_hour": 4,
  "sms_notify_hour": 6.5,
  "sms_enabled": true,
  "pdf_archive_path": "~/Desktop/PrepSheets",
  "printer_enabled": true,
  "printer_name": "default",
  "vip_senders": ["client.com", "ceo@mycompany.com"],
  "meeting_radar_minutes": 30,
  "osint_blacklist": []
}
```

### Environment Variables (`.env`)

```bash
# Calendar Access
CALENDAR_URL=https://caldav.provider.com/user/calendar

# Email Access (IMAP)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your@email.com
IMAP_PASSWORD=your-app-password

# Hermes SMS (if enabled)
HERMES_SMS_ENABLED=true
HERMES_SMS_NUMBER=+1234567890
```

---

## The Vintage Typesetting Standard

Every PDF follows the broadsheet format:

- **Three-column layout** with serif typography (Garamond)
- **Front-page banner headline** (48pt bold) featuring the day's priority
- **Section rules** (thin horizontal lines) separating content
- **Black on white only** for reliable printing
- **Archival footer** with generation timestamp and file path

---

## Privacy & Security

### Read-Only Operation

The PrepSheet **never**:

- Deletes, moves, or archives emails
- Accepts, declines, or modifies calendar invites
- Sends emails or responses
- Accesses financial accounts or payment systems
- Stores passwords in chat (only in `.env` or credential files)

### Zero-Hallucination OSINT

When gathering attendee backgrounds:

- **Only verified public sources**: LinkedIn, Crunchbase, company websites, Google News
- **No personal contact info**: Never extracts phone numbers or addresses
- **Explicit uncertainty**: States "No public record found" when data doesn't exist
- **30-day cache**: Avoids redundant lookups, respects rate limits

### Data Storage

- **Calendar/email queue**: Temporary, deleted after processing
- **OSINT cache**: 30-day TTL, public data only
- **PDFs**: Saved to local Desktop (user-controlled)
- **Logs**: Structured JSON in `$HERMES_HOME/prepsheet/logs/`

---

## Development & Customization

### Running Scripts Manually

All scripts in `ps-shared/scripts/` can be run standalone:

```bash
# Test calendar ingestion
python3 ps-shared/scripts/calendar_ingest.py --date today

# Test OSINT lookup
python3 ps-shared/scripts/osint_lookup.py \
  --attendee "test@example.com" \
  --domain "example.com" \
  --verbose

# Test PDF generation
python3 ps-shared/scripts/typesetter.py \
  --mode paper \
  --events events.json \
  --emails emails.json \
  --headline "Test Headline" \
  --output ~/Desktop/test.pdf
```

### Adding Custom Templates

Edit `ps-shared/scripts/typesetter.py` to customize:

- Font families (currently Garamond)
- Column widths
- Color schemes (keep black/white for printing)
- Section layouts

### Extending OSINT Sources

Add new data sources in `ps-shared/scripts/osint_lookup.py`:

```python
def custom_research(domain):
    """Your custom research function"""
    # Use Plow Latch to search additional sources
    results = plow_latch_search(f"{domain} your-query", domain="your-source.com")
    return parsed_results
```

---

## Troubleshooting

### "No calendar events found"

- Check `$HERMES_HOME/prepsheet/queue/calendar/` is populated
- Verify `CALENDAR_URL` in `.env` is correct
- Test calendar access: `python3 ps-shared/scripts/calendar_ingest.py --date today`

### "Printer unavailable"

- This is **not an error** — PDFs save to Desktop automatically
- To enable printing, ensure CUPS is installed: `apt-get install cups cups-client`
- Test printer: `echo "test" | lp -d default`

### "SMS not sending"

- Check `sms_enabled: true` in config
- Verify Hermes SMS credentials in `.env`
- Check logs: `$HERMES_HOME/prepsheet/logs/sms_sent.log`

### "OSINT lookups returning empty"

- Plow Latch integration is placeholder in initial build
- Check `$HERMES_HOME/prepsheet/osint_cache.json` for cached data
- Run with `--verbose` flag to see source hits/misses

---

## Hackathon Notes

### What's Implemented

✅ Complete skill architecture (6 skills + shared scripts)  
✅ Calendar & email ingestion (placeholders ready for real integration)  
✅ OSINT lookup framework with 30-day caching  
✅ Vintage PDF typesetter (HTML → PDF conversion pending)  
✅ Printer integration with Desktop fallback  
✅ SMS wrapper with rate limiting  
✅ Meeting radar monitoring  
✅ Cron job scheduling  

### What Needs Integration

🔧 **Plow Latch** for web research (current: placeholder)  
🔧 **PDF rendering** (need wkhtmltopdf or weasyprint)  
🔧 **Hermes SMS** plugin (current: simulated)  
🔧 **Real calendar parser** (CalDAV or `.ics` import)  
🔧 **Real IMAP ingestion** (current: queue-based placeholder)  

### Quick Wins for Demo

1. **Manual trigger**: `docker compose exec agent hermes skill invoke ps-dawn`
2. **Sample data**: Pre-populate queue with mock events/emails
3. **HTML preview**: View `.html` files before PDF conversion
4. **Desktop fallback**: Always works, even without printer

---

## License

See `LICENSE` and `NOTICE` files.

---

## Credits

Built with:

- **Plow** - Local-first agent infrastructure
- **Hermes** - Agent conversation framework
- **Docker** - Containerized deployment

Inspired by the need for calm, prepared mornings in the chaos of founder schedules.

---

**The PrepSheet** — Your intelligence daemon. Prepared before dawn, delivered before coffee.
