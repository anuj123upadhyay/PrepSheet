#!/usr/bin/env python3
"""
PrepSheet Email Ingest - Read-only IMAP email extraction
Fetches unread messages with VIP filtering and thread grouping.
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import os
import re

def load_config():
    """Load PrepSheet configuration"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def calculate_urgency_score(subject, sender, config):
    """
    Calculate urgency score (0-10) based on keywords and sender priority.
    
    Args:
        subject: Email subject line
        sender: Sender email address
        config: PrepSheet configuration
    
    Returns:
        Integer urgency score 0-10
    """
    score = 0
    
    # VIP sender boost
    vip_senders = config.get('vip_senders', [])
    if any(vip in sender for vip in vip_senders):
        score += 3
    
    # Keyword weights
    urgent_keywords = {
        'urgent': 3,
        'asap': 3,
        'important': 2,
        'decision': 2,
        'approval': 2,
        'action required': 3,
        'deadline': 2,
        'revenue': 2,
        'contract': 2,
        'legal': 2,
        'security': 3,
    }
    
    subject_lower = subject.lower()
    for keyword, weight in urgent_keywords.items():
        if keyword in subject_lower:
            score += weight
    
    return min(score, 10)  # Cap at 10

def parse_email_queue(since_hours, vip_only=False, participants=None, threads=False):
    """
    Parse emails from the queue directory.
    
    Args:
        since_hours: Look back this many hours
        vip_only: Filter to VIP senders only
        participants: Filter to emails involving specific participant
        threads: Group by thread
    
    Returns:
        List of email dictionaries or thread dictionaries
    """
    config = load_config()
    queue_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'queue' / 'email'
    
    if not queue_dir.exists():
        print(json.dumps([]))
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=since_hours)
    emails = []
    
    # TODO: Implement actual IMAP parsing
    # This is a placeholder structure
    for email_file in queue_dir.glob('*.json'):
        with open(email_file) as f:
            email_data = json.load(f)
            
            received_time = datetime.fromisoformat(email_data.get('received', ''))
            if received_time < cutoff_time:
                continue
            
            sender = email_data.get('from', '')
            subject = email_data.get('subject', '')
            
            # VIP filter
            if vip_only:
                vip_senders = config.get('vip_senders', [])
                if not any(vip in sender for vip in vip_senders):
                    continue
            
            # Participant filter
            if participants:
                all_participants = [sender] + email_data.get('to', []) + email_data.get('cc', [])
                if not any(participants in p for p in all_participants):
                    continue
            
            urgency = calculate_urgency_score(subject, sender, config)
            
            emails.append({
                'from': sender,
                'subject': subject,
                'received': email_data.get('received'),
                'preview': email_data.get('body_preview', '')[:200],
                'urgency_score': urgency,
                'thread_id': email_data.get('thread_id', email_data.get('message_id')),
                'unread': email_data.get('unread', True)
            })
    
    # Sort by urgency score (descending), then by received time
    emails.sort(key=lambda e: (-e['urgency_score'], e['received']), reverse=True)
    
    if threads:
        return group_by_thread(emails)
    
    return emails

def group_by_thread(emails):
    """Group emails by thread ID"""
    threads_dict = {}
    
    for email in emails:
        thread_id = email.get('thread_id', email.get('subject'))
        if thread_id not in threads_dict:
            threads_dict[thread_id] = {
                'thread_subject': email['subject'].replace('Re: ', '').replace('Fwd: ', ''),
                'message_count': 0,
                'messages': [],
                'latest_message': None
            }
        
        threads_dict[thread_id]['messages'].append(email)
        threads_dict[thread_id]['message_count'] += 1
    
    # Extract latest message and summary for each thread
    threads = []
    for thread_data in threads_dict.values():
        latest = max(thread_data['messages'], key=lambda m: m['received'])
        thread_data['latest_message'] = {
            'from': latest['from'],
            'received': latest['received'],
            'preview': latest['preview']
        }
        thread_data['summary'] = f"{thread_data['message_count']} messages in thread"
        del thread_data['messages']  # Don't return all messages, just metadata
        threads.append(thread_data)
    
    return threads

def parse_time_delta(time_str):
    """Parse time delta strings like '24h', '7d', '2w'"""
    match = re.match(r'(\d+)([hdw])', time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    
    amount, unit = match.groups()
    amount = int(amount)
    
    if unit == 'h':
        return amount
    elif unit == 'd':
        return amount * 24
    elif unit == 'w':
        return amount * 24 * 7
    
    return 24  # Default

def main():
    parser = argparse.ArgumentParser(description='PrepSheet Email Ingestion')
    parser.add_argument('--since', default='24h', help='Time window (e.g., 24h, 7d, 2w)')
    parser.add_argument('--vip-only', action='store_true', help='Filter to VIP senders only')
    parser.add_argument('--participants', help='Filter to emails with specific participant')
    parser.add_argument('--threads', action='store_true', help='Group by thread')
    
    args = parser.parse_args()
    
    since_hours = parse_time_delta(args.since)
    emails = parse_email_queue(since_hours, args.vip_only, args.participants, args.threads)
    
    print(json.dumps(emails, indent=2))

if __name__ == '__main__':
    main()
