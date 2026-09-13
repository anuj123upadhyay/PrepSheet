#!/usr/bin/env python3
"""
PrepSheet OSINT Lookup - Zero-hallucination intelligence gathering
Uses Plow Latch for LinkedIn, Crunchbase, and news searches.
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import os
import subprocess

def load_config():
    """Load PrepSheet configuration"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def load_cache():
    """Load OSINT cache"""
    cache_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'osint_cache.json'
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save OSINT cache"""
    cache_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'osint_cache.json'
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'w') as f:
        json.dump(cache, f, indent=2)

def check_cache(attendee_email, cache_ttl_days):
    """Check if cached data exists and is fresh"""
    cache = load_cache()
    
    if attendee_email not in cache:
        return None
    
    entry = cache[attendee_email]
    last_updated = datetime.fromisoformat(entry.get('last_updated', ''))
    age_days = (datetime.now() - last_updated).days
    
    if age_days > cache_ttl_days:
        return None  # Stale
    
    return entry

def plow_latch_search(query, domain=None, limit=3):
    """
    Execute Plow Latch search (placeholder - requires actual Plow Latch integration)
    
    Args:
        query: Search query string
        domain: Optional domain filter
        limit: Max results
    
    Returns:
        List of search results
    """
    # TODO: Implement actual Plow Latch integration
    # This is a placeholder that returns mock data
    
    # Simulated search results structure
    return {
        'results': [],
        'status': 'placeholder',
        'note': 'Plow Latch integration pending'
    }

def linkedin_lookup(name, company_domain):
    """Search LinkedIn for professional profile"""
    query = f"{name} {company_domain}"
    results = plow_latch_search(query, domain="linkedin.com", limit=3)
    
    # TODO: Parse actual LinkedIn results
    # Placeholder return
    return {
        'name': name,
        'title': 'Title pending LinkedIn integration',
        'company': company_domain,
        'linkedin_url': None,
        'found': False
    }

def company_research(domain):
    """Research company via website and Crunchbase"""
    # TODO: Implement actual company research
    return {
        'company_description': 'Pending company research integration',
        'funding': 'private or not disclosed',
        'news': None
    }

def recent_news_search(company_name):
    """Search for recent company news"""
    query = f"{company_name}"
    results = plow_latch_search(query, domain="news.google.com", limit=5)
    
    # TODO: Parse and filter news results
    return None

def perform_osint_lookup(attendee_email, domain, name_hint=None):
    """
    Perform full OSINT lookup on an attendee.
    
    Args:
        attendee_email: Email address
        domain: Company domain
        name_hint: Optional name hint from calendar
    
    Returns:
        Profile dictionary with confidence score
    """
    config = load_config()
    blacklist = config.get('osint_blacklist', [])
    
    # Check blacklist
    if attendee_email in blacklist:
        return {
            'name': 'OSINT disabled for this contact',
            'company': domain,
            'note': 'Manual override - OSINT lookup skipped',
            'confidence': 'none'
        }
    
    # Extract name from email if no hint
    if not name_hint and attendee_email:
        local_part = attendee_email.split('@')[0]
        name_hint = ' '.join(local_part.split('.')).title()
    
    # LinkedIn lookup
    linkedin_data = linkedin_lookup(name_hint, domain)
    
    # Company research
    company_data = company_research(domain)
    
    # Recent news
    news = recent_news_search(domain)
    
    # Determine confidence
    confidence = 'none'
    if linkedin_data.get('found'):
        confidence = 'high' if company_data.get('funding') else 'medium'
    elif company_data.get('company_description') != 'Pending company research integration':
        confidence = 'low'
    
    profile = {
        'name': linkedin_data.get('name', name_hint or 'Unknown'),
        'title': linkedin_data.get('title'),
        'company': linkedin_data.get('company', domain),
        'company_description': company_data.get('company_description'),
        'company_news': news or company_data.get('funding'),
        'linkedin_url': linkedin_data.get('linkedin_url'),
        'last_updated': datetime.now().isoformat(),
        'confidence': confidence,
        'sources': ['placeholder']
    }
    
    # Add note if no public record
    if confidence == 'none':
        profile['note'] = 'No public record found—internal contact or private profile'
    
    return profile

def search_cached_profiles(search_term, domain=None):
    """Search cached profiles by name or domain"""
    cache = load_cache()
    matches = []
    
    search_lower = search_term.lower()
    for email, profile in cache.items():
        if search_lower in profile.get('name', '').lower():
            if not domain or domain in email:
                matches.append(profile)
        elif domain and domain in email:
            matches.append(profile)
    
    return matches

def main():
    parser = argparse.ArgumentParser(description='PrepSheet OSINT Lookup')
    parser.add_argument('--attendee', help='Attendee email address')
    parser.add_argument('--domain', help='Company domain')
    parser.add_argument('--name-hint', help='Name hint from calendar')
    parser.add_argument('--cache-ttl', type=int, default=30, help='Cache TTL in days')
    parser.add_argument('--cache-only', action='store_true', help='Only search cache, no live lookup')
    parser.add_argument('--search', help='Search cached profiles by name')
    parser.add_argument('--verbose', action='store_true', help='Verbose debug output')
    
    args = parser.parse_args()
    
    # Search mode
    if args.search:
        results = search_cached_profiles(args.search, args.domain)
        print(json.dumps(results, indent=2))
        return
    
    # Require attendee for lookup
    if not args.attendee:
        print(json.dumps({'error': 'Either --attendee or --search required'}), file=sys.stderr)
        sys.exit(1)
    
    # Check cache first
    cached = check_cache(args.attendee, args.cache_ttl)
    if cached:
        if args.verbose:
            print(f"[Cache hit: {args.attendee}]", file=sys.stderr)
        print(json.dumps(cached, indent=2))
        return
    
    # Cache-only mode
    if args.cache_only:
        print(json.dumps({
            'name': 'Unknown',
            'company': args.domain or 'unknown',
            'note': 'Not found in cache',
            'confidence': 'none'
        }))
        return
    
    # Perform live lookup
    if args.verbose:
        print(f"[Live lookup: {args.attendee}]", file=sys.stderr)
    
    profile = perform_osint_lookup(args.attendee, args.domain, args.name_hint)
    
    # Save to cache
    cache = load_cache()
    cache[args.attendee] = profile
    save_cache(cache)
    
    print(json.dumps(profile, indent=2))

if __name__ == '__main__':
    main()
