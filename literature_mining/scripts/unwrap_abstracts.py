#!/usr/bin/env python3
"""
Unwrap abstracts from artl-cli dict format to plain text.

artl-cli outputs abstracts in a dict format like:
    {'content': '...', 'saved_to': None, 'windowed': False}

This script converts them back to plain text by extracting the 'content' field.

Usage:
    python unwrap_abstracts.py file1.txt file2.txt ...
    python unwrap_abstracts.py inputs/*.txt
"""

import sys
import ast


def unwrap_abstract(filepath):
    """Unwrap a single abstract file from dict format to plain text."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if file starts with dict format
    if content.strip().startswith('{'):
        try:
            # Parse the dict string
            data = ast.literal_eval(content)

            # Extract content if it's a dict with 'content' key
            if isinstance(data, dict) and 'content' in data:
                with open(filepath, 'w') as f:
                    f.write(data['content'])
                print(f"Unwrapped: {filepath}")
                return True
        except (SyntaxError, ValueError) as e:
            print(f"Warning: Could not parse {filepath}: {e}")
            return False

    return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    unwrapped_count = 0
    for filepath in sys.argv[1:]:
        if unwrap_abstract(filepath):
            unwrapped_count += 1

    print(f"\nUnwrapped {unwrapped_count} of {len(sys.argv) - 1} files")


if __name__ == '__main__':
    main()
