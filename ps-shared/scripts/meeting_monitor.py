#!/usr/bin/env python3
"""
PrepSheet Meeting Monitor - Continuous calendar watch for 30-minute radar
Triggers ps-dossier skill for upcoming external meetings.
"""

import json
import sys
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

def load_dossier_log():
    """Load log of already-generated dossiers"""
    log_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'dossier_log.json'
    if log_path.exists():
        with open(log_path) as f:
            return json.load(f)
    return []

def check_upcoming_meetings():
    """Check for meetings in the radar window"""
    config = load_config()
    radar_minutes = config.get('meeting_radar_minutes', 30)
    
    # Get today's calendar
    calendar_script = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'skills' / 'ps-shared' / 'scripts' / 'calendar_ingest.py'
    
    try:
        result = subprocess.run(
            ['python3', str(calendar_script), '--date', 'today'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Calendar ingest failed: {result.stderr}", file=sys.stderr)
            return []
        
        events = json.loads(result.stdout)
    except Exception as e:
        print(f"Error reading calendar: {e}", file=sys.stderr)
        return []
    
    # Filter for external meetings in the radar window
    now = datetime.now()
    window_start = now + timedelta(minutes=radar_minutes - 5)
    window_end = now + timedelta(minutes=radar_minutes + 5)
    
    upcoming = []
    for event in events:
        # Skip internal-only meetings
        if not event.get('external_attendees'):
            continue
        
        # Parse event time
        event_time = datetime.combine(
            datetime.now().date(),
            datetime.strptime(event['time'], '%H:%M').time()
        )
        
        # Check if in window
        if window_start <= event_time <= window_end:
            upcoming.append(event)
    
    return upcoming

def trigger_dossier_generation(meeting):
    """Trigger ps-dossier skill for a meeting"""
    meeting_id = meeting.get('meeting_id')
    
    # Check if dossier already generated today
    dossier_log = load_dossier_log()
    for entry in dossier_log:
        if entry.get('meeting_id') == meeting_id:
            today = datetime.now().date().isoformat()
            generated_date = entry.get('generated_at', '')[:10]
            if generated_date == today:
                print(f"Dossier already generated for {meeting_id}")
                return
    
    # Trigger dossier generation via hermes skill invoke
    try:
        # Save meeting data to temp file for ps-dossier to consume
        temp_meeting = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'temp_meeting.json'
        with open(temp_meeting, 'w') as f:
            json.dump(meeting, f)
        
        print(f"Triggering dossier generation for: {meeting['title']}")
        
        # TODO: Implement actual hermes skill invoke
        # For now, just log the trigger
        print(f"[Would invoke: hermes skill invoke ps-dossier --meeting-id {meeting_id}]", file=sys.stderr)
        
    except Exception as e:
        print(f"Error triggering dossier: {e}", file=sys.stderr)

def main():
    print(f"[{datetime.now().isoformat()}] Meeting monitor checking for upcoming meetings...")
    
    upcoming_meetings = check_upcoming_meetings()
    
    if not upcoming_meetings:
        print("No upcoming external meetings in radar window")
        return
    
    for meeting in upcoming_meetings:
        print(f"Found upcoming meeting: {meeting['title']} at {meeting['time']}")
        trigger_dossier_generation(meeting)

if __name__ == '__main__':
    main()
