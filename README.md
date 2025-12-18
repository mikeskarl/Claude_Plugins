# Claude Code Plugins

![GitHub stars](https://img.shields.io/github/stars/mikeskarl/Claude_Plugins?style=social)
![Version](https://img.shields.io/badge/version-1.0.16-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Plugins](https://img.shields.io/badge/plugins-2-purple)

Professional-grade Claude Code plugins that automate tedious workflows. Transform meeting transcripts into structured notes, generate study materials from any content, and more.

## Why Use These Plugins?

- **Meeting Transcriber** - Process 2-hour meeting transcripts into organized Obsidian notes in 2 minutes. Perfect for consultants, PMs, and anyone drowning in meeting notes.
- **Quiz Maker** - Generate interactive study quizzes from any source material (PDFs, images, text). Great for educators and students.

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

**Automate your meeting documentation workflow.**

- ✅ Handles transcripts up to 50,000+ words
- ✅ Generates executive summaries, action items, and decisions
- ✅ Integrates seamlessly with Obsidian vaults
- ✅ Normalizes participant names automatically
- ✅ Preserves 95-100% of original content in cleaned transcripts

**Use Cases:** Client meetings, team standups, interviews, consultations

### [Quiz Maker](./quiz-maker-plugin/)

**Generate study materials from any content source.**

- ✅ Supports text, images, and PDF sources
- ✅ Customizable question types and difficulty levels
- ✅ Interactive quiz format
- ✅ Perfect for creating homework or study guides

**Use Cases:** Teachers creating assignments, students preparing for exams, training materials

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
