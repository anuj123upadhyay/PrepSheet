#!/usr/bin/env python3
"""
PrepSheet Printer - CUPS print daemon interface
Sends PDFs to the configured printer or confirms Desktop-only fallback.
"""

import json
import sys
import argparse
from pathlib import Path
import os
import subprocess
from datetime import datetime

def load_config():
    """Load PrepSheet configuration"""
    config_path = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def log_print_job(pdf_path, status, message):
    """Log print job to printer.log"""
    log_dir = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'prepsheet' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / 'printer.log'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'file': str(pdf_path),
        'status': status,
        'message': message
    }
    
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def print_pdf(pdf_path, printer_name='default'):
    """
    Print PDF via CUPS lp command.
    
    Args:
        pdf_path: Path to PDF file
        printer_name: CUPS printer name
    
    Returns:
        (success: bool, message: str)
    """
    if not Path(pdf_path).exists():
        return False, f"File not found: {pdf_path}"
    
    try:
        # Try to print via lp command
        cmd = ['lp']
        if printer_name and printer_name != 'default':
            cmd.extend(['-d', printer_name])
        cmd.append(str(pdf_path))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, f"Print job submitted successfully: {result.stdout.strip()}"
        else:
            return False, f"Print failed: {result.stderr.strip()}"
    
    except FileNotFoundError:
        return False, "CUPS not installed (lp command not found)"
    except subprocess.TimeoutExpired:
        return False, "Print command timed out"
    except Exception as e:
        return False, f"Print error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='PrepSheet Printer')
    parser.add_argument('--file', required=True, help='PDF file to print')
    parser.add_argument('--printer-name', default='default', help='CUPS printer name')
    
    args = parser.parse_args()
    
    config = load_config()
    printer_enabled = config.get('printer_enabled', True)
    
    if not printer_enabled:
        message = f"Printer disabled in config. PDF saved to: {args.file}"
        log_print_job(args.file, 'skipped', message)
        print(message)
        return
    
    # Attempt to print
    success, message = print_pdf(args.file, args.printer_name)
    
    if success:
        log_print_job(args.file, 'success', message)
        print(f"✓ Printed: {args.file}")
    else:
        # Fallback: PDF is already saved to Desktop
        fallback_message = f"Printer unavailable ({message}). PDF saved to: {args.file}"
        log_print_job(args.file, 'fallback', fallback_message)
        print(fallback_message)
        
        # This is not an error - the product works either way
        sys.exit(0)

if __name__ == '__main__':
    main()
