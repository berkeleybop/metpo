#!/usr/bin/env python3
"""
Analyze OntoGPT YAML outputs to identify:
1. Examples where METPO successfully grounded text extractions
2. Examples where AUTO: terms indicate gaps in METPO coverage

For ICBO 2025 talk preparation.
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

def extract_entities_from_yaml(yaml_path: Path) -> Dict[str, List[str]]:
    """Extract all entity references (METPO:, AUTO:, CHEBI:, etc.) from YAML."""
    entities = defaultdict(list)

    try:
        with open(yaml_path) as f:
            content = f.read()

        # Find all CURIE-style identifiers
        curie_pattern = r'(METPO|AUTO|CHEBI|PATO|NCBITaxon|GO|ENVO|OBI|PCO|MICRO):([^\s\n,\]]+)'
        matches = re.findall(curie_pattern, content)

        for prefix, local_id in matches:
            entities[prefix].append(local_id)

    except Exception as e:
        print(f"Error processing {yaml_path}: {e}")

    return entities

def extract_template_info(yaml_path: Path) -> Dict:
    """Extract template metadata from YAML file."""
    try:
        with open(yaml_path) as f:
            # Read just the header
            lines = []
            for i, line in enumerate(f):
                lines.append(line)
                if i > 100:  # Only read first 100 lines for metadata
                    break

            content = ''.join(lines)

            # Try to parse as YAML to get template info
            try:
                docs = list(yaml.safe_load_all(content))
                if docs and isinstance(docs[0], dict):
                    first_doc = docs[0]
                    return {
                        'id': first_doc.get('id', 'unknown'),
                        'name': first_doc.get('name', 'unknown'),
                        'title': first_doc.get('title', 'unknown'),
                        'description': first_doc.get('description', 'unknown')
                    }
            except:
                pass

            # Fallback: extract from filename
            name = yaml_path.stem
            return {
                'id': f'metpo:{name}',
                'name': name,
                'title': name.replace('_', ' ').title(),
                'description': f'Extraction template: {name}'
            }

    except Exception as e:
        print(f"Error extracting template info from {yaml_path}: {e}")
        return {'id': 'unknown', 'name': 'unknown', 'title': 'unknown', 'description': 'unknown'}

def find_auto_terms_with_context(yaml_path: Path, limit=10) -> List[Dict]:
    """Find AUTO: terms with surrounding context to understand what's missing."""
    auto_examples = []

    try:
        with open(yaml_path) as f:
            content = f.read()

        # Extract template info
        template_info = extract_template_info(yaml_path)

        # Split into extraction blocks
        blocks = content.split('---\n')

        for block in blocks:
            if 'AUTO:' in block:
                # Extract pmid/doi
                pmid_match = re.search(r'pmid:\s*["\']?(\d+)', block)
                pmid = pmid_match.group(1) if pmid_match else None

                doi_match = re.search(r'doi:\s*["\']?([0-9.]+/[^\s\'"]+)', block, re.IGNORECASE)
                doi = doi_match.group(1) if doi_match else None

                # Extract paper title/source from input_text
                title_match = re.search(r'(?:Title:|#)\s*([^\n]+)', block)
                title = title_match.group(1).strip() if title_match else None

                # Find all AUTO terms in this block
                auto_terms = re.findall(r'AUTO:([^\s\n,\]]+)', block)

                if auto_terms and len(auto_examples) < limit:
                    # Get some context
                    context_match = re.search(r'input_text:\s*\|[+\-]?\s*\n(.{0,300})', block, re.DOTALL)
                    context = context_match.group(1).strip()[:200] if context_match else "No context"

                    auto_examples.append({
                        'file': yaml_path.name,
                        'template_name': template_info['name'],
                        'template_title': template_info['title'],
                        'pmid': pmid,
                        'doi': doi,
                        'title': title,
                        'auto_terms': list(set(auto_terms))[:5],  # First 5 unique
                        'context': context
                    })

    except Exception as e:
        print(f"Error finding AUTO terms in {yaml_path}: {e}")

    return auto_examples

def find_metpo_successes_with_context(yaml_path: Path, limit=10) -> List[Dict]:
    """Find examples where METPO terms successfully grounded extractions."""
    metpo_examples = []

    try:
        with open(yaml_path) as f:
            content = f.read()

        # Split into extraction blocks
        blocks = content.split('---\n')

        for block in blocks:
            if 'METPO:' in block:
                # Extract pmid if available
                pmid_match = re.search(r'pmid:\s*["\']?(\d+)', block)
                pmid = pmid_match.group(1) if pmid_match else None

                # Find all METPO terms in this block
                metpo_terms = re.findall(r'METPO:(\d+)', block)

                if metpo_terms and len(metpo_examples) < limit:
                    # Get some context
                    context_match = re.search(r'input_text:\s*\|[+\-]?\s*\n(.{0,300})', block, re.DOTALL)
                    context = context_match.group(1).strip()[:200] if context_match else "No context"

                    metpo_examples.append({
                        'file': yaml_path.name,
                        'pmid': pmid,
                        'metpo_terms': list(set(metpo_terms))[:5],  # First 5 unique
                        'context': context
                    })

    except Exception as e:
        print(f"Error finding METPO terms in {yaml_path}: {e}")

    return metpo_examples

def extract_annotators_from_template(template_path: Path) -> List[str]:
    """Extract annotator ontologies from template YAML."""
    annotators = []
    try:
        with open(template_path) as f:
            content = yaml.safe_load(f)

        # Search for annotators in classes
        if 'classes' in content:
            for class_name, class_def in content['classes'].items():
                if isinstance(class_def, dict) and 'attributes' in class_def:
                    for attr_name, attr_def in class_def['attributes'].items():
                        if isinstance(attr_def, dict) and 'annotations' in attr_def:
                            if 'annotators' in attr_def['annotations']:
                                annotators.append(attr_def['annotations']['annotators'])

                if isinstance(class_def, dict) and 'annotations' in class_def:
                    if 'annotators' in class_def['annotations']:
                        annotators.append(class_def['annotations']['annotators'])

    except Exception as e:
        pass

    return list(set(annotators))

def analyze_directory(dir_path: Path) -> Dict:
    """Analyze all YAML files in directory."""
    results = {
        'summary': Counter(),
        'auto_examples': [],
        'metpo_examples': [],
        'files_analyzed': [],
        'template_annotators': {}
    }

    yaml_files = list(dir_path.glob('*.yaml'))

    print(f"Found {len(yaml_files)} YAML files in {dir_path}")

    for yaml_file in yaml_files:
        if yaml_file.stat().st_size == 0:
            continue

        print(f"Analyzing {yaml_file.name}...")
        results['files_analyzed'].append(yaml_file.name)

        # Count all entity types
        entities = extract_entities_from_yaml(yaml_file)
        for prefix, ids in entities.items():
            results['summary'][prefix] += len(ids)

        # Collect examples
        if entities.get('AUTO'):
            auto_ex = find_auto_terms_with_context(yaml_file, limit=3)
            results['auto_examples'].extend(auto_ex)

        if entities.get('METPO'):
            metpo_ex = find_metpo_successes_with_context(yaml_file, limit=3)
            results['metpo_examples'].extend(metpo_ex)

    return results

def main():
    """Main analysis."""
    outputs_dir = Path(__file__).parent / 'outputs'

    print("=" * 80)
    print("METPO Grounding Analysis for ICBO 2025")
    print("=" * 80)
    print()

    results = analyze_directory(outputs_dir)

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"\nFiles analyzed: {len(results['files_analyzed'])}")
    print("\nEntity type counts:")
    for prefix, count in sorted(results['summary'].items(), key=lambda x: -x[1]):
        print(f"  {prefix:15s}: {count:6d}")

    # Calculate grounding rate
    metpo_count = results['summary'].get('METPO', 0)
    auto_count = results['summary'].get('AUTO', 0)
    total_phenotype = metpo_count + auto_count

    if total_phenotype > 0:
        grounding_rate = (metpo_count / total_phenotype) * 100
        print(f"\nPhenotype grounding rate: {grounding_rate:.1f}% ({metpo_count}/{total_phenotype})")
        print(f"AUTO term rate: {100-grounding_rate:.1f}% ({auto_count}/{total_phenotype})")

    # Show examples
    print("\n" + "=" * 80)
    print("EXAMPLES: SUCCESSFUL METPO GROUNDING")
    print("=" * 80)
    print(f"\nFound {len(results['metpo_examples'])} examples where METPO successfully grounded terms\n")

    for i, example in enumerate(results['metpo_examples'][:10], 1):
        print(f"\n{i}. File: {example['file']}")
        if example['pmid']:
            print(f"   PMID: {example['pmid']}")
        print(f"   METPO terms: {', '.join('METPO:' + t for t in example['metpo_terms'])}")
        print(f"   Context: {example['context'][:150]}...")

    print("\n" + "=" * 80)
    print("EXAMPLES: AUTO: TERMS INDICATING METPO GAPS")
    print("=" * 80)
    print(f"\nFound {len(results['auto_examples'])} examples with AUTO: terms\n")

    for i, example in enumerate(results['auto_examples'][:15], 1):
        print(f"\n{i}. Extraction: {example['file']}")
        print(f"   Template: {example.get('template_name', 'unknown')}")
        print(f"   Template title: {example.get('template_title', 'unknown')}")
        if example.get('pmid'):
            print(f"   PMID: {example['pmid']}")
        if example.get('doi'):
            print(f"   DOI: {example['doi']}")
        if example.get('title'):
            print(f"   Paper title: {example['title'][:80]}...")
        print(f"   AUTO terms: {', '.join(example['auto_terms'])}")
        if example['context'] != "No context":
            print(f"   Context: {example['context'][:150]}...")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR ICBO TALK")
    print("=" * 80)
    print("""
    1. Use METPO success examples to show ontology-guided text mining working
    2. Use AUTO: term examples to show where METPO needs expansion
    3. Grounding rate metric shows percentage of phenotype terms successfully mapped
    4. Common AUTO: patterns reveal systematic gaps (e.g., specific strain types, novel phenotypes)
    """)

    # Save detailed results
    output_file = Path(__file__).parent / 'metpo_grounding_analysis_icbo2025.txt'
    with open(output_file, 'w') as f:
        f.write("METPO Grounding Analysis for ICBO 2025\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {Path(__file__).stat().st_mtime}\n\n")
        f.write(f"Files analyzed: {len(results['files_analyzed'])}\n")
        f.write("\nEntity counts:\n")
        for prefix, count in sorted(results['summary'].items(), key=lambda x: -x[1]):
            f.write(f"  {prefix}: {count}\n")

        if total_phenotype > 0:
            f.write(f"\nGrounding rate: {grounding_rate:.1f}%\n")

        f.write("\n\nMETPO SUCCESS EXAMPLES:\n" + "=" * 80 + "\n")
        for example in results['metpo_examples']:
            f.write(f"\nFile: {example['file']}\n")
            if example['pmid']:
                f.write(f"PMID: {example['pmid']}\n")
            f.write(f"METPO terms: {example['metpo_terms']}\n")
            f.write(f"Context: {example['context']}\n")
            f.write("-" * 80 + "\n")

        f.write("\n\nAUTO: TERM EXAMPLES (GAPS):\n" + "=" * 80 + "\n")
        for example in results['auto_examples']:
            f.write(f"\nFile: {example['file']}\n")
            if example['pmid']:
                f.write(f"PMID: {example['pmid']}\n")
            f.write(f"AUTO terms: {example['auto_terms']}\n")
            f.write(f"Context: {example['context']}\n")
            f.write("-" * 80 + "\n")

    print(f"\nDetailed results saved to: {output_file}")

if __name__ == '__main__':
    main()
