#!/usr/bin/env python3
"""
Configuration management for Meeting Transcriber plugin.
Handles first-run setup via web dialog and provides config access for other scripts.
"""

import sys
import json
import subprocess
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler


# Config file location (in the same directory as the scripts)
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "user_config.json"

# Default paths (relative to vault root)
DEFAULT_MEETINGS_FOLDER = "Calendar/Meetings"
DEFAULT_PEOPLE_FOLDER = "Atlas/People"


def get_config():
    """Load and return the user configuration."""
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Failed to read config: {e}", file=sys.stderr)
        return None


def save_config(config):
    """Save user configuration."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save config: {e}", file=sys.stderr)
        return False


def get_meetings_dir():
    """Get the full path to the meetings directory."""
    config = get_config()
    if not config:
        raise RuntimeError("Meeting Transcriber not configured. Run config setup first.")

    vault = Path(config['obsidian_vault'])
    meetings = config.get('meetings_folder', DEFAULT_MEETINGS_FOLDER)
    return vault / meetings


def get_people_dir():
    """Get the full path to the people directory."""
    config = get_config()
    if not config:
        raise RuntimeError("Meeting Transcriber not configured. Run config setup first.")

    vault = Path(config['obsidian_vault'])
    people = config.get('people_folder', DEFAULT_PEOPLE_FOLDER)
    return vault / people


def is_configured():
    """Check if the plugin has been configured."""
    config = get_config()
    if not config:
        return False

    # Verify required fields exist
    if 'obsidian_vault' not in config:
        return False

    # Verify vault path exists
    vault_path = Path(config['obsidian_vault'])
    if not vault_path.exists():
        print(f"WARNING: Configured vault path does not exist: {vault_path}", file=sys.stderr)
        return False

    return True


class ConfigHandler(BaseHTTPRequestHandler):
    """HTTP handler for configuration web form."""
    config_data = None
    server_should_stop = False

    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

    def do_GET(self):
        """Serve the configuration form."""
        # Try to detect existing Obsidian vault
        default_vault = ""
        common_paths = [
            Path.home() / "Documents" / "ObsidianVault",
            Path.home() / "Documents" / "Obsidian",
            Path.home() / "ObsidianVault",
            Path.home() / "Obsidian",
        ]
        for path in common_paths:
            if path.exists():
                default_vault = str(path)
                break

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Meeting Transcriber Setup</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            max-width: 700px;
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
        .form-group {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            font-weight: 500;
            margin-bottom: 8px;
            color: #1d1d1f;
        }}
        .hint {{
            font-size: 12px;
            color: #86868b;
            margin-top: 4px;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 12px;
            font-size: 14px;
            border: 2px solid #d2d2d7;
            border-radius: 8px;
            box-sizing: border-box;
        }}
        input[type="text"]:focus {{
            outline: none;
            border-color: #0071e3;
        }}
        .error {{
            border-color: #ff3b30 !important;
        }}
        .error-message {{
            color: #ff3b30;
            font-size: 12px;
            margin-top: 4px;
            display: none;
        }}
        .buttons {{
            margin-top: 30px;
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
        #save {{
            background-color: #0071e3;
            color: white;
        }}
        #save:hover {{
            background-color: #0077ed;
        }}
        .info-box {{
            background-color: #f0f7ff;
            border: 1px solid #0071e3;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .info-box p {{
            color: #1d1d1f;
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Meeting Transcriber Setup</h1>

        <div class="info-box">
            <p>Configure your Obsidian vault paths. This only needs to be done once.</p>
        </div>

        <form id="configForm">
            <div class="form-group">
                <label for="vault">Obsidian Vault Path</label>
                <input type="text" id="vault" name="vault"
                       value="{default_vault}"
                       placeholder="/Users/yourname/Documents/ObsidianVault">
                <div class="hint">Full path to your Obsidian vault root directory</div>
                <div class="error-message" id="vault-error">This path does not exist</div>
            </div>

            <div class="form-group">
                <label for="meetings">Meetings Folder (relative to vault)</label>
                <input type="text" id="meetings" name="meetings"
                       value="{DEFAULT_MEETINGS_FOLDER}"
                       placeholder="Calendar/Meetings">
                <div class="hint">Where to save meeting notes (will be created if it doesn't exist)</div>
            </div>

            <div class="form-group">
                <label for="people">People Folder (relative to vault)</label>
                <input type="text" id="people" name="people"
                       value="{DEFAULT_PEOPLE_FOLDER}"
                       placeholder="Atlas/People">
                <div class="hint">Where your people notes are stored (for name matching)</div>
            </div>

            <div class="buttons">
                <button type="button" id="cancel" onclick="handleCancel()">Cancel</button>
                <button type="submit" id="save">Save Configuration</button>
            </div>
        </form>
    </div>

    <script>
        document.getElementById('configForm').addEventListener('submit', function(e) {{
            e.preventDefault();

            const vault = document.getElementById('vault').value.trim();
            const meetings = document.getElementById('meetings').value.trim();
            const people = document.getElementById('people').value.trim();

            if (!vault) {{
                document.getElementById('vault').classList.add('error');
                document.getElementById('vault-error').style.display = 'block';
                document.getElementById('vault-error').textContent = 'Vault path is required';
                return;
            }}

            // Submit configuration
            fetch('/save', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    obsidian_vault: vault,
                    meetings_folder: meetings || '{DEFAULT_MEETINGS_FOLDER}',
                    people_folder: people || '{DEFAULT_PEOPLE_FOLDER}'
                }})
            }}).then(response => response.json())
              .then(data => {{
                if (data.success) {{
                    document.body.innerHTML = '<div class="container"><h1>Setup Complete!</h1><p>Configuration saved. You can close this window and continue using the Meeting Transcriber.</p></div>';
                }} else {{
                    document.getElementById('vault').classList.add('error');
                    document.getElementById('vault-error').style.display = 'block';
                    document.getElementById('vault-error').textContent = data.error || 'Failed to save configuration';
                }}
            }});
        }});

        function handleCancel() {{
            if (confirm('Cancel setup? The Meeting Transcriber will not work without configuration.')) {{
                fetch('/cancel', {{method: 'POST'}}).then(() => {{
                    window.close();
                }});
            }}
        }}

        // Clear error on input
        document.getElementById('vault').addEventListener('input', function() {{
            this.classList.remove('error');
            document.getElementById('vault-error').style.display = 'none';
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
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())

                # Validate vault path exists
                vault_path = Path(data['obsidian_vault'])
                if not vault_path.exists():
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': f'Path does not exist: {vault_path}'
                    }).encode())
                    return

                # Create meetings directory if needed
                meetings_dir = vault_path / data.get('meetings_folder', DEFAULT_MEETINGS_FOLDER)
                meetings_dir.mkdir(parents=True, exist_ok=True)

                # Save configuration
                ConfigHandler.config_data = data

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())

                # Signal server to stop
                ConfigHandler.server_should_stop = True

            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())

        elif self.path == '/cancel':
            ConfigHandler.config_data = None
            ConfigHandler.server_should_stop = True

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')


def run_config_dialog():
    """Show web form dialog for configuration."""
    # Reset state
    ConfigHandler.config_data = None
    ConfigHandler.server_should_stop = False

    # Start local web server
    port = 8766  # Different port from get_transcript.py
    server = HTTPServer(('127.0.0.1', port), ConfigHandler)

    # Run server in background thread
    def run_server():
        while not ConfigHandler.server_should_stop:
            server.handle_request()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Open browser
    url = f'http://127.0.0.1:{port}'
    print(f"\nOpening configuration at {url}")
    print("Please configure your Obsidian vault paths...")

    try:
        subprocess.run(['open', url], check=True)
    except Exception:
        print(f"Please open this URL in your browser: {url}")

    # Wait for form submission
    server_thread.join(timeout=300)  # 5 minute timeout

    config = ConfigHandler.config_data

    if config is None:
        print("INFO: Configuration cancelled", file=sys.stderr)
        return False

    # Save configuration
    if save_config(config):
        print(f"SUCCESS: Configuration saved to {CONFIG_FILE}")
        return True

    return False


def ensure_configured():
    """Ensure the plugin is configured, prompting user if needed."""
    if is_configured():
        return True

    print("Meeting Transcriber requires initial configuration.")
    return run_config_dialog()


def main():
    """Main entry point - run configuration dialog."""
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        # Just check if configured
        if is_configured():
            config = get_config()
            print(f"CONFIGURED=true")
            print(f"VAULT={config['obsidian_vault']}")
            print(f"MEETINGS={config.get('meetings_folder', DEFAULT_MEETINGS_FOLDER)}")
            print(f"PEOPLE={config.get('people_folder', DEFAULT_PEOPLE_FOLDER)}")
            return 0
        else:
            print("CONFIGURED=false")
            return 1

    elif len(sys.argv) > 1 and sys.argv[1] == '--reconfigure':
        # Force reconfiguration
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        success = run_config_dialog()
        return 0 if success else 1

    else:
        # Normal mode - configure if needed
        success = ensure_configured()
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
