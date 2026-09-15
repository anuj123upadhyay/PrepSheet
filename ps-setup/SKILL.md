---
name: ps-setup
description: Conversational onboarding wizard. Configure domains, VIP senders, schedule preferences, and initialize PrepSheet.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, setup, onboarding, configuration]
    related_skills: [ps-shared]
---

# Conversational Setup Wizard

This skill runs during the executive's first conversation with The PrepSheet (or upon asking to "reconfigure settings").
Because PrepSheet connects via **Plow Latch** (leveraging authenticated browser sessions) and native Mac Calendar, **no API keys or email passwords are ever requested in chat**.

---

## Onboarding Conversation Flow

Guide the executive through 4 quick, high-signal questions:

### 1. Internal Team Domains
> "What are your company's primary email domains? (e.g., `mycompany.com`)"
- **Why**: Anyone with an email outside these domains is classified as an external attendee, triggering attendee background research and dossiers. Internal meetings are kept clean of unnecessary dossiers.

### 2. Morning Paper Timing
> "What time would you like your morning broadside prepared? (Default is 6:00 AM)"
- **Why**: Configures the daily autonomous intelligence engine.

### 3. VIP Senders
> "Are there key domains or executive senders you'd like highlighted in your Urgent Email Triage? (e.g., `keyclient.com`, `board@`, `investor@`)"
- **Why**: Directs the priority scoring algorithm for the front-page headline.

### 4. PDF Archive Directory
> "By default, papers and dossiers save to `~/Desktop/PrepSheets/`. Does that work for you?"
- **Why**: Creates a central, accessible folder on the executive's desktop.

---

## Writing the Configuration

Save the responses to `$HERMES_HOME/prepsheet/config.json`:

```json
{
  "internal_domains": ["mycompany.com"],
  "vip_senders": ["keyclient.com", "investor@vc.com"],
  "calendar_sources": ["mac", "plow-google"],
  "dawn_hour": 6,
  "meeting_radar_minutes": 30,
  "pdf_archive_path": "~/Desktop/PrepSheets",
  "sms_enabled": true,
  "use_plow_latch": true,
  "osint_blacklist": []
}
```

---

## Directory Initialization

Initialize the desktop archive and cache stores:

```bash
mkdir -p "$HOME/Desktop/PrepSheets"
mkdir -p "$HERMES_HOME/prepsheet/logs"
echo '{}' > "$HERMES_HOME/prepsheet/osint_cache.json"
echo '[]' > "$HERMES_HOME/prepsheet/dossier_log.json"
```

---

## Register Autonomous Tasks

Register the 6:00 AM dawn cron job:

```bash
hermes cron create "0 6 * * *" \
  "Generate the morning PrepSheet: ingest today's calendar and unread VIP emails, research external attendees, synthesize the headline priority, and render the vintage broadside PDF." \
  --name ps-dawn --skill ps-dawn
```

---

## Completion Confirmation

Confirm setup in a single crisp message:
```
✓ The PrepSheet is now online and active:
• Morning Broadside: 6:00 AM daily
• Archive Directory: ~/Desktop/PrepSheets/
• Internal Domains: mycompany.com (external attendees will be prepped)
• Meeting Radar: Active 30 minutes before all external meetings

Say "Generate my morning PrepSheet" anytime to produce an immediate sample.
```
