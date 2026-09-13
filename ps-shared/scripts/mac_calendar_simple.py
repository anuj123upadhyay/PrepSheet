#!/usr/bin/env python3
"""
Mac Calendar Simple Wrapper - Minimal EventKit integration
"""
import json, sys, argparse
from datetime import datetime, timedelta

try:
    import EventKit
    from Foundation import NSDate
    HAS_EVENTKIT = True
except ImportError:
    HAS_EVENTKIT = False

def read_events(date_str):
    if not HAS_EVENTKIT:
        return []
    
    store = EventKit.EKEventStore.alloc().init()
    store.requestAccessToEntityType_completion_(EventKit.EKEntityTypeEvent, None)
    
    target = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str != 'today' else datetime.now().date()
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    
    start_ns = NSDate.dateWithTimeIntervalSince1970_(start.timestamp())
    end_ns = NSDate.dateWithTimeIntervalSince1970_(end.timestamp())
    
    calendars = store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(start_ns, end_ns, calendars)
    events = store.eventsMatchingPredicate_(predicate)
    
    result = []
    for e in events:
        attendees = [a.emailAddress() for a in (e.attendees() or []) if a.emailAddress()]
        duration = int(e.endDate().timeIntervalSinceDate_(e.startDate()) / 60) if e.endDate() else 60
        
        result.append({
            'time': datetime.fromtimestamp(e.startDate().timeIntervalSince1970()).strftime('%H:%M'),
            'title': e.title() or 'Untitled',
            'attendees': attendees,
            'duration_min': duration,
            'location': e.location() or '',
            'notes': e.notes() or ''
        })
    
    return result

def create_event(title, start, duration, attendees, location, notes):
    if not HAS_EVENTKIT:
        return None
    
    store = EventKit.EKEventStore.alloc().init()
    store.requestAccessToEntityType_completion_(EventKit.EKEntityTypeEvent, None)
    
    event = EventKit.EKEvent.eventWithEventStore_(store)
    event.setTitle_(title)
    event.setLocation_(location)
    event.setNotes_(notes + "\n\nAttendees: " + ", ".join(attendees) if attendees else notes)
    
    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M')
    end_dt = start_dt + timedelta(minutes=duration)
    
    event.setStartDate_(NSDate.dateWithTimeIntervalSince1970_(start_dt.timestamp()))
    event.setEndDate_(NSDate.dateWithTimeIntervalSince1970_(end_dt.timestamp()))
    event.setCalendar_(store.defaultCalendarForNewEvents())
    
    success = store.saveEvent_span_commit_error_(event, EventKit.EKSpanThisEvent, True, None)
    return event.eventIdentifier() if success else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['read', 'create'], default='read')
    parser.add_argument('--date', default='today')
    parser.add_argument('--title', default='')
    parser.add_argument('--start', default='')
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--attendees', default='')
    parser.add_argument('--location', default='')
    parser.add_argument('--notes', default='')
    args = parser.parse_args()
    
    if args.action == 'read':
        print(json.dumps(read_events(args.date), indent=2))
    else:
        attendees = [a.strip() for a in args.attendees.split(',') if a.strip()]
        event_id = create_event(args.title, args.start, args.duration, attendees, args.location, args.notes)
        print(json.dumps({'success': bool(event_id), 'event_id': event_id}))
