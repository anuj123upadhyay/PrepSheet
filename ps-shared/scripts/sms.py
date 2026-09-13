#!/usr/bin/env python3
"""
PrepSheet SMS - Hermes telephony wrapper
Sends SMS notifications with rate limiting and retry logic.
"""

import json
import sys
import argparse
from pathlib import Path
import os
from datetime import datetime, timedelta

def load_config():
    """Load PrepSheet configuration"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def check_rate_limit():
    """Check if rate limit (5 messages per 10 minutes) is exceeded"""
    log_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'logs'
    log_path = log_dir / 'sms_sent.log'
    
    if not log_path.exists():
        return True  # No history, allow
    
    cutoff = datetime.now() - timedelta(minutes=10)
    recent_count = 0
    
    with open(log_path) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                sent_time = datetime.fromisoformat(entry['timestamp'])
                if sent_time > cutoff:
                    recent_count += 1
            except:
                continue
    
    return recent_count < 5

def log_sms(message, status):
    """Log SMS to sms_sent.log"""
    log_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / 'sms_sent.log'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'message_preview': message[:50] + ('...' if len(message) > 50 else ''),
        'status': status,
        'length': len(message)
    }
    
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def queue_sms_for_retry(message):
    """Queue SMS for retry when service is unavailable"""
    queue_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet'
    queue_file = queue_dir / 'sms_queue.json'
    
    queue = []
    if queue_file.exists():
        with open(queue_file) as f:
            queue = json.load(f)
    
    queue.append({
        'message': message,
        'queued_at': datetime.now().isoformat(),
        'attempts': 0
    })
    
    with open(queue_file, 'w') as f:
        json.dump(queue, f, indent=2)

def send_sms_hermes(message):
    """
    Send SMS via Hermes telephony plugin (placeholder).
    
    Args:
        message: SMS body text
    
    Returns:
        (success: bool, status_message: str)
    """
    # TODO: Implement actual Hermes telephony integration
    # This is a placeholder that simulates the send
    
    print(f"[SMS] {message}", file=sys.stderr)
    
    # Placeholder: assume success
    return True, "SMS sent (placeholder)"

def main():
    parser = argparse.ArgumentParser(description='PrepSheet SMS Sender')
    parser.add_argument('message', nargs='?', help='SMS message body (or read from stdin)')
    parser.add_argument('--force', action='store_true', help='Bypass rate limit')
    
    args = parser.parse_args()
    
    # Read message from stdin if not provided as argument
    if args.message:
        message = args.message
    else:
        message = sys.stdin.read().strip()
    
    if not message:
        print("Error: No message provided", file=sys.stderr)
        sys.exit(1)
    
    # Check config
    config = load_config()
    if not config.get('sms_enabled', True):
        print("SMS disabled in config", file=sys.stderr)
        log_sms(message, 'disabled')
        sys.exit(0)
    
    # Rate limit check
    if not args.force and not check_rate_limit():
        print("Rate limit exceeded (5 messages per 10 minutes). Use --force to override.", file=sys.stderr)
        log_sms(message, 'rate_limited')
        sys.exit(1)
    
    # Send SMS
    success, status = send_sms_hermes(message)
    
    if success:
        log_sms(message, 'sent')
        print(f"✓ SMS sent ({len(message)} chars)")
    else:
        # Queue for retry
        queue_sms_for_retry(message)
        log_sms(message, 'queued')
        print(f"SMS service unavailable. Message queued for retry.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
