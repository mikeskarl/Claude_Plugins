# Clipboard Utilities Plugin

Copy formatted text directly to your system clipboard without paste formatting issues.

## Features

- **Clean paragraph formatting** - Each paragraph formatted as single line, no extra returns when pasting
- **Cross-platform support** - Works on macOS, Linux, Windows, WSL, and SSH
- **Email drafting** - Draft emails that paste cleanly into any email client
- **Document creation** - Create formatted documents ready to paste into text editors

## Installation

### Via Claude Code Marketplace

```bash
/plugin marketplace add mikeskarl/Claude_Plugins
/plugin install clipboard-utilities@claude-plugins
```

Then restart Claude Code.

## Usage

Simply ask Claude to draft content and it will automatically copy it to your clipboard:

```
Draft an email to Sarah following up on our meeting about the platform demo
```

```
Create a technical requirements document for the new dashboard feature
```

```
Write a project update email for the team
```

After Claude runs the command, paste with `Cmd+V` (macOS) or `Ctrl+V` (Windows/Linux).

## How It Works

The plugin formats text so each paragraph is a single continuous line, separated by blank lines. This prevents unwanted line breaks when pasting into TextEdit, Word, email clients, and other applications.

**Before (normal terminal copy):**
```
This is a paragraph that wraps
in the terminal and creates extra
line breaks when you paste it.
```

**After (with clipboard-text):**
```
This is a paragraph that wraps in the terminal and creates extra line breaks when you paste it.
```

## Platform Support

- **macOS** - Uses `pbcopy`
- **Linux** - Uses `xclip` (install with `sudo apt-get install xclip`)
- **Windows** - Uses `clip`
- **WSL2** - Uses `clip.exe`
- **SSH** - Uses OSC 52 escape sequences

## Requirements

- Claude Code
- Platform-specific clipboard utility (pre-installed on macOS/Windows, `xclip` required on Linux)

## License

MIT License
