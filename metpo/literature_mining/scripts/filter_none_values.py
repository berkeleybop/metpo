"""
Filter 'none' placeholder values from OntoGPT extraction output.

Removes AUTO:none and incorrectly grounded 'none' entities (like NCBITaxon:32644)
while preserving legitimate AUTO: CURIEs for real ungrounded entities.
"""
import sys
from pathlib import Path

import yaml


def is_none_value(value):
    """Check if a value is a 'none' placeholder."""
    if isinstance(value, str):
        val_lower = value.lower()
        # Check for obvious none placeholders
        if val_lower in ("none", "auto:none", "ncbitaxon:32644"):
            return True
        # Check for AUTO:none with URL encoding
        if "auto:none" in val_lower or "auto%3anone" in val_lower:
            return True
    elif isinstance(value, dict):
        # For relationship objects, check if subject/object is 'none'
        if is_none_value(value.get("subject")) or is_none_value(value.get("object")):
            return True
    return False


def filter_none_from_list(items):
    """Filter none values from a list."""
    if not items:
        return items
    return [item for item in items if not is_none_value(item)]


def filter_none_from_dict(obj):
    """Recursively filter none values from extracted_object."""
    if not isinstance(obj, dict):
        return obj

    filtered = {}
    for key, value in obj.items():
        if value is None:
            continue

        if isinstance(value, list):
            # Filter lists (strains, taxa, relationships, etc.)
            filtered_list = filter_none_from_list(value)
            if filtered_list:  # Only include non-empty lists
                filtered[key] = filtered_list
        elif isinstance(value, dict):
            # Recursively filter nested dicts
            filtered_dict = filter_none_from_dict(value)
            if filtered_dict:
                filtered[key] = filtered_dict
        elif not is_none_value(value):
            # Keep non-none scalar values
            filtered[key] = value

    return filtered


def filter_named_entities(entities):
    """Filter 'none' from named_entities list."""
    if not entities:
        return entities

    filtered = []
    for entity in entities:
        # Skip entities with 'none' as label or ID
        if is_none_value(entity.get("id")) or is_none_value(entity.get("label")):
            continue
        filtered.append(entity)

    return filtered


def process_document(doc):
    """Process a single YAML document."""
    # Filter extracted_object
    if "extracted_object" in doc:
        doc["extracted_object"] = filter_none_from_dict(doc["extracted_object"])

    # Filter named_entities
    if "named_entities" in doc:
        doc["named_entities"] = filter_named_entities(doc["named_entities"])

    return doc


def main():
    if len(sys.argv) != 3:
        print("Usage: filter_none_values.py <input.yaml> <output.yaml>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)

    # Load all documents from YAML
    with Path(input_file).open() as f:
        docs = list(yaml.safe_load_all(f))

    # Process each document
    filtered_docs = [process_document(doc) for doc in docs]

    # Write filtered documents
    with Path(output_file).open( "w") as f:
        yaml.dump_all(filtered_docs, f, default_flow_style=False, sort_keys=False)

    print(f"Filtered {len(filtered_docs)} documents: {input_file} → {output_file}")


if __name__ == "__main__":
    main()
