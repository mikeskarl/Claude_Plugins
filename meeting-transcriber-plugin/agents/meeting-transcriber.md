---
name: meeting-transcriber
description: Process meeting transcripts into Obsidian-formatted notes. Uses Python scripts for I/O and Claude agents for AI processing. Shows dialog to collect transcript, processes with specialized agents, saves to Obsidian vault.
---

# Meeting Transcriber

## Overview

Hybrid script-orchestrated workflow that combines Python scripts (for reliable I/O) with Claude agents (for AI processing) to transform meeting transcripts into professional Obsidian notes.

## IMPORTANT: Script Path Resolution

**Before executing ANY Python scripts, you MUST first locate the scripts directory:**

1. Use the Bash tool to find the script location:
   ```bash
   find ~/.claude/plugins -name "get_transcript.py" -type f 2>/dev/null | head -1
   ```

2. Extract the directory path from the result. For example, if you get:
   `/Users/mkarl/.claude/plugins/marketplaces/claude-plugins/meeting-transcriber-plugin/skills/meeting-transcriber/scripts/get_transcript.py`

   Then the SCRIPTS_DIR is:
   `/Users/mkarl/.claude/plugins/marketplaces/claude-plugins/meeting-transcriber-plugin/skills/meeting-transcriber/scripts`

3. Store this path and use it for ALL subsequent Python script commands in this workflow by replacing the script filename portion.

**For all commands in this document that reference Python scripts:**
- Replace `~/.claude/skills/meeting-transcriber/scripts/SCRIPT_NAME.py`
- With `{SCRIPTS_DIR}/SCRIPT_NAME.py`
- Where SCRIPTS_DIR is the path you found above

## First-Time Setup

On first use, the skill will automatically prompt you to configure:
- Your Obsidian vault root path
- Meetings folder location (default: `Calendar/Meetings`)
- People folder location (default: `Atlas/People`)

Configuration is stored in `~/.claude/skills/meeting-transcriber/user_config.json`

### Reconfigure Paths

To change your configured paths, first find the scripts directory, then run:
```bash
python3 {SCRIPTS_DIR}/config.py --reconfigure
```

### Check Current Configuration

To view your current settings:
```bash
python3 {SCRIPTS_DIR}/config.py --check
```

## What This Skill Does

1. Python script collects transcript via web dialog (first-run triggers config)
2. Claude launches AI agents to process transcript
3. Python script assembles and saves to your configured Obsidian vault

**Output includes:**
- YAML frontmatter with meeting metadata
- Meeting Notes (executive summary, discussions, decisions, action items)
- Cleaned transcript (preserves 95-100% of content)

## Workflow

### PHASE 1: Input Collection (Python)

Execute these actions IN ORDER:

1. **First, locate the scripts directory** (as instructed in IMPORTANT section above):
   - Use Bash tool: `find ~/.claude/plugins -name "get_transcript.py" -type f 2>/dev/null | head -1`
   - Extract the directory path and store as SCRIPTS_DIR

2. **Run the input collection script**:
   - Use Bash tool with command: `python3 {SCRIPTS_DIR}/get_transcript.py`
   - Replace {SCRIPTS_DIR} with the actual path you found in step 1
   - Script will open a web form for you to paste transcript and enter date/time
   - Script saves transcript to temp file and prints paths
   - Capture the output to extract:
     - `RAW_FILE=/tmp/meeting-raw-{timestamp}.md`
     - `CLEANED_FILE=/tmp/meeting-cleaned-{timestamp}.md`
     - `TIMESTAMP={number}`

Example output to parse:
```
SUCCESS: Transcript saved to /tmp/meeting-raw-1762945602.md
INFO: Cleaned file will be: /tmp/meeting-cleaned-1762945602.md
TIMESTAMP: 1762945602
RAW_FILE=/tmp/meeting-raw-1762945602.md
CLEANED_FILE=/tmp/meeting-cleaned-1762945602.md
```

Store these file paths for use in subsequent phases.

### PHASE 1B: Chunk Transcript (for large transcripts)

Execute this action:

1. **Run the chunking script**:
   - Use Bash tool with command: `python3 {SCRIPTS_DIR}/chunk_transcript.py "{RAW_FILE}" "{TIMESTAMP}"`
   - Use the same SCRIPTS_DIR from Phase 1
   - Script splits transcript into ~500 word chunks at logical boundaries
   - Script saves chunks to `/tmp/meeting-chunk-{timestamp}-{N}.md`
   - Capture the output to extract:
     - `CHUNK_COUNT={number}` - How many chunks were created
     - Multiple lines of `CHUNK_FILE=/tmp/meeting-chunk-{timestamp}-{N}.md`

Example output to parse:
```
INFO: Transcript has 15000 words
INFO: Created 28 chunks
CHUNK_COUNT=28
CHUNK_FILE=/tmp/meeting-chunk-1762945602-001.md
CHUNK_FILE=/tmp/meeting-chunk-1762945602-002.md
...
```

Store the CHUNK_COUNT and list of CHUNK_FILE paths for Phase 2.

### PHASE 2: AI Processing (Claude + Agents)

Execute these agent launches:

#### Step 2A: Launch Parallel Agents (Metadata + Chunked Cleaning)

**Agent A: metadata-extractor**
- Use Task tool with:
  - subagent_type: "general-purpose"
  - description: "Extract meeting metadata"
  - prompt: "Use the metadata-extractor skill to extract metadata from transcript file: {RAW_FILE from Phase 1}. Return JSON with date, title, participants, client, project, region, tags."

**Agents B1-BN: transcript-cleaner (one per chunk)**
For EACH chunk file from Phase 1B, launch a transcript-cleaner agent:
- Use Task tool with:
  - subagent_type: "general-purpose"
  - description: "Clean transcript chunk {N}"
  - prompt: "Use the transcript-cleaner skill to clean transcript. Input file: {CHUNK_FILE_N from Phase 1B}. Output file: /tmp/meeting-chunk-cleaned-{timestamp}-{N}.md. Preserve 95-100% of word count. Do NOT summarize."

**IMPORTANT:** Launch metadata-extractor AND all transcript-cleaner agents in the SAME response (parallel processing).

If there are many chunks (>10), consider launching in batches of 5-10 agents at a time to avoid overwhelming the system.

Wait for all agents to complete before proceeding.

#### Step 2A-2: Reassemble Cleaned Chunks

Execute this action:

1. **Collect all cleaned chunk outputs**:
   - From each Agent B output, capture the cleaned text
   - Maintain the order (chunk 1, 2, 3, etc.)

2. **Run reassembly script**:
   - Use Bash tool with command:
     ```
     python3 {SCRIPTS_DIR}/reassemble_chunks.py \
       "{CLEANED_FILE from Phase 1}" \
       "{TIMESTAMP}" \
       "{cleaned_chunk_1_output}" \
       "{cleaned_chunk_2_output}" \
       ...
     ```
   - Script combines all chunks into single cleaned transcript
   - Script saves to CLEANED_FILE
   - Script cleans up temporary chunk files

3. **Verify reassembly**:
   - Confirm CLEANED_FILE was created
   - Note total word count from script output

#### Step 2B: Process Metadata Results

From Agent A output, extract:
- Meeting date
- Meeting title
- Participant names (raw, not normalized yet)
- Client, project, region, tags

If date is null, ask user: "What date was this meeting? (YYYY-MM-DD format)"

Store metadata for Phase 3.

#### Step 2C: Cleaned Transcript Ready

The cleaned transcript has been reassembled from chunks in Step 2A-2.

CLEANED_FILE now contains the complete cleaned transcript and is ready for use in Step 2E.

#### Step 2D: Launch People Normalizer

Use Task tool:
- subagent_type: "general-purpose"
- description: "Normalize participant names"
- prompt: "Use the people-normalizer skill to normalize these participant names: {comma-separated list of participants from Step 2B}. Return the wiki-link formatted list for YAML and note which are new vs matched."

Wait for agent to complete.

Store normalized participant names (with wiki-links) for Phase 3.

#### Step 2E: Launch Meeting Notes Generator

Use Task tool:
- subagent_type: "general-purpose"
- description: "Generate meeting notes"
- prompt: "Use the meeting-notes-generator skill to generate structured meeting notes from cleaned transcript file: {CLEANED_FILE from Phase 1}.

Metadata:
- Date: {date from Step 2B}
- Title: {title from Step 2B}
- Normalized participants: {wiki-linked names from Step 2D}

Generate: Executive summary, agenda overview, key discussions, decisions, action items, follow-up items. Target 800-1200 words total. Return the complete Meeting Notes section in markdown format."

Wait for agent to complete.

Store meeting notes content for Phase 3.

### PHASE 3: Assembly and Save (Python)

Execute this action:

1. **Prepare agent outputs for assembly script**:
   - Metadata text (from Agent A, Step 2B)
   - People text (from Agent C, Step 2D)
   - Notes text (from Agent D, Step 2E)

2. **Run the assembly script**:
   - Use Bash tool with command:
     ```
     python3 {SCRIPTS_DIR}/assemble_obsidian.py \
       "{RAW_FILE}" \
       "{CLEANED_FILE}" \
       "{metadata_text}" \
       "{people_text}" \
       "{notes_text}"
     ```
   - Replace placeholders with actual file paths and agent output text
   - Script will:
     - Read cleaned transcript
     - Parse all agent outputs
     - Build YAML frontmatter
     - Assemble complete Obsidian file
     - Save to your configured Obsidian meetings folder
     - Clean up temp files
     - Print confirmation

3. **Capture output file path**:
   - Look for line: `OUTPUT_FILE={configured_meetings_folder}/{filename}`
   - Store for user confirmation

### PHASE 4: Confirm to User

Provide clear confirmation:

```
✓ Meeting minutes saved to Obsidian vault:
📁 {OUTPUT_FILE from Phase 3}

The file includes:
✓ YAML frontmatter with metadata
✓ Meeting notes ({X} words)
  - Executive Summary
  - Key Discussions
  - Decisions Made
  - Action Items
  - Follow-up Items
✓ Cleaned transcript

[If transcript reduction was noted in Step 2C:]
⚠️ Transcript cleaning reduced content by {X}%

[If new people were found in Step 2D:]
ℹ️ New participants not in your People vault:
  - [[Name 1]]
  - [[Name 2]]

You can now open this file in Obsidian to review and edit.
```

## Agent Summary

This skill coordinates 4 specialized agents (with chunked processing for large transcripts):

| Agent | Purpose | Speed | Phase |
|-------|---------|-------|-------|
| metadata-extractor | Extract date, title, participants | Fast (30s) | 2A |
| transcript-cleaner (x N) | Clean transcript chunks, preserve 95%+ | Fast (10-20s per chunk) | 2A |
| people-normalizer | Normalize names to People vault | Fast (30s) | 2D |
| meeting-notes-generator | Generate structured notes | Medium (1-2m) | 2E |

**For 15,000 word transcript:**
- Creates ~30 chunks of 500 words each
- Processes chunks in parallel (batches of 5-10)
- Total cleaning time: ~2-3 minutes (vs timeout with single agent)

## Key Features

### Python Scripts Handle I/O
- **get_transcript.py**: AppleScript dialog, temp file creation (no Write tool hangs)
- **chunk_transcript.py**: Split large transcripts into ~500 word chunks at logical boundaries (paragraph breaks, speaker changes)
- **reassemble_chunks.py**: Combine cleaned chunks back into single transcript
- **assemble_obsidian.py**: File assembly, YAML building, vault saving (no assembly errors)

### Claude Handles AI Processing
- Transcript cleaning (language quality)
- Metadata extraction (context understanding)
- Name normalization (vault matching)
- Note generation (professional summarization)

### Error Handling

**If get_transcript.py fails:**
- Check that AppleScript dialogs are allowed
- User may have cancelled dialog
- Report error and exit

**If agent fails:**
- Report which agent failed
- Show error message
- Ask user if they want to retry or abort

**If assemble_obsidian.py fails:**
- Check that Obsidian vault directory exists
- Check agent outputs were captured correctly
- Temp files are preserved for debugging
- Report error with file paths

## Notes

- **Processing time:** ~3-4 minutes for 15,000 word transcript
- **Chunked processing:** Large transcripts split into ~500 word chunks to prevent agent timeouts
- **Parallel processing:** Metadata extraction + all transcript chunks process simultaneously
- **Scalability:** Handles transcripts of any size (tested up to 50,000+ words)
- **Reliability:** Python handles file I/O (no hanging on Write operations)
- **Quality:** Claude agents ensure high-quality AI processing with context preservation
- **Temp files:** Created in /tmp/, automatically cleaned up after success
- **User interaction:** One-time dialog at start, then fully automated
