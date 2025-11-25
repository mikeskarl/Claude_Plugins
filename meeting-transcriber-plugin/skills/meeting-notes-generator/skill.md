---
name: meeting-notes-generator
description: Generate structured meeting notes (800-1200 words) from cleaned transcripts. Creates executive summary, key discussions, decisions, action items, and follow-ups. This is where transcript reduction happens.
---

# Meeting Notes Generator

## Purpose

Generate professional, structured meeting notes from cleaned transcripts. This agent performs the actual summarization and content reduction (15,000 words → 800-1200 words of notes).

## Input Expected

The user will provide:
- **Cleaned transcript file path** (required): Path to cleaned transcript
- **Metadata** (required): Meeting date, title, normalized participant names
- **Meeting duration** (optional): Used to adjust content length

Or:
- **Cleaned transcript text** (alternative): Cleaned transcript as text
- **Metadata** (required): As above

## Process

### Step 1: Read Cleaned Transcript

If file path provided:
- Use Read tool to load cleaned transcript from file

If transcript text provided:
- Use the provided text

**Note:** This should be the CLEANED transcript (from transcript-cleaner), not the raw transcript.

### Step 2: Determine Target Length

Based on transcript word count or meeting duration:

- **Short meeting** (<2,000 words or <20 min): 400-600 words
- **Standard meeting** (2,000-5,000 words or 20-40 min): 800-1000 words
- **Long meeting** (>5,000 words or >40 min): 1000-1200 words

### Step 3: Generate Executive Summary

**Length:** 100-150 words

**Structure:**
1. **Meeting purpose** (2-3 sentences): Why did this meeting happen?
2. **Key outcomes** (2-3 bullet points): What was accomplished?
3. **Critical action items** (2-3 items): Most urgent next steps

**Guidelines:**
- Write for someone who didn't attend
- Focus on decisions and outcomes, not process
- Highlight what changed or was decided
- Use active voice and clear language

**Example:**
```markdown
### Executive Summary

This meeting addressed the SCADA system upgrade timeline and technical standards
alignment. The team reviewed vendor proposals and identified potential schedule
risks related to equipment lead times.

Key outcomes:
- Approved technical standards document v2.1
- Selected Vendor A for control system hardware
- Identified 6-week delay risk in Q2 delivery

Critical action items:
- John to finalize vendor contract by November 20
- Sarah to update project schedule with new milestones
- Mike to brief client on timeline adjustment next week
```

### Step 4: Generate Agenda Overview

**Length:** 50-100 words

Brief outline of what was covered:

```markdown
### Agenda Overview

**Key Discussions:** 4 topics
- SCADA technical standards review
- Vendor proposal evaluation
- Schedule and budget implications
- Client communication strategy

**Decisions Made:** 3
**Action Items:** 6
**Follow-up Items:** 2
```

### Step 5: Generate Key Discussions

**Length:** 400-600 words total (for standard meeting)

**Guidelines:**
- Cover 3-5 most important topics ONLY
- Skip small talk, procedural items, minor updates
- Each topic: 2-3 paragraphs (80-120 words)
- Focus on substance: what was said, viewpoints, data, implications

**Structure for each topic:**
```markdown
#### [Topic Title] (5-8 words, bold)

[2-3 paragraphs summarizing the discussion]

Key points raised:
- [Important point 1]
- [Important point 2]
- [Important point 3]
```

**What to include:**
- Context and background
- Different viewpoints or concerns
- Data or facts discussed
- Implications or consequences
- How the discussion concluded

**What to exclude:**
- Small talk and pleasantries
- Procedural items ("let's move to next topic")
- Repetitive points
- Off-topic tangents
- Individual speaking styles

**Example:**
```markdown
#### SCADA Technical Standards Alignment

The team conducted a detailed review of the proposed technical standards document
v2.1, focusing on communication protocols and cybersecurity requirements. John
presented research comparing DNP3 and Modbus TCP protocols, highlighting that DNP3
offers better security features but requires more expensive hardware.

Sarah raised concerns about compatibility with the client's existing infrastructure,
noting that their current HMI system only supports Modbus. The team discussed upgrade
options and associated costs. Mike suggested a hybrid approach using protocol gateways
to maintain compatibility while improving security.

Key points raised:
- DNP3 provides better cybersecurity but costs 15-20% more
- Existing client infrastructure is Modbus-based
- Protocol gateways could bridge the gap for $50K additional cost
- Client may need to budget for HMI upgrade in Phase 3
```

### Step 6: Generate Decisions Made

**Length:** 100-150 words total

**Guidelines:**
- List ONLY actual decisions (not discussions)
- 2-5 decisions typically
- Each decision: 1-2 sentences on what and why
- If no decisions made, say so explicitly

**Structure:**
```markdown
### Decisions Made

1. **[Decision in 5-10 words]**
   - [1-2 sentences on what was decided and why]

2. **[Decision in 5-10 words]**
   - [1-2 sentences on what was decided and why]
```

**Example:**
```markdown
### Decisions Made

1. **Approve Technical Standards Document v2.1**
   - The team approved the standards document with minor revisions to Section 4
   (cybersecurity protocols). This establishes the technical baseline for vendor proposals.

2. **Select Vendor A for Control System Hardware**
   - Vendor A was selected based on superior technical capabilities and competitive
   pricing, despite a 2-week longer lead time than Vendor B.

3. **Implement Hybrid Protocol Approach**
   - Approved using protocol gateways to support both DNP3 and Modbus, allowing
   security improvements while maintaining compatibility with existing systems.
```

**If no decisions:**
```markdown
### Decisions Made

No formal decisions were made in this meeting. Discussions were exploratory and
informational, with action items assigned for further investigation.
```

### Step 7: Generate Tasks To Do

**Length:** 5-7 action items maximum

**Guidelines:**
- Extract only clear, actionable items
- Be specific about the action
- Include owner (use wiki-link format: `[[Name]]`)
- Include deadline if mentioned
- If no owner, use "TBD"
- Prioritize by urgency if more than 7 identified

**Format:**
```markdown
## Tasks To Do

- [ ] **[Action in 5-10 words]** - [[Owner Name]] (Deadline if mentioned)
- [ ] **[Action in 5-10 words]** - [[Owner Name]] (Deadline if mentioned)
```

**Use normalized participant names from metadata** (already wiki-linked)

**Example:**
```markdown
## Tasks To Do

- [ ] **Finalize vendor contract with Vendor A** - [[John Smith]] (November 20)
- [ ] **Update project schedule with new milestones** - [[Sarah Johnson]] (November 25)
- [ ] **Brief client on timeline adjustment** - [[Mike Karl]] (Next week)
- [ ] **Research protocol gateway options and costs** - [[John Smith]] (December 1)
- [ ] **Draft cybersecurity assessment report** - [[Bob Wilson]] (November 30)
- [ ] **Schedule Phase 2 kickoff meeting** - [[Sarah Johnson]] (TBD)
```

### Step 8: Generate Follow-up Items

**Length:** 50-100 words (0-5 items)

**Guidelines:**
- Include items needing future discussion but not immediate action
- Topics tabled for later
- Questions raised but not answered
- Dependencies to revisit
- Omit if nothing requires follow-up

**Format:**
```markdown
### Follow-up Items

- **[Topic in 5-10 words]** - [Brief note, 1 sentence]
- **[Topic in 5-10 words]** - [Brief note, 1 sentence]
```

**Example:**
```markdown
### Follow-up Items

- **HMI System Upgrade Budget** - Revisit in Phase 3 planning once protocol gateway
performance is validated
- **Vendor B Backup Option** - Keep warm relationship in case Vendor A encounters
delivery issues
```

### Step 9: Format Complete Output

Return the meeting notes in this structure:

```markdown
## Meeting Notes

### Executive Summary

[100-150 words]

### Agenda Overview

[50-100 words]

### Key Discussions

#### [Topic 1]
[2-3 paragraphs]

#### [Topic 2]
[2-3 paragraphs]

#### [Topic 3]
[2-3 paragraphs]

[... 3-5 topics total]

### Decisions Made

1. **[Decision]**
   - [Details]

[2-5 decisions]

### Action Items Reference

See Tasks To Do section below for all actionable items.

### Follow-up Items

[0-5 items, or omit section if none]

## Tasks To Do

- [ ] **[Action]** - [[Owner]] (Deadline)
- [ ] **[Action]** - [[Owner]] (Deadline)

[5-7 action items]
```

### Step 10: Report Word Count

After generating notes, report:

```
Meeting Notes Generation Complete

Total length: {word_count} words
- Executive Summary: {exec_summary_words} words
- Agenda Overview: {agenda_words} words
- Key Discussions: {discussions_words} words
- Decisions Made: {decisions_words} words
- Follow-up Items: {followup_words} words

Action items: {task_count}

Target range: {target_min}-{target_max} words
Status: [✅ Within target / ⚠️ Under target / ⚠️ Over target]
```

## Quality Standards

### Excellent Meeting Notes
- Within target word count range (±10%)
- Scannable structure with clear headings
- Action items are specific with owners
- Covers what matters, skips routine details
- Professional business language
- Uses wiki-links for all participant names

### Content Selection Rules

**INCLUDE:**
- Decisions made
- Action items assigned
- Problems or risks identified
- Data, numbers, facts discussed
- Different viewpoints or concerns
- Context needed to understand outcomes

**EXCLUDE:**
- Small talk and greetings
- Procedural items ("let's move on")
- Repetitive statements
- Verbatim quotes (summarize instead)
- Minor clarifications
- Off-topic tangents

### Length Calibration

If meeting notes are too long:
- Reduce Key Discussions: cover fewer topics or shorten
- Combine related discussion points
- Remove less important follow-up items

If meeting notes are too short:
- Add more detail to Key Discussions
- Cover additional topics
- Expand decision explanations

## Using Metadata

**Normalized participant names** (provided by coordinator):
- Use wiki-link format throughout: `[[Mike Karl]]`, `[[John Smith]]`
- Apply in action items: `- [ ] **Task** - [[John Smith]]`
- Apply in narrative: "[[Sarah Johnson]] raised concerns..."

**Meeting date and title:**
- Use for context but don't include in output (coordinator handles this)

## Error Handling

**If cleaned transcript file not found:**
- Report error: "Cannot read cleaned transcript: [path]"
- Ask for transcript text

**If metadata missing:**
- Report error: "Required metadata not provided"
- Ask for: date, title, normalized participant names

**If transcript is very short (<500 words):**
- Adjust target: 200-400 words of meeting notes
- Note: "Short meeting, reduced notes length accordingly"

## Notes

- This skill is designed to be called by orchestrator agents
- Target processing time: 1-2 minutes
- THIS is where the 15,000 → 1,000 word reduction happens
- Focus on what matters in 6 months, not today
- Meeting notes are separate from the cleaned transcript (which preserves everything)
