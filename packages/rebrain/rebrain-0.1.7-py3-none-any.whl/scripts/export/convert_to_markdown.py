#!/usr/bin/env python3
"""
Simple JSON to Markdown converter for learnings.json and cognitions.json
"""

import json
import sys
from pathlib import Path


def convert_learnings_to_md(data: dict) -> str:
    """Convert learnings.json to markdown format"""
    lines = ["# Learnings\n"]
    
    learnings = data.get("learnings", [])
    for learning in learnings:
        title = learning.get("title", "Untitled")
        content = learning.get("content", "")
        
        lines.append(f"**{title}**")
        lines.append(content)
        lines.append("")  # Empty line between entries
    
    return "\n".join(lines)


def convert_cognitions_to_md(data: dict) -> str:
    """Convert cognitions.json to markdown format"""
    lines = ["# Cognitions\n"]
    
    cognitions = data.get("cognitions", [])
    for idx, cognition in enumerate(cognitions, start=1):
        content = cognition.get("content", "")
        
        lines.append(f"**Cognition {idx}**")
        lines.append(content)
        lines.append("")  # Empty line between entries
    
    return "\n".join(lines)


def detect_file_type(data: dict) -> str:
    """Detect if file is learnings or cognitions based on content"""
    if "learnings" in data:
        return "learnings"
    elif "cognitions" in data:
        return "cognitions"
    else:
        raise ValueError("Unable to detect file type. Expected 'learnings' or 'cognitions' key.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_markdown.py <input_json_file>")
        print("\nExample:")
        print("  python convert_to_markdown.py data/learnings/learnings.json")
        print("  python convert_to_markdown.py data/cognitions/cognitions.json")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    # Read JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Detect type and convert
    file_type = detect_file_type(data)
    
    if file_type == "learnings":
        markdown_content = convert_learnings_to_md(data)
        output_file = input_file.parent / "learnings.md"
    else:  # cognitions
        markdown_content = convert_cognitions_to_md(data)
        output_file = input_file.parent / "cognitions.md"
    
    # Write markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✓ Converted {file_type} to markdown")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()

