---
name: clipboard-text
description: Copy formatted text directly to the system clipboard with proper paragraph formatting. Use when drafting emails, documents, or any text content that needs to be pasted cleanly into text editors without extra line breaks. Automatically detects platform (macOS/Linux/Windows/WSL/SSH) and uses appropriate clipboard command.
---

# Clipboard Text

## Overview

Copy formatted text directly to the system clipboard using platform-appropriate commands. Each paragraph is formatted as a single continuous line to prevent unwanted line breaks when pasting into text editors like TextEdit, Word, or email clients.

## When to Use This Skill

Use this skill whenever you need to:
- Draft emails or documents for the user to paste elsewhere
- Copy formatted text without terminal selection issues
- Ensure clean paragraph formatting (no extra returns when pasting)
- Work across different platforms (macOS, Linux, Windows, SSH)

## How It Works

1. Format each paragraph as a single continuous line (no internal breaks)
2. Separate paragraphs with double newlines
3. Pipe the result to the appropriate clipboard command for the user's platform
4. User pastes with Cmd+V (macOS) or Ctrl+V (Windows/Linux)

## Platform Commands

### Local Shells

Detect platform and use the appropriate command:

**macOS:**
```bash
echo "text" | pbcopy
```

**Linux (X11):**
```bash
echo "text" | xclip -selection clipboard
```

**Windows:**
```bash
echo "text" | clip
```

**WSL2:**
```bash
echo "text" | clip.exe
```

### SSH / Remote Shells

When running over SSH, use OSC 52 to write to the local clipboard:

```bash
echo "text" | printf '\e]52;c;%s\a' "$(base64 | tr -d '\n')"
```

## Usage Pattern

Use a heredoc to format multi-paragraph text cleanly:

```bash
cat << 'EOF' | pbcopy
This is the first paragraph and it will be one continuous line no matter how long it gets so when you paste it you get exactly one paragraph with no extra line breaks.

This is the second paragraph also as one continuous line for the same reason.

Here is a list if needed:
- First item
- Second item
- Third item

And a closing paragraph formatted the same way.
EOF
```

**Key points:**
- Each paragraph is one continuous line
- Blank lines separate paragraphs
- Lists can have individual items on separate lines
- Use single quotes in `cat << 'EOF'` to prevent variable expansion

## Example: Email Draft

```bash
cat << 'EOF' | pbcopy
Subject: Following up on our meeting

Hi Sarah,

Thank you for taking the time to meet yesterday. I appreciated hearing about the challenges your team faces with data accessibility and current workflows.

Based on our conversation, I wanted to highlight a few capabilities that might address your specific needs. The platform provides real-time analysis with automated alerts, which could help your team identify issues before they impact operations.

Would it make sense to schedule a brief demo? I can walk through how the system would integrate with your existing infrastructure and answer any technical questions.

Looking forward to hearing from you.

Best regards,
Mike
EOF
```

After running this command, the user can paste the email directly into their email client with clean paragraph formatting.

## Example: Document Draft

```bash
cat << 'EOF' | pbcopy
Technical Requirements

The system must support real-time data ingestion from multiple sources with a maximum latency of 5 minutes. All data should be stored in a time-series database optimized for analytics queries.

Security requirements include role-based access control, audit logging for all data access, and encryption at rest and in transit. The system should comply with SOC 2 Type II standards.

Performance requirements specify that dashboard queries must return results within 2 seconds for datasets up to 1 million records. The system should support at least 100 concurrent users without degradation.
EOF
```

## Tips

- Always format paragraphs as single continuous lines
- Use blank lines to separate paragraphs and maintain structure
- Lists work best with each item on a separate line
- Test the paste in the target application to verify formatting
- For very long documents, consider breaking into sections

## Troubleshooting

**Extra line breaks when pasting:**
- Verify each paragraph is formatted as one continuous line in the heredoc
- Check that you're using double newlines between paragraphs

**Text not appearing in clipboard:**
- Confirm the correct platform command is being used
- For Linux, ensure xclip is installed: `sudo apt-get install xclip`
- For SSH, verify terminal supports OSC 52 sequences

**Special characters appearing incorrectly:**
- Use single quotes in heredoc (`'EOF'`) to prevent shell expansion
- Avoid backticks or dollar signs in the text content
