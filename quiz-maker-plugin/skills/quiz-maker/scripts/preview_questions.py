#!/usr/bin/env python3
"""
Preview generated quiz questions.
Allows user to review, edit, and request regeneration of questions.
"""

import subprocess
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class QuestionPreviewHandler(BaseHTTPRequestHandler):
    questions_data = None
    edited_questions = None
    regenerate_requests = []
    user_confirmed = False
    server_should_stop = False

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        """Serve the question preview page."""
        if not QuestionPreviewHandler.questions_data:
            self.send_error(500, "No questions data available")
            return

        questions = QuestionPreviewHandler.questions_data

        # Build HTML for each question
        question_items = []
        for i, q in enumerate(questions):
            q_type = q.get('type', 'multiple-choice')
            question_text = q.get('question', '')
            options = q.get('options', [])
            correct_answer = q.get('correctAnswer', '')
            notes = q.get('notes', '')

            # Format options display
            if q_type == 'multiple-choice':
                options_html = '<ul class="options-list">'
                for opt in options:
                    is_correct = '✓' if opt == correct_answer else ''
                    options_html += f'<li>{opt} {is_correct}</li>'
                options_html += '</ul>'
            elif q_type == 'true-false':
                options_html = f'<div class="answer-display">Answer: {correct_answer}</div>'
            elif q_type == 'fill-blank':
                options_html = f'<div class="answer-display">Answer: {correct_answer}</div>'
            else:
                options_html = ''

            item_html = f'''
            <div class="question-item" data-index="{i}">
                <div class="question-header">
                    <span class="question-number">Question {i + 1}</span>
                    <span class="question-type">{q_type}</span>
                    <button class="regenerate-btn" data-index="{i}">Regenerate</button>
                </div>
                <div class="question-content">
                    <div class="editable-section">
                        <label>Question Text:</label>
                        <textarea class="question-text" data-index="{i}" data-field="question">{question_text}</textarea>
                    </div>
                    <div class="editable-section">
                        <label>Current Options/Answer:</label>
                        {options_html}
                    </div>
                    <div class="editable-section">
                        <label>Study Notes:</label>
                        <textarea class="question-notes" data-index="{i}" data-field="notes">{notes}</textarea>
                    </div>
                </div>
            </div>
            '''
            question_items.append(item_html)

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Review Quiz Questions</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #000000;
        }}
        .header {{
            background-color: #800000;
            color: white;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}
        .subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        .instructions {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .instructions h3 {{
            color: #800000;
            margin-bottom: 10px;
        }}
        .question-item {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .question-item.regenerate-requested {{
            border: 3px solid #ffc107;
            background-color: #fffbf0;
        }}
        .question-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .question-number {{
            font-weight: 600;
            font-size: 16px;
        }}
        .question-type {{
            background-color: #800000;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .regenerate-btn {{
            margin-left: auto;
            padding: 6px 12px;
            background-color: #ffc107;
            color: #000;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .regenerate-btn:hover {{
            background-color: #ffb300;
        }}
        .regenerate-btn.requested {{
            background-color: #28a745;
            color: white;
        }}
        .editable-section {{
            margin-bottom: 15px;
        }}
        .editable-section label {{
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            font-size: 13px;
            color: #6c757d;
        }}
        textarea {{
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            min-height: 60px;
        }}
        textarea:focus {{
            outline: none;
            border-color: #800000;
        }}
        .options-list {{
            list-style: none;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .options-list li {{
            padding: 8px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
        }}
        .answer-display {{
            padding: 10px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            font-weight: 600;
        }}
        .buttons {{
            position: sticky;
            bottom: 0;
            background: #800000;
            padding: 20px;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .regenerate-status {{
            font-size: 14px;
            color: white;
            font-weight: 600;
        }}
        .button-group {{
            display: flex;
            gap: 10px;
        }}
        button {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        #cancel {{
            background-color: #000000;
            color: white;
        }}
        #cancel:hover {{
            background-color: #333333;
        }}
        #continue {{
            background-color: white;
            color: #800000;
            border: 2px solid white;
        }}
        #continue:hover {{
            background-color: #f0f0f0;
        }}
        button:active {{
            transform: scale(0.98);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Review Quiz Questions</h1>
        <div class="subtitle">{len(questions)} questions generated - Edit or regenerate as needed</div>
    </div>

    <div class="container">
        <div class="instructions">
            <h3>Instructions</h3>
            <p>Review the generated questions below. You can:</p>
            <ul style="margin-left: 20px; margin-top: 10px; line-height: 1.8;">
                <li>Edit question text and study notes directly in the text areas</li>
                <li>Click "Regenerate" on any question to mark it for regeneration</li>
                <li>When ready, click "Continue" to proceed (or "Regenerate Selected" if you marked any)</li>
            </ul>
        </div>

        {''.join(question_items)}
    </div>

    <div class="buttons">
        <div class="regenerate-status" id="status">Ready to continue</div>
        <div class="button-group">
            <button id="cancel">Cancel</button>
            <button id="continue">Continue</button>
        </div>
    </div>

    <script>
        let regenerateRequests = new Set();

        // Handle regenerate button clicks
        document.querySelectorAll('.regenerate-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const index = parseInt(this.dataset.index);
                const item = document.querySelector(`.question-item[data-index="${{index}}"]`);

                if (regenerateRequests.has(index)) {{
                    regenerateRequests.delete(index);
                    item.classList.remove('regenerate-requested');
                    this.classList.remove('requested');
                    this.textContent = 'Regenerate';
                }} else {{
                    regenerateRequests.add(index);
                    item.classList.add('regenerate-requested');
                    this.classList.add('requested');
                    this.textContent = '✓ Marked';
                }}

                updateStatus();
            }});
        }});

        function updateStatus() {{
            const status = document.getElementById('status');
            const continueBtn = document.getElementById('continue');

            if (regenerateRequests.size > 0) {{
                status.textContent = `${{regenerateRequests.size}} question(s) marked for regeneration`;
                continueBtn.textContent = 'Regenerate Selected';
            }} else {{
                status.textContent = 'Ready to continue';
                continueBtn.textContent = 'Continue';
            }}
        }}

        document.getElementById('continue').addEventListener('click', function() {{
            // Collect edited questions
            const questions = [];
            document.querySelectorAll('.question-item').forEach(item => {{
                const index = parseInt(item.dataset.index);
                const questionText = item.querySelector('.question-text').value;
                const notes = item.querySelector('.question-notes').value;

                questions.push({{
                    index: index,
                    question: questionText,
                    notes: notes
                }});
            }});

            // Send data
            fetch('/submit', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    questions: questions,
                    regenerate: Array.from(regenerateRequests)
                }})
            }}).then(() => {{
                document.body.innerHTML = '<div class="header"><h1>Success!</h1></div><div style="padding: 30px; text-align: center;">Questions confirmed. You can close this window.</div>';
            }});
        }});

        document.getElementById('cancel').addEventListener('click', function() {{
            if (confirm('Cancel quiz creation?')) {{
                fetch('/cancel', {{method: 'POST'}}).then(() => window.close());
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
                QuestionPreviewHandler.edited_questions = data['questions']
                QuestionPreviewHandler.regenerate_requests = data['regenerate']
                QuestionPreviewHandler.user_confirmed = True
            except:
                pass

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

            QuestionPreviewHandler.server_should_stop = True

        elif self.path == '/cancel':
            QuestionPreviewHandler.user_confirmed = False
            QuestionPreviewHandler.server_should_stop = True

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')


def preview_questions(questions_json):
    """Show preview dialog with questions."""
    QuestionPreviewHandler.questions_data = json.loads(questions_json)

    port = 8768
    server = HTTPServer(('127.0.0.1', port), QuestionPreviewHandler)

    def run_server():
        while not QuestionPreviewHandler.server_should_stop:
            server.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = f'http://127.0.0.1:{port}'
    print(f"\nOpening question preview at {url}")

    try:
        subprocess.run(['open', url], check=True)
    except:
        print(f"Please open this URL in your browser: {url}")

    server_thread.join(timeout=1800)  # 30 minute timeout

    if not QuestionPreviewHandler.user_confirmed:
        print("INFO: User cancelled", file=sys.stderr)
        sys.exit(0)

    return {
        'questions': QuestionPreviewHandler.edited_questions,
        'regenerate': QuestionPreviewHandler.regenerate_requests
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: preview_questions.py '<questions_json>'", file=sys.stderr)
        sys.exit(1)

    questions_json = sys.argv[1]

    print("=== Question Preview ===")
    result = preview_questions(questions_json)

    print("\n=== Review Result ===")
    print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
