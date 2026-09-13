# PrepSheet Development Guide

Quick reference for developers working on The PrepSheet.

---

## Project Structure

```
PrepSheet/
├── runtime/
│   └── SOUL.md                 # Agent persona & core principles
├── ps-setup/                   # Initial configuration wizard
│   └── SKILL.md
├── ps-dawn/                    # Morning newspaper generator
│   └── SKILL.md
├── ps-dossier/                 # Meeting radar & dossiers
│   └── SKILL.md
├── ps-query/                   # On-demand SMS queries
│   └── SKILL.md
├── ps-osint/                   # OSINT intelligence engine
│   └── SKILL.md
├── ps-shared/                  # Shared infrastructure
│   ├── SKILL.md
│   └── scripts/
│       ├── calendar_ingest.py   # Calendar parsing
│       ├── email_ingest.py      # Email extraction
│       ├── osint_lookup.py      # OSINT research
│       ├── typesetter.py        # PDF generation
│       ├── printer.py           # CUPS interface
│       ├── sms.py               # SMS wrapper
│       └── meeting_monitor.py   # Continuous radar
├── Dockerfile                  # Container image
├── compose.yml                 # Docker Compose config
├── .env.example                # Environment template