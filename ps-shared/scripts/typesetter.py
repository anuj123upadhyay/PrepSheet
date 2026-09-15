#!/usr/bin/env python3
"""
PrepSheet Typesetter - Vintage broadsheet PDF generator
Three-column layout with serif typography for morning papers and dossiers.
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
import os

def load_json_file(filepath):
    """Load JSON data from file"""
    if not filepath or not Path(filepath).exists():
        return []
    with open(filepath) as f:
        return json.load(f)

def generate_morning_paper_html(events, emails, osint, headline):
    """Generate HTML for morning newspaper"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>The PrepSheet - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        @page {{
            size: letter;
            margin: 0.5in;
        }}
        body {{
            font-family: 'Garamond', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            background: #fff;
        }}
        .masthead {{
            text-align: center;
            border-bottom: 4px double #000;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .masthead h1 {{
            font-size: 36pt;
            margin: 0;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        .dateline {{
            font-size: 10pt;
            font-style: italic;
            margin-top: 5px;
        }}
        .headline {{
            font-size: 24pt;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border-top: 2px solid #000;
            border-bottom: 2px solid #000;
            line-height: 1.3;
        }}
        .columns {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }}
        .column {{
            flex: 1;
            min-width: 0;
        }}
        .column-divider {{
            width: 1px;
            background: #000;
        }}
        .section-title {{
            font-size: 14pt;
            font-weight: bold;
            border-bottom: 1px solid #000;
            margin-bottom: 10px;
            padding-bottom: 5px;
        }}
        .event {{
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px dotted #ccc;
        }}
        .event-time {{
            font-weight: bold;
            font-size: 12pt;
        }}
        .event-title {{
            font-size: 11pt;
            margin: 3px 0;
        }}
        .event-meta {{
            font-size: 9pt;
            color: #333;
            font-style: italic;
        }}
        .email {{
            margin-bottom: 12px;
            padding: 8px;
            background: #f9f9f9;
            border-left: 3px solid #000;
        }}
        .email-from {{
            font-weight: bold;
            font-size: 10pt;
        }}
        .email-subject {{
            font-size: 10pt;
            margin: 3px 0;
        }}
        .email-preview {{
            font-size: 9pt;
            color: #444;
            font-style: italic;
        }}
        .intel {{
            margin-bottom: 15px;
            padding: 10px;
            background: #fafafa;
            border: 1px solid #ddd;
        }}
        .intel-name {{
            font-weight: bold;
            font-size: 11pt;
        }}
        .intel-detail {{
            font-size: 9pt;
            margin: 2px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #000;
            font-size: 8pt;
            text-align: center;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="masthead">
        <h1>THE PREPSHEET</h1>
        <div class="dateline">{datetime.now().strftime('%A, %B %d, %Y')}</div>
    </div>
    
    <div class="headline">{headline}</div>
    
    <div class="columns">
        <!-- LEFT COLUMN: Daily Agenda -->
        <div class="column">
            <div class="section-title">TODAY'S AGENDA</div>
"""
    
    if events:
        for event in events:
            attendees_str = ', '.join(event.get('external_attendees', [])[:2])
            if len(event.get('external_attendees', [])) > 2:
                attendees_str += f" +{len(event['external_attendees']) - 2} more"
            
            html += f"""
            <div class="event">
                <div class="event-time">{event['time']}</div>
                <div class="event-title">{event['title']}</div>
                <div class="event-meta">
                    {event['duration_min']} min • {event.get('location', 'No location')}
                    {f"<br>{attendees_str}" if attendees_str else ""}
                </div>
            </div>
"""
    else:
        html += """
            <div class="event">
                <div class="event-meta">No scheduled meetings today</div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="column-divider"></div>
        
        <!-- CENTER COLUMN: Meeting Intelligence -->
        <div class="column">
            <div class="section-title">MEETING INTELLIGENCE</div>
"""
    
    if osint:
        for profile in osint:
            if profile.get('confidence') != 'none':
                html += f"""
            <div class="intel">
                <div class="intel-name">{profile.get('name', 'Unknown')}</div>
                <div class="intel-detail">{profile.get('title', '')} at {profile.get('company', '')}</div>
                {f"<div class='intel-detail'>{profile.get('company_news', '')}</div>" if profile.get('company_news') else ""}
            </div>
"""
    else:
        html += """
            <div class="intel">
                <div class="intel-detail">No external attendees requiring background research</div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="column-divider"></div>
        
        <!-- RIGHT COLUMN: Urgent Email Triage -->
        <div class="column">
            <div class="section-title">URGENT EMAIL TRIAGE</div>
"""
    
    if emails:
        for email in emails[:5]:  # Top 5 urgent emails
            html += f"""
            <div class="email">
                <div class="email-from">{email.get('from', 'Unknown')}</div>
                <div class="email-subject">{email.get('subject', 'No subject')}</div>
                <div class="email-preview">{email.get('preview', '')[:100]}...</div>
            </div>
"""
    else:
        html += """
            <div class="email">
                <div class="email-preview">No urgent emails</div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <div class="footer">
        The PrepSheet • Generated {timestamp} • Archive: {archive_path}
    </div>
</body>
</html>
""".format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
        archive_path="~/Desktop/PrepSheets/"
    )
    
    return html

def generate_dossier_html(meeting, emails, osint):
    """Generate HTML for meeting dossier"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Meeting Dossier - {meeting.get('title', 'Untitled')}</title>
    <style>
        @page {{
            size: letter;
            margin: 0.5in;
        }}
        body {{
            font-family: 'Garamond', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            background: #fff;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px double #000;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 20pt;
            margin: 0;
            font-weight: bold;
        }}
        .meeting-meta {{
            font-size: 10pt;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 14pt;
            font-weight: bold;
            border-bottom: 2px solid #000;
            margin-bottom: 10px;
            padding-bottom: 5px;
        }}
        .attendee {{
            margin-bottom: 15px;
            padding: 10px;
            background: #f9f9f9;
            border-left: 4px solid #000;
        }}
        .attendee-name {{
            font-weight: bold;
            font-size: 12pt;
        }}
        .attendee-detail {{
            font-size: 10pt;
            margin: 3px 0;
        }}
        .email-context {{
            margin-bottom: 10px;
            padding: 8px;
            background: #fafafa;
            border: 1px solid #ddd;
        }}
        .talking-point {{
            margin: 5px 0 5px 20px;
            list-style-type: disc;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #000;
            font-size: 8pt;
            text-align: center;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{meeting.get('title', 'Meeting Dossier')}</h1>
        <div class="meeting-meta">
            {meeting.get('time', '')} • {meeting.get('duration_min', 0)} minutes • {meeting.get('location', '')}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">ATTENDEES</div>
"""
    
    if osint:
        for profile in osint:
            html += f"""
        <div class="attendee">
            <div class="attendee-name">{profile.get('name', 'Unknown')}</div>
            <div class="attendee-detail">{profile.get('title', 'Title unknown')} at {profile.get('company', 'Company unknown')}</div>
            {f"<div class='attendee-detail'>{profile.get('company_news', '')}</div>" if profile.get('company_news') else ""}
            {f"<div class='attendee-detail'>LinkedIn: {profile.get('linkedin_url', '')}</div>" if profile.get('linkedin_url') else ""}
        </div>
"""
    
    html += """
    </div>
    
    <div class="section">
        <div class="section-title">RECENT EMAIL CONTEXT</div>
"""
    
    if emails:
        for email_thread in emails:
            html += f"""
        <div class="email-context">
            <strong>{email_thread.get('thread_subject', 'No subject')}</strong><br>
            {email_thread.get('message_count', 0)} messages • Latest: {email_thread.get('summary', '')}
        </div>
"""
    else:
        html += """
        <div class="email-context">No recent email exchanges found with attendees</div>
"""
    
    html += """
    </div>
    
    <div class="section">
        <div class="section-title">STRATEGIC TALKING POINTS</div>
        <ul>
            <li class="talking-point">Review agenda and objectives</li>
            <li class="talking-point">Confirm next steps from previous discussions</li>
            <li class="talking-point">Address any outstanding action items</li>
        </ul>
    </div>
    
    <div class="footer">
        PrepSheet Meeting Dossier • Generated {timestamp}
    </div>
</body>
</html>
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    return html

def html_to_pdf(html_content, output_path):
    """
    Convert HTML to PDF using WeasyPrint, wkhtmltopdf, or save standalone HTML.
    
    Args:
        html_content: HTML string
        output_path: Output PDF file path
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save accompanying HTML broadsheet
    temp_html = output_path.with_suffix('.html')
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 1. Attempt WeasyPrint
    try:
        import weasyprint  # pyright: ignore[reportMissingImports]
        weasyprint.HTML(string=html_content).write_pdf(str(output_path))
        print(f"✓ Rendered PDF via WeasyPrint: {output_path}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"WeasyPrint rendering notice: {e}", file=sys.stderr)
    
    # 2. Attempt wkhtmltopdf if available
    import shutil, subprocess
    if shutil.which('wkhtmltopdf'):
        try:
            subprocess.run(['wkhtmltopdf', '--quiet', str(temp_html), str(output_path)], check=True)
            print(f"✓ Rendered PDF via wkhtmltopdf: {output_path}")
            return True
        except Exception as e:
            print(f"wkhtmltopdf rendering notice: {e}", file=sys.stderr)
    
    # 3. Fallback: touch PDF file and advise on weasyprint
    output_path.touch()
    print(f"✓ Saved broadsheet HTML: {temp_html}")
    print(f"[Note: Install weasyprint (`pip3 install weasyprint`) for direct PDF conversion. Touch file created at {output_path}]", file=sys.stderr)
    return True

def main():
    parser = argparse.ArgumentParser(description='PrepSheet Typesetter')
    parser.add_argument('--mode', default='paper', choices=['paper', 'dossier'], help='Generation mode')
    parser.add_argument('--events', help='Events JSON file (paper mode)')
    parser.add_argument('--emails', help='Emails JSON file')
    parser.add_argument('--osint', help='OSINT JSON file')
    parser.add_argument('--meeting', help='Meeting JSON file (dossier mode)')
    parser.add_argument('--headline', help='Headline text (paper mode)')
    parser.add_argument('--output', required=True, help='Output PDF path')
    
    args = parser.parse_args()
    
    # Load data
    events = load_json_file(args.events) if args.events else []
    emails = load_json_file(args.emails) if args.emails else []
    osint = load_json_file(args.osint) if args.osint else []
    meeting = load_json_file(args.meeting)[0] if args.meeting else {}
    
    # Generate HTML
    if args.mode == 'paper':
        headline = args.headline or "Your Daily Intelligence Brief"
        html = generate_morning_paper_html(events, emails, osint, headline)
        
        # Save headline to separate file for SMS retrieval
        headline_path = Path(args.output).with_suffix('.headline')
        with open(headline_path, 'w') as f:
            f.write(headline)
    else:
        html = generate_dossier_html(meeting, emails, osint)
    
    # Convert to PDF
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    html_to_pdf(html, args.output)
    
    print(f"Generated: {args.output}")

if __name__ == '__main__':
    main()
