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

**Agents B1-BN: Launch Cleaning Agents for Each Chunk**

⛔ **CRITICAL: DO NOT CREATE SHORT PROMPTS** ⛔

**YOU MUST NOT write prompts like:**
- "Use the transcript-cleaner skill to clean this transcript..."
- "Please clean the transcript using the skill..."
- "Apply the cleaning skill to this file..."

**If your Task tool prompt contains phrases like "use the skill" or "apply the skill", YOU HAVE FAILED.**

**Instead, you MUST copy the complete prompt text provided below.**

---

For EACH chunk file from Phase 1B, you must launch a Task tool with these EXACT parameters:

**TASK TOOL PARAMETERS:**
- `subagent_type`: "general-purpose"
- `description`: "Clean transcript chunk {N}" (replace {N} with actual number like 001, 002, etc.)
- `prompt`: [See the EXAMPLE below first, then COPY THE FULL TEXT from the text block, replacing placeholders]

**EXAMPLE TASK TOOL CALL FOR CHUNK 1:**

Here is what your Task tool call should look like (with placeholders replaced):

```
Task tool with:
  subagent_type: "general-purpose"
  description: "Clean transcript chunk 001"
  prompt: "Clean this transcript chunk. Follow these steps exactly:

STEP 1: Use Read tool to read the input file:
- file_path: /tmp/meeting-chunk-1764101485-001.md

STEP 2: Clean the transcript by removing ONLY filler words:
- Remove: \"um\", \"uh\", \"like\" (when filler), \"you know\", \"sort of\", \"kind of\"
- Fix spelling/grammar errors
- Add punctuation where missing
- Keep speaker labels consistent
- DO NOT rewrite sentences or summarize
- Preserve 95-100% of original word count

STEP 3: Use Write tool to save the cleaned transcript:
- file_path: /tmp/meeting-chunk-cleaned-1764101485-001.md
- content: [your cleaned transcript]

STEP 4: Count words and output verification block:
=== TRANSCRIPT-CLEANER VERIFICATION ===
OUTPUT_FILE_WRITTEN: YES
OUTPUT_FILE_PATH: /tmp/meeting-chunk-cleaned-1764101485-001.md
INPUT_WORD_COUNT: [original word count]
OUTPUT_WORD_COUNT: [cleaned word count]
REDUCTION_PERCENT: [percentage]%
STATUS: SUCCESS
=== END VERIFICATION ===

CRITICAL: You MUST use Read and Write tools. If you just describe what you would do, you have FAILED."
```

---

**NOW: COPY THE TEXT BELOW EXACTLY, WORD FOR WORD, CHARACTER FOR CHARACTER**

**PLACEHOLDER REPLACEMENT:**
Before using, replace:
- `{CHUNK_FILE_PATH}`: Actual input chunk path (e.g., /tmp/meeting-chunk-1764101485-001.md)
- `{OUTPUT_FILE_PATH}`: Output path (e.g., /tmp/meeting-chunk-cleaned-1764101485-001.md)
  Format: /tmp/meeting-chunk-cleaned-{TIMESTAMP}-{NNN}.md

**===== START PROMPT TEXT (copy everything between these markers) =====**

Clean this transcript chunk. Follow these steps exactly:

STEP 1: Use Read tool to read the input file:
- file_path: {CHUNK_FILE_PATH}
  (Example: /tmp/meeting-chunk-1764101485-001.md)

STEP 2: Clean the transcript by removing ONLY filler words:
- Remove: "um", "uh", "like" (when filler), "you know", "sort of", "kind of"
- Fix spelling/grammar errors
- Add punctuation where missing
- Keep speaker labels consistent
- DO NOT rewrite sentences or summarize
- Preserve 95-100% of original word count

STEP 3: Use Write tool to save the cleaned transcript:
- file_path: {OUTPUT_FILE_PATH}
  (Example: /tmp/meeting-chunk-cleaned-1764101485-001.md)
- content: [your cleaned transcript]

STEP 4: Count words and output verification block:
=== TRANSCRIPT-CLEANER VERIFICATION ===
OUTPUT_FILE_WRITTEN: YES
OUTPUT_FILE_PATH: {OUTPUT_FILE_PATH}
INPUT_WORD_COUNT: [original word count]
OUTPUT_WORD_COUNT: [cleaned word count]
REDUCTION_PERCENT: [percentage]%
STATUS: SUCCESS
=== END VERIFICATION ===

CRITICAL: You MUST use Read and Write tools. If you just describe what you would do, you have FAILED.

**===== END PROMPT TEXT =====**

---

**IMPORTANT:** Launch metadata-extractor AND all cleaning agents in the SAME response (parallel processing).

If there are many chunks (>10), launch in batches of 10 agents at a time.

Wait for all agents to complete before proceeding.

---

## ⛔ STOP - CHECKPOINT 1 ⛔

### Step 2A-VERIFY: YOU MUST DO THIS BEFORE CONTINUING

**DO NOT SKIP THIS STEP. Run these commands NOW:**

```bash
# Count how many cleaned files exist
ls /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md 2>/dev/null | wc -l
```

**GATE CHECK:**
- Expected files: {CHUNK_COUNT}
- Actual files: [result of ls command]
- If actual < expected: SOME AGENTS FAILED

**Also check agent summaries:**
- Any agent with "0 tool uses" = FAILED (did not use Read/Write)

### If files are missing:

**Step A: Identify which chunks failed**
```bash
# List what exists
ls /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md
```
Compare to expected: 001.md, 002.md, ... {CHUNK_COUNT}.md

**Step B: Retry failed chunks ONCE**
Re-launch transcript-cleaner for ONLY the missing chunk numbers.

**Step C: If retry still fails, use FALLBACK (copy original)**
```bash
cp /tmp/meeting-chunk-{TIMESTAMP}-{N}.md /tmp/meeting-chunk-cleaned-{TIMESTAMP}-{N}.md
```
Do this for each still-missing file.

**Step D: Final count MUST equal CHUNK_COUNT**
```bash
ls /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md | wc -l
```

**⛔ DO NOT PROCEED until file count equals CHUNK_COUNT ⛔**

---

#### Step 2A-2: Reassemble Cleaned Chunks

## 🚫🚫🚫 DO NOT READ CHUNK FILES INTO CONTEXT 🚫🚫🚫

**⚠️ CRITICAL WARNING ⚠️**

**DO NOT use the Read tool to read cleaned chunk files.**

**WHY THIS IS CRITICAL:**
- Reading 18 chunk files wastes ~20,000 tokens
- You will consume massive context for no benefit
- The cat command or reassemble script does this in 0 tokens
- You risk running out of context if you read files

**If you use Read tool on chunk files, you are doing it wrong.**

---

## PRIMARY METHOD: Use cat command (RECOMMENDED)

This is the simplest, most reliable method:

```bash
cat $(ls -v /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md | sort -V) > {CLEANED_FILE}
```

**Replace {TIMESTAMP} with actual timestamp (e.g., 1764102089)**
**Replace {CLEANED_FILE} with actual cleaned file path from Phase 1**

**Example:**
```bash
cat $(ls -v /tmp/meeting-chunk-cleaned-1764102089-*.md | sort -V) > /tmp/meeting-cleaned-1764102089.md
```

This command:
- Lists all cleaned chunk files in order (001, 002, 003...)
- Concatenates them in the correct sequence
- Writes the result to the cleaned file
- Uses zero context tokens

---

## ALTERNATIVE METHOD: Use reassemble script

**Only use this if cat command fails:**

```bash
python3 {SCRIPTS_DIR}/reassemble_chunks.py \
  "{CLEANED_FILE}" \
  "{TIMESTAMP}" \
  --from-files \
  $(ls -v /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md | sort -V)
```

**CRITICAL: The --from-files flag is REQUIRED when using file paths.**

**Example:**
```bash
python3 /Users/mkarl/.claude/plugins/.../scripts/reassemble_chunks.py \
  "/tmp/meeting-cleaned-1764102089.md" \
  "1764102089" \
  --from-files \
  /tmp/meeting-chunk-cleaned-1764102089-*.md
```

---

## Verify Reassembly

**After reassembly, verify it worked:**
```bash
wc -w {CLEANED_FILE}
```

Expected: Word count close to original (within 10-15% reduction for cleaned transcript).

**If word count is 0 or suspiciously low:**
- Check if cat command succeeded
- Verify chunk files exist
- Try the reassemble script as alternative

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

#### Step 2D: Normalize Participant Names

⛔ **DO NOT create prompts like "Use the people-normalizer skill"** ⛔

Use Task tool with direct instructions:
- subagent_type: "general-purpose"
- description: "Normalize participant names"
- prompt: "Normalize these participant names against the Obsidian People vault: {comma-separated list of participants from Step 2B}

Follow these steps:

STEP 1: Find the People directory path
- Look for config file: find ~/.claude/plugins -name user_config.json -path '*meeting-transcriber*' 2>/dev/null | head -1
- Read the config to get obsidian_vault and people_folder values
- Construct path: {obsidian_vault}/{people_folder}

STEP 2: Scan People directory with Glob tool
- Use Glob tool with pattern: \"*.md\" and path: [People directory from Step 1]
- Extract person names from filenames (remove .md extension)

STEP 3: Match each input name to existing person files
- Use fuzzy matching: exact match, first name match, last name match, nickname matching
- Common nicknames: Mike/Michael, Bob/Robert, Jim/James, etc.
- If no match found: apply Title Case and mark as \"new\"

STEP 4: Output verification block:
=== PEOPLE-NORMALIZER VERIFICATION ===
NAMES_PROCESSED: [count]
NAMES_MATCHED: [count]
NAMES_NEW: [count]
STATUS: SUCCESS
WIKI_LINK_LIST:
  - [[Name 1]]
  - [[Name 2]]
=== END VERIFICATION ===

CRITICAL: You MUST use Glob tool to check the People vault. Don't guess which names exist."

Wait for agent to complete.

**Verify people-normalizer success:**
1. Check agent output for `=== PEOPLE-NORMALIZER VERIFICATION ===` block
2. Verify `STATUS: SUCCESS` and `NAMES_PROCESSED` > 0
3. Extract `WIKI_LINK_LIST` from verification block

**If verification missing or "0 tool uses":**
1. RETRY once with same prompt
2. If retry fails, use FALLBACK:
   - Apply Title Case to each participant name
   - Wrap in wiki-links: `[[First Last]]`
   - Log: "WARNING: People normalizer failed, using fallback formatting"

Store normalized participant names (with wiki-links) for Phase 3.

#### Step 2E: Generate Meeting Notes

⛔ **DO NOT create prompts like "Use the meeting-notes-generator skill"** ⛔

Use Task tool with direct instructions:
- subagent_type: "general-purpose"
- description: "Generate meeting notes"
- prompt: "Generate structured meeting notes from the cleaned transcript.

Input Information:
- Cleaned transcript file: {CLEANED_FILE from Phase 1}
- Date: {date from Step 2B}
- Title: {title from Step 2B}
- Participants: {wiki-linked names from Step 2D}

Follow these steps:

STEP 1: Read the cleaned transcript file with Read tool

STEP 2: Determine target length based on word count
- Short meeting (<2,000 words): 400-600 words
- Standard meeting (2,000-5,000 words): 800-1200 words
- Long meeting (>5,000 words): 1200-2000 words

STEP 3: Generate structured notes with these sections:

### Executive Summary (100-150 words)
- Meeting purpose (why this meeting happened)
- Key outcomes (what was accomplished)
- Critical action items (most urgent next steps)

### Agenda Overview (30-60 words)
- Brief list of topics discussed

### Key Discussions (400-800 words)
- Organized by topic
- Focus on substance, not who said what
- Include context and reasoning
- Use bullet points for clarity

### Decisions Made (100-200 words)
- List each decision clearly
- Include rationale if significant
- Note any conditions or caveats

### Action Items (100-200 words)
- Format: Owner, task, deadline (if mentioned)
- Prioritize by urgency
- Be specific about deliverables

### Follow-up Items (50-100 words)
- Questions to be answered
- Topics for future discussion
- Dependencies or blockers

STEP 4: Return the complete Meeting Notes in markdown format

Target total length: 800-1200 words (for standard meeting)

Focus on decisions and outcomes, not process. Write for someone who didn't attend."

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

### Error Handling and Agent Failure Detection

**CRITICAL: Agents can fail silently. You MUST verify success.**

#### Detecting Agent Failures

After each agent batch completes, check for these failure indicators:

1. **"0 tool uses" in agent summary** = Agent likely failed without doing work
2. **Missing verification block** = Agent did not complete properly
3. **Missing output files** = Agent failed to write results
4. **STATUS: FAILED** in verification block = Agent reported failure

#### Verifying Transcript Cleaner Success

After transcript-cleaner agents complete:

1. **Check which output files were created:**
   ```bash
   ls -la /tmp/meeting-chunk-cleaned-{TIMESTAMP}-*.md
   ```

2. **Compare against expected chunks:**
   - If CHUNK_COUNT was 18, you should see 18 cleaned files
   - Missing files indicate failed agents

3. **Check for verification blocks in agent output:**
   - Look for `=== TRANSCRIPT-CLEANER VERIFICATION ===`
   - Check `OUTPUT_FILE_WRITTEN: YES` and `STATUS: SUCCESS`

#### Retry Logic for Failed Chunks

If any transcript-cleaner agents failed (0 tool uses, missing files, or STATUS: FAILED):

1. **Identify failed chunks** by comparing expected vs actual output files
2. **Retry failed chunks ONCE** by re-launching agents for just those chunks
3. **If retry fails**, use original chunk content as fallback:
   - Copy original chunk to cleaned file path
   - Log warning: "Chunk {N} could not be cleaned, using original"

#### Verifying People Normalizer Success

After people-normalizer agent completes:

1. **Check for verification block:**
   - Look for `=== PEOPLE-NORMALIZER VERIFICATION ===`
   - Verify `STATUS: SUCCESS` and `NAMES_PROCESSED` > 0

2. **If verification missing or STATUS: FAILED:**
   - Retry ONCE
   - If retry fails, use fallback: Title Case all names with wiki-links

#### Verifying Other Agents

**metadata-extractor:**
- Must return JSON with at least `date` and `title` fields
- If missing, ask user for date and use "Meeting Notes" as title

**meeting-notes-generator:**
- Output must be >200 words
- Must contain `##` headers for structure
- If failed, report error (cannot fallback - notes are required)

#### If get_transcript.py fails:
- Check that AppleScript dialogs are allowed
- User may have cancelled dialog
- Report error and exit

#### If assemble_obsidian.py fails:
- Check that Obsidian vault directory exists
- Check agent outputs were captured correctly
- Temp files are preserved for debugging
- Report error with file paths
- Assembly script now validates inputs and reports which agents may have failed

## Notes

- **Processing time:** ~3-4 minutes for 15,000 word transcript
- **Chunked processing:** Large transcripts split into ~500 word chunks to prevent agent timeouts
- **Parallel processing:** Metadata extraction + all transcript chunks process simultaneously
- **Scalability:** Handles transcripts of any size (tested up to 50,000+ words)
- **Reliability:** Python handles file I/O (no hanging on Write operations)
- **Quality:** Claude agents ensure high-quality AI processing with context preservation
- **Temp files:** Created in /tmp/, automatically cleaned up after success
- **User interaction:** One-time dialog at start, then fully automated
