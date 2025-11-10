#!/usr/bin/env python3
"""
Filtered METPO grounding analysis - analyze only production-quality extractions.
Excludes experimental/superseded runs to show realistic, representative results.
"""

import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
from analyze_metpo_grounding import (
    extract_entities_from_yaml,
    find_auto_terms_with_context,
    find_metpo_successes_with_context
)

# Define production-quality file patterns
PRODUCTION_PATTERNS = {
    'fullcorpus_strict': [
        # Strict: Only Oct 31 fullcorpus runs with gpt4o temp=0.0
        '*_fullcorpus_gpt4o_t00_20251031*.yaml'
    ],
    'fullcorpus_and_hybrid': [
        # Includes fullcorpus + hybrid template runs from Oct 31
        '*_fullcorpus_gpt4o_t00_20251031*.yaml',
        '*_hybrid_gpt4o_t00_20251031*.yaml'
    ],
    'all_oct31_production': [
        # All Oct 31 production files (excluding archive/, test, prototype)
        '*_gpt4o_t00_20251031*.yaml',
        '*_fullcorpus_*_20251031*.yaml',
        '*_hybrid_*_20251031*.yaml',
        'cmm_fullcorpus_*.yaml'
    ]
}

EXCLUDE_PATTERNS = [
    'archive/',
    '*_test_*',
    '*_prototype_*',
    '*_v2_*',
    '*_v3_*',
    '*_v4_*'
]

def filter_yaml_files(dir_path: Path, pattern_set: str = 'fullcorpus_strict') -> List[Path]:
    """Filter YAML files based on production quality criteria."""
    patterns = PRODUCTION_PATTERNS.get(pattern_set, PRODUCTION_PATTERNS['fullcorpus_strict'])

    all_files = []
    for pattern in patterns:
        all_files.extend(dir_path.glob(pattern))

    # Remove duplicates
    all_files = list(set(all_files))

    # Filter out excluded patterns
    filtered_files = []
    for f in all_files:
        exclude = False
        for exclude_pattern in EXCLUDE_PATTERNS:
            if exclude_pattern in str(f):
                exclude = True
                break
        if not exclude:
            filtered_files.append(f)

    return sorted(filtered_files)

def analyze_directory_filtered(dir_path: Path, pattern_set: str = 'fullcorpus_strict') -> Dict:
    """Analyze only production-quality YAML files."""
    results = {
        'summary': Counter(),
        'auto_examples': [],
        'metpo_examples': [],
        'files_analyzed': [],
        'template_annotators': {},
        'pattern_set': pattern_set
    }

    yaml_files = filter_yaml_files(dir_path, pattern_set)

    print(f"Pattern set: {pattern_set}")
    print(f"Found {len(yaml_files)} production-quality YAML files in {dir_path}")
    print("\nFiles included:")
    for f in yaml_files:
        print(f"  - {f.name}")
    print()

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
            auto_ex = find_auto_terms_with_context(yaml_file, limit=5)
            results['auto_examples'].extend(auto_ex)

        if entities.get('METPO'):
            metpo_ex = find_metpo_successes_with_context(yaml_file, limit=5)
            results['metpo_examples'].extend(metpo_ex)

    return results

def main():
    """Main analysis with pattern set selection."""
    outputs_dir = Path(__file__).parent / 'outputs'

    # Parse command line argument for pattern set
    pattern_set = 'fullcorpus_strict'
    if len(sys.argv) > 1:
        pattern_set = sys.argv[1]
        if pattern_set not in PRODUCTION_PATTERNS:
            print(f"Unknown pattern set: {pattern_set}")
            print(f"Available: {list(PRODUCTION_PATTERNS.keys())}")
            sys.exit(1)

    print("=" * 80)
    print("METPO GROUNDING ANALYSIS - PRODUCTION QUALITY ONLY")
    print("For ICBO 2025 - Representative Results")
    print("=" * 80)
    print()

    results = analyze_directory_filtered(outputs_dir, pattern_set)

    print("\n" + "=" * 80)
    print("PRODUCTION FILE SUMMARY")
    print("=" * 80)
    print(f"\nPattern set: {pattern_set}")
    print(f"Files analyzed: {len(results['files_analyzed'])}")
    for fname in results['files_analyzed']:
        print(f"  - {fname}")

    print("\n" + "=" * 80)
    print("ENTITY STATISTICS")
    print("=" * 80)
    print(f"\nEntity type counts:")
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
    else:
        print(f"\nNo METPO or AUTO terms found")

    # Count total extractions
    total_extractions = 0
    for fname in results['files_analyzed']:
        fpath = outputs_dir / fname
        with open(fpath) as f:
            total_extractions += f.read().count('input_text:')

    print(f"\nTotal paper extractions: {total_extractions}")

    # Show examples
    print("\n" + "=" * 80)
    print("EXAMPLES: SUCCESSFUL METPO GROUNDING")
    print("=" * 80)
    print(f"\nFound {len(results['metpo_examples'])} examples where METPO successfully grounded terms\n")

    for i, example in enumerate(results['metpo_examples'][:10], 1):
        print(f"\n{i}. File: {example['file']}")
        print(f"   Template: {example.get('template_name', 'unknown')}")
        if example.get('pmid'):
            print(f"   PMID: {example['pmid']}")
        if example.get('doi'):
            print(f"   DOI: {example['doi']}")
        print(f"   METPO terms: {', '.join('METPO:' + t for t in example['metpo_terms'])}")
        if example['context'] != "No context":
            print(f"   Context: {example['context'][:150]}...")

    print("\n" + "=" * 80)
    print("EXAMPLES: AUTO: TERMS INDICATING METPO GAPS")
    print("=" * 80)
    print(f"\nFound {len(results['auto_examples'])} examples with AUTO: terms\n")

    for i, example in enumerate(results['auto_examples'][:20], 1):
        print(f"\n{i}. Extraction: {example['file']}")
        print(f"   Template: {example.get('template_name', 'unknown')}")
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
    print("INTERPRETATION FOR ICBO TALK")
    print("=" * 80)
    print(f"""
This analysis uses ONLY production-quality extractions ({pattern_set}):
- Late October 2025 runs (mature templates)
- Full corpus or hybrid optimized templates
- GPT-4o with temperature 0.0 (deterministic)
- Excludes experimental/superseded runs

Key findings:
1. Grounding rate: {grounding_rate:.1f}% shows realistic free-text mining performance
2. AUTO: terms reveal systematic gaps - candidates for METPO expansion
3. Contrast with structured DB alignment (54-60% coverage) shows METPO optimized for
   semi-structured data integration, not free-text mining
4. Total corpus: {total_extractions} paper extractions across {len(results['files_analyzed'])} extraction runs

Recommendation: Report these numbers for ICBO - honest, representative, reproducible.
""")

    # Save results
    output_file = Path(__file__).parent / f'metpo_grounding_production_{pattern_set}.txt'
    with open(output_file, 'w') as f:
        f.write("METPO Grounding Analysis - Production Quality\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Pattern set: {pattern_set}\n")
        f.write(f"Files analyzed: {len(results['files_analyzed'])}\n\n")
        for fname in results['files_analyzed']:
            f.write(f"  {fname}\n")

        f.write(f"\nTotal extractions: {total_extractions}\n")
        f.write(f"\nEntity counts:\n")
        for prefix, count in sorted(results['summary'].items(), key=lambda x: -x[1]):
            f.write(f"  {prefix}: {count}\n")

        if total_phenotype > 0:
            f.write(f"\nGrounding rate: {grounding_rate:.1f}%\n")
            f.write(f"AUTO rate: {100-grounding_rate:.1f}%\n")

        f.write("\n\nAUTO: TERM EXAMPLES (METPO GAPS):\n" + "=" * 80 + "\n")
        for example in results['auto_examples'][:30]:
            f.write(f"\nFile: {example['file']}\n")
            f.write(f"Template: {example.get('template_name', 'unknown')}\n")
            if example.get('pmid'):
                f.write(f"PMID: {example['pmid']}\n")
            if example.get('doi'):
                f.write(f"DOI: {example['doi']}\n")
            f.write(f"AUTO terms: {example['auto_terms']}\n")
            if example['context'] != "No context":
                f.write(f"Context: {example['context'][:200]}\n")
            f.write("-" * 80 + "\n")

    print(f"\nDetailed results saved to: {output_file}")
    print("\nTo run with different pattern sets:")
    print(f"  uv run python {Path(__file__).name} fullcorpus_strict")
    print(f"  uv run python {Path(__file__).name} fullcorpus_and_hybrid")
    print(f"  uv run python {Path(__file__).name} all_oct31_production")

if __name__ == '__main__':
    main()
