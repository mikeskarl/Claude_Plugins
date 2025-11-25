---
name: transcript-cleaner
description: Clean meeting transcripts while preserving 95-100% of original word count. Fixes grammar, removes filler words, adds punctuation. Does NOT summarize. Saves to specified output file.
---

# Transcript Cleaner

## ⛔ STOP - READ THIS FIRST ⛔

**YOU WILL FAIL THIS TASK IF YOU DO NOT:**

1. **USE THE READ TOOL** to read the input file
2. **USE THE WRITE TOOL** to write the output file
3. **OUTPUT THE VERIFICATION BLOCK** at the end

**If you just describe what you would do without using tools, YOU HAVE FAILED.**

---

## 🔴 REQUIRED ACTIONS - DO ALL THREE 🔴

### ACTION 1: Read the input file
```
Use Read tool with file_path: [input file from prompt]
```

### ACTION 2: Write the output file
```
Use Write tool with file_path: [output file from prompt]
```

### ACTION 3: Output this verification block
```
=== TRANSCRIPT-CLEANER VERIFICATION ===
OUTPUT_FILE_WRITTEN: YES
OUTPUT_FILE_PATH: [the output path you wrote to]
INPUT_WORD_COUNT: [number]
OUTPUT_WORD_COUNT: [number]
REDUCTION_PERCENT: [number]%
STATUS: SUCCESS
=== END VERIFICATION ===
```

**If you do not do ALL THREE, the workflow breaks and you have failed.**

---

## 🚫 WHAT "CLEANING" MEANS - NOT SUMMARIZING 🚫

**CLEANING = Remove ONLY these words:**
- "um", "uh", "like" (when filler)
- "you know", "sort of", "kind of"
- "I mean", "basically", "actually" (when filler)

**CLEANING ≠ Rewriting sentences**
**CLEANING ≠ Combining ideas**
**CLEANING ≠ Making it shorter**
**CLEANING ≠ Paraphrasing**

### Word Count Rule

| Reduction | Status |
|-----------|--------|
| 0-5% | ✅ CORRECT - only fillers removed |
| 5-10% | ⚠️ BORDERLINE - review carefully |
| >10% | ❌ WRONG - you summarized, not cleaned |

**If your output is more than 10% shorter, you removed real content.**

---

## Process

### Step 1: Read Input
Use the Read tool to load the transcript file.
Count the words: `original_count`

### Step 2: Clean (NOT Summarize)
Only make these changes:
- Fix spelling/grammar errors
- Remove filler words (um, uh, like, you know)
- Add punctuation where missing
- Format speaker labels consistently

**Keep everything else exactly as-is.**

### Step 3: Validate Word Count
Count words in your cleaned version: `cleaned_count`
Calculate: `reduction = (original_count - cleaned_count) / original_count * 100`

**If reduction > 10%, you removed too much. Add content back.**

## ⚠️ STOP - IF REDUCTION EXCEEDS 10% ⚠️

If your cleaned version is more than 10% shorter than the original:

**YOU HAVE SUMMARIZED, NOT CLEANED. You must fix this before continuing.**

**Required actions:**
1. **GO BACK** and re-read the original transcript
2. **IDENTIFY** what content you removed that wasn't just filler words
3. **ADD BACK** all contextual phrases, connecting words, and substantive content
4. **REMEMBER:** Only remove actual filler words:
   - "um", "uh", "like" (when used as filler)
   - "you know", "sort of", "kind of"
   - "I mean", "basically", "actually" (when filler)
5. **DO NOT** remove:
   - Contextual phrases ("so", "well", "okay" when used meaningfully)
   - Connecting words ("and", "but", "so" when connecting ideas)
   - Repetitions that add emphasis
   - Any words that carry meaning or context
6. **RE-COUNT** and verify reduction is under 10%

**If you cannot get reduction under 10%:**
- The transcript may have very few filler words
- In this case, just fix spelling/grammar/punctuation
- Leave the content otherwise unchanged
- A 0-5% reduction is BETTER than a 10% reduction

**Example of what NOT to do:**
- ❌ Original: "So the thing is, we really need to focus on getting this done"
- ❌ Cleaned: "We need to get this done" (too much removed)
- ✅ Cleaned: "So the thing is, we really need to focus on getting this done" (only fix grammar if needed)

---

### Step 4: Write Output
Use the Write tool to save to the output file path.

**YOU MUST USE THE WRITE TOOL. Do not just say "I would write..."**

### Step 5: Output Verification Block
Copy and complete this block:

```
=== TRANSCRIPT-CLEANER VERIFICATION ===
OUTPUT_FILE_WRITTEN: YES
OUTPUT_FILE_PATH: [path]
INPUT_WORD_COUNT: [number]
OUTPUT_WORD_COUNT: [number]
REDUCTION_PERCENT: [number]%
STATUS: SUCCESS
=== END VERIFICATION ===
```

---

## Examples

### ✅ CORRECT Cleaning

**Input (52 words):**
```
Um, so like, the thing is, uh, we really need to, you know, kind of focus on, um, getting the SCADA system, like, updated before, uh, the end of Q2, you know, because, um, the client is really, like, pushing for that deadline, you know what I mean?
```

**Output (35 words):**
```
So the thing is, we really need to focus on getting the SCADA system updated before the end of Q2, because the client is really pushing for that deadline.
```

Reduction: 33% - but this is OK because ONLY filler words were removed. The actual content is 100% preserved.

### ❌ WRONG - This is Summarizing

**Input (52 words):**
```
Um, so like, the thing is, uh, we really need to, you know, kind of focus on, um, getting the SCADA system, like, updated before, uh, the end of Q2, you know, because, um, the client is really, like, pushing for that deadline, you know what I mean?
```

**Output (12 words):**
```
We need to update the SCADA system by Q2 for the client.
```

❌ This is SUMMARIZING. You rewrote the sentence. Don't do this.

---

## Error Handling

If input file doesn't exist:
1. Report the error
2. Write an error message to the output file
3. Set STATUS: FAILED in verification block

If any other error:
1. Write the ORIGINAL content to the output file (as fallback)
2. Set STATUS: FAILED in verification block
3. Include ERROR_REASON

**The output file MUST be created no matter what.**

---

## Final Reminder

Before you finish, check:
- [ ] Did I use the Read tool?
- [ ] Did I use the Write tool?
- [ ] Did I output the verification block?
- [ ] Is my word count reduction under 10%?

**If any answer is NO, go back and fix it.**
