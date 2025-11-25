# Meeting Transcriber Plugin for Claude Code

A Claude Code plugin that transforms meeting transcripts into professional Obsidian-formatted notes with AI-powered processing.

## Features

- Web-based transcript input dialog
- Handles transcripts of any size (tested up to 50,000+ words)
- Chunked processing prevents timeouts on long transcripts
- Parallel AI agent processing for efficiency
- Automatic YAML frontmatter generation
- Meeting notes with executive summary, discussions, decisions, and action items
- Cleaned transcript preservation (95-100% of original content)
- People name normalization against your Obsidian vault
- User-specific configuration for Obsidian paths

## Installation

### Quick Install

```bash
git clone <repository-url> meeting-transcriber-plugin
cd meeting-transcriber-plugin
./install.sh
```

### Manual Install

Copy the skills to your Claude Code skills directory:

```bash
cp -r skills/* ~/.claude/skills/
```

## First-Time Setup

On first use, a web dialog will prompt you to configure:

1. **Obsidian Vault Path** - The root directory of your Obsidian vault
2. **Meetings Folder** - Where to save meeting notes (default: `Calendar/Meetings`)
3. **People Folder** - Where your people notes are stored (default: `Atlas/People`)

Configuration is saved locally and not tracked in git.

## Usage

In Claude Code, invoke the skill:

```
Use the meeting-transcriber skill to process my meeting transcript
```

Or simply:

```
Process my meeting transcript
```

The plugin will:
1. Open a web dialog to paste your transcript
2. Extract metadata (date, title, participants)
3. Clean the transcript
4. Normalize participant names against your People vault
5. Generate structured meeting notes
6. Save everything to your Obsidian vault

## Reconfigure

To change your Obsidian paths:

```bash
python3 ~/.claude/skills/meeting-transcriber/scripts/config.py --reconfigure
```

To view current configuration:

```bash
python3 ~/.claude/skills/meeting-transcriber/scripts/config.py --check
```

## Skills Included

| Skill | Purpose |
|-------|---------|
| meeting-transcriber | Main orchestrator - coordinates all other skills |
| metadata-extractor | Extracts date, title, participants from transcript |
| transcript-cleaner | Cleans transcript while preserving 95%+ content |
| people-normalizer | Normalizes names against your People vault |
| meeting-notes-generator | Generates structured meeting notes |

## Requirements

- Claude Code
- Python 3.8+
- macOS (for `open` command in web dialogs)
- Obsidian vault (for output)

## Configuration File

User configuration is stored at:
```
~/.claude/skills/meeting-transcriber/user_config.json
```

Format:
```json
{
  "obsidian_vault": "/path/to/your/ObsidianVault",
  "meetings_folder": "Calendar/Meetings",
  "people_folder": "Atlas/People"
}
```

## Troubleshooting

### Web dialog doesn't open
- Ensure Python 3 is installed
- Check that port 8765 (transcript) and 8766 (config) are available
- Try opening the URL manually in your browser

### Configuration issues
- Delete `~/.claude/skills/meeting-transcriber/user_config.json` and run again
- Ensure your Obsidian vault path exists

### Processing errors
- Check the terminal output for specific error messages
- Large transcripts (>30,000 words) may take 3-5 minutes to process

## License

MIT License
