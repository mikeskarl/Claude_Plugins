---
name: question-generator
description: Generate quiz questions from extracted source material based on specified parameters and difficulty level.
---

# Question Generator

## Overview

Generates quiz questions from processed source material according to user specifications. Creates multiple choice, true/false, and fill-in-the-blank questions with appropriate difficulty and study notes.

## Input Expected

```json
{
  "extracted_content": [...],
  "quiz_params": {
    "className": "Economics 101",
    "subject": "Supply and Demand",
    "questionCount": 40,
    "questionTypes": {
      "multipleChoice": true,
      "trueFalse": true,
      "fillBlank": true
    },
    "includeNotes": true,
    "difficulty": "medium"
  }
}
```

## Question Generation Guidelines

### Question Distribution

Based on selected types, distribute questions proportionally:
- If only multiple choice: 100% multiple choice
- If multiple choice + fill blank: 90% MC, 10% fill blank
- If all three types: 70% MC, 20% true/false, 10% fill blank

### Difficulty Levels

**Easy:**
- Direct recall questions
- Simple definitions
- Basic concepts
- Straightforward examples

**Medium:**
- Application of concepts
- Comparison questions
- "Why" and "how" questions
- Requires understanding, not just recall

**Hard:**
- Analysis and evaluation
- Multi-step reasoning
- Edge cases and exceptions
- Integration of multiple concepts

### Multiple Choice Questions

Format:
```json
{
  "type": "multiple-choice",
  "question": "What is the primary factor that shifts the demand curve?",
  "options": [
    "Change in consumer income",
    "Change in production costs",
    "Change in supply chain efficiency",
    "Change in government regulations"
  ],
  "correctAnswer": "Change in consumer income",
  "notes": "Demand curve shifts are caused by factors affecting consumer behavior..."
}
```

**Requirements:**
- 4 options per question
- One clearly correct answer
- Plausible distractors (wrong answers that seem reasonable)
- Options of similar length and complexity
- Randomize correct answer position
- Avoid "all of the above" or "none of the above"

### True/False Questions

Format:
```json
{
  "type": "true-false",
  "question": "The law of demand states that as price increases, quantity demanded decreases.",
  "options": ["True", "False"],
  "correctAnswer": "True",
  "notes": "The law of demand describes the inverse relationship between price and quantity..."
}
```

**Requirements:**
- Clear, unambiguous statements
- Avoid trick questions or technicalities
- Balance true vs false answers across quiz
- Test important concepts, not trivial facts

### Fill in the Blank Questions

Format:
```json
{
  "type": "fill-blank",
  "question": "The point where supply and demand curves intersect is called the _______ point.",
  "correctAnswer": "equilibrium",
  "notes": "Market equilibrium occurs when quantity supplied equals quantity demanded..."
}
```

**Requirements:**
- Single word or short phrase answer
- Only one correct way to fill the blank
- Blank should test key terminology or concepts
- Provide context so answer is clear from question
- Accept common variations in answer checking (handled by HTML)

### Study Notes

If includeNotes is true, provide for each question:
- Brief explanation of the correct answer
- Reference to source material
- Key concept reinforcement
- 1-3 sentences maximum
- Clear and educational

If includeNotes is false, set notes to empty string.

## Quality Requirements

1. **Accuracy**: Every question must be directly supported by source material
2. **Clarity**: Questions should be unambiguous and well-worded
3. **Coverage**: Distribute questions across all major topics in source material
4. **Balance**: Mix of difficulty and question types
5. **Variety**: Avoid repetitive question patterns
6. **Relevance**: Focus on important concepts, not trivial details

## Question Generation Process

1. **Analyze source material**
   - Identify main topics and subtopics
   - Note key concepts, definitions, and relationships
   - Find examples and applications
   - Determine concept importance and complexity

2. **Plan question distribution**
   - Allocate questions to major topics proportionally
   - Ensure coverage of all important concepts
   - Mix question types as specified
   - Vary difficulty appropriately

3. **Generate questions**
   - Write clear, specific questions
   - Create plausible options for MC
   - Ensure answers are definitively correct
   - Add helpful study notes
   - Review for quality and accuracy

4. **Review and refine**
   - Check for ambiguity
   - Verify all answers are correct
   - Ensure appropriate difficulty
   - Confirm source material support

## Output Format

Return a JSON array of questions:

```json
[
  {
    "type": "multiple-choice",
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correctAnswer": "...",
    "notes": "..."
  },
  {
    "type": "fill-blank",
    "question": "...",
    "correctAnswer": "...",
    "notes": "..."
  }
]
```

## Error Handling

- If source material is insufficient, generate fewer questions and explain
- If a specific question type is requested but not feasible, notify and adjust
- Ensure minimum question count of 5 even with limited material

## Example

Given source material about economics and request for 10 medium difficulty questions:

Output would include:
- 7 multiple choice questions on key concepts
- 2 true/false questions on important principles
- 1 fill-in-blank on critical terminology
- All with appropriate study notes
- Distributed across major topics (supply, demand, equilibrium, etc.)
