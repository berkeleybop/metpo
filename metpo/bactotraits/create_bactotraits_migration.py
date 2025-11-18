#!/usr/bin/env python3
"""
Script to convert BactoTraits sheet to minimal_classes format
Handles column mapping, duplicate resolution, and OBO standardization
"""

import csv
import sys
from pathlib import Path


def convert_iri_to_curie(iri):
    """Convert full IRI to METPO CURIE format"""
    if iri.startswith("https://w3id.org/metpo/"):
        return iri.replace("https://w3id.org/metpo/", "METPO:")
    return iri

def resolve_duplicate_labels(label, iri, all_rows):
    """Add qualifiers to duplicate labels based on context analysis"""
    # Handle specific known duplicates based on our analysis
    if label == "pH optimum":
        if "1000233" in iri:
            return "pH optimum (growth range)"
        if "1000331" in iri:
            return "pH optimum (metabolic efficiency)"
    elif label == "pH range":
        if "1000235" in iri:
            return "pH range (growth tolerance)"
        if "1000332" in iri:
            return "pH range (cellular homeostasis)"
    elif label == "temperature optimum":
        if "1000304" in iri:
            return "temperature optimum (growth range)"
        if "1000329" in iri:
            return "temperature optimum (metabolic activity)"
    elif label == "temperature range":
        if "1000306" in iri:
            return "temperature range (growth tolerance)"
        if "1000330" in iri:
            return "temperature range (metabolic viability)"

    # Return original label if no conflicts
    return label

def map_parent_iri_to_label(parent_iri):
    """Map parent class IRIs to their corresponding labels from minimal_classes"""
    parent_mapping = {
        "https://w3id.org/metpo/1000523": "phenotype",  # pH adaptation parent
        "https://w3id.org/metpo/1000245": "phenotype",  # pH/temp metrics
        "https://w3id.org/metpo/1000147": "quality",    # general measurement quality
        "https://w3id.org/metpo/1000522": "phenotype",  # salinity tolerance
        "https://w3id.org/metpo/1000217": "biological process",  # metabolic process
        "https://w3id.org/metpo/1000232": "pH delta",   # pH delta subclasses
        "https://w3id.org/metpo/1000303": "temperature delta",  # temp delta subclasses
        "https://w3id.org/metpo/1000331": "pH optimum (metabolic efficiency)",  # pH optimum subclasses
        "https://w3id.org/metpo/1000332": "pH range (cellular homeostasis)",   # pH range subclasses
        "https://w3id.org/metpo/1000333": "NaCl optimum",  # NaCl optimum subclasses
        "https://w3id.org/metpo/1000334": "NaCl range",    # NaCl range subclasses
        "https://w3id.org/metpo/1000335": "NaCl delta",    # NaCl delta subclasses
        "https://w3id.org/metpo/1000304": "temperature optimum (growth range)",  # temp optimum subclasses
        "https://w3id.org/metpo/1000306": "temperature range (growth tolerance)",   # temp range subclasses
        "https://w3id.org/metpo/1000127": "GC content",    # GC content subclasses
        "https://w3id.org/metpo/1000139": "quality",      # genomic feature
        "https://w3id.org/metpo/1000300": "material entity"  # genomic component
    }
    return parent_mapping.get(parent_iri.strip(), "phenotype")  # default to phenotype

def process_parent_classes(parent_str):
    """Convert parent class IRIs to single label, taking first parent if multiple"""
    if not parent_str or parent_str.strip() == "":
        return ""

    # Take only the first parent if multiple (split by |)
    first_parent = parent_str.split("|")[0].strip()
    return map_parent_iri_to_label(first_parent)

def integrate_range_into_description(description, range_min, range_max, units):
    """Integrate range information into description using standard OBO language"""
    if not description:
        description = ""

    # Build range clause
    range_parts = []
    if range_min and range_max:
        range_parts.append(f"ranging from {range_min} to {range_max}")
    elif range_min:
        range_parts.append(f"with minimum value of {range_min}")
    elif range_max:
        range_parts.append(f"with maximum value of {range_max}")

    if units and range_parts:
        range_parts.append(f"{units}")

    if range_parts:
        range_clause = " ".join(range_parts)
        if description and not description.endswith("."):
            description += "."
        if description:
            description += f" Values {range_clause}."
        else:
            description = f"Values {range_clause}."

    return description

def main():
    bactotraits_file = Path("downloads/sheets/bactotraits.tsv")
    output_file = Path("bactotraits_migration_ready.tsv")

    if not bactotraits_file.exists():
        print(f"Error: {bactotraits_file} not found")
        sys.exit(1)

    # Track labels to resolve duplicates

    # Output header matching exactly minimal_classes format
    output_header = [
        "ID", "label", "TYPE", "parent class", "TYPE", "description",
        "definition source", "comment", "biolink equivalent",
        "confirmed exact synonym", "literature mining synonyms",
        "madin synonym or field", "synonym source",
        "bacdive keyword synonym", "synonym source",
        "bactotraits synonym", "synonym source"
    ]

    # ROBOT template row matching minimal_classes
    robot_row = [
        "ID", "LABEL", "TYPE", "SC %", "TYPE", "A IAO:0000115",
        ">A IAO:0000119", "A rdfs:comment", "AI skos:closeMatch",
        "A oboInOwl:hasExactSynonym SPLIT=|", "A oboInOwl:hasRelatedSynonym SPLIT=|",
        "A oboInOwl:hasRelatedSynonym SPLIT=|", ">AI IAO:0000119 SPLIT=|",
        "A oboInOwl:hasRelatedSynonym SPLIT=|", ">AI IAO:0000119",
        "A oboInOwl:hasRelatedSynonym SPLIT=|", ">AI IAO:0000119"
    ]

    migrated_rows = []

    with open(bactotraits_file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip header row
        next(reader)  # Skip robot template row

        for row in reader:
            if len(row) < 4:  # Skip incomplete rows
                continue

            iri = row[0].strip()
            if not iri.startswith("https://w3id.org/metpo/"):
                continue

            # Convert IRI to CURIE
            curie_id = convert_iri_to_curie(iri)

            # Handle label with duplicate resolution
            original_label = row[1].strip()
            unique_label = resolve_duplicate_labels(original_label, iri, None)

            # Process parent classes
            parent_classes = process_parent_classes(row[3])

            # Get description
            description = row[4].strip() if len(row) > 4 else ""

            # Get exact synonyms (column 5)
            exact_synonyms = row[5].strip() if len(row) > 5 else ""

            # Get BactoTraits synonym (column 9)
            bactotraits_synonym = row[9].strip() if len(row) > 9 else ""

            # Get range data
            units = row[10].strip() if len(row) > 10 else ""
            range_min = row[11].strip() if len(row) > 11 else ""
            range_max = row[12].strip() if len(row) > 12 else ""

            # Integrate range information into description
            enhanced_description = integrate_range_into_description(description, range_min, range_max, units)

            # Build output row matching minimal_classes format exactly
            output_row = [
                curie_id,                                           # ID
                unique_label,                                       # label
                "owl:Class",                                        # TYPE
                parent_classes,                                     # parent class
                "owl:Class",                                        # TYPE
                enhanced_description,                               # description
                "",                                                 # definition source
                "",                                                 # comment
                "",                                                 # biolink equivalent
                exact_synonyms,                                     # confirmed exact synonym
                "",                                                 # literature mining synonyms
                "",                                                 # madin synonym or field
                "",                                                 # synonym source
                "",                                                 # bacdive keyword synonym
                "",                                                 # synonym source
                bactotraits_synonym,                                # bactotraits synonym
                "https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv" if bactotraits_synonym else ""  # synonym source
            ]

            migrated_rows.append(output_row)

    # Write output file
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(output_header)
        writer.writerow(robot_row)
        writer.writerows(migrated_rows)

    print(f"Migration file created: {output_file}")
    print(f"Processed {len(migrated_rows)} BactoTraits entities")
    print(f"Resolved {len([r for r in migrated_rows if '(' in r[1]])} label conflicts")

if __name__ == "__main__":
    main()
