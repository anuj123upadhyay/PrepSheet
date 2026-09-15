# PrepSheet Development Guide

Quick reference for developers working on The PrepSheet.

---

## Project Structure

```
PrepSheet/
├── runtime/
│   └── SOUL.md                 # Agent persona & conversational protocols
├── ps-setup/                   # Conversational onboarding & configuration
│   └── SKILL.md
├── ps-dawn/                    # Morning newspaper broadside (6:00 AM)
│   └── SKILL.md
├── ps-dossier/                 # Meeting radar & just-in-time dossiers
│   └── SKILL.md
├── ps-query/                   # On-demand conversational queries (WHO IS, NEXT, DIGEST, URGENT)
│   └── SKILL.md
├── ps-schedule/                # Conversational meeting scheduler
│   └── SKILL.md
├── ps-osint/                   # Zero-hallucination OSINT intelligence via Plow Latch
│   └── SKILL.md
├── ps-shared/                  # Shared infrastructure toolbox
│   ├── SKILL.md
│   └── scripts/
│       ├── mac_calendar_simple.py   # Native EventKit calendar read/create
│       ├── osint_cache.py           # 30-day OSINT cache manager
│       ├── osint_lookup.py          # Fast profile lookup and cache matcher
│       ├── typesetter.py            # Vintage broadsheet PDF & HTML layout
│       ├── sms.py                   # Outbound SMS wrapper & rate-limiter
│       └── meeting_monitor.py       # Continuous 30-min meeting radar
├── Dockerfile                  # Container image
├── compose.yml                 # Docker Compose config
├── plow-credentials           # Plow Latch credential hook
└── START_HERE.md               # Quickstart guide
```

---

## Testing Skills & Scripts Locally

```bash
# Test Mac calendar access
python3 ps-shared/scripts/mac_calendar_simple.py --action read --date today

# Test next upcoming meeting
python3 ps-shared/scripts/mac_calendar_simple.py --action read --date today --next-only

# Test OSINT cache check
python3 ps-shared/scripts/osint_cache.py --check "test@example.com"

# Test meeting monitor
python3 ps-shared/scripts/meeting_monitor.py

# Test typesetter help
python3 ps-shared/scripts/typesetter.py --help
```