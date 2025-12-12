#!/usr/bin/env python3
"""
Preview extracted content from source materials.
Shows side-by-side view of originals and extractions.
Allows user to make edits before question generation.
"""

import subprocess
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from urllib.parse import unquote
import html
import base64
from pathlib import Path


class PreviewHandler(BaseHTTPRequestHandler):
    extractions_data = None
    edited_data = None
    user_confirmed = False
    server_should_stop = False

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        """Serve the preview page."""
        if not PreviewHandler.extractions_data:
            self.send_error(500, "No extraction data available")
            return

        extractions = PreviewHandler.extractions_data

        # Build HTML sections for each extraction
        sections_html = []
        for i, item in enumerate(extractions):
            file_type = item.get('type', 'text')
            file_name = item.get('name', 'Unknown')
            file_path = item.get('path', '')
            extracted = item.get('extracted', '')

            # Escape HTML in extracted content for safe display in textarea
            extracted_escaped = html.escape(extracted)

            # Show image preview for image files
            if file_type == 'image':
                try:
                    # Convert image to base64 for display in browser
                    img_path = Path(file_path)
                    if img_path.exists():
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                            # Determine MIME type from extension
                            ext = img_path.suffix.lower()
                            mime_map = {
                                '.jpg': 'image/jpeg',
                                '.jpeg': 'image/jpeg',
                                '.png': 'image/png',
                                '.gif': 'image/gif',
                                '.bmp': 'image/bmp',
                                '.heic': 'image/heic'
                            }
                            mime_type = mime_map.get(ext, 'image/jpeg')
                            preview = f'<div class="image-preview"><img src="data:{mime_type};base64,{img_data}" alt="{file_name}"></div>'
                    else:
                        preview = f'<div class="text-preview">Image not found: {file_path}</div>'
                except Exception as e:
                    preview = f'<div class="text-preview">Error loading image: {str(e)}</div>'
            else:
                preview = f'<div class="text-preview"><strong>Source:</strong> {file_path}</div>'

            section = f'''
            <div class="extraction-item" data-index="{i}">
                <div class="extraction-header">
                    <div class="file-info">
                        <span class="file-type">{file_type.upper()}</span>
                        <span class="file-name">{file_name}</span>
                    </div>
                </div>
                <div class="extraction-content">
                    <div class="preview-column">
                        <h4>Original</h4>
                        {preview}
                    </div>
                    <div class="extracted-column">
                        <h4>Extracted Content</h4>
                        <textarea class="extracted-text" data-index="{i}">{extracted_escaped}</textarea>
                    </div>
                </div>
            </div>
            '''
            sections_html.append(section)

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Review Extracted Content</title>
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
            max-width: 1400px;
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
        .extraction-item {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .extraction-header {{
            margin-bottom: 15px;
        }}
        .file-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .file-type {{
            background-color: #800000;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .file-name {{
            font-weight: 600;
            font-size: 14px;
        }}
        .extraction-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .preview-column, .extracted-column {{
            display: flex;
            flex-direction: column;
        }}
        h4 {{
            font-size: 14px;
            margin-bottom: 10px;
            color: #6c757d;
        }}
        .image-preview {{
            background: #f8f9fa;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }}
        .image-preview img {{
            max-width: 100%;
            max-height: 400px;
            object-fit: contain;
        }}
        .text-preview {{
            background: #f8f9fa;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            color: #333;
            font-size: 12px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        .text-preview strong {{
            color: #800000;
            font-weight: 600;
        }}
        .extracted-text {{
            width: 100%;
            min-height: 200px;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: Monaco, monospace;
            font-size: 12px;
            resize: vertical;
        }}
        .extracted-text:focus {{
            outline: none;
            border-color: #800000;
        }}
        .buttons {{
            position: sticky;
            bottom: 0;
            background: #800000;
            padding: 20px;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: flex-end;
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
        <h1>Review Extracted Content</h1>
        <div class="subtitle">Review and edit extracted content before generating questions</div>
    </div>

    <div class="container">
        <div class="instructions">
            <h3>Instructions</h3>
            <p>Review the extracted content below. You can edit any text in the "Extracted Content" sections. When ready, click "Continue to Questions" to generate quiz questions.</p>
        </div>

        {''.join(sections_html)}
    </div>

    <div class="buttons">
        <button id="cancel">Cancel</button>
        <button id="continue">Continue to Questions</button>
    </div>

    <script>
        document.getElementById('continue').addEventListener('click', function() {{
            const extractions = [];
            document.querySelectorAll('.extracted-text').forEach(textarea => {{
                extractions.push({{
                    index: parseInt(textarea.dataset.index),
                    content: textarea.value
                }});
            }});

            fetch('/submit', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(extractions)
            }}).then(() => {{
                document.body.innerHTML = '<div class="header"><h1>Success!</h1></div><div style="padding: 30px; text-align: center;">Content confirmed. You can close this window.</div>';
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
                PreviewHandler.edited_data = json.loads(post_data.decode())
                PreviewHandler.user_confirmed = True
            except:
                pass

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

            PreviewHandler.server_should_stop = True

        elif self.path == '/cancel':
            PreviewHandler.user_confirmed = False
            PreviewHandler.server_should_stop = True

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')


def preview_extractions(extractions_json):
    """Show preview dialog with extractions."""
    PreviewHandler.extractions_data = json.loads(extractions_json)

    port = 8767
    server = HTTPServer(('127.0.0.1', port), PreviewHandler)

    def run_server():
        while not PreviewHandler.server_should_stop:
            server.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    url = f'http://127.0.0.1:{port}'
    print(f"\nOpening extraction preview at {url}")

    try:
        subprocess.run(['open', url], check=True)
    except:
        print(f"Please open this URL in your browser: {url}")

    server_thread.join(timeout=1800)  # 30 minute timeout

    if not PreviewHandler.user_confirmed:
        print("INFO: User cancelled", file=sys.stderr)
        sys.exit(0)

    return PreviewHandler.edited_data


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: preview_extractions.py '<extractions_json>'", file=sys.stderr)
        sys.exit(1)

    extractions_json = sys.argv[1]

    print("=== Extraction Preview ===")
    edited = preview_extractions(extractions_json)

    print("\n=== Updated Extractions ===")
    print(json.dumps(edited, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
