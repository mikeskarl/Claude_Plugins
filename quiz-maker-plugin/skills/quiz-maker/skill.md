---
name: quiz-maker
description: Generate interactive study quizzes from source materials (text, images, PDFs) with customizable question types and difficulty levels. Full workflow orchestrator.
---

# Quiz Maker

## Overview

Complete workflow to generate custom study quizzes from source materials. Handles everything from parameter collection to final HTML quiz generation with print support and answer keys.

## IMPORTANT: Script Path Resolution

**Before executing ANY Python scripts, you MUST first locate the scripts directory:**

1. Use the Bash tool to find the script location:
   ```bash
   find ~/.claude/plugins -name "get_quiz_params.py" -type f 2>/dev/null | head -1
   ```

2. Extract the directory path from the result. For example, if you get:
   `/Users/mkarl/.claude/plugins/marketplaces/custom-plugins/quiz-maker-plugin/skills/quiz-maker/scripts/get_quiz_params.py`

   Then the SCRIPTS_DIR is:
   `/Users/mkarl/.claude/plugins/marketplaces/custom-plugins/quiz-maker-plugin/skills/quiz-maker/scripts`

3. Store this path and use it for ALL subsequent Python script commands by replacing the filename portion.

## First-Time Setup

On first use, the skill will automatically prompt you to configure:
- Storage root path for quiz files (default: `~/Library/Mobile Documents/com~apple~CloudDocs/Family/StudyGuides`)

Configuration is stored in user_config.json within the plugin.

### Reconfigure Paths

To change your configured paths:
```bash
python3 {SCRIPTS_DIR}/config.py --reconfigure
```

### Check Current Configuration

To view your current settings:
```bash
python3 {SCRIPTS_DIR}/config.py --check
```

## What This Skill Does

1. Collects quiz parameters via web form
2. Scans and inventories source files
3. Extracts content from all materials (with Opus for handwriting)
4. Shows extraction preview with edit capability
5. Generates quiz questions
6. Shows question preview with edit and regenerate capability
7. Builds final HTML quiz with print support and answer key
8. Saves to configured location with metadata

## Complete Workflow

### PHASE 1: Parameter Collection

**Step 1.1: Locate Scripts Directory**

Execute:
```bash
find ~/.claude/plugins -name "get_quiz_params.py" -type f 2>/dev/null | head -1
```

Store the directory path as SCRIPTS_DIR for all subsequent commands.

**Step 1.2: Run Parameter Collection Script**

Execute:
```bash
python3 {SCRIPTS_DIR}/get_quiz_params.py
```

This opens a web form to collect:
- Class name and subject
- Test information
- Source file/folder paths
- Number of questions
- Question types (multiple choice, true/false, fill-in-blank)
- Include study notes (yes/no)
- Difficulty level (easy/medium/hard)

The script outputs JSON with all parameters.

Capture the output JSON and store as QUIZ_PARAMS for later phases.

### PHASE 2: Source File Scanning

**Step 2.1: Scan Source Locations**

Execute:
```bash
python3 {SCRIPTS_DIR}/scan_source_files.py {path1} {path2} {path3} ...
```

Replace {path1}, {path2}, etc. with the sourcePaths from QUIZ_PARAMS.

The script will:
- Recursively scan all provided paths
- Categorize files by type (text, image, PDF)
- Output inventory JSON

Look for the "=== FILE_INVENTORY ===" section in output.

Capture the FILE_INVENTORY JSON and store for Phase 3.

### PHASE 3: Content Extraction

**Step 3.1: Launch Source Material Processor Agent**

Use Task tool with:
- subagent_type: "general-purpose"
- model: "claude-opus-4-5-20251101" (IMPORTANT: Use Opus 4.5 or newer for image processing)
- description: "Extract content from source materials"
- prompt: "Use the source-material-processor skill to extract content from all source files.

File inventory:
{FILE_INVENTORY from Phase 2}

Extract all text from text files, images (including handwriting), and PDFs. Return JSON array with extracted content for each file."

**CRITICAL**: Specify model: "opus" when launching this agent to ensure handwriting is properly detected.

Wait for agent to complete.

Store the extraction results as EXTRACTED_CONTENT.

**Step 3.2: Preview Extractions**

**IMPORTANT**: Only run this step AFTER you have received the complete EXTRACTED_CONTENT from the agent in Step 3.1. Do NOT run the preview script before the extraction is complete.

Execute:
```bash
python3 {SCRIPTS_DIR}/preview_extractions.py '{EXTRACTED_CONTENT}'
```

This opens a web page showing:
- Side-by-side view of originals and extracted text
- Editable text areas for corrections
- Continue button when satisfied

The script will wait for user confirmation and return updated extractions.

Capture the updated extractions output and store as FINAL_EXTRACTIONS.

### PHASE 4: Question Generation

**Step 4.1: Launch Question Generator Agent**

Use Task tool with:
- subagent_type: "general-purpose"
- description: "Generate quiz questions"
- prompt: "Use the question-generator skill to generate quiz questions.

Extracted content:
{FINAL_EXTRACTIONS from Phase 3}

Quiz parameters:
{QUIZ_PARAMS from Phase 1}

Generate {questionCount} questions with the specified types and difficulty. Include study notes if requested. Return JSON array of questions."

Wait for agent to complete.

Store the generated questions as QUESTIONS.

**Step 4.2: Preview Questions**

Execute:
```bash
python3 {SCRIPTS_DIR}/preview_questions.py '{QUESTIONS}'
```

This opens a web page showing:
- All generated questions
- Editable question text and notes
- Regenerate button for each question
- Continue or Regenerate Selected button

The script returns:
```json
{
  "questions": [...edited questions...],
  "regenerate": [3, 7, 12]  // indices to regenerate
}
```

**Step 4.3: Handle Regeneration Requests (if any)**

If the regenerate array is not empty:

For each index in the regenerate array, launch a Task with:
- subagent_type: "general-purpose"
- description: "Regenerate question {index}"
- prompt: "Use the question-generator skill to regenerate question {index}.

Original question:
{questions[index]}

Extracted content:
{FINAL_EXTRACTIONS}

Quiz parameters:
{QUIZ_PARAMS}

Generate a NEW question of the same type covering the same topic but with different wording and options. Return the new question in the same JSON format."

Wait for all regeneration agents to complete.

Merge the regenerated questions back into the questions array.

Re-run Step 4.2 (preview_questions.py) with updated questions.

Repeat Step 4.3 until user confirms without regeneration requests.

Store the final approved questions as FINAL_QUESTIONS.

### PHASE 5: Build Final HTML

**Step 5.1: Build Quiz File**

Execute:
```bash
python3 {SCRIPTS_DIR}/build_final_html.py '{QUIZ_PARAMS}' '{FINAL_QUESTIONS}' '{FINAL_EXTRACTIONS}'
```

The script will:
- Read the template from /Users/mkarl/1Code/JaysieTest/WebApp/index.html
- Enhance with print support and answer key modal
- Embed the question data
- Create output directory: {storage_root}/{YYYY-MM-DD}_{subject}/
- Save files:
  - quiz.html (the interactive quiz)
  - questions.json (for future edits)
  - metadata.json (generation info)
  - extracted_content.json (raw extracted content)
  - extracted_content.md (readable reference material)
  - source_files/ (copies of all original source materials)

Capture the output paths:
- OUTPUT_DIR
- HTML_FILE

### PHASE 6: Confirm to User

Provide clear confirmation:

```
✓ Quiz generated successfully!

📁 Location: {OUTPUT_DIR}

Files created:
  ✓ quiz.html - Interactive quiz (open in browser)
  ✓ questions.json - Question bank for future edits
  ✓ metadata.json - Generation metadata
  ✓ extracted_content.json - Raw extracted content (JSON)
  ✓ extracted_content.md - Readable reference material (Markdown)
  ✓ source_files/ - Copies of all original source materials

Quiz Details:
  • Class: {className}
  • Subject: {subject}
  • Questions: {count}
  • Difficulty: {difficulty}
  • Study Notes: {included/not included}

Features:
  ✓ Randomized question order
  ✓ Immediate feedback
  ✓ Study notes (toggle per question)
  ✓ Print support
  ✓ Answer key viewer
  ✓ Progress tracking

To use:
  1. Open quiz.html in any browser
  2. Use "Print Quiz" button for paper version
  3. Use "View Answer Key" to see all answers

To edit questions later:
  • Edit questions.json
  • Re-run the skill to regenerate HTML
```

## Error Handling

**If get_quiz_params.py fails:**
- User may have cancelled the form
- Report cancellation and exit gracefully

**If scan_source_files.py finds no files:**
- Report issue with source paths
- Ask user to verify paths and retry

**If source-material-processor agent fails:**
- Report which files failed to process
- Continue with successfully processed files
- Ask user if they want to proceed or retry

**If question-generator agent produces insufficient questions:**
- Report the shortfall
- Explain if source material was insufficient
- Ask user if they want to proceed with fewer questions

**If preview scripts are cancelled:**
- Report user cancellation
- Clean up any temp files
- Exit gracefully

**If build_final_html.py fails:**
- Report the error
- Preserve all intermediate files for debugging
- Provide file paths for manual inspection

## Notes

- **Processing time**: Varies by source material size (typically 5-15 minutes)
- **Opus model**: Automatically used for image processing to detect handwriting
- **Scalability**: Handles large quantities of source material
- **Edit capability**: Questions stored in JSON for future modification
- **Quality**: Multiple review stages ensure accuracy
- **Flexibility**: Customizable question types, counts, and difficulty

## Advanced Usage

### Editing Existing Quizzes

To edit an existing quiz's questions:

1. Locate the questions.json file in the quiz directory
2. Edit the JSON directly or use the skill to regenerate
3. Run build_final_html.py with the edited questions.json to regenerate quiz.html

### Batch Quiz Generation

To generate multiple quizzes:

1. Run the skill once for each quiz topic
2. Each quiz is saved in a separate dated directory
3. All quizzes are stored under the configured storage root

### Custom Templates

To use a custom HTML template:

1. Modify /Users/mkarl/1Code/JaysieTest/WebApp/index.html
2. The build script will use the updated template
3. Ensure the template has the questionBank array marker
