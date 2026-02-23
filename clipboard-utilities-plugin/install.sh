#!/bin/bash
#
# Clipboard Utilities Plugin Installer
# Note: This plugin is installed automatically by Claude Code marketplace
# This script is provided for manual installation if needed
#

set -e

echo "=== Clipboard Utilities Plugin ==="
echo ""
echo "This plugin provides clipboard utilities for copying formatted text"
echo "without paste issues across all platforms (macOS, Linux, Windows, SSH)."
echo ""
echo "Installation:"
echo "  The plugin is automatically installed via Claude Code marketplace."
echo "  No additional setup required."
echo ""
echo "Platform requirements:"
echo "  - macOS: Uses pbcopy (pre-installed)"
echo "  - Linux: Requires xclip (install with: sudo apt-get install xclip)"
echo "  - Windows: Uses clip (pre-installed)"
echo "  - WSL2: Uses clip.exe (pre-installed)"
echo "  - SSH: Uses OSC 52 escape sequences"
echo ""
echo "Usage:"
echo "  Simply ask Claude to draft emails or documents, and they will be"
echo "  copied directly to your clipboard with clean formatting."
echo ""
echo "Examples:"
echo "  'Draft an email to Sarah about the project update'"
echo "  'Create a technical requirements document'"
echo ""
