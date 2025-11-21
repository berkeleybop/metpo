#!/usr/bin/env python3
"""
Check edge patterns for Biolink Model domain/range violations.
"""

import csv
import json
import sys
from collections import defaultdict

# Biolink class hierarchy (simplified - main categories we care about)
# Format: class -> [parent_classes_including_self, ...]
CLASS_HIERARCHY = {
    # Root
    "NamedThing": ["NamedThing"],

    # Biological entities
    "BiologicalEntity": ["BiologicalEntity", "NamedThing"],
    "biolink:OrganismTaxon": ["biolink:OrganismTaxon", "BiologicalEntity", "NamedThing", "OntologyClass"],

    # Chemical entities
    "ChemicalEntity": ["ChemicalEntity", "NamedThing"],
    "biolink:ChemicalEntity": ["biolink:ChemicalEntity", "ChemicalEntity", "NamedThing"],
    "biolink:ChemicalSubstance": ["biolink:ChemicalSubstance", "ChemicalEntity", "NamedThing"],

    # Phenotypic features
    "PhenotypicFeature": ["PhenotypicFeature", "NamedThing"],
    "biolink:PhenotypicFeature": ["biolink:PhenotypicFeature", "PhenotypicFeature", "NamedThing"],
    "biolink:PhenotypicQuality": ["biolink:PhenotypicQuality", "PhenotypicFeature", "NamedThing"],

    # Processes
    "Occurrent": ["Occurrent", "NamedThing"],
    "biolink:BiologicalProcess": ["biolink:BiologicalProcess", "Occurrent", "NamedThing"],

    # Other
    "OntologyClass": ["OntologyClass", "NamedThing"],
    "biolink:OntologyClass": ["biolink:OntologyClass", "OntologyClass", "NamedThing"],
    "biolink:EnvironmentalFeature": ["biolink:EnvironmentalFeature", "NamedThing"],
    "biolink:Enzyme": ["biolink:Enzyme", "NamedThing"],

    # Invalid/empty
    "(empty)": [],
    "(unknown)": []
}

def is_subclass_of(child, parent):
    """Check if child is a subclass of parent in Biolink hierarchy."""
    if child == parent:
        return True
    if child in CLASS_HIERARCHY:
        return parent in CLASS_HIERARCHY[child]
    return False

def check_domain_range(subject_cat, predicate, object_cat, constraints):
    """Check if edge violates domain/range constraints."""
    if predicate not in constraints:
        return "UNKNOWN_PREDICATE", f"Predicate {predicate} not in Biolink Model"

    required_domain = constraints[predicate]["domain"]
    required_range = constraints[predicate]["range"]

    violations = []

    # Check domain (subject)
    if required_domain != "UNKNOWN" and not is_subclass_of(subject_cat, required_domain):
        violations.append(f"Domain violation: {subject_cat} is not a {required_domain}")

    # Check range (object)
    if required_range != "UNKNOWN" and not is_subclass_of(object_cat, required_range):
        violations.append(f"Range violation: {object_cat} is not a {required_range}")

    if violations:
        return "VIOLATION", "; ".join(violations)
    return "OK", ""

def main():
    if len(sys.argv) < 3:
        print("Usage: python check_biolink_violations.py <patterns.tsv> <constraints.json>", file=sys.stderr)
        sys.exit(1)

    patterns_file = sys.argv[1]
    constraints_file = sys.argv[2]

    with open(constraints_file, 'r') as f:
        constraints = json.load(f)

    violations_by_type = defaultdict(int)

    writer = csv.writer(sys.stdout, delimiter='\t')
    writer.writerow(['source', 'subject_category', 'subject_prefix', 'predicate',
                     'object_category', 'object_prefix', 'count', 'status', 'violation'])

    with open(patterns_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            source = row['source']
            subj_cat = row['subject_category']
            subj_prefix = row['subject_prefix']
            pred = row['predicate']
            obj_cat = row['object_category']
            obj_prefix = row['object_prefix']
            count = row['count']

            status, violation = check_domain_range(subj_cat, pred, obj_cat, constraints)

            if status != "OK":
                violations_by_type[violation] += int(count)

            writer.writerow([source, subj_cat, subj_prefix, pred, obj_cat, obj_prefix,
                           count, status, violation])

    # Summary to stderr
    print("\n=== VIOLATION SUMMARY ===", file=sys.stderr)
    for violation, count in sorted(violations_by_type.items(), key=lambda x: -x[1]):
        print(f"{count:,} edges: {violation}", file=sys.stderr)

if __name__ == '__main__':
    main()
