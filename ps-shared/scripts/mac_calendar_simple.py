#!/usr/bin/env python3
"""
Mac Calendar Simple Wrapper - Minimal EventKit integration with domain analysis
Extracts events for a given date, categorizes external attendees, and supports event creation.
"""
import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import EventKit  # pyright: ignore[reportMissingImports]
    from Foundation import NSDate  # pyright: ignore[reportMissingImports]
    HAS_EVENTKIT = True
except ImportError:
    EventKit = None
    NSDate = None
    HAS_EVENTKIT = False

def load_config() -> Dict[str, Any]:
    """Load PrepSheet configuration for internal domains"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def slugify(text: str) -> str:
    """Create a URL/filename-friendly slug from text"""
    clean_text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', clean_text)[:40] or 'event'

def read_events(date_str: str, next_only: bool = False, search_attendee: Optional[str] = None) -> List[Dict[str, Any]]:
    if not HAS_EVENTKIT or EventKit is None or NSDate is None:
        return []
    
    ek: Any = EventKit
    ns_date: Any = NSDate
    
    config = load_config()
    internal_domains = [d.lower().strip() for d in config.get('internal_domains', [])]
    
    store = ek.EKEventStore.alloc().init()
    store.requestAccessToEntityType_completion_(ek.EKEntityTypeEvent, None)
    
    target = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str != 'today' else datetime.now().date()
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    
    start_ns = ns_date.dateWithTimeIntervalSince1970_(start.timestamp())
    end_ns = ns_date.dateWithTimeIntervalSince1970_(end.timestamp())
    
    calendars = store.calendarsForEntityType_(ek.EKEntityTypeEvent)
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(start_ns, end_ns, calendars)
    events = store.eventsMatchingPredicate_(predicate) or []
    
    result: List[Dict[str, Any]] = []
    for e in events:
        attendees = [str(a.emailAddress()).lower() for a in (e.attendees() or []) if a.emailAddress()]
        duration = int(e.endDate().timeIntervalSinceDate_(e.startDate()) / 60) if e.endDate() else 60
        event_time = datetime.fromtimestamp(e.startDate().timeIntervalSince1970()).strftime('%H:%M')
        title = str(e.title() or 'Untitled')
        
        # Categorize external attendees
        external_attendees: List[str] = []
        external_domains = set()
        for a in attendees:
            if '@' in a:
                domain = a.split('@')[1].lower()
                if not any(domain == d or domain.endswith('.' + d) for d in internal_domains):
                    external_attendees.append(a)
                    external_domains.add(domain)
        
        meeting_id = f"{target.isoformat()}-{event_time.replace(':', '')}-{slugify(title)}"
        
        event_dict: Dict[str, Any] = {
            'time': event_time,
            'title': title,
            'attendees': attendees,
            'external_attendees': external_attendees,
            'external_domains': sorted(list(external_domains)),
            'duration_min': duration,
            'location': str(e.location() or ''),
            'notes': str(e.notes() or ''),
            'meeting_id': meeting_id
        }
        result.append(event_dict)
    
    # Sort chronologically
    result.sort(key=lambda x: x['time'])
    
    if search_attendee:
        search_term = search_attendee.lower()
        result = [
            e for e in result
            if any(search_term in a for a in e['attendees']) or
               any(search_term in d for d in e['external_domains'])
        ]
    
    if next_only:
        now_time = datetime.now().strftime('%H:%M')
        upcoming = [e for e in result if e['time'] >= now_time]
        return upcoming[:1]
    
    return result

def create_event(title: str, start: str, duration: int, attendees: List[str], location: str, notes: str) -> Optional[str]:
    if not HAS_EVENTKIT or EventKit is None or NSDate is None:
        return None
    
    ek: Any = EventKit
    ns_date: Any = NSDate
    
    store = ek.EKEventStore.alloc().init()
    store.requestAccessToEntityType_completion_(ek.EKEntityTypeEvent, None)
    
    event = ek.EKEvent.eventWithEventStore_(store)
    event.setTitle_(title)
    event.setLocation_(location)
    notes_with_attendees = (notes + "\n\nAttendees: " + ", ".join(attendees)) if attendees else notes
    event.setNotes_(notes_with_attendees)
    
    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M')
    end_dt = start_dt + timedelta(minutes=duration)
    
    event.setStartDate_(ns_date.dateWithTimeIntervalSince1970_(start_dt.timestamp()))
    event.setEndDate_(ns_date.dateWithTimeIntervalSince1970_(end_dt.timestamp()))
    event.setCalendar_(store.defaultCalendarForNewEvents())
    
    success = store.saveEvent_span_commit_error_(event, ek.EKSpanThisEvent, True, None)
    return str(event.eventIdentifier()) if success else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PrepSheet Mac Calendar Access')
    parser.add_argument('--action', choices=['read', 'create'], default='read')
    parser.add_argument('--date', default='today')
    parser.add_argument('--next-only', action='store_true', help='Return only the next upcoming meeting')
    parser.add_argument('--search-attendee', help='Search for meetings with attendee email or domain')
    parser.add_argument('--title', default='')
    parser.add_argument('--start', default='')
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--attendees', default='')
    parser.add_argument('--location', default='')
    parser.add_argument('--notes', default='')
    args = parser.parse_args()
    
    if args.action == 'read':
        print(json.dumps(read_events(args.date, next_only=args.next_only, search_attendee=args.search_attendee), indent=2))
    else:
        parsed_attendees = [a.strip() for a in args.attendees.split(',') if a.strip()]
        event_id = create_event(args.title, args.start, args.duration, parsed_attendees, args.location, args.notes)
        print(json.dumps({'success': bool(event_id), 'event_id': event_id}))
