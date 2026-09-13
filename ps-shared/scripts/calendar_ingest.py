#!/usr/bin/env python3
"""
PrepSheet Calendar Ingest - Read-only calendar parsing
Extracts events for a given date and identifies external attendees.
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import os

def load_config():
    """Load PrepSheet configuration"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def get_internal_domains(config):
    """Extract internal email domains from configuration"""
    # TODO: Implement domain detection from config or environment
    return ['mycompany.com']  # Placeholder

def parse_calendar_queue(date_str):
    """
    Parse calendar events from the queue directory.
    
    Args:
        date_str: Date in YYYY-MM-DD format or 'today'
    
    Returns:
        List of event dictionaries
    """
    if date_str == 'today':
        target_date = datetime.now().date()
    else:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    queue_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'queue' / 'calendar'
    
    if not queue_dir.exists():
        print(json.dumps([]))
        return []
    
    events = []
    internal_domains = get_internal_domains(load_config())
    
    # TODO: Implement actual calendar parsing (CalDAV, .ics, or other format)
    # This is a placeholder structure
    for event_file in queue_dir.glob('*.json'):
        with open(event_file) as f:
            event_data = json.load(f)
            
            # Filter by date
            event_date = datetime.fromisoformat(event_data.get('start', '')).date()
            if event_date != target_date:
                continue
            
            # Extract external attendees
            attendees = event_data.get('attendees', [])
            external_attendees = [a for a in attendees if not any(d in a for d in internal_domains)]
            external_domains = list(set([a.split('@')[1] for a in external_attendees if '@' in a]))
            
            events.append({
                'time': datetime.fromisoformat(event_data['start']).strftime('%H:%M'),
                'title': event_data.get('summary', 'Untitled Event'),
                'attendees': attendees,
                'external_attendees': external_attendees,
                'external_domains': external_domains,
                'duration_min': event_data.get('duration_minutes', 30),
                'location': event_data.get('location', ''),
                'organizer': event_data.get('organizer', ''),
                'meeting_id': f"{target_date}-{event_data.get('uid', 'unknown')}"
            })
    
    # Sort by time
    events.sort(key=lambda e: e['time'])
    
    return events

def get_next_meeting(events):
    """Get only the next upcoming meeting"""
    now = datetime.now().time()
    for event in events:
        event_time = datetime.strptime(event['time'], '%H:%M').time()
        if event_time > now:
            return [event]
    return []

def main():
    parser = argparse.ArgumentParser(description='PrepSheet Calendar Ingestion')
    parser.add_argument('--date', default='today', help='Date to parse (YYYY-MM-DD or "today")')
    parser.add_argument('--next-only', action='store_true', help='Return only the next upcoming meeting')
    parser.add_argument('--search-attendee', help='Search for meetings with specific attendee domain')
    
    args = parser.parse_args()
    
    events = parse_calendar_queue(args.date)
    
    if args.next_only:
        events = get_next_meeting(events)
    
    if args.search_attendee:
        events = [e for e in events if args.search_attendee in str(e.get('external_domains', []))]
    
    print(json.dumps(events, indent=2))

if __name__ == '__main__':
    main()
