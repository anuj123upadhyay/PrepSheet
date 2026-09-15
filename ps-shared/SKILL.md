---
name: ps-shared
description: Shared toolbox for PrepSheet: Mac calendar access, OSINT cache, PDF typesetting, and SMS alerts.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, toolbox, typesetter, osint, calendar, sms]
---

# PrepSheet Toolbox

This directory is the core utility toolkit that other PrepSheet skills invoke. Web browsing, email scanning, and Google Calendar operations are driven directly through **Plow Latch**, while the local utilities below handle system-level execution.

---

## `scripts/mac_calendar_simple.py`

Native macOS EventKit integration. Reads calendar events, classifies internal vs. external attendees using `config.json`, and creates new events.

**Usage:**
```bash
# Read today's events (JSON output with external attendees and meeting_id)
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" --action read --date today

# Read next upcoming meeting only
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" --action read --date today --next-only

# Search for meetings with a specific attendee or company domain
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" --action read --search-attendee "acme.com"

# Create a new event
python3 "$HERMES_HOME/skills/ps-shared/scripts/mac_calendar_simple.py" \
  --action create \
  --title "Strategy Sync" \
  --start "2026-09-16 14:00" \
  --duration 60 \
  --attendees "john@acme.com" \
  --location "Google Meet"
```

**Output:** Standardized JSON with `time`, `title`, `attendees`, `external_attendees`, `external_domains`, `duration_min`, `location`, `meeting_id`.

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`, `ps-schedule`, `meeting_monitor.py`

---

## `scripts/osint_cache.py`

Lightweight 30-day cache manager for OSINT profile lookups, stored at `~/.hermes/prepsheet/osint_cache.json`.

**Usage:**
```bash
# Check if an email is cached and fresh (<30 days)
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_cache.py" --check "john@acme.com"

# Save an OSINT profile into cache with a custom TTL (default 30 days)
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_cache.py" \
  --save "john@acme.com" \
  --data '{"name": "John Smith", "title": "VP of Eng", "company": "Acme Corp"}' \
  --ttl 30
```

**Called by:** `ps-osint`, `ps-query`

---

## `scripts/osint_lookup.py`

Profile synthesis and fast lookup tool. Checks cache first, formats profile structure, and respects blacklists.

**Usage:**
```bash
# Search cached profiles by name or domain
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" --search "Sarah" --domain "acme.com"

# Inspect profile with cache-only flag
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_lookup.py" --attendee "sarah@acme.com" --cache-only
```

**Called by:** `ps-osint`, `ps-query`, `ps-dawn`, `ps-dossier`

---

## `scripts/typesetter.py`

Vintage broadsheet layout engine. Renders print-ready PDFs using **WeasyPrint, which is pre-installed in this container**. Output goes directly to `~/Desktop/PrepSheets/` which is bind-mounted to the Mac's Desktop — the file appears on the Mac instantly with no transfer step.

> **CRITICAL: Do NOT attempt to transfer files to the Mac. Do NOT try base64 encoding, Safari automation, Homebrew installation, plow_write_file chunking, or any other workaround. WeasyPrint works inside this container. Just run typesetter.py and the PDF appears on the Mac desktop automatically via the volume mount.**

**Temp files must be written to `/var/lib/hermes/tmp/`** (inside `HERMES_WRITE_SAFE_ROOT`). Never use `/tmp/`.

**Usage:**
```bash
# Always create the staging directory first
mkdir -p /var/lib/hermes/tmp
mkdir -p "$HOME/Desktop/PrepSheets"

# Render Morning Paper
python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --mode paper \
  --events /var/lib/hermes/tmp/events.json \
  --emails /var/lib/hermes/tmp/emails.json \
  --osint  /var/lib/hermes/tmp/osint.json \
  --headline "Q4 Strategy Review with Acme Corp" \
  --output "$HOME/Desktop/PrepSheets/$(date +%Y-%m-%d)-MorningPrepsheet.pdf"

# Render Meeting Dossier
python3 "$HERMES_HOME/skills/ps-shared/scripts/typesetter.py" \
  --mode dossier \
  --meeting /var/lib/hermes/tmp/meeting.json \
  --emails  /var/lib/hermes/tmp/email_context.json \
  --osint   /var/lib/hermes/tmp/osint.json \
  --output "$HOME/Desktop/PrepSheets/$(date +%Y-%m-%d)-AcmeCorp-meeting-dossier.pdf"
```

**What happens:**
1. typesetter.py generates HTML and calls WeasyPrint (installed at `/opt/hermes/.venv`)
2. WeasyPrint renders the PDF entirely inside the container
3. The PDF lands at `/root/Desktop/PrepSheets/` in the container = `~/Desktop/PrepSheets/` on the Mac (bind-mount)
4. Done. No transfer, no Mac-side tools needed.

**Called by:** `ps-dawn`, `ps-dossier`

---

## `scripts/sms.py`

Outbound executive telephony wrapper. Dispatches SMS messages with built-in rate-limiting (5 messages / 10 minutes) and audit logging.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/sms.py" "Good morning. Your PrepSheet is ready on your desk."
```

**Called by:** `ps-dawn`, `ps-dossier`, `ps-query`

---

## `scripts/meeting_monitor.py`

Continuous background calendar radar. Checks for upcoming external meetings in the 30-minute radar window and prepares context for `ps-dossier`.

**Usage:**
```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/meeting_monitor.py"
```

**Called by:** System cron / daemon interval

---

## Configuration Standard

All scripts and skills read from `$HERMES_HOME/prepsheet/config.json`:

```json
{
  "internal_domains": ["mycompany.com"],
  "vip_senders": ["client.com", "investor@vc.com"],
  "calendar_sources": ["mac", "plow-google"],
  "dawn_hour": 6,
  "meeting_radar_minutes": 30,
  "pdf_archive_path": "~/Desktop/PrepSheets",
  "sms_enabled": true,
  "osint_blacklist": []
}
```

- `internal_domains`: Your team's email domains. Anyone not matching this list is classified as external and triggers research/dossiers.
- `pdf_archive_path`: Standardized destination for all output PDFs and HTML briefs.
