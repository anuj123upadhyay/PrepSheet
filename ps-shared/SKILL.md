---
name: ps-shared
description: Shared scripts for PrepSheet: calendar/email ingestion, OSINT lookup, PDF typesetting, printer, SMS.
---

# PrepSheet toolbox

This directory is not a procedure—it's the toolbox that other PrepSheet skills call. Nothing here executes "because the skill was loaded"; each script has a named caller.

## `scripts/calendar_ingest.py`

Read-only calendar parsing via CalDAV or local `.ics` files. Extracts events for a given date range and identifies external attendees.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/calendar_ingest.py" --date today
python3 "$HERMES_HOME/skills/ps-shared/scripts/calendar_ingest.py" --date 2026-09-15
python3 "$HERMES_HOME/skills/ps-shared/scripts/calendar_ingest.py" --next-only
```

**Output:** JSON array of events with `time`, `title`, `attendees`, `external_domains`, `duration_min`, `location`.

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`

## `scripts/email_ingest.py`

Read-only IMAP email extraction. Fetches unread messages, filters by VIP senders, and groups by thread.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/email_ingest.py" --vip-only --since 24h
python3 "$HERMES_HOME/skills/ps-shared/scripts/email_ingest.py" --participants "john@client.com" --since 7d --threads
```

**Output:** JSON array of emails with `from`, `subject`, `received`, `preview`, `urgency_score`.

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`

## `scripts/osint_lookup.py`

Zero-hallucination OSINT via Plow Latch. Searches LinkedIn, Crunchbase, company sites, and recent news.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --attendee "john.smith@client.com" \
  --domain "client.com" \
  --cache-ttl 30

python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" \
  --search "Sarah" \
  --domain "acme.com" \
  --cache-only
```

**Output:** JSON profile with `name`, `title`, `company`, `company_news`, `linkedin_url`, `confidence`.

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`, `ps-osint`

## `scripts/typesetter.py`

Vintage broadsheet PDF generator. Three-column layout with serif typography (Garamond), section rules, and print-ready output.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --events events.json \
  --emails emails.json \
  --osint osint.json \
  --headline "Q4 Strategy Review with Client Corp" \
  --output "$HOME/Desktop/PrepSheets/2026-09-12-MorningPaper.pdf"

python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --mode dossier \
  --meeting meeting.json \
  --emails email_context.json \
  --osint osint.json \
  --output "$HOME/Desktop/PrepSheets/2026-09-12-Q4StrategyReview.pdf"
```

**Output:** Print-ready PDF (black on white, no color) and a `.headline` text file for SMS retrieval.

**Called by:** `ps-dawn`, `ps-dossier`

## `scripts/printer.py`

CUPS print daemon interface. Sends PDF to the configured printer or confirms Desktop-only fallback.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/printer.py" \
  --file "$HOME/Desktop/PrepSheets/2026-09-12-MorningPaper.pdf" \
  --printer-name "default"
```

**Output:** Success/failure status, logged to `$HERMES_HOME/prepsheet/printer.log`.

**Called by:** `ps-dawn`, `ps-dossier` (optional)

## `scripts/sms.py`

Hermes telephony wrapper. Sends SMS notifications with rate limiting and retry logic.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/sms.py" "Good morning. Your PrepSheet is ready."
echo "Message body" | python3 "$HERMES_HOME/skills/ps-shared/scripts/sms.py"
```

**Output:** Delivery confirmation or queued retry if service unavailable.

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`

## `scripts/meeting_monitor.py`

Continuous calendar monitor for the 30-minute meeting radar. Runs on a 15-minute cron interval.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/meeting_monitor.py"
```

**Output:** Triggers `ps-dossier` skill for upcoming external meetings.

**Called by:** System cron (configured in `ps-setup`)

## Path discipline

Always call scripts via `$HERMES_HOME/skills/ps-shared/scripts/...`.

The image delivers skills to `/opt/hermes/skills`, the runtime reconciles them to `$HERMES_HOME/skills`, and the latter is what an executing agent finds. A skill that hardcodes `/opt/hermes` works at build time and fails later.

The root-owned copy in `/opt/plow/ps-shared/` exists for what runs alone under the supervisor. It's not yours to call—what you run inside a turn comes from the home; what runs without anyone watching comes from `/opt/plow`, and that separation prevents a single prompt-injection edit from becoming scheduled code.

## Configuration reference

All scripts read from `$HERMES_HOME/prepsheet/config.json`:

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

Never hardcode paths, hours, or preferences—always read from config.

## Error logging

All scripts log to `$HERMES_HOME/prepsheet/logs/[script_name].log` with ISO 8601 timestamps and structured JSON entries:

```json
{"timestamp": "2026-09-12T04:05:13Z", "script": "calendar_ingest", "level": "INFO", "message": "Parsed 5 events for 2026-09-12"}
{"timestamp": "2026-09-12T04:05:18Z", "script": "osint_lookup", "level": "WARN", "message": "Rate limit hit for linkedin.com, using cache"}
```

This makes debugging autonomous runs tractable—the owner can see exactly what happened at 4 AM without being awake for it.
