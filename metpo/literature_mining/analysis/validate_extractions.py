#!/usr/bin/env python3
"""
Validation script for OntoGPT extraction quality.
Flags suspicious patterns that might indicate poor extraction.
"""

import click
import yaml
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

class ExtractionValidator:
    """Validates extraction quality and flags issues."""

    def __init__(self, yaml_file: Path):
        self.yaml_file = yaml_file
        self.docs = []
        self.issues = []

        with open(yaml_file) as f:
            self.docs = list(yaml.safe_load_all(f))

    def validate_all(self) -> List[Dict]:
        """Run all validation checks."""
        for i, doc in enumerate(self.docs, 1):
            doc_issues = self.validate_document(doc, i)
            if doc_issues:
                self.issues.extend(doc_issues)

        return self.issues

    def validate_document(self, doc: Dict, doc_num: int) -> List[Dict]:
        """Validate a single document extraction."""
        issues = []

        if not doc or 'extracted_object' not in doc:
            issues.append({
                'document': doc_num,
                'severity': 'ERROR',
                'issue': 'Missing extracted_object',
                'details': 'Document has no extracted_object field'
            })
            return issues

        extracted = doc['extracted_object']
        input_len = len(doc.get('input_text', ''))

        # Check 1: Low extraction yield from large input
        if input_len > 10000:  # Full paper territory (>10K chars)
            issues.extend(self._check_extraction_yield(doc_num, extracted, input_len))

        # Check 2: Poor grounding quality
        issues.extend(self._check_grounding_quality(doc_num, doc))

        # Check 3: Missing critical fields
        issues.extend(self._check_missing_fields(doc_num, extracted))

        # Check 4: Inconsistent strain identifiers
        issues.extend(self._check_strain_consistency(doc_num, extracted))

        return issues

    def _check_extraction_yield(self, doc_num: int, extracted: Dict, input_len: int) -> List[Dict]:
        """Check if extraction yield is suspiciously low for long inputs.

        GOAL: Extract many well-formed relationships for knowledge graph construction.
        """
        issues = []

        chemicals = extracted.get('chemicals_mentioned', [])
        chem_rels = extracted.get('chemical_utilizations', [])

        if not isinstance(chem_rels, list):
            chem_rels = [chem_rels] if chem_rels else []

        # Count valid relationships (have subject, predicate, object)
        valid_rels = [r for r in chem_rels if isinstance(r, dict)
                      and all(k in r for k in ['subject', 'predicate', 'object'])]

        # For full papers (>10K chars), expect many relationships
        if input_len > 10000:
            if len(valid_rels) < 5:
                issues.append({
                    'document': doc_num,
                    'severity': 'ERROR',
                    'issue': 'LOW EXTRACTION YIELD - Critical for KG',
                    'details': f'Only {len(valid_rels)} valid chemical relationships from {input_len:,} char full paper. Expected ≥5 for useful knowledge graph.'
                })
        elif input_len > 5000:  # Medium papers
            if len(valid_rels) < 2:
                issues.append({
                    'document': doc_num,
                    'severity': 'WARNING',
                    'issue': 'Low extraction yield',
                    'details': f'Only {len(valid_rels)} relationships from {input_len:,} chars. Expected ≥2.'
                })

        # If chemicals mentioned but no relationships - MAJOR ISSUE
        if chemicals and not valid_rels:
            issues.append({
                'document': doc_num,
                'severity': 'ERROR',
                'issue': 'No relationships despite chemicals present',
                'details': f'{len(chemicals) if isinstance(chemicals, list) else 1} chemicals found, but 0 valid relationships. Cannot build knowledge graph!'
            })

        return issues

    def _check_grounding_quality(self, doc_num: int, doc: Dict) -> List[Dict]:
        """Check grounding quality of entities.

        GOAL: Minimize AUTO: prefixes for high-quality knowledge graph.
        Best outcome = entities grounded to CHEBI, NCBITaxon, etc.
        """
        issues = []

        named_entities = doc.get('named_entities', [])
        if not named_entities:
            issues.append({
                'document': doc_num,
                'severity': 'WARNING',
                'issue': 'No named entities',
                'details': 'No entities grounded. May affect KG quality.'
            })
            return issues

        auto_count = sum(1 for e in named_entities if 'AUTO:' in str(e.get('id', '')))
        none_count = sum(1 for e in named_entities if 'none' in str(e.get('id', '')).lower())
        chebi_count = sum(1 for e in named_entities if 'CHEBI:' in str(e.get('id', '')))
        ncbi_count = sum(1 for e in named_entities if 'NCBITaxon:' in str(e.get('id', '')))

        total_count = len(named_entities)
        grounded_count = total_count - auto_count - none_count

        if total_count > 0:
            auto_ratio = auto_count / total_count
            grounded_ratio = grounded_count / total_count

            # Flag if >50% are AUTO (poor grounding - major issue for KG)
            if auto_ratio > 0.5:
                issues.append({
                    'document': doc_num,
                    'severity': 'ERROR',
                    'issue': 'POOR GROUNDING - Critical for KG',
                    'details': f'{auto_count}/{total_count} ({auto_ratio*100:.0f}%) entities are AUTO. Need CHEBI/NCBITaxon for quality knowledge graph. Only {chebi_count} CHEBI, {ncbi_count} NCBITaxon.'
                })
            elif auto_ratio > 0.3:
                issues.append({
                    'document': doc_num,
                    'severity': 'WARNING',
                    'issue': 'Moderate AUTO usage',
                    'details': f'{auto_count}/{total_count} ({auto_ratio*100:.0f}%) entities are AUTO. {grounded_count} grounded ({grounded_ratio*100:.0f}%): {chebi_count} CHEBI, {ncbi_count} NCBITaxon.'
                })
            else:
                # Good grounding - report it!
                issues.append({
                    'document': doc_num,
                    'severity': 'INFO',
                    'issue': '✅ Good grounding quality',
                    'details': f'{grounded_count}/{total_count} ({grounded_ratio*100:.0f}%) entities grounded: {chebi_count} CHEBI, {ncbi_count} NCBITaxon. Only {auto_count} AUTO.'
                })

        return issues

    def _check_missing_fields(self, doc_num: int, extracted: Dict) -> List[Dict]:
        """Check for missing critical fields."""
        issues = []

        # Check for study taxa
        if not extracted.get('study_taxa'):
            issues.append({
                'document': doc_num,
                'severity': 'WARNING',
                'issue': 'Missing study_taxa',
                'details': 'No organism taxa extracted'
            })

        return issues

    def _check_strain_consistency(self, doc_num: int, extracted: Dict) -> List[Dict]:
        """Check if strain identifiers are consistent across fields."""
        issues = []

        strains = extracted.get('strains', [])
        if not isinstance(strains, list):
            strains = [strains] if strains else []

        # Get strains used in relationships
        chem_rels = extracted.get('chemical_utilizations', [])
        strain_rels = extracted.get('strain_relationships', [])

        if not isinstance(chem_rels, list):
            chem_rels = [chem_rels] if chem_rels else []
        if not isinstance(strain_rels, list):
            strain_rels = [strain_rels] if strain_rels else []

        # Extract subjects from relationships
        chem_subjects = set()
        for rel in chem_rels:
            if isinstance(rel, dict) and 'subject' in rel:
                subj = str(rel['subject']).split(':')[-1]  # Remove AUTO: prefix
                chem_subjects.add(subj)

        strain_subjects = set()
        for rel in strain_rels:
            if isinstance(rel, dict) and 'subject' in rel:
                subj = str(rel['subject']).split(':')[-1]
                strain_subjects.add(subj)

        # Check if relationship subjects are in the strains list
        strain_ids = set(str(s).split(':')[-1] for s in strains)

        unrecognized = (chem_subjects | strain_subjects) - strain_ids
        if unrecognized:
            issues.append({
                'document': doc_num,
                'severity': 'INFO',
                'issue': 'Inconsistent strain identifiers',
                'details': f'Strains used in relationships but not in strains list: {", ".join(unrecognized)}'
            })

        return issues

    def print_report(self):
        """Print validation report."""
        click.echo("=" * 80)
        click.echo(f"EXTRACTION VALIDATION REPORT: {self.yaml_file.name}")
        click.echo("=" * 80)
        click.echo()

        if not self.issues:
            click.echo("✅ No issues found!")
            return

        # Group by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue['severity']].append(issue)

        # Print summary
        click.echo(f"Total documents: {len(self.docs)}")
        click.echo(f"Total issues: {len(self.issues)}")
        click.echo(f"  ERROR: {len(by_severity['ERROR'])}")
        click.echo(f"  WARNING: {len(by_severity['WARNING'])}")
        click.echo(f"  INFO: {len(by_severity['INFO'])}")
        click.echo()

        # Print details
        for severity in ['ERROR', 'WARNING', 'INFO']:
            issues = by_severity[severity]
            if not issues:
                continue

            click.echo(f"\n{severity} ISSUES ({len(issues)}):")
            click.echo("-" * 80)

            for issue in issues:
                click.echo(f"Document {issue['document']}: {issue['issue']}")
                click.echo(f"  └─ {issue['details']}")

        click.echo("\n" + "=" * 80)


@click.command()
def main():
    if len(sys.argv) < 2:
        click.echo("Usage: python validate_extractions.py <extraction_output.yaml>")
        sys.exit(1)

    yaml_file = Path(sys.argv[1])

    if not yaml_file.exists():
        click.echo(f"Error: File not found: {yaml_file}")
        sys.exit(1)

    validator = ExtractionValidator(yaml_file)
    validator.validate_all()
    validator.print_report()

    # Exit with error code if any ERROR level issues
    errors = [i for i in validator.issues if i['severity'] == 'ERROR']
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
