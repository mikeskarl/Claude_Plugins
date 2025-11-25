---
name: transcript-cleaner
description: Clean meeting transcripts while preserving 95-100% of original word count. Fixes grammar, removes filler words, adds punctuation. Does NOT summarize. Saves to specified output file.
---

# Transcript Cleaner

## Purpose

Clean and improve transcript readability while preserving ALL substantive content. This agent transforms raw transcripts into professional, readable text WITHOUT reducing content or summarizing.

**CRITICAL RULE: Preserve 95-100% of original word count**

## Input Expected

The user will provide:
- **Input file path** (required): Path to raw transcript file
- **Output file path** (required): Where to save cleaned transcript

Or:
- **Transcript text** (alternative): Raw transcript as text
- **Output file path** (required): Where to save cleaned transcript

## Process

### Step 1: Read Input Transcript

If file path provided:
- Use Read tool to load transcript from file
- Count words in original: `original_word_count`

If transcript text provided:
- Use the provided text
- Count words: `original_word_count`

**Report to yourself:**
"Original transcript: {original_word_count} words"

### Step 2: Clean the Transcript

Apply these improvements ONLY:

**Grammar and Spelling:**
- Fix obvious grammatical errors
- Correct spelling mistakes
- Fix verb tenses and agreement
- Add proper capitalization

**Filler Words:**
- Remove excessive filler words: "um", "uh", "like", "you know", "sort of", "kind of"
- Keep some fillers if they add meaning or natural speech pattern
- Don't remove ALL instances, just excessive ones

**Punctuation:**
- Add proper punctuation: periods, commas, question marks
- Add paragraph breaks for readability
- Add line breaks between speakers or major topic shifts

**Speaker Labels:**
- If present, keep them and format consistently
- Format: "**Speaker Name:** [dialogue]"
- If not present, don't add them

**Technical Terms:**
- Standardize technical terminology consistently
- Use proper capitalization for acronyms
- Fix technical term spellings

**Readability:**
- Break very long sentences into shorter ones (preserve meaning)
- Add paragraph breaks for readability (every 3-5 sentences)
- Add spacing between different speakers or topics

### Step 3: What NOT to Do

**NEVER:**
- Summarize or condense discussions
- Remove any substantive content
- Remove topics or discussions
- Paraphrase to make shorter
- Combine multiple points into one
- Skip over "boring" or repetitive parts
- Remove context or background information
- Remove explanations or elaborations

**The goal is CLEANING, not SUMMARIZING**

### Step 4: Validate Word Count

After cleaning:
- Count words in cleaned transcript: `cleaned_word_count`
- Calculate: `reduction_pct = (1 - cleaned_word_count / original_word_count) * 100`

**Validation rules:**
- ✅ Reduction 0-5%: Excellent (only fillers removed)
- ✅ Reduction 5-10%: Acceptable (some redundancy removed)
- ⚠️ Reduction 10-15%: Warning (may have removed too much)
- ❌ Reduction >15%: ERROR (definitely removed content, not just cleaning)

**If reduction >10%:**
- Review what was removed
- Restore any substantive content
- Re-clean more conservatively
- Target: Keep reduction under 10%

### Step 5: Save Output

**ALWAYS write an output file, regardless of cleaning quality:**

1. If reduction is 0-15%: Write the cleaned transcript
2. If reduction is >15%: Write the best cleaned version available, include warning in report
3. If input file cannot be read: Copy input text to output file
4. If any error occurs: Write original content to output file

Use Write tool to save cleaned transcript to output file path.

**Critical:** The output file MUST be created even if cleaning was unsuccessful. The coordinator skill depends on this file existing.

### Step 6: Report Results

Provide this summary:

```
Transcript Cleaning Complete

Input: [input file path]
Output: [output file path]

Word Count Analysis:
- Original: {original_word_count} words
- Cleaned: {cleaned_word_count} words
- Reduction: {reduction_pct}% ({words_removed} words removed)

Status: [✅ Excellent / ✅ Acceptable / ⚠️ Review recommended / ❌ Error]

Quality improvements applied:
- Grammar and spelling corrections
- Filler word removal (um, uh, like, etc.)
- Punctuation and paragraph structure
- Technical term standardization
- Speaker label formatting [if applicable]

Content preserved:
- All discussions and topics
- All decisions and action items
- All context and explanations
- All participant contributions
```

**If reduction >10%, add warning:**
```
⚠️ WARNING: Reduction exceeded 10% target
This may indicate content was removed beyond just cleaning.
Coordinator should review if this is acceptable.
```

## Quality Standards

### Excellent Cleaning (Target)
- 0-5% word reduction
- Significantly improved readability
- No substantive content lost
- Natural conversational flow maintained
- Professional appearance

### Acceptable Cleaning
- 5-10% word reduction
- Good readability improvement
- Minimal content loss (only redundant phrases)
- Maintains original meaning completely

### Unacceptable Cleaning
- >10% word reduction
- Content removed or summarized
- Topics or discussions omitted
- Meaning changed or lost

## Examples

### Good Cleaning Example

**Before (52 words):**
```
Um, so like, the thing is, uh, we really need to, you know, kind of focus on, um,
getting the SCADA system, like, updated before, uh, the end of Q2, you know,
because, um, the client is really, like, pushing for that deadline, you know what I mean?
```

**After (42 words):**
```
The thing is, we really need to focus on getting the SCADA system updated before
the end of Q2, because the client is pushing for that deadline.
```

**Analysis:**
- Original: 52 words
- Cleaned: 42 words
- Reduction: 19% (only fillers removed)
- Content: 100% preserved
- ✅ Excellent

### Bad Cleaning Example (DON'T DO THIS)

**Before (52 words):**
```
Um, so like, the thing is, uh, we really need to, you know, kind of focus on, um,
getting the SCADA system, like, updated before, uh, the end of Q2, you know,
because, um, the client is really, like, pushing for that deadline, you know what I mean?
```

**After (12 words):**
```
We need to update the SCADA system by Q2 for the client.
```

**Analysis:**
- Original: 52 words
- Cleaned: 12 words
- Reduction: 77%
- ❌ ERROR: This is summarizing, not cleaning!

## Handling Large Transcripts

For transcripts >10,000 words:

1. **Process in sections** (keep context):
   - Break into 2,000-3,000 word segments
   - Clean each segment separately
   - Maintain continuity between segments

2. **Track cumulative word count:**
   - Monitor total reduction across all segments
   - Ensure overall reduction stays <10%

3. **Reassemble:**
   - Combine cleaned segments
   - Smooth transitions between segments
   - Verify overall coherence

## Error Handling

**If input file not found:**
- Report error: "Cannot read input file: [path]"
- Ask for transcript text or correct path

**If output file path invalid:**
- Report error: "Cannot write to output path: [path]"
- Suggest valid path

**If transcript is empty:**
- Report error: "Input transcript is empty"
- Cannot proceed

**If cleaning results in >15% reduction:**
- Write the cleaned transcript to output file anyway (don't skip writing)
- Report warning: "Excessive reduction detected: {X}% removed"
- Include both cleaned and original word counts
- Note: "File saved with warning. Coordinator may choose to use original chunk instead."

## Fallback Output Guarantee

If ANY error prevents proper cleaning:
1. Write the original input content to the output file path
2. Report the error clearly
3. Mark status as "FALLBACK: Original content preserved"

This ensures downstream processing can continue even if cleaning fails.

## Notes

- This skill is designed to be called by orchestrator agents
- Target processing time: 2-3 minutes for 15,000 word transcript
- Focus on cleaning, NOT summarizing
- Preserve discourse markers that add meaning
- Maintain natural conversational flow
- The 95-100% word count preservation is NON-NEGOTIABLE
