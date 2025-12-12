#!/usr/bin/env python3
"""
Get quiz parameters via web form.
Returns parameters as JSON for Claude to process.
"""

import subprocess
import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from config import ensure_configured


class ParamsHandler(BaseHTTPRequestHandler):
    params_data = None
    server_should_stop = False

    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

    def do_GET(self):
        """Serve the input form."""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quiz Maker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #000000;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header {
            background-color: #800000;
            color: white;
            padding: 20px;
            margin: -30px -30px 30px -30px;
            border-radius: 12px 12px 0 0;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            font-size: 18px;
            color: #800000;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #800000;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #000000;
        }
        input[type="text"],
        input[type="number"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #800000;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
            font-family: Monaco, monospace;
            font-size: 12px;
        }
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .checkbox-item:hover {
            background-color: #e9ecef;
        }
        .checkbox-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            cursor: pointer;
        }
        .checkbox-item label {
            margin: 0;
            cursor: pointer;
            font-weight: normal;
        }
        .radio-group {
            display: flex;
            gap: 20px;
        }
        .radio-item {
            display: flex;
            align-items: center;
        }
        .radio-item input[type="radio"] {
            width: 18px;
            height: 18px;
            margin-right: 8px;
            cursor: pointer;
        }
        .radio-item label {
            margin: 0;
            cursor: pointer;
            font-weight: normal;
        }
        .help-text {
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }
        .buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        #cancel {
            background-color: #6c757d;
            color: white;
        }
        #cancel:hover {
            background-color: #5a6268;
        }
        #submit {
            background-color: #800000;
            color: white;
        }
        #submit:hover {
            background-color: #660000;
        }
        button:active {
            transform: scale(0.98);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Quiz Maker</h1>
            <div class="subtitle">Create a custom study quiz from your source materials</div>
        </div>

        <form id="quizForm">
            <div class="section">
                <h2>Class Information</h2>
                <div class="form-group">
                    <label for="className">Class Name</label>
                    <input type="text" id="className" name="className" placeholder="e.g., Economics 101, AP Biology" required>
                    <div class="help-text">The name of the class or course</div>
                </div>
                <div class="form-group">
                    <label for="subject">Subject/Topic</label>
                    <input type="text" id="subject" name="subject" placeholder="e.g., Supply and Demand, Cell Biology" required>
                    <div class="help-text">The specific topic being studied</div>
                </div>
                <div class="form-group">
                    <label for="testInfo">Test Information</label>
                    <textarea id="testInfo" name="testInfo" placeholder="Any additional details about the test (optional)"></textarea>
                    <div class="help-text">Date, format, chapters covered, etc.</div>
                </div>
            </div>

            <div class="section">
                <h2>Source Materials</h2>
                <div class="form-group">
                    <label for="sourcePaths">Source File Locations</label>
                    <textarea id="sourcePaths" name="sourcePaths" placeholder="/path/to/notes&#10;/path/to/images&#10;/path/to/pdfs" required></textarea>
                    <div class="help-text">Enter file or folder paths, one per line. All files in folders will be scanned.</div>
                </div>
            </div>

            <div class="section">
                <h2>Quiz Settings</h2>
                <div class="form-group">
                    <label for="questionCount">Number of Questions</label>
                    <input type="number" id="questionCount" name="questionCount" min="5" max="200" value="40">
                    <div class="help-text">Total number of questions to generate (5-200)</div>
                </div>

                <div class="form-group">
                    <label>Question Types</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="multipleChoice" name="multipleChoice" checked>
                            <label for="multipleChoice">Multiple Choice (4 options)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trueFalse" name="trueFalse">
                            <label for="trueFalse">True/False</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="fillBlank" name="fillBlank" checked>
                            <label for="fillBlank">Fill in the Blank</label>
                        </div>
                    </div>
                    <div class="help-text">Select at least one question type</div>
                </div>

                <div class="form-group">
                    <label>Include Study Notes</label>
                    <div class="radio-group">
                        <div class="radio-item">
                            <input type="radio" id="notesYes" name="includeNotes" value="yes" checked>
                            <label for="notesYes">Yes</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="notesNo" name="includeNotes" value="no">
                            <label for="notesNo">No</label>
                        </div>
                    </div>
                    <div class="help-text">Include relevant notes/explanations for each question</div>
                </div>

                <div class="form-group">
                    <label for="difficulty">Difficulty Level</label>
                    <div class="radio-group">
                        <div class="radio-item">
                            <input type="radio" id="diffEasy" name="difficulty" value="easy">
                            <label for="diffEasy">Easy</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="diffMedium" name="difficulty" value="medium" checked>
                            <label for="diffMedium">Medium</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="diffHard" name="difficulty" value="hard">
                            <label for="diffHard">Hard</label>
                        </div>
                    </div>
                    <div class="help-text">Overall difficulty of questions</div>
                </div>
            </div>

            <div class="buttons">
                <button type="button" id="cancel">Cancel</button>
                <button type="submit" id="submit">Generate Quiz</button>
            </div>
        </form>
    </div>

    <script>
        document.getElementById('quizForm').addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate at least one question type selected
            const multipleChoice = document.getElementById('multipleChoice').checked;
            const trueFalse = document.getElementById('trueFalse').checked;
            const fillBlank = document.getElementById('fillBlank').checked;

            if (!multipleChoice && !trueFalse && !fillBlank) {
                alert('Please select at least one question type');
                return;
            }

            // Collect form data
            const data = {
                className: document.getElementById('className').value.trim(),
                subject: document.getElementById('subject').value.trim(),
                testInfo: document.getElementById('testInfo').value.trim(),
                sourcePaths: document.getElementById('sourcePaths').value.trim().split('\\n').map(p => p.trim()).filter(p => p),
                questionCount: parseInt(document.getElementById('questionCount').value),
                questionTypes: {
                    multipleChoice: multipleChoice,
                    trueFalse: trueFalse,
                    fillBlank: fillBlank
                },
                includeNotes: document.querySelector('input[name="includeNotes"]:checked').value === 'yes',
                difficulty: document.querySelector('input[name="difficulty"]:checked').value
            };

            // Submit
            fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => {
                document.body.innerHTML = '<div class="container"><div class="header"><h1>Success!</h1></div><p style="padding: 30px;">Quiz parameters received. You can close this window.</p></div>';
            });
        });

        document.getElementById('cancel').addEventListener('click', function() {
            if (confirm('Cancel quiz creation?')) {
                fetch('/cancel', {method: 'POST'}).then(() => window.close());
            }
        });
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
                ParamsHandler.params_data = json.loads(post_data.decode())
            except:
                pass

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

            ParamsHandler.server_should_stop = True

        elif self.path == '/cancel':
            ParamsHandler.params_data = None
            ParamsHandler.server_should_stop = True

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')


def get_params_via_dialog():
    """Show web form to collect quiz parameters."""
    port = 8766
    server = HTTPServer(('127.0.0.1', port), ParamsHandler)

    def run_server():
        while not ParamsHandler.server_should_stop:
            server.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = f'http://127.0.0.1:{port}'
    print(f"\nOpening quiz configuration form at {url}")

    try:
        subprocess.run(['open', url], check=True)
    except:
        print(f"Please open this URL in your browser: {url}")

    server_thread.join(timeout=600)

    if ParamsHandler.params_data is None:
        print("INFO: User cancelled", file=sys.stderr)
        sys.exit(0)

    return ParamsHandler.params_data


def main():
    """Main entry point."""
    print("=== Quiz Maker: Parameter Collection ===")

    if not ensure_configured():
        print("ERROR: Configuration required", file=sys.stderr)
        sys.exit(1)

    params = get_params_via_dialog()

    print("\n=== Quiz Parameters ===")
    print(json.dumps(params, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
