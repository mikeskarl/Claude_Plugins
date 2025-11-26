#!/usr/bin/env python3
"""
Chunk large transcripts into ~500 word sections at logical boundaries.
This allows processing long transcripts without agent timeouts.
"""

import sys
import re
import json
from pathlib import Path


CHUNK_SIZE = 500  # Target words per chunk
MIN_CHUNK_SIZE = 300  # Minimum words to avoid tiny chunks


def read_transcript(raw_file):
    """Read the raw transcript file."""
    try:
        return Path(raw_file).read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read transcript: {e}", file=sys.stderr)
        sys.exit(1)


def find_logical_breaks(text):
    """Find logical break points in the text (paragraphs, speaker changes)."""
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n', text)

    # Further split by speaker labels if present (e.g., "John:", "Speaker 1:", etc.)
    segments = []
    for para in paragraphs:
        # Check if paragraph has speaker labels
        speaker_pattern = r'^([A-Z][^:\n]{0,30}:)'
        if re.match(speaker_pattern, para.strip(), re.MULTILINE):
            # Split on speaker labels
            parts = re.split(r'(\n[A-Z][^:\n]{0,30}:)', para)
            current = ""
            for part in parts:
                if re.match(speaker_pattern, part.strip()):
                    if current:
                        segments.append(current.strip())
                    current = part
                else:
                    current += part
            if current:
                segments.append(current.strip())
        else:
            segments.append(para.strip())

    return [s for s in segments if s]  # Remove empty segments


def create_chunks(segments, chunk_size=CHUNK_SIZE, min_size=MIN_CHUNK_SIZE):
    """Group segments into chunks of approximately chunk_size words."""
    chunks = []
    current_chunk = []
    current_word_count = 0

    for segment in segments:
        segment_words = len(segment.split())

        # If adding this segment would exceed chunk_size significantly
        if current_word_count > 0 and current_word_count + segment_words > chunk_size * 1.5:
            # Save current chunk if it meets minimum size
            if current_word_count >= min_size:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [segment]
                current_word_count = segment_words
            else:
                # Chunk too small, add this segment anyway
                current_chunk.append(segment)
                current_word_count += segment_words
        else:
            current_chunk.append(segment)
            current_word_count += segment_words

        # If we've reached a good chunk size, save it
        if current_word_count >= chunk_size:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_word_count = 0

    # Add remaining content
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def save_chunks(chunks, timestamp):
    """Save chunks to individual temp files."""
    chunk_files = []

    for i, chunk in enumerate(chunks, 1):
        chunk_file = Path(f"/tmp/meeting-chunk-{timestamp}-{i:03d}.md")
        try:
            chunk_file.write_text(chunk, encoding='utf-8')
            chunk_files.append(str(chunk_file))
        except Exception as e:
            print(f"ERROR: Failed to save chunk {i}: {e}", file=sys.stderr)
            sys.exit(1)

    return chunk_files


def generate_task_tool_calls(num_chunks, timestamp):
    """Generate pre-configured Task tool call JSON for all chunks.

    This eliminates the need for the orchestrating agent to create prompts,
    which has been unreliable across multiple versions.
    """
    task_calls = []

    for i in range(1, num_chunks + 1):
        chunk_num = f"{i:03d}"
        input_path = f"/tmp/meeting-chunk-{timestamp}-{chunk_num}.md"
        output_path = f"/tmp/meeting-chunk-cleaned-{timestamp}-{chunk_num}.md"

        # The full prompt template with verification token
        prompt = f"""[VERIFICATION:TRANSCRIPT_CLEANER_V1.0.16]

Clean this transcript chunk. Follow these steps exactly:

STEP 1: Use Read tool to read the input file:
- file_path: {input_path}

STEP 2: Clean the transcript by removing ONLY filler words:
- Remove: "um", "uh", "like" (when filler), "you know", "sort of", "kind of"
- Fix spelling/grammar errors
- Add punctuation where missing
- Keep speaker labels consistent
- DO NOT rewrite sentences or summarize
- Preserve 95-100% of original word count

STEP 3: Use Write tool to save the cleaned transcript:
- file_path: {output_path}
- content: [your cleaned transcript]

STEP 4: Count words and output verification block:
=== TRANSCRIPT-CLEANER VERIFICATION ===
OUTPUT_FILE_WRITTEN: YES
OUTPUT_FILE_PATH: {output_path}
INPUT_WORD_COUNT: [original word count]
OUTPUT_WORD_COUNT: [cleaned word count]
REDUCTION_PERCENT: [percentage]%
STATUS: SUCCESS
=== END VERIFICATION ===

CRITICAL: You MUST use Read and Write tools. If you just describe what you would do, you have FAILED."""

        task_call = {
            "subagent_type": "general-purpose",
            "description": f"Clean transcript chunk {chunk_num}",
            "prompt": prompt
        }

        task_calls.append(task_call)

    return task_calls


def save_task_calls_json(task_calls, timestamp):
    """Save the pre-generated Task tool calls to a JSON file."""
    json_path = Path(f"/tmp/meeting-task-calls-{timestamp}.json")

    try:
        json_path.write_text(
            json.dumps({"task_calls": task_calls}, indent=2),
            encoding='utf-8'
        )
        return str(json_path)
    except Exception as e:
        print(f"ERROR: Failed to save task calls JSON: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: chunk_transcript.py <raw_file> <timestamp>", file=sys.stderr)
        sys.exit(1)

    raw_file = sys.argv[1]
    timestamp = sys.argv[2]

    print("=== Meeting Transcriber: Chunking Transcript ===")

    # Read transcript
    transcript = read_transcript(raw_file)
    total_words = len(transcript.split())
    print(f"INFO: Transcript has {total_words} words")

    # Find logical breaks
    segments = find_logical_breaks(transcript)
    print(f"INFO: Found {len(segments)} logical segments")

    # Create chunks
    chunks = create_chunks(segments)
    num_chunks = len(chunks)
    print(f"INFO: Created {num_chunks} chunks")

    # Print chunk statistics
    for i, chunk in enumerate(chunks, 1):
        word_count = len(chunk.split())
        print(f"INFO: Chunk {i}: {word_count} words")

    # Save chunks
    chunk_files = save_chunks(chunks, timestamp)

    # Generate pre-configured Task tool calls
    task_calls = generate_task_tool_calls(num_chunks, timestamp)
    task_calls_json = save_task_calls_json(task_calls, timestamp)

    print(f"SUCCESS: Saved {num_chunks} chunks")
    print(f"CHUNK_COUNT={num_chunks}")

    # Print chunk files (one per line for easy parsing)
    for chunk_file in chunk_files:
        print(f"CHUNK_FILE={chunk_file}")

    # Print task calls JSON path
    print(f"TASK_CALLS_JSON={task_calls_json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
