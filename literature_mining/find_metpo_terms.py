#!/usr/bin/env python3
"""
Thoroughly search extraction YAML files for METPO terms.
Parse YAML properly to find METPO IDs in nested structures.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict

def find_metpo_in_obj(obj, path=""):
    """Recursively search for METPO terms in nested data structures."""
    metpo_terms = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            metpo_terms.extend(find_metpo_in_obj(value, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            metpo_terms.extend(find_metpo_in_obj(item, new_path))
    elif isinstance(obj, str):
        if obj.startswith("METPO:"):
            metpo_terms.append((path, obj))

    return metpo_terms

def analyze_yaml_file(yaml_path):
    """Parse YAML file and find all METPO terms."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {yaml_path.name}")
    print(f"{'='*80}")

    with open(yaml_path) as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            print(f"ERROR parsing YAML: {e}")
            return

    print(f"Number of documents in file: {len(docs)}")

    all_metpo_terms = []
    auto_terms = []

    for i, doc in enumerate(docs):
        if not doc:
            continue

        # Find METPO terms in entire document
        metpo_in_doc = find_metpo_in_obj(doc)
        all_metpo_terms.extend([(i, path, term) for path, term in metpo_in_doc])

        # Also find AUTO terms for comparison
        auto_in_doc = [(path, term) for path, term in find_metpo_in_obj(doc)
                       if isinstance(term, str) and term.startswith("AUTO:")]
        auto_terms.extend([(i, path, term) for path, term in auto_in_doc])

        # Show extracted_object structure for first few docs
        if i < 3 and 'extracted_object' in doc:
            print(f"\nDocument {i} extracted_object structure:")
            print(json.dumps(doc['extracted_object'], indent=2)[:500])

    print(f"\n{'='*80}")
    print(f"RESULTS FOR {yaml_path.name}")
    print(f"{'='*80}")
    print(f"Total METPO terms found: {len(all_metpo_terms)}")
    print(f"Total AUTO terms found: {len(auto_terms)}")

    if all_metpo_terms:
        print(f"\n✓ METPO TERMS FOUND:")
        # Show first 20
        for doc_idx, path, term in all_metpo_terms[:20]:
            print(f"  Doc {doc_idx}: {path} = {term}")
        if len(all_metpo_terms) > 20:
            print(f"  ... and {len(all_metpo_terms) - 20} more")
    else:
        print(f"\n✗ NO METPO TERMS FOUND")
        print(f"\nAUTO terms (first 10):")
        for doc_idx, path, term in auto_terms[:10]:
            print(f"  Doc {doc_idx}: {path} = {term}")

    return {
        'file': yaml_path.name,
        'metpo_count': len(all_metpo_terms),
        'auto_count': len(auto_terms),
        'metpo_terms': all_metpo_terms,
        'auto_terms': auto_terms
    }

def main():
    """Search all production YAML files for METPO terms."""
    outputs_dir = Path(__file__).parent / 'outputs'

    # Production files from fullcorpus_strict filter
    production_files = sorted(outputs_dir.glob('*_fullcorpus_gpt4o_t00_20251031*.yaml'))

    print(f"Searching {len(production_files)} production YAML files for METPO terms...")
    print(f"Using proper YAML parsing to find nested METPO IDs")

    results = []
    for yaml_file in production_files:
        result = analyze_yaml_file(yaml_file)
        results.append(result)

    # Summary
    print(f"\n{'='*80}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*80}")

    total_metpo = sum(r['metpo_count'] for r in results)
    total_auto = sum(r['auto_count'] for r in results)

    print(f"\nTotal METPO terms across all files: {total_metpo}")
    print(f"Total AUTO terms across all files: {total_auto}")

    if total_metpo > 0:
        print(f"\n✓ SUCCESS! Found METPO terms in extraction files!")
        print(f"\nFiles with METPO terms:")
        for r in results:
            if r['metpo_count'] > 0:
                print(f"  {r['file']}: {r['metpo_count']} METPO terms")
    else:
        print(f"\n✗ No METPO terms found in any production files")
        print(f"\nThis suggests:")
        print(f"  1. Templates may not have METPO annotators configured")
        print(f"  2. METPO path in templates may be incorrect")
        print(f"  3. Genuine grounding failures")

if __name__ == '__main__':
    main()
