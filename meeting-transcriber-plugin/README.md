# Meeting Transcriber Plugin for Claude Code

A Claude Code plugin that transforms meeting transcripts into professional Obsidian-formatted notes with AI-powered processing.

## Features

- Web-based input dialog with date/time collection
- Handles transcripts of any size (tested up to 50,000+ words)
- Optional meeting date and time input (defaults to today/09:00 if not provided)
- Chunked processing prevents timeouts on long transcripts
- Parallel AI agent processing for efficiency
- Automatic YAML frontmatter generation with separate date and time fields
- Meeting notes with executive summary, discussions, decisions, and action items
- Cleaned transcript preservation (95-100% of original content)
- People name normalization against your Obsidian vault
- User-specific configuration for Obsidian paths

## Installation

### Via Claude Code Marketplace (Recommended)

1. **Add the marketplace** - In Claude Code, run:
   ```
   /plugin marketplace add mikeskarl/Claude_Plugins
   ```

2. **Install the plugin:**
   ```
   /plugin install meeting-transcriber@claude-plugins
   ```

3. **Restart Claude Code** to load the plugin

### Verify Installation

Check that the plugin is installed:
```
/plugin list
```

You should see `meeting-transcriber@claude-plugins` in the list.

## First-Time Setup

On first use, a web dialog will prompt you to configure:

1. **Obsidian Vault Path** - The root directory of your Obsidian vault
2. **Meetings Folder** - Where to save meeting notes (default: `Calendar/Meetings`)
3. **People Folder** - Where your people notes are stored (default: `Atlas/People`)

Configuration is saved locally and not tracked in git.

## Usage

In Claude Code, ask Claude to process your meeting transcript:

```
Process my meeting transcript
```

Or:

```
Use the meeting transcriber to process my transcript
```

The plugin will:
1. Open a web dialog where you can:
   - Enter the meeting date (defaults to today)
   - Enter the meeting time (defaults to 09:00)
   - Paste your transcript
2. Extract metadata (title, participants, client, project, etc.)
3. Clean the transcript
4. Normalize participant names against your People vault
5. Generate structured meeting notes
6. Save everything to your Obsidian vault with proper YAML frontmatter

**Note:** Date and time fields are optional. If you don't provide them, the system will attempt to extract them from the transcript. If extraction fails, you'll be prompted to provide the date.

## Reconfigure

To change your Obsidian paths, the config is stored at:
```
~/.claude/plugins/marketplaces/claude-plugins/meeting-transcriber-plugin/skills/meeting-transcriber/user_config.json
```

Delete this file and run the plugin again to reconfigure, or run:
```bash
python3 ~/.claude/plugins/marketplaces/claude-plugins/meeting-transcriber-plugin/skills/meeting-transcriber/scripts/config.py --reconfigure
```

## Agents Included

| Agent | Purpose |
|-------|---------|
| meeting-transcriber | Main orchestrator - coordinates all processing |

The meeting-transcriber agent coordinates these sub-skills:
- metadata-extractor - Extracts date, time, title, participants from transcript (prefers user-provided values)
- transcript-cleaner - Cleans transcript while preserving 95%+ content
- people-normalizer - Normalizes names against your People vault
- meeting-notes-generator - Generates structured meeting notes

## Requirements

- Claude Code
- Python 3.8+
- macOS (for `open` command in web dialogs)
- Obsidian vault (for output)

## Updating the Plugin

To get the latest version:
```
/plugin marketplace update claude-plugins
```

Then restart Claude Code.

## Uninstalling

```
/plugin uninstall meeting-transcriber@claude-plugins
```

## Troubleshooting

### Plugin not recognized after installation
- Make sure you restarted Claude Code after installing
- Run `/plugin list` to verify installation
- Try `/plugin marketplace update claude-plugins` and restart again

### Web dialog doesn't open
- Ensure Python 3 is installed
- Check that port 8765 (transcript) and 8766 (config) are available
- Try opening the URL manually in your browser

### Configuration issues
- Delete the `user_config.json` file and run again
- Ensure your Obsidian vault path exists

### Processing errors
- Check the terminal output for specific error messages
- Large transcripts (>30,000 words) may take 3-5 minutes to process

## License

MIT License
