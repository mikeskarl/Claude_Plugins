---
name: source-material-processor
description: Extract and process content from source materials (text, images, PDFs). Automatically uses Opus for handwriting detection.
---

# Source Material Processor

## Overview

Processes source files and extracts text content. Automatically detects and handles:
- Text files (markdown, txt)
- Images (with handwriting detection)
- PDF documents

## Usage

This skill is called with a file inventory and returns extracted content for each file.

## Input Expected

JSON inventory of files from scan_source_files.py:
```json
{
  "total_count": 15,
  "by_type": {
    "text": {"count": 3, "files": [...]},
    "image": {"count": 10, "files": [...]},
    "pdf": {"count": 2, "files": [...]}
  }
}
```

## Processing Logic

### Text Files
- Read directly using the Read tool
- No transformation needed
- Preserve exact content

### Image Files
- **IMPORTANT**: Use Opus model for ALL image processing
- Read each image file using the Read tool (supports images)
- Extract all visible text, including handwritten content
- Describe any diagrams, charts, or visual elements
- Output plain text representation

### PDF Files
- Use available PDF reading tools or MCP servers
- Extract all text content page by page
- Note any embedded images or diagrams
- Output plain text representation

## Output Format

Return a JSON array with extracted content for each file:

```json
[
  {
    "path": "/path/to/file1.jpg",
    "type": "image",
    "name": "notes_page1.jpg",
    "extracted": "Chapter 3: Economics\n\nSupply and Demand\n- Supply: quantity producers are willing to sell..."
  },
  {
    "path": "/path/to/file2.md",
    "type": "text",
    "name": "study_notes.md",
    "extracted": "# Key Concepts\n\n## Market Equilibrium\n..."
  }
]
```

## Error Handling

- If a file cannot be read, include error message in extracted field
- Continue processing remaining files
- Report all errors at the end

## Model Selection

**CRITICAL**: For image processing, you MUST use the Opus model to ensure accurate handwriting recognition. The Opus model has superior vision capabilities for detecting and transcribing handwritten text.

When processing images:
1. Use the Read tool to load the image
2. Carefully examine all visible text (printed and handwritten)
3. Transcribe all content accurately
4. Describe visual elements (diagrams, drawings, highlights)
5. Maintain the original structure and organization

## Example Workflow

```
Input: File inventory with 5 images, 2 markdown files, 1 PDF

Step 1: Process text files
- Read each markdown file using Read tool
- Store content as-is

Step 2: Process images (using Opus)
- For each image:
  - Use Read tool to view image
  - Extract all printed text
  - Extract all handwritten text
  - Describe diagrams/visual elements
  - Combine into coherent text output

Step 3: Process PDFs
- Extract text from each PDF
- Maintain page structure
- Note any visual elements

Step 4: Return complete extraction array
```

## Quality Guidelines

- Preserve the original meaning and structure
- Maintain terminology exactly as written
- Don't summarize or paraphrase
- Include ALL content, even if repetitive
- Note any unclear or illegible sections
- Preserve mathematical notation, formulas, and symbols
