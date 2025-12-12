#!/usr/bin/env python3
"""
Build final HTML quiz file with embedded question data.
Includes print support and answer key export functionality.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import shutil

from config import get_storage_root


def read_template():
    """Read the HTML template from the reference file."""
    template_path = Path("/Users/mkarl/1Code/JaysieTest/WebApp/index.html")

    if not template_path.exists():
        print(f"ERROR: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    return template_path.read_text()


def enhance_template_with_features(template_html):
    """Add print support and answer key export features to the template."""

    # Add print styles and answer key button
    enhanced_styles = """
        @media print {
            .header {
                break-after: avoid;
            }
            .nav-buttons,
            .restart-button,
            .notes-toggle,
            .submit-button {
                display: none !important;
            }
            .question-card {
                break-inside: avoid;
                page-break-inside: avoid;
                margin-bottom: 30px;
            }
            .notes-content {
                display: block !important;
            }
            body {
                background-color: white;
            }
        }

        .utility-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .utility-button {
            flex: 1;
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }

        .utility-button:hover {
            background-color: #5a6268;
        }

        .utility-button:active {
            transform: scale(0.98);
        }

        .answer-key-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            overflow-y: auto;
        }

        .answer-key-modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .answer-key-content {
            background: white;
            border-radius: 12px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .answer-key-header {
            background-color: #800000;
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .answer-key-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
        }

        .answer-key-body {
            padding: 20px;
        }

        .answer-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #800000;
        }

        .answer-item-number {
            font-weight: 600;
            color: #800000;
            margin-bottom: 5px;
        }

        .answer-item-text {
            margin: 5px 0;
        }

        .answer-item-correct {
            font-weight: 600;
            color: #28a745;
            margin-top: 5px;
        }
    </style>"""

    # Insert enhanced styles before the closing </style> tag
    template_html = template_html.replace('</style>', enhanced_styles)

    # Add utility buttons and answer key modal before closing </body>
    utility_html = """
    <div class="utility-buttons">
        <button class="utility-button" onclick="window.print()">Print Quiz</button>
        <button class="utility-button" onclick="showAnswerKey()">View Answer Key</button>
    </div>

    <div class="answer-key-modal" id="answerKeyModal">
        <div class="answer-key-content">
            <div class="answer-key-header">
                <h2>Answer Key</h2>
                <button class="answer-key-close" onclick="hideAnswerKey()">&times;</button>
            </div>
            <div class="answer-key-body" id="answerKeyBody"></div>
        </div>
    </div>

    <script>
        function showAnswerKey() {
            const modal = document.getElementById('answerKeyModal');
            const body = document.getElementById('answerKeyBody');

            let html = '';
            questionBank.forEach((q, index) => {
                html += `
                    <div class="answer-item">
                        <div class="answer-item-number">Question ${index + 1}</div>
                        <div class="answer-item-text">${q.question}</div>
                        <div class="answer-item-correct">Answer: ${q.correctAnswer}</div>
                    </div>
                `;
            });

            body.innerHTML = html;
            modal.classList.add('show');
        }

        function hideAnswerKey() {
            document.getElementById('answerKeyModal').classList.remove('show');
        }

        // Close modal when clicking outside
        document.getElementById('answerKeyModal').addEventListener('click', function(e) {
            if (e.target === this) {
                hideAnswerKey();
            }
        });
    </script>"""

    # Insert before the last </body> tag
    template_html = template_html.replace('</body>', utility_html + '\n</body>')

    return template_html


def build_quiz_html(quiz_data, questions, template_html):
    """Build the complete HTML quiz file."""

    # Convert questions to JavaScript array
    questions_js = json.dumps(questions, indent=12)

    # Replace the questionBank array in template
    # Find the questionBank definition and replace it
    start_marker = "const questionBank = ["
    end_marker = "];"

    start_idx = template_html.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find questionBank in template", file=sys.stderr)
        sys.exit(1)

    end_idx = template_html.find(end_marker, start_idx)
    if end_idx == -1:
        print("ERROR: Could not find end of questionBank", file=sys.stderr)
        sys.exit(1)

    # Replace with new questions
    new_html = (
        template_html[:start_idx] +
        "const questionBank = " +
        questions_js +
        template_html[end_idx + len(end_marker):]
    )

    # Update the title
    title = f"{quiz_data.get('className', 'Study Quiz')} - {quiz_data.get('subject', 'Quiz')}"
    new_html = new_html.replace('<title>Study Quiz</title>', f'<title>{title}</title>')
    new_html = new_html.replace('<h1>Study Quiz</h1>', f'<h1>{title}</h1>')

    return new_html


def save_quiz_file(quiz_data, html_content, questions_json, extracted_content_json=None):
    """Save the quiz HTML and supporting files."""

    storage_root = get_storage_root()

    # Create subfolder with date and subject
    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = quiz_data.get('subject', 'quiz').replace('/', '-').replace(' ', '-')
    folder_name = f"{date_str}_{subject}"

    output_dir = storage_root / folder_name

    # Check if directory needs to be created
    if not output_dir.exists():
        print(f"\nOutput directory does not exist: {output_dir}")
        response = input("Create this directory? (y/n): ").strip().lower()
        if response != 'y':
            print("ERROR: User declined to create directory", file=sys.stderr)
            sys.exit(1)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created: {output_dir}")
        except Exception as e:
            print(f"ERROR: Could not create directory: {e}", file=sys.stderr)
            sys.exit(1)

    # Save HTML file
    html_file = output_dir / "quiz.html"
    html_file.write_text(html_content, encoding='utf-8')

    # Save question bank JSON for future edits
    json_file = output_dir / "questions.json"
    json_file.write_text(questions_json, encoding='utf-8')

    # Save extracted content as reference material
    if extracted_content_json:
        extracted_file = output_dir / "extracted_content.json"
        extracted_file.write_text(extracted_content_json, encoding='utf-8')

        # Copy source files to output directory
        try:
            extracted_data = json.loads(extracted_content_json)
            source_files_dir = output_dir / "source_files"
            source_files_dir.mkdir(exist_ok=True)

            copied_files = []
            for i, item in enumerate(extracted_data, 1):
                file_path = item.get('path', '')
                if file_path:
                    source_path = Path(file_path)
                    if source_path.exists():
                        try:
                            # Copy file with unique name if needed
                            dest_name = source_path.name
                            dest_path = source_files_dir / dest_name

                            # Handle name conflicts
                            counter = 1
                            while dest_path.exists():
                                stem = source_path.stem
                                suffix = source_path.suffix
                                dest_name = f"{stem}_{counter}{suffix}"
                                dest_path = source_files_dir / dest_name
                                counter += 1

                            shutil.copy2(source_path, dest_path)
                            copied_files.append(dest_name)
                        except Exception as e:
                            print(f"WARNING: Could not copy {source_path.name}: {e}", file=sys.stderr)

            print(f"Copied {len(copied_files)} source files to source_files/")
        except Exception as e:
            print(f"WARNING: Could not copy source files: {e}", file=sys.stderr)

        # Also create a readable markdown version
        try:
            extracted_data = json.loads(extracted_content_json)
            md_content = "# Extracted Source Material\n\n"
            md_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for i, item in enumerate(extracted_data, 1):
                file_name = item.get('name', 'Unknown')
                file_type = item.get('type', 'unknown')
                file_path = item.get('path', '')
                extracted_text = item.get('extracted', '')

                md_content += f"## {i}. {file_name}\n\n"
                md_content += f"**Type:** {file_type}  \n"
                md_content += f"**Source:** `{file_path}`  \n"
                md_content += f"**Copied to:** `source_files/{file_name}`\n\n"
                md_content += "### Extracted Content\n\n"
                md_content += f"{extracted_text}\n\n"
                md_content += "---\n\n"

            md_file = output_dir / "extracted_content.md"
            md_file.write_text(md_content, encoding='utf-8')
        except Exception as e:
            print(f"WARNING: Could not create markdown version: {e}", file=sys.stderr)

    # Save metadata
    metadata = {
        'generated': datetime.now().isoformat(),
        'className': quiz_data.get('className'),
        'subject': quiz_data.get('subject'),
        'testInfo': quiz_data.get('testInfo'),
        'questionCount': len(json.loads(questions_json)),
        'difficulty': quiz_data.get('difficulty'),
        'sourcePaths': quiz_data.get('sourcePaths', [])
    }
    metadata_file = output_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    print(f"\n=== Quiz Files Saved ===")
    print(f"HTML: {html_file}")
    print(f"Questions JSON: {json_file}")
    print(f"Metadata: {metadata_file}")
    if extracted_content_json:
        print(f"Extracted Content JSON: {output_dir / 'extracted_content.json'}")
        print(f"Extracted Content MD: {output_dir / 'extracted_content.md'}")
        print(f"Source Files: {output_dir / 'source_files/'}")

    print(f"\nOUTPUT_DIR={output_dir}")
    print(f"HTML_FILE={html_file}")

    return output_dir, html_file


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: build_final_html.py '<quiz_data_json>' '<questions_json>' ['<extracted_content_json>']", file=sys.stderr)
        sys.exit(1)

    quiz_data_json = sys.argv[1]
    questions_json = sys.argv[2]
    extracted_content_json = sys.argv[3] if len(sys.argv) > 3 else None

    quiz_data = json.loads(quiz_data_json)
    questions = json.loads(questions_json)

    print("=== Building Final Quiz HTML ===")
    print(f"Question count: {len(questions)}")

    # Read and enhance template
    template = read_template()
    enhanced_template = enhance_template_with_features(template)

    # Build final HTML
    html_content = build_quiz_html(quiz_data, questions, enhanced_template)

    # Save files (including extracted content if provided)
    output_dir, html_file = save_quiz_file(quiz_data, html_content, questions_json, extracted_content_json)

    print("\n✓ Quiz generation complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
