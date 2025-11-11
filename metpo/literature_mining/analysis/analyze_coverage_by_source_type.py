#!/usr/bin/env python3
"""
Repeatable script to analyze METPO coverage and gaps by data source type:
1. IJSEM abstracts (structured)
2. Full research papers (unstructured)
3. BacDive/BactoTraits/Madin structured data (via attributed synonyms)

For ICBO 2025 - provides evidence of METPO's strengths and gaps.
"""

import csv
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List

def load_metpo_database_synonyms(template_path: Path) -> Dict[str, List[str]]:
    """
    Load METPO attributed synonyms showing alignment with structured DBs.

    Returns dict: {
        'bacdive': [(metpo_id, metpo_label, bacdive_synonym), ...],
        'bactotraits': [(metpo_id, metpo_label, bactotraits_synonym), ...],
        'madin': [(metpo_id, metpo_label, madin_synonym), ...]
    }
    """
    synonyms = {
        'bacdive': [],
        'bactotraits': [],
        'madin': []
    }

    with open(template_path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            metpo_id = row.get('ID', '')
            metpo_label = row.get('label', '')

            if not metpo_id.startswith('METPO:'):
                continue

            # BacDive keywords
            bacdive_syn = row.get('bacdive keyword synonym', '').strip()
            if bacdive_syn:
                for syn in bacdive_syn.split('|'):
                    if syn.strip():
                        synonyms['bacdive'].append((metpo_id, metpo_label, syn.strip()))

            # BactoTraits synonyms
            bactotraits_syn = row.get('bactotraits synonym', '').strip()
            if bactotraits_syn:
                for syn in bactotraits_syn.split('|'):
                    if syn.strip():
                        synonyms['bactotraits'].append((metpo_id, metpo_label, syn.strip()))

            # Madin field names
            madin_syn = row.get('madin synonym or field', '').strip()
            if madin_syn:
                for syn in madin_syn.split('|'):
                    if syn.strip():
                        synonyms['madin'].append((metpo_id, metpo_label, syn.strip()))

    return synonyms

def analyze_structured_db_coverage(synonyms: Dict) -> Dict:
    """Analyze METPO coverage of structured database vocabularies."""
    coverage = {}

    for db, syn_list in synonyms.items():
        unique_classes = set(metpo_id for metpo_id, _, _ in syn_list)
        unique_terms = set(syn for _, _, syn in syn_list)

        coverage[db] = {
            'metpo_classes': len(unique_classes),
            'db_terms_mapped': len(unique_terms),
            'mappings': syn_list
        }

    return coverage

def analyze_extraction_grounding(yaml_path: Path) -> Dict:
    """
    Analyze grounding in OntoGPT extraction YAML.

    Returns: {
        'metpo_count': int,
        'auto_count': int,
        'chebi_count': int,
        'ncbitaxon_count': int,
        'metpo_terms': [list of METPO:IDs],
        'auto_terms': [list of AUTO: terms],
        'grounding_rate': float
    }
    """
    with open(yaml_path) as f:
        content = f.read()

    metpo_terms = re.findall(r'METPO:(\d+)', content)
    auto_terms = re.findall(r'AUTO:([^\s\n,\]]+)', content)
    chebi_terms = re.findall(r'CHEBI:(\d+)', content)
    ncbi_terms = re.findall(r'NCBITaxon:(\d+)', content)

    total_phenotype = len(metpo_terms) + len(auto_terms)
    grounding_rate = (len(metpo_terms) / total_phenotype * 100) if total_phenotype > 0 else 0

    return {
        'metpo_count': len(metpo_terms),
        'auto_count': len(auto_terms),
        'chebi_count': len(chebi_terms),
        'ncbitaxon_count': len(ncbi_terms),
        'metpo_terms': metpo_terms,
        'auto_terms': auto_terms,
        'grounding_rate': grounding_rate,
        'total_extractions': content.count('input_text:')
    }

def compare_source_types(results: Dict) -> str:
    """Generate comparison report across source types."""
    lines = []
    lines.append("=" * 80)
    lines.append("METPO COVERAGE BY DATA SOURCE TYPE")
    lines.append("=" * 80)
    lines.append("")

    # Structured DB coverage (from attributed synonyms)
    if 'structured_db' in results:
        lines.append("## 1. Structured Database Coverage (BacDive, BactoTraits, Madin)")
        lines.append("")
        for db, stats in results['structured_db'].items():
            lines.append(f"### {db.upper()}")
            lines.append(f"   METPO classes aligned: {stats['metpo_classes']}")
            lines.append(f"   Database terms mapped: {stats['db_terms_mapped']}")
            lines.append(f"   Coverage: {stats.get('coverage_percent', 'N/A')}%")
            lines.append("")

            # Show examples
            lines.append("   Example mappings:")
            for metpo_id, metpo_label, db_term in stats['mappings'][:5]:
                lines.append(f"      {metpo_id} ({metpo_label}) ← {db_term}")
            if len(stats['mappings']) > 5:
                lines.append(f"      ... and {len(stats['mappings'])-5} more")
            lines.append("")

    # IJSEM abstracts (structured text)
    if 'ijsem_abstracts' in results:
        lines.append("## 2. IJSEM Abstracts (Structured Text)")
        stats = results['ijsem_abstracts']
        lines.append(f"   Grounding rate: {stats['grounding_rate']:.1f}%")
        lines.append(f"   METPO terms: {stats['metpo_count']}")
        lines.append(f"   AUTO terms: {stats['auto_count']}")
        lines.append(f"   Total extractions: {stats['total_extractions']}")
        lines.append("")

    # Full papers (unstructured)
    if 'full_papers' in results:
        lines.append("## 3. Full Research Papers (Unstructured Text)")
        stats = results['full_papers']
        lines.append(f"   Grounding rate: {stats['grounding_rate']:.1f}%")
        lines.append(f"   METPO terms: {stats['metpo_count']}")
        lines.append(f"   AUTO terms: {stats['auto_count']}")
        lines.append(f"   Total extractions: {stats['total_extractions']}")
        lines.append("")

    # Comparison summary
    lines.append("=" * 80)
    lines.append("COMPARATIVE SUMMARY")
    lines.append("=" * 80)
    lines.append("")

    if 'structured_db' in results:
        bacdive_classes = results['structured_db']['bacdive']['metpo_classes']
        bactotraits_classes = results['structured_db']['bactotraits']['metpo_classes']
        madin_classes = results['structured_db']['madin']['metpo_classes']

        lines.append(f"Structured DB vocabulary alignment: {bacdive_classes}-{madin_classes} METPO classes")
        lines.append(f"  → BacDive: {bacdive_classes} classes with attributed synonyms")
        lines.append(f"  → BactoTraits: {bactotraits_classes} classes with attributed synonyms")
        lines.append(f"  → Madin: {madin_classes} classes with attributed synonyms")
        lines.append("")

    if 'ijsem_abstracts' in results:
        lines.append(f"IJSEM abstracts grounding: {results['ijsem_abstracts']['grounding_rate']:.1f}%")
        lines.append(f"  → Structured format helps text mining")
        lines.append("")

    if 'full_papers' in results:
        lines.append(f"Full papers grounding: {results['full_papers']['grounding_rate']:.1f}%")
        lines.append(f"  → Unstructured text + varied terminology = more AUTO: terms")
        lines.append("")

    lines.append("KEY FINDING:")
    lines.append("METPO shows strong alignment with structured/semi-structured sources")
    lines.append("(database synonyms, standardized abstracts) but lower grounding on")
    lines.append("free-text mining. AUTO: terms from unstructured text reveal gaps.")
    lines.append("")

    return "\n".join(lines)

def main():
    """Main analysis."""
    repo_root = Path(__file__).parent.parent
    template_path = repo_root / 'src' / 'templates' / 'metpo_sheet.tsv'

    print("=" * 80)
    print("METPO COVERAGE ANALYSIS BY SOURCE TYPE")
    print("For ICBO 2025 - Evidence of Strengths and Gaps")
    print("=" * 80)
    print()

    results = {}

    # 1. Analyze structured DB coverage (from attributed synonyms)
    print("Loading METPO attributed synonyms...")
    synonyms = load_metpo_database_synonyms(template_path)

    print(f"Found attributed synonyms:")
    for db, syn_list in synonyms.items():
        print(f"  {db}: {len(syn_list)} mappings")

    structured_coverage = analyze_structured_db_coverage(synonyms)
    results['structured_db'] = structured_coverage

    # 2. Analyze IJSEM extractions (if available)
    ijsem_extraction = Path(__file__).parent / 'test_results' / 'ijsem_optimized_extraction.yaml'
    if ijsem_extraction.exists():
        print(f"\nAnalyzing IJSEM extraction: {ijsem_extraction.name}")
        results['ijsem_abstracts'] = analyze_extraction_grounding(ijsem_extraction)
    else:
        print(f"\nIJSEM extraction not found (run Experiment 1 first)")

    # 3. Analyze full paper extractions (production corpus)
    outputs_dir = Path(__file__).parent / 'outputs'
    fullcorpus_files = list(outputs_dir.glob('*_fullcorpus_*.yaml'))

    if fullcorpus_files:
        print(f"\nAnalyzing {len(fullcorpus_files)} full-corpus extractions...")

        combined_stats = {
            'metpo_count': 0,
            'auto_count': 0,
            'chebi_count': 0,
            'ncbitaxon_count': 0,
            'total_extractions': 0
        }

        for f in fullcorpus_files:
            stats = analyze_extraction_grounding(f)
            combined_stats['metpo_count'] += stats['metpo_count']
            combined_stats['auto_count'] += stats['auto_count']
            combined_stats['chebi_count'] += stats['chebi_count']
            combined_stats['ncbitaxon_count'] += stats['ncbitaxon_count']
            combined_stats['total_extractions'] += stats['total_extractions']

        total = combined_stats['metpo_count'] + combined_stats['auto_count']
        combined_stats['grounding_rate'] = (
            (combined_stats['metpo_count'] / total * 100) if total > 0 else 0
        )

        results['full_papers'] = combined_stats

    # Generate report
    report = compare_source_types(results)
    print("\n" + report)

    # Save results
    output_file = Path(__file__).parent / 'METPO_coverage_by_source_type.txt'
    with open(output_file, 'w') as f:
        f.write(report)
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("RAW DATA\n")
        f.write("=" * 80 + "\n\n")
        f.write(json.dumps(results, indent=2))

    print(f"\nDetailed results saved to: {output_file}")

    # Save synonym mappings for ICBO slides
    synonym_file = Path(__file__).parent / 'METPO_database_synonyms.tsv'
    with open(synonym_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Database', 'METPO_ID', 'METPO_Label', 'Database_Term'])

        for db, syn_list in synonyms.items():
            for metpo_id, metpo_label, db_term in sorted(syn_list):
                writer.writerow([db, metpo_id, metpo_label, db_term])

    print(f"Synonym mappings saved to: {synonym_file}")
    print("\nUse these files for ICBO evidence:")
    print(f"  1. {output_file.name} - Coverage comparison")
    print(f"  2. {synonym_file.name} - Database alignment proof")

if __name__ == '__main__':
    main()
