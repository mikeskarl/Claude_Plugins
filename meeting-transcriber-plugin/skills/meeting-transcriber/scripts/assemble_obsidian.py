#!/usr/bin/env python3
"""
Assemble complete Obsidian meeting notes file from agent outputs.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Import config module from same directory
from config import get_meetings_dir, ensure_configured


def read_file(file_path):
    """Read file content."""
    try:
        return Path(file_path).read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read {file_path}: {e}", file=sys.stderr)
        return None


def parse_metadata(metadata_text):
    """Parse metadata from agent output."""
    # Look for JSON in the output
    json_match = re.search(r'\{[\s\S]*"date"[\s\S]*\}', metadata_text)
    if json_match:
        try:
            metadata = json.loads(json_match.group())
            # Ensure time field exists (backward compatibility)
            if 'time' not in metadata:
                # Try to extract time from date field if it's in old format
                if metadata.get('date') and ' ' in str(metadata['date']):
                    date_parts = metadata['date'].split()
                    metadata['date'] = date_parts[0]
                    metadata['time'] = date_parts[1] if len(date_parts) > 1 else "09:00"
                else:
                    metadata['time'] = "09:00"
            return metadata
        except:
            pass

    # Fallback: parse line by line
    metadata = {
        "date": None,
        "time": "09:00",
        "title": "Meeting Notes",
        "participants": [],
        "client": "",
        "project": "",
        "region": "",
        "tags": []
    }

    for line in metadata_text.split('\n'):
        if 'Date:' in line:
            date_str = line.split('Date:')[1].strip()
            # Handle old format with time included
            if ' ' in date_str:
                date_parts = date_str.split()
                metadata['date'] = date_parts[0]
                metadata['time'] = date_parts[1] if len(date_parts) > 1 else "09:00"
            else:
                metadata['date'] = date_str
        elif 'Time:' in line:
            metadata['time'] = line.split('Time:')[1].strip()
        elif 'Title:' in line:
            metadata['title'] = line.split('Title:')[1].strip()
        elif 'Client:' in line:
            metadata['client'] = line.split('Client:')[1].strip()
        elif 'Project:' in line:
            metadata['project'] = line.split('Project:')[1].strip()
        elif 'Region:' in line:
            metadata['region'] = line.split('Region:')[1].strip()

    return metadata


def parse_participants(people_text):
    """Parse normalized participant names from people-normalizer output."""
    participants = []

    # Look for wiki-link formatted list
    wiki_link_pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(wiki_link_pattern, people_text)

    if matches:
        return [f"[[{name}]]" for name in matches]

    # Fallback: look for bullet list
    for line in people_text.split('\n'):
        if line.strip().startswith('-') or line.strip().startswith('*'):
            # Extract name from line
            name = line.strip().lstrip('-*').strip()
            if name and not name.startswith('[['):
                participants.append(f"[[{name}]]")
            elif name:
                participants.append(name)

    return participants if participants else ["[[Mike Karl]]"]


def extract_meeting_notes(notes_text):
    """Extract meeting notes content."""
    # Remove any thinking/processing text before actual notes
    if "## Meeting Notes" in notes_text:
        notes_text = notes_text.split("## Meeting Notes", 1)[1]
        notes_text = "## Meeting Notes" + notes_text

    # Clean up any system messages
    notes_text = re.sub(r'^\s*Meeting Notes Generation Complete[\s\S]*?(?=##)', '', notes_text)

    return notes_text.strip()


def build_yaml_frontmatter(metadata, participants):
    """Build YAML frontmatter."""
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Get date and time separately - use 'or' to handle None values
    date_met = metadata.get('date') or created_date.split()[0]
    time_met = metadata.get('time') or '09:00'

    # Ensure time is properly formatted (HH:mm)
    if time_met and ':' not in str(time_met):
        time_met = '09:00'

    # Format tags - handle None
    tags_list = metadata.get('tags') or []
    if tags_list:
        tags_str = '[' + ', '.join(f'"{tag}"' for tag in tags_list) + ']'
    else:
        tags_str = '[]'

    # Format participants (with quotes around wiki-links for proper YAML)
    participants_yaml = '\n'.join(f'  - "{p}"' for p in participants)

    # Extract first sentence from meeting notes for summary (will be added by caller)
    # Use 'or' to handle None values for all metadata fields
    yaml = f"""---
created date: {created_date}
type: Meeting
tags: {tags_str}
date met: {date_met}
time: {time_met}
client: "{metadata.get('client') or ''}"
project: "{metadata.get('project') or ''}"
region: "{metadata.get('region') or ''}"
participants:
{participants_yaml}
previous meeting:
summary: {{SUMMARY_PLACEHOLDER}}
home: "[[Home]]"
---"""

    return yaml


def extract_first_sentence(meeting_notes):
    """Extract first sentence from meeting notes for YAML summary."""
    # Look for Executive Summary section
    exec_summary_match = re.search(r'###\s*Executive Summary\s*\n\n(.+?)\n', meeting_notes, re.DOTALL)
    if exec_summary_match:
        text = exec_summary_match.group(1).strip()
        # Get first sentence
        sentence_match = re.match(r'([^.!?]+[.!?])', text)
        if sentence_match:
            return sentence_match.group(1).strip()

    return "Meeting discussion and planning session."


def sanitize_filename(title):
    """Remove invalid filename characters."""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        title = title.replace(char, '')
    return title.strip()


def validate_inputs(cleaned_file, metadata_text, people_text, notes_text):
    """Validate all inputs before assembly. Returns (is_valid, errors)."""
    errors = []
    warnings = []

    # Check cleaned file exists and has content
    if not Path(cleaned_file).exists():
        errors.append(f"Cleaned transcript file not found: {cleaned_file}")
    else:
        content = read_file(cleaned_file)
        if not content or len(content.strip()) < 100:
            errors.append(f"Cleaned transcript file is empty or too short: {cleaned_file}")
        else:
            word_count = len(content.split())
            if word_count < 50:
                warnings.append(f"Cleaned transcript has very few words ({word_count})")

    # Check metadata is not empty/default
    if not metadata_text or len(metadata_text.strip()) < 20:
        errors.append("Metadata text is empty or too short - metadata-extractor may have failed")

    # Check people text has wiki-links
    if not people_text or '[[' not in people_text:
        warnings.append("People text has no wiki-links - people-normalizer may have failed")

    # Check notes text has substantial content
    if not notes_text or len(notes_text.strip()) < 200:
        errors.append("Notes text is empty or too short - meeting-notes-generator may have failed")

    return (len(errors) == 0, errors, warnings)


def assemble_and_save(cleaned_file, metadata_text, people_text, notes_text):
    """Assemble complete Obsidian file and save."""
    print("=== Meeting Transcriber: Assembly ===")

    # Validate all inputs first
    is_valid, errors, warnings = validate_inputs(cleaned_file, metadata_text, people_text, notes_text)

    if errors:
        print("ERROR: Input validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("\nOne or more agents may have failed silently. Check agent outputs.", file=sys.stderr)
        return None

    if warnings:
        print("WARNING: Some inputs may be incomplete:")
        for warning in warnings:
            print(f"  - {warning}")

    # Read cleaned transcript
    cleaned_transcript = read_file(cleaned_file)
    if not cleaned_transcript:
        print("ERROR: Could not read cleaned transcript", file=sys.stderr)
        return None

    # Parse metadata
    metadata = parse_metadata(metadata_text)
    print(f"INFO: Meeting title: {metadata['title']}")
    print(f"INFO: Meeting date: {metadata['date']}")
    print(f"INFO: Meeting time: {metadata.get('time', '09:00')}")

    # Parse participants
    participants = parse_participants(people_text)
    print(f"INFO: Participants: {len(participants)}")

    # Extract meeting notes
    meeting_notes = extract_meeting_notes(notes_text)

    # Extract first sentence for summary
    summary = extract_first_sentence(meeting_notes)

    # Build YAML frontmatter
    yaml = build_yaml_frontmatter(metadata, participants)
    yaml = yaml.replace('{SUMMARY_PLACEHOLDER}', summary)

    # Assemble complete file
    complete_content = f"""{yaml}

{meeting_notes}

## Transcript

{cleaned_transcript}
"""

    # Build filename (date only, no time)
    # Use 'or' to handle both missing keys AND None values
    date_str = metadata.get('date') or datetime.now().strftime("%Y-%m-%d")
    title_clean = sanitize_filename(metadata.get('title') or "Meeting Notes")
    filename = f"{date_str} {title_clean}.md"

    # Save to Obsidian vault
    meetings_dir = get_meetings_dir()
    meetings_dir.mkdir(parents=True, exist_ok=True)
    output_path = meetings_dir / filename

    try:
        output_path.write_text(complete_content, encoding='utf-8')
        print(f"SUCCESS: Saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}", file=sys.stderr)
        return None


def cleanup_temp_files(raw_file, cleaned_file):
    """Clean up temporary files."""
    try:
        if Path(raw_file).exists():
            Path(raw_file).unlink()
            print(f"INFO: Cleaned up {raw_file}")
        if Path(cleaned_file).exists():
            Path(cleaned_file).unlink()
            print(f"INFO: Cleaned up {cleaned_file}")
    except Exception as e:
        print(f"WARNING: Failed to cleanup temp files: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    # Ensure configuration exists
    if not ensure_configured():
        print("ERROR: Configuration required. Please run config setup.", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 6:
        print("Usage: assemble_obsidian.py <raw_file> <cleaned_file> <metadata_text> <people_text> <notes_text>", file=sys.stderr)
        print("OR: assemble_obsidian.py <raw_file> <cleaned_file> <metadata_file> <people_file> <notes_file>", file=sys.stderr)
        sys.exit(1)

    raw_file = sys.argv[1]
    cleaned_file = sys.argv[2]

    # Determine if we're receiving text or file paths
    metadata_input = sys.argv[3]
    people_input = sys.argv[4]
    notes_input = sys.argv[5]

    # If inputs look like file paths, read them
    try:
        metadata_text = read_file(metadata_input) if Path(metadata_input).exists() else metadata_input
    except (OSError, ValueError):
        metadata_text = metadata_input

    try:
        people_text = read_file(people_input) if Path(people_input).exists() else people_input
    except (OSError, ValueError):
        people_text = people_input

    try:
        notes_text = read_file(notes_input) if Path(notes_input).exists() else notes_input
    except (OSError, ValueError):
        notes_text = notes_input

    if not all([metadata_text, people_text, notes_text]):
        print("ERROR: Failed to read agent outputs", file=sys.stderr)
        sys.exit(1)

    # Assemble and save
    output_path = assemble_and_save(cleaned_file, metadata_text, people_text, notes_text)

    if not output_path:
        sys.exit(1)

    # Cleanup temp files
    cleanup_temp_files(raw_file, cleaned_file)

    print("=== Assembly Complete ===")
    print(f"OUTPUT_FILE={output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
