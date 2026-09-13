#!/usr/bin/env python3
"""
OSINT Cache Management - Simple JSON storage
"""
import json, sys, argparse
from datetime import datetime, timedelta
from pathlib import Path
import os

CACHE_FILE = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'osint_cache.json'

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(data):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_cache(email):
    cache = load_cache()
    if email in cache:
        entry = cache[email]
        last_updated = datetime.fromisoformat(entry.get('last_updated', '2000-01-01'))
        ttl_days = entry.get('ttl_days', 30)
        if datetime.now() - last_updated < timedelta(days=ttl_days):
            return entry
    return None

def save_entry(email, data, ttl=30):
    cache = load_cache()
    data['last_updated'] = datetime.now().isoformat()
    data['ttl_days'] = ttl
    cache[email] = data
    save_cache(cache)
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', help='Check cache for email')
    parser.add_argument('--save', help='Save entry for email')
    parser.add_argument('--data', help='JSON data to save')
    parser.add_argument('--ttl', type=int, default=30, help='TTL in days')
    args = parser.parse_args()
    
    if args.check:
        entry = check_cache(args.check)
        if entry:
            print(json.dumps(entry, indent=2))
        else:
            print(json.dumps({'cached': False}))
    elif args.save and args.data:
        data = json.loads(args.data)
        save_entry(args.save, data, args.ttl)
        print(json.dumps({'success': True}))
    else:
        print(json.dumps({'error': 'Specify --check or --save with --data'}))
