#!/usr/bin/env python3
"""
Get meeting transcript via web form and save to temp file.
Returns the temp file path for Claude to process.
"""

import subprocess
import sys
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import threading
import json

# Import config module from same directory
from config import ensure_configured


class TranscriptHandler(BaseHTTPRequestHandler):
    transcript_data = None
    meeting_date = None
    meeting_time = None
    server_should_stop = False

    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

    def do_GET(self):
        """Serve the input form."""
        # Get today's date for default value
        today = datetime.now().strftime("%Y-%m-%d")

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Meeting Transcriber</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f7;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1d1d1f;
            margin-top: 0;
        }}
        p {{
            color: #6e6e73;
            line-height: 1.5;
        }}
        .metadata-section {{
            margin-bottom: 20px;
            padding: 20px;
            background-color: #f5f5f7;
            border-radius: 8px;
        }}
        .metadata-section h3 {{
            margin-top: 0;
            color: #1d1d1f;
            font-size: 16px;
        }}
        .metadata-fields {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        .field-group {{
            flex: 1;
        }}
        .field-group label {{
            display: block;
            margin-bottom: 5px;
            font-size: 13px;
            color: #6e6e73;
            font-weight: 500;
        }}
        .field-group input {{
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border: 2px solid #d2d2d7;
            border-radius: 8px;
            box-sizing: border-box;
        }}
        .field-group input:focus {{
            outline: none;
            border-color: #0071e3;
        }}
        .help-text {{
            margin-top: 8px;
            font-size: 12px;
            color: #86868b;
            font-style: italic;
        }}
        textarea {{
            width: 100%;
            height: 350px;
            padding: 15px;
            font-family: Monaco, Menlo, monospace;
            font-size: 12px;
            border: 2px solid #d2d2d7;
            border-radius: 8px;
            resize: vertical;
            box-sizing: border-box;
        }}
        textarea:focus {{
            outline: none;
            border-color: #0071e3;
        }}
        .buttons {{
            margin-top: 20px;
            text-align: right;
        }}
        button {{
            padding: 12px 24px;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-left: 10px;
            font-weight: 500;
        }}
        #cancel {{
            background-color: #e5e5ea;
            color: #1d1d1f;
        }}
        #cancel:hover {{
            background-color: #d1d1d6;
        }}
        #continue {{
            background-color: #0071e3;
            color: white;
        }}
        #continue:hover {{
            background-color: #0077ed;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Meeting Transcriber</h1>
        <p>Enter meeting details and paste your transcript below.</p>

        <form id="transcriptForm" method="POST" action="/submit">
            <div class="metadata-section">
                <h3>Meeting Details</h3>
                <div class="metadata-fields">
                    <div class="field-group">
                        <label for="meetingDate">Meeting Date</label>
                        <input type="date" id="meetingDate" name="meetingDate" value="{today}">
                        <div class="help-text">Optional - defaults to today if blank</div>
                    </div>
                    <div class="field-group">
                        <label for="meetingTime">Meeting Time</label>
                        <input type="time" id="meetingTime" name="meetingTime" value="09:00">
                        <div class="help-text">Optional - defaults to 09:00 if blank</div>
                    </div>
                </div>
            </div>

            <textarea id="transcript" name="transcript" placeholder="Paste your meeting transcript here..." autofocus></textarea>

            <div class="buttons">
                <button type="button" id="cancel" onclick="handleCancel()">Cancel</button>
                <button type="submit" id="continue">Continue</button>
            </div>
        </form>
    </div>
    <script>
        document.getElementById('transcriptForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const text = document.getElementById('transcript').value.trim();
            if (!text) {{
                alert('Please paste your transcript before continuing.');
                return;
            }}

            const date = document.getElementById('meetingDate').value || '';
            const time = document.getElementById('meetingTime').value || '';

            // Submit form
            fetch('/submit', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    transcript: text,
                    date: date,
                    time: time
                }})
            }}).then(() => {{
                document.body.innerHTML = '<div class="container"><h1>Success!</h1><p>Transcript received. You can close this window.</p></div>';
            }});
        }});
        function handleCancel() {{
            if (confirm('Are you sure you want to cancel?')) {{
                fetch('/cancel', {{method: 'POST'}}).then(() => {{
                    window.close();
                }});
            }}
        }}
        // Handle Cmd+Enter
        document.getElementById('transcript').addEventListener('keydown', function(e) {{
            if (e.metaKey && e.key === 'Enter') {{
                document.getElementById('transcriptForm').dispatchEvent(new Event('submit'));
            }}
        }});
    </script>
</body>
</html>'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        """Handle form submission."""
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())
                TranscriptHandler.transcript_data = data.get('transcript', '')
                TranscriptHandler.meeting_date = data.get('date', '')
                TranscriptHandler.meeting_time = data.get('time', '')
            except:
                pass

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

            # Signal server to stop
            TranscriptHandler.server_should_stop = True

        elif self.path == '/cancel':
            TranscriptHandler.transcript_data = None
            TranscriptHandler.meeting_date = None
            TranscriptHandler.meeting_time = None
            TranscriptHandler.server_should_stop = True

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')


def get_transcript_via_dialog():
    """Show web form dialog to get transcript, date, and time."""

    # Start local web server with port fallback
    port = 8765
    max_retries = 5
    server = None

    for attempt in range(max_retries):
        try:
            server = HTTPServer(('127.0.0.1', port), TranscriptHandler)
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"INFO: Port {port} in use, trying {port + 1}", file=sys.stderr)
                port += 1
            else:
                raise

    if server is None:
        print(f"ERROR: Could not find available port after {max_retries} attempts", file=sys.stderr)
        sys.exit(1)

    # Run server in background thread
    def run_server():
        while not TranscriptHandler.server_should_stop:
            server.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Open browser
    url = f'http://127.0.0.1:{port}'
    print(f"\nOpening web form at {url}")
    print("Enter meeting date/time and paste your transcript, then click Continue...")

    try:
        subprocess.run(['open', url], check=True)
    except:
        print(f"Please open this URL in your browser: {url}")

    # Wait for form submission
    server_thread.join(timeout=600)  # 10 minute timeout

    transcript = TranscriptHandler.transcript_data
    meeting_date = TranscriptHandler.meeting_date
    meeting_time = TranscriptHandler.meeting_time

    if transcript is None:
        print("INFO: User canceled or timeout", file=sys.stderr)
        sys.exit(0)

    if not transcript:
        print("ERROR: No transcript provided", file=sys.stderr)
        sys.exit(1)

    return transcript, meeting_date, meeting_time


def save_to_temp_file(transcript):
    """Save transcript to temp file with unique timestamp."""
    timestamp = int(time.time())
    raw_file = Path(f"/tmp/meeting-raw-{timestamp}.md")
    cleaned_file = Path(f"/tmp/meeting-cleaned-{timestamp}.md")

    try:
        raw_file.write_text(transcript, encoding='utf-8')
        print(f"SUCCESS: Transcript saved to {raw_file}")
        print(f"INFO: Cleaned file will be: {cleaned_file}")
        print(f"TIMESTAMP: {timestamp}")
        return raw_file, cleaned_file, timestamp

    except Exception as e:
        print(f"ERROR: Failed to save transcript: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    print("=== Meeting Transcriber: Input Collection ===")

    # Ensure configuration exists (first-run setup)
    if not ensure_configured():
        print("ERROR: Configuration required. Please run config setup.", file=sys.stderr)
        sys.exit(1)

    print("Starting web form...")

    transcript, meeting_date, meeting_time = get_transcript_via_dialog()

    word_count = len(transcript.split())
    print(f"INFO: Received transcript with {word_count} words")

    if meeting_date:
        print(f"INFO: Meeting date provided: {meeting_date}")
    if meeting_time:
        print(f"INFO: Meeting time provided: {meeting_time}")

    raw_file, cleaned_file, timestamp = save_to_temp_file(transcript)

    print(f"INFO: Ready for AI processing")
    print(f"RAW_FILE={raw_file}")
    print(f"CLEANED_FILE={cleaned_file}")
    print(f"TIMESTAMP={timestamp}")
    print(f"MEETING_DATE={meeting_date if meeting_date else ''}")
    print(f"MEETING_TIME={meeting_time if meeting_time else ''}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
