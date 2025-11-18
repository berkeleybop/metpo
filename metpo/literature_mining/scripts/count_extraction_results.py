#!/usr/bin/env python3
"""
Count entities and relationships from OntoGPT YAML extraction output.
Properly parses the YAML structure instead of using grep.
"""

import argparse
import sys
from pathlib import Path

import yaml


def count_entities_and_relationships(yaml_file: Path) -> tuple[int, int]:
    """
    Count entities and relationships from OntoGPT extraction YAML.

    Returns:
        (entity_count, relationship_count)
    """
    try:
        with open(yaml_file) as f:
            # Standard YAML method for multi-document files
            documents = yaml.safe_load_all(f)

            entity_count = 0
            relationship_count = 0

            for doc in documents:
                if doc is None:
                    continue

                # Count named entities (at document root)
                if "named_entities" in doc and isinstance(doc["named_entities"], list):
                    entity_count += len(doc["named_entities"])

                # Relationships are in the extracted_object field
                extracted = doc.get("extracted_object", {})
                if isinstance(extracted, dict):
                    for _key, value in extracted.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and "subject" in item and "predicate" in item and "object" in item:
                                    relationship_count += 1

            return entity_count, relationship_count

    except FileNotFoundError:
        return 0, 0
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return 0, 0


def main():
    parser = argparse.ArgumentParser(
        description="Count entities and relationships from OntoGPT YAML output",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("yaml_file", type=Path, help="Path to OntoGPT YAML output file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    entities, relationships = count_entities_and_relationships(args.yaml_file)

    if args.json:
        import json
        print(json.dumps({"entities": entities, "relationships": relationships}))
    else:
        print(f"Entities: {entities}")
        print(f"Relationships: {relationships}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
