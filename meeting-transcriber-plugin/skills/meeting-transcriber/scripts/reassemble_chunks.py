#!/usr/bin/env python3
"""
Reassemble cleaned transcript chunks into a single file.
"""

import sys
import re
from pathlib import Path


def read_chunk_file(chunk_file):
    """Read a single chunk file."""
    try:
        return Path(chunk_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read chunk {chunk_file}: {e}", file=sys.stderr)
        return None


def extract_cleaned_content(agent_output):
    """Extract the cleaned content from agent output (may have status messages)."""
    # Agent output might include "Transcript Cleaning Complete" and stats
    # We want just the cleaned text

    # Remove any thinking/status messages
    content = agent_output

    # Remove lines that look like status reports
    lines = content.split('\n')
    cleaned_lines = []
    skip_patterns = [
        r'^Transcript Cleaning Complete',
        r'^Input:',
        r'^Output:',
        r'^Word Count Analysis:',
        r'^Status:',
        r'^Quality improvements',
        r'^Content preserved:',
        r'^Original:.*words',
        r'^Cleaned:.*words',
        r'^Reduction:.*%',
        r'^WARNING:',
        r'^===',
    ]

    for line in lines:
        # Skip status/report lines
        if any(re.match(pattern, line.strip(), re.IGNORECASE) for pattern in skip_patterns):
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def reassemble_chunks(chunk_outputs, cleaned_file):
    """Reassemble cleaned chunks into single file."""
    print("=== Meeting Transcriber: Reassembling Chunks ===")

    cleaned_sections = []
    total_words = 0

    for i, chunk_output in enumerate(chunk_outputs, 1):
        if not chunk_output:
            print(f"ERROR: Missing output for chunk {i}", file=sys.stderr)
            return False

        # Extract just the cleaned text
        cleaned_text = extract_cleaned_content(chunk_output)

        if not cleaned_text:
            print(f"WARNING: Chunk {i} is empty after extraction", file=sys.stderr)
            continue

        word_count = len(cleaned_text.split())
        print(f"INFO: Chunk {i}: {word_count} words")

        cleaned_sections.append(cleaned_text)
        total_words += word_count

    if not cleaned_sections:
        print("ERROR: No cleaned content to reassemble", file=sys.stderr)
        return False

    # Combine all chunks
    complete_cleaned = '\n\n'.join(cleaned_sections)

    # Save to cleaned file
    try:
        Path(cleaned_file).write_text(complete_cleaned, encoding='utf-8')
        print(f"SUCCESS: Reassembled {len(cleaned_sections)} chunks")
        print(f"INFO: Total cleaned transcript: {total_words} words")
        print(f"OUTPUT: {cleaned_file}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save reassembled transcript: {e}", file=sys.stderr)
        return False


def cleanup_chunk_files(timestamp):
    """Clean up temporary chunk files."""
    try:
        chunk_pattern = f"/tmp/meeting-chunk-{timestamp}-*.md"
        import glob
        chunk_files = glob.glob(chunk_pattern)

        for chunk_file in chunk_files:
            Path(chunk_file).unlink()

        print(f"INFO: Cleaned up {len(chunk_files)} chunk files")
    except Exception as e:
        print(f"WARNING: Failed to cleanup chunk files: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: reassemble_chunks.py <cleaned_file> <timestamp> <chunk_output_1> [chunk_output_2] ...", file=sys.stderr)
        print("  Or: reassemble_chunks.py <cleaned_file> <timestamp> --from-files <chunk_file_1> ...", file=sys.stderr)
        sys.exit(1)

    cleaned_file = sys.argv[1]
    timestamp = sys.argv[2]

    # Check if we're reading from files or receiving text directly
    if sys.argv[3] == "--from-files":
        # Read from chunk files
        chunk_files = sys.argv[4:]
        chunk_outputs = []
        for chunk_file in chunk_files:
            content = read_chunk_file(chunk_file)
            if content:
                chunk_outputs.append(content)
    else:
        # Chunk outputs provided as arguments
        chunk_outputs = sys.argv[3:]

    if not chunk_outputs:
        print("ERROR: No chunk outputs provided", file=sys.stderr)
        sys.exit(1)

    # Reassemble
    success = reassemble_chunks(chunk_outputs, cleaned_file)

    if not success:
        sys.exit(1)

    # Cleanup chunk files
    cleanup_chunk_files(timestamp)

    print("=== Reassembly Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
