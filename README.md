# Claude Code Plugins

A collection of Claude Code plugins for productivity workflows.

## Installation via Claude Code Marketplace

The easiest way to install these plugins is through Claude Code's plugin marketplace:

### Step 1: Add the Marketplace

In Claude Code, run:
```
/plugin marketplace add mikeskarl/Claude_Plugins
```

### Step 2: Install a Plugin

```
/plugin install meeting-transcriber@claude-plugins
```

Or use the interactive plugin browser:
```
/plugin
```

### Step 3: Restart Claude Code

After installation, restart Claude Code to load the new plugins.

## Available Plugins

### [Meeting Transcriber](./meeting-transcriber-plugin/)

Transform meeting transcripts into professional Obsidian-formatted notes with AI-powered processing.

**Features:**
- Web-based transcript input dialog
- Handles transcripts of any size (tested up to 50,000+ words)
- Chunked processing prevents timeouts on long transcripts
- Parallel AI agent processing for efficiency
- User-specific configuration for Obsidian vault paths

## Managing Plugins

### List Installed Plugins
```
/plugin list
```

### Update Plugins
```
/plugin marketplace update claude-plugins
```

### Remove a Plugin
```
/plugin uninstall meeting-transcriber@claude-plugins
```

### Remove the Marketplace
```
/plugin marketplace remove claude-plugins
```

## Requirements

- Claude Code
- Python 3.8+
- macOS (some plugins use macOS-specific features)

## License

MIT License
