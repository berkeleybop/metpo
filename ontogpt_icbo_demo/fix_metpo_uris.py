#!/usr/bin/env python3
"""
Fix METPO URIs in OntoGPT YAML outputs.

Converts angle-bracketed full URIs like:
  object: <https://w3id.org/metpo/1000143>

To proper format without brackets:
  object: https://w3id.org/metpo/1000143

This allows proper OWL conversion with rdflib.
"""

import re
import sys
from pathlib import Path

def fix_metpo_uris(yaml_content):
    """Remove angle brackets from METPO URIs."""
    # Pattern to match: object: <https://w3id.org/metpo/XXXXXX>
    pattern = r'(object:\s+)<(https://w3id\.org/metpo/\d+)>'
    replacement = r'\1\2'

    fixed = re.sub(pattern, replacement, yaml_content)

    # Count changes
    original_count = len(re.findall(r'<https://w3id\.org/metpo/\d+>', yaml_content))

    return fixed, original_count

def main():
    outputs_dir = Path("/home/mark/gitrepos/metpo/ontogpt_icbo_demo/outputs")

    yaml_files = list(outputs_dir.glob("*.yaml"))

    if not yaml_files:
        print("No YAML files found in outputs/")
        return 1

    total_fixed = 0

    for yaml_file in sorted(yaml_files):
        print(f"Processing {yaml_file.name}...", end=" ")

        content = yaml_file.read_text()
        fixed_content, count = fix_metpo_uris(content)

        if count > 0:
            # Write fixed content
            yaml_file.write_text(fixed_content)
            print(f"Fixed {count} URIs")
            total_fixed += count
        else:
            print("No METPO URIs found")

    print(f"\nTotal: Fixed {total_fixed} METPO URIs across {len(yaml_files)} files")
    return 0

if __name__ == "__main__":
    sys.exit(main())
