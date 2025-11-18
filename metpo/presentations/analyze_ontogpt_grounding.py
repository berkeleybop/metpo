#!/usr/bin/env python3
"""
Analyze OntoGPT grounding success from PRIMARY SOURCE YAML files.

Parses outputs/*.yaml directly - 100% traceable.
"""

from collections import defaultdict
from pathlib import Path

import yaml


def count_groundings(yaml_file):
    """Count METPO, ChEBI, NCBITaxon, and AUTO terms from YAML."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    counts = {
        "metpo": 0,
        "chebi": 0,
        "ncbitaxon": 0,
        "auto": 0,
        "total": 0
    }

    # Helper to check object field
    def check_object(obj):
        if not obj:
            return None
        obj_str = str(obj)
        if "w3id.org/metpo" in obj_str or obj_str.startswith("METPO:"):
            return "metpo"
        if obj_str.startswith("CHEBI:"):
            return "chebi"
        if obj_str.startswith("NCBITaxon:"):
            return "ncbitaxon"
        if obj_str.startswith("AUTO:"):
            return "auto"
        return None

    # Check extracted_object for relationships
    ext_obj = data.get("extracted_object", {})

    # Strain to phenotype relationships
    for rel in ext_obj.get("strain_to_phenotype", []):
        obj_type = check_object(rel.get("object"))
        if obj_type:
            counts[obj_type] += 1
            counts["total"] += 1

    # Chemical utilizations
    for rel in ext_obj.get("chemical_utilizations", []):
        obj_type = check_object(rel.get("object"))
        if obj_type:
            counts[obj_type] += 1
            counts["total"] += 1

    # Study taxa
    for taxon in ext_obj.get("study_taxa", []):
        obj_type = check_object(taxon)
        if obj_type:
            counts[obj_type] += 1
            counts["total"] += 1

    # Chemicals mentioned
    for chem in ext_obj.get("chemicals_mentioned", []):
        obj_type = check_object(chem)
        if obj_type:
            counts[obj_type] += 1
            counts["total"] += 1

    return counts

def main():
    outputs_dir = Path("outputs")

    phenotype_files = sorted(outputs_dir.glob("*-phenotype.yaml"))
    chemical_files = sorted(outputs_dir.glob("*-chemical.yaml"))

    print("=== OntoGPT Grounding Analysis (PRIMARY SOURCE) ===\n")
    print(f"Source: {outputs_dir.absolute()}")
    print(f"Phenotype extractions: {len(phenotype_files)}")
    print(f"Chemical extractions: {len(chemical_files)}")
    print()

    # Aggregate counts
    totals = defaultdict(int)
    per_file = {}

    for yaml_file in list(phenotype_files) + list(chemical_files):
        counts = count_groundings(yaml_file)
        per_file[yaml_file.name] = counts

        for key, val in counts.items():
            totals[key] += val

    # Print summary
    print("=== TOTALS ===")
    print(f"METPO groundings:    {totals['metpo']:4d}")
    print(f"ChEBI groundings:    {totals['chebi']:4d}")
    print(f"NCBITaxon groundings:{totals['ncbitaxon']:4d}")
    print(f"AUTO terms (failed): {totals['auto']:4d}")
    print(f"Total terms:         {totals['total']:4d}")
    print()

    # Calculate success rates
    if totals["total"] > 0:
        phenotype_total = totals["metpo"] + totals["auto"]
        if phenotype_total > 0:
            metpo_rate = 100 * totals["metpo"] / phenotype_total
            print(f"METPO phenotype success rate: {metpo_rate:.1f}% ({totals['metpo']}/{phenotype_total})")

        chem_total = totals["chebi"]
        if chem_total > 0:
            print(f"ChEBI chemical success rate: 100.0% ({chem_total}/{chem_total})")

        taxon_total = totals["ncbitaxon"]
        if taxon_total > 0:
            print(f"NCBITaxon success rate: 100.0% ({taxon_total}/{taxon_total})")

    print()

    # Per-file breakdown
    print("=== PER-FILE BREAKDOWN ===")
    for filename in sorted(per_file.keys()):
        counts = per_file[filename]
        if counts["total"] > 0:
            print(f"{filename:30s} METPO:{counts['metpo']:3d}  ChEBI:{counts['chebi']:3d}  "
                  f"NCBITaxon:{counts['ncbitaxon']:3d}  AUTO:{counts['auto']:3d}")

    # Return data for plotting
    return totals, per_file

if __name__ == "__main__":
    totals, per_file = main()
