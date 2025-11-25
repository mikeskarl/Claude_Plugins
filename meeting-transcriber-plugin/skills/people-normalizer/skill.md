---
name: people-normalizer
description: Normalize participant names against the Obsidian People vault. Takes a list of names and returns normalized wiki-link formatted names by matching against existing person files. Fast, focused utility for name standardization.
---

# People Name Normalizer

## Purpose

This is a lightweight, focused utility that normalizes participant names against your Obsidian People vault. It performs fuzzy matching and returns properly formatted wiki-links.

## ⚠️ MANDATORY SUCCESS VERIFICATION ⚠️

**At the END of your processing, you MUST include this verification block:**

```
=== PEOPLE-NORMALIZER VERIFICATION ===
NAMES_PROCESSED: [number]
NAMES_MATCHED: [number]
NAMES_NEW: [number]
STATUS: [SUCCESS/PARTIAL/FAILED]
WIKI_LINK_LIST:
  - [[Name 1]]
  - [[Name 2]]
=== END VERIFICATION ===
```

**This verification block is REQUIRED. The orchestrator will check for it to verify the agent completed successfully.**

If you encounter errors:
1. Set STATUS: FAILED or PARTIAL
2. Include ERROR_REASON: [explanation]
3. Still provide any names you were able to process

**Never return "Done" without this verification block. Never exit silently.**

## Configuration

**People Directory Path:**
The path to your People vault folder can be provided in two ways:

1. **As a parameter:** Pass `people_path=/path/to/your/People` when calling this skill
2. **From meeting-transcriber config:** If using with meeting-transcriber, it will read from `~/.claude/skills/meeting-transcriber/user_config.json`
3. **Default fallback:** If neither is provided, you will be prompted to specify the path

To get the configured path, run:
```bash
python3 ~/.claude/skills/meeting-transcriber/scripts/config.py --check
```

## Input Expected

**IMPORTANT:** This skill expects names to be provided in the calling prompt. Look for phrases like:
- "normalize these participant names: John, Sarah, Mike"
- "normalize the following names: [list]"
- "participant names: [list]"

The names can be in any format:
- Full names: "John Smith", "jane doe"
- First names only: "Mike", "Sarah"
- Last names only: "Smith"
- Variations: "Mike", "Michael", "Bob", "Robert"

## Process

### Step 1: Extract Names from Prompt
**Look in the calling prompt for the list of names.** They will typically be provided as:
- A comma-separated list
- A bulleted list
- Part of the prompt text

**DO NOT ask the user for names** - they should already be in the prompt that invoked this skill. If you cannot find names in the prompt, return an error message stating that names must be provided in the prompt.

### Step 2: Scan People Directory

Determine the People directory path:
1. If `people_path` parameter was provided, use that
2. Otherwise, check if `~/.claude/skills/meeting-transcriber/user_config.json` exists:
   - If yes, read the `obsidian_vault` and `people_folder` values
   - Construct path: `{obsidian_vault}/{people_folder}`
3. If no config exists, ask the user for the People directory path

Use Glob tool to list all files in the People directory.

Extract person names from filenames (remove .md extension).

### Step 3: Match Each Name

For each input name, find the best match using this priority order:

1. **Exact match** (case-insensitive)
   - "john smith" matches "John Smith.md"

2. **Full name variations**
   - "JOHN SMITH" matches "John Smith.md"
   - "John smith" matches "John Smith.md"

3. **First name only** (if unique)
   - "John" matches "John Smith.md" (only if no other Johns exist)

4. **Last name only** (if unique)
   - "Smith" matches "John Smith.md" (only if no other Smiths exist)

5. **Nickname matching**
   - "Mike" matches "Michael Smith.md"
   - "Bob" matches "Robert Jones.md"
   - Common nicknames:
     - Mike/Michael
     - Bob/Robert
     - Jim/James
     - Bill/William
     - Tom/Thomas
     - Beth/Elizabeth
     - Chris/Christopher/Christine
     - Dan/Daniel
     - Matt/Matthew
     - Sam/Samuel/Samantha
     - Alex/Alexander/Alexandra
     - Joe/Joseph
     - Dave/David
     - Rick/Richard

6. **No match found**
   - Apply Title Case to input name
   - Mark as "new" (not in vault)

### Step 4: Format Results

For each normalized name, create output in this format:

```
INPUT_NAME → [[Normalized Name]] (status)
```

Status can be:
- `matched` - Found in People vault
- `new` - Not found, using Title Case

### Step 5: Return Summary

Provide a clear summary in this format:

```
Name Normalization Complete

Matched participants (X):
- INPUT_NAME → [[Normalized Name]]
- INPUT_NAME → [[Normalized Name]]

New participants not in vault (Y):
- INPUT_NAME → [[Normalized Name]]
- INPUT_NAME → [[Normalized Name]]

Wiki-link formatted list for YAML:
  - [[Normalized Name 1]]
  - [[Normalized Name 2]]
  - [[Normalized Name 3]]
```

## Output Format

The final output must include:
1. **Mapping** of each input name to normalized name with status
2. **Summary** of matched vs new names
3. **Ready-to-use YAML list** in proper format with wiki-links

## Quality Standards

- Always include "Mike Karl" with exact formatting if "Mike", "Michael", or "Karl" appears
- Be conservative with partial matches (don't match if ambiguous)
- Always apply Title Case to unmatched names
- Use exact filenames from People directory for matched names
- Preserve special characters in matched names

## Error Handling

**If People directory is inaccessible:**
- Report error clearly
- Apply Title Case to all input names
- Mark all as "new"

**If input names list is empty:**
- Ask user to provide names

## Notes

- This skill is designed to be called by other skills (like meeting-obsidian)
- Keep processing fast - just scan and match, no complex analysis
- The goal is to standardize names for Obsidian wiki-links
- Always include the ready-to-use YAML format in output
