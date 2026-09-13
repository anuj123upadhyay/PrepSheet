---
name: ps-osint
description: Zero-hallucination OSINT research on meeting attendees via Plow Latch.
version: 2.0.0
author: PrepSheet
metadata:
  hermes:
    tags: [prepsheet, osint, research, linkedin, companies]
    related_skills: [ps-shared]
---

# OSINT Research (via Plow Latch)

Research external meeting attendees using only verified public sources through Plow Latch.
**Never hallucinate.** If data doesn't exist, say so explicitly.

## Data sources (via Plow)

All accessed through Plow Latch (using your logged-in browser sessions):

1. **LinkedIn** - Job title, company, employment history
2. **Company websites** - About page, leadership
3. **Crunchbase** - Funding, valuation, investors
4. **Google News** - Recent articles (past 90 days)
5. **GitHub** - For technical roles

## Check cache first

Before any lookup, check `~/.hermes/prepsheet/osint_cache.json`:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_cache.py" \
  --check "john@acme.com"
```

If cached entry exists and is fresh (<30 days), return immediately. **No redundant lookups.**

## LinkedIn search via Plow

```bash
# Navigate to LinkedIn (already logged in)
rote browser navigate "https://www.linkedin.com/search/results/people/?keywords=John%20Smith%20Acme%20Corp"
rote browser wait 2000

# Extract first result
rote browser eval 'JSON.stringify({
  name: document.querySelector(".entity-result__title-text")?.textContent?.trim(),
  title: document.querySelector(".entity-result__primary-subtitle")?.textContent?.trim(),
  company: document.querySelector(".entity-result__secondary-subtitle")?.textContent?.trim(),
  profile_url: document.querySelector(".app-aware-link")?.href
})'
```

Verify email domain matches company name. If multiple matches, prefer most recent profile.

## Company research via Plow

```bash
# Company website
rote browser navigate "https://acme.com/about"
rote browser wait 2000
rote browser eval 'document.querySelector("main")?.textContent'

# Extract: company description (one sentence), industry, HQ location
```

## Crunchbase via Plow

```bash
rote browser navigate "https://www.crunchbase.com/organization/acme-corp"
rote browser wait 2000

# Extract: latest funding round, amount, date, total funding, investors
```

If no Crunchbase entry, note: `"funding": "private or not disclosed"`

## Recent news via Plow

```bash
# Google News search
rote browser navigate "https://news.google.com/search?q=Acme%20Corp&hl=en-US&gl=US&ceid=US:en"
rote browser wait 2000

# Extract top 3 relevant articles (funding, product launches, partnerships)
# Ignore: blog posts, webinars, generic press releases
```

Select the single most relevant item (usually most recent funding/product news).

## Confidence scoring

- **High**: LinkedIn confirmed, company info verified, recent news found
- **Medium**: LinkedIn or company found, but incomplete
- **Low**: Minimal public footprint, inferred from domain only
- **None**: No public record found

If confidence is "None":

```json
{
  "name": "Unknown",
  "company": "acme.com",
  "note": "No public record found—internal contact or private profile",
  "confidence": "none"
}
```

**Do not guess.** If you don't have data, say so.

## Cache the result

Save to `~/.hermes/prepsheet/osint_cache.json`:

```bash
python3 "$HERMES_HOME/skills/ps-shared/scripts/osint_cache.py" \
  --save "john@acme.com" \
  --data '<json-profile>' \
  --ttl 30
```

Prevents redundant lookups for 30 days.

## Output format

```json
{
  "name": "John Smith",
  "title": "VP of Engineering",
  "company": "Acme Corp",
  "company_description": "Enterprise SaaS for supply chain",
  "company_news": "Series B $50M led by Sequoia (TechCrunch, Aug 2026)",
  "linkedin_url": "https://linkedin.com/in/johnsmith",
  "last_updated": "2026-09-13T10:30:00Z",
  "confidence": "high",
  "sources": ["linkedin", "crunchbase", "google_news"]
}
```

## Privacy

- **No personal contact info**: Never extract phone numbers, addresses, family details
- **Public data only**: No paywall circumvention
- **No social media scraping**: LinkedIn yes (professional); Facebook/Twitter/Instagram no
- **Respect robots.txt**: Plow enforces this automatically

## Blacklist

If config contains `osint_blacklist`, skip those emails:

```json
{
  "osint_blacklist": ["jane@partner.com"]
}
```

Use for close partners or privacy-sensitive contacts.
