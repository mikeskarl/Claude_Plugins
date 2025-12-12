# Quiz Maker Plugin

Generate interactive study quizzes from your source materials with AI-powered question generation.

## Features

- **Multi-format source support**: Process text files, images (with handwriting), and PDFs
- **Customizable quizzes**: Choose question count, types, and difficulty
- **Interactive previews**: Review and edit extracted content and generated questions
- **Smart regeneration**: Request regeneration of specific questions
- **Enhanced HTML output**: Print support and answer key viewer
- **Persistent storage**: Questions saved as JSON for future edits

## Installation

```bash
cd ~/.claude/plugins/marketplaces/custom-plugins/quiz-maker-plugin
chmod +x install.sh
./install.sh
```

The installation script will:
1. Make all Python scripts executable
2. Prompt for configuration (storage location)
3. Verify setup

## Configuration

On first use, you'll be prompted to configure:

- **Storage Root**: Where quiz files are saved
  - Default: `~/Library/Mobile Documents/com~apple~CloudDocs/Family/StudyGuides`
  - Quizzes saved in subfolders: `{YYYY-MM-DD}_{subject}/`

### Reconfigure

```bash
python3 ~/.claude/plugins/marketplaces/custom-plugins/quiz-maker-plugin/skills/quiz-maker/scripts/config.py --reconfigure
```

### Check Configuration

```bash
python3 ~/.claude/plugins/marketplaces/custom-plugins/quiz-maker-plugin/skills/quiz-maker/scripts/config.py --check
```

## Usage

In Claude Code, run the skill:

```
/quiz-maker
```

or directly call the skill in conversation:

```
Use the quiz-maker skill to create a quiz for my Economics test
```

## Workflow

1. **Parameters**: Web form collects quiz settings
   - Class name and subject
   - Source file/folder locations
   - Number of questions
   - Question types (multiple choice, true/false, fill-in-blank)
   - Include study notes
   - Difficulty level

2. **Scanning**: Inventories all files in specified locations
   - Supports: .txt, .md, .jpg, .png, .pdf, and more

3. **Extraction**: Processes all materials
   - Text files read directly
   - Images processed with Opus (handwriting detection)
   - PDFs extracted page by page

4. **Preview Extractions**: Web page shows extracted content
   - Side-by-side view of originals and extractions
   - Editable text areas for corrections

5. **Question Generation**: AI creates quiz questions
   - Follows specified distribution and difficulty
   - Includes study notes if requested

6. **Preview Questions**: Web page shows all questions
   - Edit question text and notes
   - Mark questions for regeneration
   - Continue when satisfied

7. **Final Build**: Creates HTML quiz with features
   - Print support for paper quizzes
   - Answer key viewer
   - Progress tracking
   - Study notes toggle

8. **Output**: Three files saved
   - `quiz.html` - Interactive quiz
   - `questions.json` - Question bank
   - `metadata.json` - Generation info

## Quiz Features

The generated HTML quiz includes:

- **Randomized questions**: Different order each session
- **Immediate feedback**: See correct/incorrect instantly
- **Study notes**: Toggle notes for each question
- **Progress tracking**: "X of Y" counter
- **Navigation**: Previous/Next buttons
- **Print support**: Clean layout for paper quizzes
- **Answer key**: View all answers at once
- **Mobile-friendly**: Works on phones and tablets
- **No dependencies**: Pure HTML/CSS/JS

## Question Types

### Multiple Choice
- 4 options per question
- Plausible distractors
- Randomized correct answer position

### True/False
- Clear, unambiguous statements
- Balanced true vs false distribution

### Fill in the Blank
- Single word or short phrase answers
- Case-insensitive checking
- Key terminology focus

## Source Material Support

### Text Files
- Markdown (.md)
- Plain text (.txt)
- Direct reading with no transformation

### Images
- JPEG, PNG, HEIC, and more
- Automatic handwriting detection (Opus model)
- Diagram and chart descriptions
- High accuracy OCR

### PDFs
- Page-by-page extraction
- Embedded image handling
- Structure preservation

## Advanced Usage

### Editing Existing Quizzes

Locate the `questions.json` file in your quiz directory and edit directly:

```json
[
  {
    "type": "multiple-choice",
    "question": "Your edited question text?",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": "A",
    "notes": "Your notes"
  }
]
```

Then regenerate the HTML:

```bash
python3 {scripts_dir}/build_final_html.py '{quiz_params}' '{edited_questions.json}'
```

### Batch Generation

Run the skill multiple times for different subjects. Each quiz is saved in a separate dated directory.

### Custom Styling

Modify the template at `/Users/mkarl/1Code/JaysieTest/WebApp/index.html` before generation. The build script uses this template.

## File Structure

```
quiz-maker-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── quiz-maker/
│   │   ├── skill.md
│   │   ├── user_config.json (created on first run)
│   │   └── scripts/
│   │       ├── config.py
│   │       ├── get_quiz_params.py
│   │       ├── scan_source_files.py
│   │       ├── preview_extractions.py
│   │       ├── preview_questions.py
│   │       └── build_final_html.py
│   ├── source-material-processor/
│   │   └── skill.md
│   └── question-generator/
│       └── skill.md
├── README.md
├── install.sh
└── .gitignore
```

## Output Structure

```
{storage_root}/
└── {YYYY-MM-DD}_{subject}/
    ├── quiz.html
    ├── questions.json
    └── metadata.json
```

## Troubleshooting

### Configuration Issues

If the skill can't find configuration:
```bash
python3 {scripts_dir}/config.py --reconfigure
```

### Source Files Not Found

Verify paths are correct:
- Use absolute paths
- Check file permissions
- Ensure files exist

### Poor Handwriting Detection

The plugin automatically uses Opus for image processing, which has excellent handwriting recognition. If detection is poor:
- Ensure images are clear and well-lit
- Check image resolution
- Verify handwriting is legible

### Question Quality Issues

- Provide more comprehensive source material
- Adjust difficulty level
- Use the regenerate feature for specific questions
- Edit questions directly in preview

### Browser Compatibility

The generated quiz works in:
- Chrome/Edge
- Safari
- Firefox
- Mobile browsers

For best experience, use a modern browser.

## Requirements

- Python 3.7+
- Claude Code CLI
- Web browser (for previews and quiz)

## Support

For issues or questions:
- Check the skill documentation in `skills/quiz-maker/skill.md`
- Review error messages in Claude Code output
- Verify configuration with `config.py --check`

## License

Created by Mike Karl
