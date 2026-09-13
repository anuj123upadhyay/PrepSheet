---
name: ps-setup
description: First conversation. Configure calendar/email access, printer, SMS alerts, and enable the dawn intelligence engine.
---

# Bring The PrepSheet online

The calendar and email ingestion run via read-only access configured in `.env`. The printer daemon connects to the local CUPS service. **Never ask for passwords in chat**—they belong in `.env` or credential files only.

If `$HERMES_HOME/prepsheet/config.json` already exists, this is a reconfiguration.

## What to ask

1. **What time to generate the morning paper.** Default 04:00 AM for printing before dawn, with SMS notification at 06:30 AM. Explain that most preparation happens silently—the paper only prints when there are meetings or urgent emails that day.

2. **Where to save PrepSheet PDFs.** Default `~/Desktop/PrepSheets/`. Confirm the path exists or offer to create it. Every paper is archived as `[Date]-MorningPaper.pdf`, and meeting dossiers as `[Date]-[MeetingName].pdf`.

3. **Whether they have a printer configured.** If yes, test with a blank page via CUPS. If no printer is available, all PDFs save to Desktop only (this is the fallback, not a failure—tell them the paper will be there when they wake up).

4. **SMS notification preferences.** The Hermes telephony plugin sends:
   - 06:30 AM: "Your PrepSheet is ready" (only if there were events/emails to process)
   - 30 min before meetings: 3-bullet executive brief with dossier path
   - Responses to on-demand queries (WHO IS, NEXT, DIGEST, URGENT)
   
   Ask if they want SMS enabled and confirm the phone number from their Hermes config.

5. **Which email senders are VIPs.** Ask for a short list of domains or sender names that signal urgent/important (e.g., "client domains", "ceo@company", "billing@"). These drive the "Urgent Email Triage" column. Optional—if they skip it, you'll use heuristics (unread + subject keywords like "urgent", "decision", "approval").

6. **Calendar access confirmation.** Verify that `$HERMES_HOME/prepsheet/queue/calendar/` is receiving events. If empty and no errors, the calendar integration hasn't started yet. Don't proceed with scheduling until you see at least one event file.

Don't ask for more. No credit cards, no bank accounts, no API keys in chat—you don't need them and must never store them from a message.

## One important clarification

The intelligence archive starts empty. It only sees calendar events and emails **from now forward**. A meeting from last month isn't in the new system. Tell them: "The PrepSheet gets smarter after the first full week—think of this first week as the learning period."

Underpromise now so they trust what you deliver later.

## Write the configuration

```json
{
  "dawn_hour": 4,
  "sms_notify_hour": 6.5,
  "sms_enabled": true,
  "pdf_archive_path": "~/Desktop/PrepSheets",
  "printer_enabled": true,
  "printer_name": "default",
  "vip_senders": ["client.com", "ceo@mycompany.com"],
  "meeting_radar_minutes": 30
}
```

Save to `$HERMES_HOME/prepsheet/config.json`.

Create the archive directory:
```bash
mkdir -p ~/Desktop/PrepSheets
```

## Initialize the intelligence stores

Create empty structures for the daemon to populate:

```bash
mkdir -p "$HERMES_HOME/prepsheet/queue/calendar"
mkdir -p "$HERMES_HOME/prepsheet/queue/email"
mkdir -p "$HERMES_HOME/prepsheet/osint_cache"
echo '{}' > "$HERMES_HOME/prepsheet/osint_cache.json"
echo '[]' > "$HERMES_HOME/prepsheet/meeting_history.json"
```

## Register the cron jobs

The dawn broadside (daily paper):
```bash
hermes cron create "0 4 * * *" \
  "Generate the morning PrepSheet now: ingest today's calendar and unread emails, run OSINT enrichment, synthesize the headline priority, render the vintage newspaper PDF, print (or save to Desktop), and archive." \
  --name ps-dawn --skill ps-dawn
```

The SMS notification (sent only if the morning paper was generated):
```bash
hermes cron create "30 6 * * *" \
  "If a morning paper was generated today, send the SMS notification to alert the owner it's ready." \
  --name ps-dawn-notify --skill ps-dawn --deliver
```

Check existing jobs first:
```bash
hermes cron list
```

If `ps-dawn` or `ps-dawn-notify` already exist, don't recreate them.

## If calendar/email ingestion has no credentials

The container starts even without `.env`—by design, so the missing config becomes your message, not a Docker error.

If `$HERMES_HOME/prepsheet/queue/calendar/` is empty and logs show `missing CALENDAR_URL` or `missing IMAP_HOST`, say this in one line:

> I can't reach your calendar or email yet—you'll need to add those credentials to the `.env` file in the project directory. Copy `.env.example` to `.env`, fill in your calendar URL and email app password, then run `docker compose up -d` again. I'll confirm when the first events arrive.

**Do not** try to configure anything yourself and **do not** proceed with scheduling. Without live data, everything you set up is hypothetical.

## Test the printer

If they said they have a printer configured:

```bash
echo "PrepSheet test print - $(date)" | lp -d default
```

If this succeeds, confirm: "Printer test succeeded—your morning papers will print automatically."

If it fails, confirm: "No printer detected—all PrepSheets will be saved to `~/Desktop/PrepSheets/` instead. You'll get the same intelligence, just on-screen instead of on-paper."

This is the fallback, not a failure. The product works either way.

## Final confirmation

Summarize in one message:
- Morning paper generated at [time], SMS alert at [time]
- PDFs archived to [path]
- Printer status: [enabled/Desktop-only]
- VIP senders: [list or "auto-detected"]
- Meeting radar active: [minutes] before external meetings

Then: "You're all set. I'll generate the first PrepSheet tomorrow morning. If you want to test it now, say 'run dawn' and I'll create a sample based on what's in your calendar today."
