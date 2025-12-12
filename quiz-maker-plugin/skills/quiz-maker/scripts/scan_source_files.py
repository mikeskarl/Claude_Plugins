#!/usr/bin/env python3
"""
Scan source file locations and inventory all materials.
Detects file types and prepares for processing.
"""

import sys
import json
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    'text': ['.txt', '.md', '.markdown'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic'],
    'pdf': ['.pdf'],
}


def categorize_file(file_path):
    """Determine file category based on extension."""
    ext = file_path.suffix.lower()

    for category, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions:
            return category

    return 'unknown'


def scan_path(path_str):
    """Scan a file or directory path and return inventory."""
    path = Path(path_str).expanduser().resolve()

    if not path.exists():
        print(f"WARNING: Path does not exist: {path}", file=sys.stderr)
        return []

    files = []

    if path.is_file():
        category = categorize_file(path)
        if category != 'unknown':
            files.append({
                'path': str(path),
                'type': category,
                'name': path.name,
                'size': path.stat().st_size
            })
    elif path.is_dir():
        for item in path.rglob('*'):
            if item.is_file():
                category = categorize_file(item)
                if category != 'unknown':
                    files.append({
                        'path': str(item),
                        'type': category,
                        'name': item.name,
                        'size': item.stat().st_size
                    })

    return files


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: scan_source_files.py <path1> [path2] [path3] ...", file=sys.stderr)
        sys.exit(1)

    source_paths = sys.argv[1:]

    print("=== Scanning Source Materials ===\n")

    all_files = []
    for path_str in source_paths:
        print(f"Scanning: {path_str}")
        files = scan_path(path_str)
        all_files.extend(files)

    # Categorize by type
    by_type = {'text': [], 'image': [], 'pdf': []}
    for file_info in all_files:
        by_type[file_info['type']].append(file_info)

    # Summary
    print(f"\n=== Scan Summary ===")
    print(f"Total files found: {len(all_files)}")
    print(f"  Text files: {len(by_type['text'])}")
    print(f"  Image files: {len(by_type['image'])}")
    print(f"  PDF files: {len(by_type['pdf'])}")

    # Output JSON
    output = {
        'total_count': len(all_files),
        'by_type': {
            'text': {'count': len(by_type['text']), 'files': by_type['text']},
            'image': {'count': len(by_type['image']), 'files': by_type['image']},
            'pdf': {'count': len(by_type['pdf']), 'files': by_type['pdf']}
        }
    }

    print("\n=== FILE_INVENTORY ===")
    print(json.dumps(output, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
