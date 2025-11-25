---
name: metadata-extractor
description: Extract structured metadata from meeting transcripts. Fast, focused utility that scans transcripts to identify participants, dates, titles, and other meeting details. Returns JSON for downstream processing.
---

# Meeting Metadata Extractor

## Purpose

Lightweight utility that extracts structured metadata from meeting transcripts. Designed to be called by orchestrator agents as part of a multi-agent workflow.

## Input Expected

The user will provide:
- **Transcript file path** (required): Path to the raw transcript file
- Or **Transcript text** (alternative): Raw transcript as text
- **User-provided date** (optional): Meeting date from user input (YYYY-MM-DD format)
- **User-provided time** (optional): Meeting time from user input (HH:mm format)

## Process

### Step 1: Read Transcript

If file path provided:
- Use Read tool to load transcript from file

If transcript text provided:
- Use the provided text directly

### Step 2: Extract Required Fields

**Meeting Date and Time** (REQUIRED)
- **PRIORITY 1:** Use user-provided date and time if provided (passed from coordinator)
- **PRIORITY 2:** If not provided by user, extract from transcript:
  - Look for explicit date/time references: "Today is November 12", "Meeting on 11/12/2025"
  - Look for context clues: "last Tuesday", "this morning"
  - Look for calendar invites or headers in transcript
- **Formatting:**
  - Date format: YYYY-MM-DD
  - Time format: HH:mm (24-hour)
  - If time not mentioned and not provided, use "09:00" as default
  - If date unclear and not provided, set to null (coordinator will ask user)

**Meeting Title/Subject** (REQUIRED)
- Extract from: Meeting headers, calendar invites, opening remarks
- Generate from content: Identify 2-3 main topics discussed
- Create concise 5-10 word title that captures meeting purpose
- Examples:
  - "SCADA System Standards Review"
  - "Q3 Budget Planning and Resource Allocation"
  - "Client Kickoff for Water Treatment Project"

**Participants** (REQUIRED)
- Extract ONLY actual meeting participants, not people merely mentioned or discussed
- Primary sources (highest priority):
  - Speaker labels that actively spoke: "John Smith:", "Sarah:", "Speaker 1:", "Speaker 2:"
  - Attendee lists if present at start/end of transcript
  - Self-introductions: "Hi, this is John calling in"
- DO NOT include:
  - People only mentioned in discussion: "As Mike mentioned..." (unless Mike is also a speaker)
  - People referenced in past tense: "Bob suggested last week..."
  - People in examples or stories
  - People who sent emails/messages being discussed
- Always include "Mike Karl" if "Mike" or "Michael" appears as a speaker
- Capture name variations:
  - Full names: "John Smith"
  - First names only: "Sarah", "Mike"
  - Last names: "Smith said..."
- Deduplicate intelligently:
  - "Speaker 1" + "John" at same points = same person
  - "Mike" + "Michael" + "Mike Karl" = same person
  - "Smith" + "John Smith" = same person
  - Different speaker patterns (voice style, topics) = different people
  - If uncertain whether two labels are same person, keep separate
- Return as list of strings (deduplicated)
- Focus on quality over quantity - better to miss a passive attendee than include someone not present

### Step 3: Extract Optional Fields

**Client Name**
- Look for company or organization names
- Common patterns: "for [Client]", "[Client] wants", "working with [Client]"
- Skip if not clearly mentioned
- Return as string or empty string

**Project Name/Code**
- Look for project names, codes, or identifiers
- Patterns: "Project [Name]", "the [Name] project", project codes like "WTP-2024"
- Skip if not mentioned
- Return as string or empty string

**Region**
- Look for geographic references: city, state, region names
- Only include if explicitly relevant to meeting
- Examples: "Northern California", "Dallas office", "EMEA region"
- Return as string or empty string

**Tags** (2-5 recommended)
- Analyze meeting content to categorize
- Common tags:
  - Type: "planning", "review", "kickoff", "status-update", "technical", "budget"
  - Phase: "discovery", "design", "implementation", "closeout"
  - Topic: "standards", "procurement", "staffing", "schedule"
- Return as list of strings (2-5 items)
- If unclear, return empty list

### Step 4: Format Output

Return results in this exact JSON structure:

```json
{
  "date": "2025-11-12",
  "time": "14:30",
  "title": "SCADA System Standards Review",
  "participants": ["Mike", "John Smith", "Sarah", "Bob"],
  "client": "ABC Water District",
  "project": "SCADA Upgrade Phase 2",
  "region": "Northern California",
  "tags": ["technical", "standards", "planning"]
}
```

**Field requirements:**
- `date`: String in "YYYY-MM-DD" format, or null if unclear (prefer user-provided value)
- `time`: String in "HH:mm" format (24-hour), or "09:00" if unclear (prefer user-provided value)
- `title`: String, 5-10 words
- `participants`: Array of strings (minimum 1, always include Mike if mentioned)
- `client`: String or empty string ""
- `project`: String or empty string ""
- `region`: String or empty string ""
- `tags`: Array of strings (0-5 items)

Also provide a human-readable summary after the JSON:

```
Metadata Extraction Complete

Date: 2025-11-12
Time: 14:30
Source: User-provided (or "Extracted from transcript")
Title: SCADA System Standards Review
Participants: 4 people identified
  - Mike
  - John Smith
  - Sarah
  - Bob
Client: ABC Water District
Project: SCADA Upgrade Phase 2
Region: Northern California
Tags: technical, standards, planning
```

## Quality Standards

### Participant Names
- Capture ONLY people who spoke or were listed as attendees
- EXCLUDE people only mentioned in discussion or referenced in past tense
- When you see generic speaker labels (Speaker 1, Speaker 2, etc.):
  - Look for name reveals: "Speaker 1: Hi, this is John"
  - Analyze conversation flow to detect if labels are duplicates
  - Check if same speaker has multiple labels by tracking topics/voice
- Deduplicate aggressively:
  - Consolidate obvious variants (Mike/Michael/Mike Karl)
  - Merge speaker labels with revealed names
  - If two generic speakers never reveal names, keep both as "Speaker 1" and "Speaker 2"
- Always include "Mike Karl" if any variant appears as a speaker
- Don't assume relationships (e.g., don't expand "Smith" to "John Smith" unless confirmed)
- When in doubt, prefer fewer participants (false negatives) over including non-attendees (false positives)

### Date/Time Extraction
- **Always prioritize user-provided date/time over transcript extraction**
- Be conservative: only extract from transcript if confident
- Prefer explicit dates over implied dates
- If unclear and not provided by user, return null for date (don't guess)
- If time unclear and not provided by user, default to "09:00"

### Title Generation
- Be specific and descriptive
- Reflect actual meeting content
- 5-10 words target
- Use professional language
- Avoid generic titles like "Team Meeting"

### Tags
- Be selective (2-5 max)
- Use consistent terminology
- Reflect meeting purpose and content
- Skip if content is unclear

## Participant Extraction Examples

### Example 1: Generic Speaker Labels with Name Reveals
```
Speaker 1: Hi everyone, this is John calling in
Speaker 2: Thanks John, Sarah here
Speaker 1: So about the budget...
```
**Extract:** ["John", "Sarah"] (not "Speaker 1" or "Speaker 2")

### Example 2: Duplicate Speaker Detection
```
Speaker 1: Let's discuss the project timeline
Mike: I think we need two weeks
Speaker 1: Agreed, that sounds reasonable
```
**Extract:** ["Mike", "Speaker 1"] (keep separate - different people)

### Example 3: Mentioned Names (NOT Participants)
```
Sarah: Mike mentioned in his email that Bob approved the budget
John: Yes, and Alice from accounting said we're good to proceed
```
**Extract:** ["Sarah", "John"] (NOT Mike, Bob, or Alice - they were only mentioned)

### Example 4: Same Person, Multiple Labels
```
Mike: Good morning everyone
Michael: To follow up on my earlier point...
Mike Karl: Let me share my screen
```
**Extract:** ["Mike Karl"] (deduplicated)

### Example 5: Speaker Labels Without Names
```
Speaker 1: What's the status on deliverables?
Speaker 2: We're on track for next week
Speaker 1: Great, keep me posted
```
**Extract:** ["Speaker 1", "Speaker 2"] (no names revealed, keep labels)

## Error Handling

**If transcript file not found:**
- Report error clearly: "Cannot read file: [path]"
- Ask for transcript text directly

**If transcript is empty:**
- Report error: "Transcript is empty or invalid"
- Cannot proceed

**If date cannot be determined:**
- Set `date: null` and `time: "09:00"`
- Note in summary: "Date: Not specified (user did not provide, not found in transcript)"
- Coordinator will ask user for date
- Time will default to 09:00 unless user provided it

**If participants cannot be identified:**
- At minimum, include ["Mike Karl"] if Mike appears anywhere
- If no speakers identified, return empty list []
- Note in summary: "Limited participant information in transcript"

## Notes

- This skill is designed to be called by orchestrator agents
- Keep processing fast (target <30 seconds)
- Focus on extraction, not interpretation
- Return structured data for downstream processing
- The JSON output will be parsed by the coordinator agent
