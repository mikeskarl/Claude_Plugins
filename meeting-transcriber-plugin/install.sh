#!/bin/bash
#
# Meeting Transcriber Plugin Installer
# Installs the meeting transcriber skills to ~/.claude/skills/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DEST="$HOME/.claude/skills"

echo "=== Meeting Transcriber Plugin Installer ==="
echo ""

# Check if skills source directory exists
if [ ! -d "$SKILLS_SRC" ]; then
    echo "ERROR: Skills directory not found at $SKILLS_SRC"
    echo "Please run this script from the plugin root directory."
    exit 1
fi

# Create destination directory if needed
mkdir -p "$SKILLS_DEST"

# List of skills to install
SKILLS=(
    "meeting-transcriber"
    "meeting-notes-generator"
    "metadata-extractor"
    "people-normalizer"
    "transcript-cleaner"
)

echo "Installing skills to $SKILLS_DEST..."
echo ""

for skill in "${SKILLS[@]}"; do
    if [ -d "$SKILLS_SRC/$skill" ]; then
        echo "  Installing $skill..."

        # Remove existing skill directory if present
        if [ -d "$SKILLS_DEST/$skill" ]; then
            rm -rf "$SKILLS_DEST/$skill"
        fi

        # Copy skill directory
        cp -r "$SKILLS_SRC/$skill" "$SKILLS_DEST/"

        # Make Python scripts executable
        if [ -d "$SKILLS_DEST/$skill/scripts" ]; then
            chmod +x "$SKILLS_DEST/$skill/scripts/"*.py 2>/dev/null || true
        fi
    else
        echo "  WARNING: Skill not found: $skill"
    fi
done

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Skills installed to: $SKILLS_DEST"
echo ""
echo "Next steps:"
echo "1. Open Claude Code"
echo "2. Say: 'Use the meeting-transcriber skill'"
echo "3. On first use, you'll be prompted to configure your Obsidian vault paths"
echo ""
echo "To reconfigure paths later:"
echo "  python3 ~/.claude/skills/meeting-transcriber/scripts/config.py --reconfigure"
echo ""
