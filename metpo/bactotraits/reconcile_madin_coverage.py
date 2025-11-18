"""
Reconcile Madin MongoDB field values against METPO synonyms attributed to Madin source.

This script:
1. Connects to MongoDB and extracts unique values from a specified Madin field
2. Reads the SPARQL synonym-sources.tsv report
3. Filters for synonyms attributed to https://github.com/jmadin/bacteria_archaea_traits
4. Reports which Madin values are covered/missing in METPO
"""

import csv
import re
import sys
from pathlib import Path

import click
import yaml
from pymongo import MongoClient

MADIN_SOURCE_URI = "https://github.com/jmadin/bacteria_archaea_traits"

# Entity type mappings to OWL CURIEs
ENTITY_TYPE_MAP = {
    "class": "owl:Class",
    "property": "owl:ObjectProperty"  # Default for properties
}

def get_entity_curie(entity_uri: str) -> str:
    """
    Convert entity URI to CURIE format.

    :param entity_uri: Full URI like 'https://w3id.org/metpo/1000602'
    :return: CURIE like 'METPO:1000602'
    """
    if entity_uri.startswith("https://w3id.org/metpo/"):
        return "METPO:" + entity_uri.split("/")[-1]
    return entity_uri


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace: trim left/right and collapse internal whitespace.

    :param text: Input text
    :return: Normalized text
    """
    return re.sub(r"\s+", " ", text.strip())


def get_madin_field_values(field_path: str, db_name: str = "madin", collection_name: str = "madin") -> dict[str, str]:
    """
    Extract unique values from a Madin MongoDB field.

    :param field_path: MongoDB field path (e.g., 'gram_stain', 'metabolism')
    :param db_name: MongoDB database name
    :param collection_name: MongoDB collection name
    :return: Dict mapping normalized values to original values (to track if normalization occurred)
    """
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    values = collection.distinct(field_path)

    value_map = {}
    for v in values:
        if v and v != "NA":
            normalized = normalize_whitespace(v)
            value_map[normalized] = v

    return value_map


def load_madin_synonyms(tsv_path: str) -> dict[str, dict[str, str]]:
    """
    Load synonyms attributed to Madin source from synonym-sources.tsv.

    :param tsv_path: Path to reports/synonym-sources.tsv
    :return: Dictionary mapping normalized synonym values to their METPO entity and predicate info
    """
    madin_synonyms = {}
    entity_labels = {}

    with Path(tsv_path).open() as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            entity = row.get("?entity", "").strip("<>")
            entity_type = row.get("?entityType", "").strip('"')
            pred = row.get("?synonymPred", "").strip("<>")
            syn_value = row.get("?synValue", "").strip('"')
            src = row.get("?src", "").strip("<>")

            if entity and pred and syn_value:
                if pred == "http://www.w3.org/2000/01/rdf-schema#label":
                    entity_labels[entity] = syn_value

                if src == MADIN_SOURCE_URI:
                    normalized_syn = normalize_whitespace(syn_value)
                    if normalized_syn not in madin_synonyms:
                        madin_synonyms[normalized_syn] = {
                            "entity": entity,
                            "entity_type": entity_type,
                            "predicate": pred,
                            "source": src,
                            "label": None
                        }

    for syn_value, info in madin_synonyms.items():
        entity = info["entity"]
        if entity in entity_labels:
            info["label"] = entity_labels[entity]

    return madin_synonyms


def get_all_madin_fields(db_name: str = "madin", collection_name: str = "madin") -> list[str]:
    """
    Get all field names from the Madin MongoDB collection.

    :param db_name: MongoDB database name
    :param collection_name: MongoDB collection name
    :return: List of all field names
    """
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    sample_doc = collection.find_one()

    if sample_doc:
        return [key for key in sample_doc if key != "_id"]
    return []


def get_all_madin_values_with_fields(db_name: str = "madin", collection_name: str = "madin") -> dict[str, list[str]]:
    """
    Get ALL unique values from ALL fields in the Madin MongoDB collection.

    :param db_name: MongoDB database name
    :param collection_name: MongoDB collection name
    :return: Dict mapping normalized values to list of field names where they appear
    """
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    value_to_fields = {}
    fields = get_all_madin_fields(db_name, collection_name)

    for field in fields:
        values = collection.distinct(field)
        for v in values:
            if v and v != "NA":
                normalized = normalize_whitespace(str(v))
                if normalized not in value_to_fields:
                    value_to_fields[normalized] = []
                value_to_fields[normalized].append(field)

    return value_to_fields


def reconcile_all_field_names(tsv_path: str, output_format: str = "text", output_file: str | None = None) -> None:
    """
    Check if ALL Madin field names are synonyms in METPO.

    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    """
    madin_fields = get_all_madin_fields()
    madin_synonyms = load_madin_synonyms(tsv_path)

    # Get value counts for each field
    client = MongoClient()
    db = client["madin"]
    collection = db["madin"]

    field_value_counts = {}
    for field in madin_fields:
        values = collection.distinct(field)
        non_na_count = sum(1 for v in values if v and v != "NA")
        field_value_counts[field] = non_na_count

    covered_entries = []
    missing_entries = []

    for field_path in sorted(madin_fields):
        field_name = normalize_whitespace(field_path.replace("_", " "))
        field_path_normalized = normalize_whitespace(field_path)
        value_count = field_value_counts[field_path]

        if field_path_normalized in madin_synonyms or field_name in madin_synonyms:
            if field_path_normalized in madin_synonyms:
                info = madin_synonyms[field_path_normalized]
            else:
                info = madin_synonyms[field_name]

            metpo_curie = get_entity_curie(info["entity"])
            label = info.get("label", "")
            entity_type_raw = info.get("entity_type", "unknown")
            entity_type = ENTITY_TYPE_MAP.get(entity_type_raw, entity_type_raw)

            covered_entries.append({
                "field": field_path,
                "metpo_id": metpo_curie,
                "label": label,
                "entity_type": entity_type,
                "unique_values": value_count
            })
        else:
            missing_entries.append({
                "field": field_path,
                "unique_values": value_count
            })

    # Sort missing entries by value count (descending) to highlight high-value missing fields
    missing_entries.sort(key=lambda x: x["unique_values"], reverse=True)

    total = len(madin_fields)
    covered_count = len(covered_entries)
    missing_count = len(missing_entries)
    coverage_pct = 100 * covered_count / total if total > 0 else 0

    if output_format == "yaml":
        # Create separate copies for high_value_missing_fields to avoid YAML anchors/aliases
        # High-value = fields with small controlled vocabularies (2-20 values) that could be ontology classes
        high_value_missing = [
            {"field": e["field"], "unique_values": e["unique_values"]}
            for e in missing_entries if 2 <= e["unique_values"] <= 20
        ]

        result = {
            "field_name_reconciliation": {
                "summary": {
                    "total_fields": total,
                    "covered": covered_count,
                    "missing": missing_count,
                    "coverage_percentage": round(coverage_pct, 1)
                },
                "covered_fields": covered_entries,
                "missing_fields": missing_entries,
                "high_value_missing_fields": high_value_missing
            }
        }
        print(yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True))
    else:
        print(f"\n{'='*80}")
        print("Checking ALL Madin field names against METPO synonyms")
        print(f"{'='*80}\n")
        print(f"Total Madin fields: {total}\n")
        print(f"COVERED ({covered_count}/{total} = {coverage_pct:.1f}%):")
        print("-" * 80)
        for entry in covered_entries:
            if entry["label"]:
                print(f"  ✓ '{entry['field']}' → {entry['metpo_id']} ({entry['label']}) [{entry['unique_values']} unique values]")
            else:
                print(f"  ✓ '{entry['field']}' → {entry['metpo_id']} [{entry['unique_values']} unique values]")

        if missing_entries:
            print(f"\nMISSING ({missing_count}/{total} = {100*missing_count/total:.1f}%):")
            print("-" * 80)
            for entry in missing_entries:
                print(f"  ✗ '{entry['field']}' [{entry['unique_values']} unique values]")

            # High-value = small controlled vocabularies (2-20 values) that could be ontology classes
            high_value_missing = [e for e in missing_entries if 2 <= e["unique_values"] <= 20]
            if high_value_missing:
                print(f"\nHIGH-VALUE MISSING FIELDS ({len(high_value_missing)} fields with 2-20 unique values - good ontology class candidates):")
                print("-" * 80)
                for entry in high_value_missing:
                    print(f"  ⚠ '{entry['field']}' [{entry['unique_values']} unique values]")

        print(f"\n{'='*80}\n")


def reconcile_coverage(field_path: str, tsv_path: str, output_format: str = "text", output_file: str | None = None) -> None:
    """
    Reconcile Madin field values against METPO synonyms.

    :param field_path: MongoDB field path to check
    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    """
    madin_value_map = get_madin_field_values(field_path)
    madin_synonyms = load_madin_synonyms(tsv_path)

    covered_entries = []
    missing_entries = []

    for normalized_value in sorted(madin_value_map.keys()):
        original_value = madin_value_map[normalized_value]
        was_normalized = (normalized_value != original_value)

        if normalized_value in madin_synonyms:
            info = madin_synonyms[normalized_value]
            metpo_curie = get_entity_curie(info["entity"])
            label = info.get("label", "")
            entity_type_raw = info.get("entity_type", "unknown")
            entity_type = ENTITY_TYPE_MAP.get(entity_type_raw, entity_type_raw)

            covered_entries.append({
                "value": normalized_value,
                "original_value": original_value if was_normalized else None,
                "metpo_id": metpo_curie,
                "label": label,
                "entity_type": entity_type
            })
        else:
            missing_entries.append({
                "value": normalized_value,
                "original_value": original_value if was_normalized else None
            })

    total = len(madin_value_map)
    covered_count = len(covered_entries)
    missing_count = len(missing_entries)
    coverage_pct = 100 * covered_count / total if total > 0 else 0

    if output_format == "yaml":
        result = {
            "field_value_reconciliation": {
                "field": field_path,
                "summary": {
                    "total_values": total,
                    "covered": covered_count,
                    "missing": missing_count,
                    "coverage_percentage": round(coverage_pct, 1)
                },
                "covered_values": covered_entries,
                "missing_values": missing_entries
            }
        }
        print(yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True))
    else:
        print(f"\n{'='*80}")
        print(f"Reconciling Madin field: {field_path}")
        print(f"{'='*80}\n")
        print(f"MongoDB values found: {total} (excluding 'NA')")
        print(f"Madin synonyms in METPO: {len(madin_synonyms)}\n")
        print(f"COVERED ({covered_count}/{total} = {coverage_pct:.1f}%):")
        print("-" * 80)
        for entry in covered_entries:
            normalization_note = f" [NORMALIZED from '{entry['original_value']}']" if entry["original_value"] else ""
            if entry["label"]:
                print(f"  ✓ '{entry['value']}' → {entry['metpo_id']} ({entry['label']}){normalization_note}")
            else:
                print(f"  ✓ '{entry['value']}' → {entry['metpo_id']}{normalization_note}")

        if missing_entries:
            print(f"\nMISSING ({missing_count}/{total} = {100*missing_count/total:.1f}%):")
            print("-" * 80)
            for entry in missing_entries:
                normalization_note = f" [NORMALIZED from '{entry['original_value']}']" if entry["original_value"] else ""
                print(f"  ✗ '{entry['value']}'{normalization_note}")

        print(f"\n{'='*80}\n")


def verify_madin_synonyms(tsv_path: str, output_format: str = "text", output_file: str | None = None) -> None:
    """
    Verify that all METPO synonyms attributed to Madin actually exist in the Madin MongoDB.

    This checks the reverse direction: do the synonyms claimed in METPO actually appear
    in the source data?

    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    """
    value_to_fields = get_all_madin_values_with_fields()
    madin_synonyms = load_madin_synonyms(tsv_path)

    verified_entries = []
    unverified_entries = []

    for syn_value, info in madin_synonyms.items():
        metpo_curie = get_entity_curie(info["entity"])
        entity_type_raw = info.get("entity_type", "unknown")
        entity_type = ENTITY_TYPE_MAP.get(entity_type_raw, entity_type_raw)
        label = info.get("label", "")

        if syn_value in value_to_fields:
            fields = value_to_fields[syn_value]
            verified_entries.append({
                "synonym": syn_value,
                "metpo_id": metpo_curie,
                "entity_type": entity_type,
                "label": label,
                "found_in_fields": fields,
                "field_count": len(fields)
            })
        else:
            unverified_entries.append({
                "synonym": syn_value,
                "metpo_id": metpo_curie,
                "entity_type": entity_type,
                "label": label
            })

    total_madin_values = len(value_to_fields)
    total_synonyms = len(madin_synonyms)
    verified_count = len(verified_entries)
    unverified_count = len(unverified_entries)
    verification_pct = 100 * verified_count / total_synonyms if total_synonyms > 0 else 0

    if output_format == "yaml":
        result = {
            "synonym_verification": {
                "summary": {
                    "total_madin_values": total_madin_values,
                    "total_metpo_madin_synonyms": total_synonyms,
                    "verified": verified_count,
                    "unverified": unverified_count,
                    "verification_percentage": round(verification_pct, 1)
                },
                "verified_synonyms": verified_entries,
                "unverified_synonyms": unverified_entries,
                "false_synonym_claims": unverified_entries  # Highlight false claims
            }
        }
        print(yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True))
    else:
        print(f"\n{'='*80}")
        print("Verifying METPO Madin synonyms against actual Madin data")
        print(f"{'='*80}\n")
        print("Loading all Madin values from MongoDB...")
        print(f"Total unique Madin values found: {total_madin_values}\n")
        print("Loading METPO synonyms attributed to Madin...")
        print(f"Total METPO synonyms attributed to Madin: {total_synonyms}\n")
        print(f"VERIFIED ({verified_count}/{total_synonyms} = {verification_pct:.1f}%):")
        print("-" * 80)
        for entry in sorted(verified_entries, key=lambda x: x["synonym"]):
            fields_str = ", ".join(entry["found_in_fields"]) if entry["field_count"] <= 3 else f"{', '.join(entry['found_in_fields'][:3])}, ..."
            if entry["label"]:
                print(f"  ✓ '{entry['synonym']}' ({entry['metpo_id']} [{entry['entity_type']}] - {entry['label']}) in {entry['field_count']} field(s): [{fields_str}]")
            else:
                print(f"  ✓ '{entry['synonym']}' ({entry['metpo_id']} [{entry['entity_type']}]) in {entry['field_count']} field(s): [{fields_str}]")

        if unverified_entries:
            print(f"\nUNVERIFIED ({unverified_count}/{total_synonyms} = {100*unverified_count/total_synonyms:.1f}%):")
            print("-" * 80)
            print("These synonyms are attributed to Madin in METPO but NOT found in Madin field VALUES:")
            print("⚠ FALSE SYNONYM CLAIMS - METPO incorrectly attributes these to Madin source")
            print()
            for entry in sorted(unverified_entries, key=lambda x: x["synonym"]):
                if entry["label"]:
                    print(f"  ✗ '{entry['synonym']}' ({entry['metpo_id']} [{entry['entity_type']}] - {entry['label']})")
                else:
                    print(f"  ✗ '{entry['synonym']}' ({entry['metpo_id']} [{entry['entity_type']}])")

        print(f"\n{'='*80}\n")


def generate_integrated_report(tsv_path: str, output_format: str = "yaml", output_file: str | None = None) -> None:
    """
    Generate integrated reconciliation report combining field mappings, value coverage, and false claims.

    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    :param output_file: Output file path (None = stdout)
    """
    madin_synonyms = load_madin_synonyms(tsv_path)
    value_to_fields = get_all_madin_values_with_fields()
    madin_fields = get_all_madin_fields()

    client = MongoClient()
    db = client["madin"]
    collection = db["madin"]

    # Build integrated field analysis
    field_analysis = []

    for field_name in sorted(madin_fields):
        field_values = collection.distinct(field_name)
        non_na_values = [v for v in field_values if v and v != "NA"]
        total_values = len(non_na_values)

        # Check if field name itself is mapped
        field_name_normalized = normalize_whitespace(field_name)
        field_name_alt = normalize_whitespace(field_name.replace("_", " "))

        field_mapped = False
        field_metpo_id = None
        field_metpo_label = None
        field_entity_type = None

        if field_name_normalized in madin_synonyms or field_name_alt in madin_synonyms:
            field_mapped = True
            info = madin_synonyms.get(field_name_normalized) or madin_synonyms.get(field_name_alt)
            field_metpo_id = get_entity_curie(info["entity"])
            field_metpo_label = info.get("label", "")
            field_entity_type = ENTITY_TYPE_MAP.get(info.get("entity_type", "unknown"), "unknown")

        # Check value coverage
        # Special handling for pathways field which contains comma-separated lists
        if field_name == "pathways":
            # For pathways, we need to extract individual pathway values
            all_pathway_values = set()
            for v in non_na_values:
                # Split on comma and normalize each pathway
                pathways_in_value = [normalize_whitespace(p.strip()) for p in str(v).split(",")]
                all_pathway_values.update(pathways_in_value)

            # Check coverage for individual pathways
            covered_pathways = []
            missing_pathways = []

            for pathway in sorted(all_pathway_values):
                if pathway in madin_synonyms:
                    info = madin_synonyms[pathway]
                    covered_pathways.append({
                        "value": pathway,
                        "metpo_id": get_entity_curie(info["entity"]),
                        "label": info.get("label", ""),
                        "entity_type": ENTITY_TYPE_MAP.get(info.get("entity_type", "unknown"), "unknown")
                    })
                else:
                    missing_pathways.append(pathway)

            covered_values = covered_pathways
            missing_values = missing_pathways
            total_values = len(all_pathway_values)
            value_coverage_pct = 100 * len(covered_pathways) / total_values if total_values > 0 else 0
        else:
            # Normal handling for other fields
            covered_values = []
            missing_values = []

            for v in non_na_values:
                normalized_v = normalize_whitespace(str(v))
                if normalized_v in madin_synonyms:
                    info = madin_synonyms[normalized_v]
                    covered_values.append({
                        "value": v,
                        "metpo_id": get_entity_curie(info["entity"]),
                        "label": info.get("label", ""),
                        "entity_type": ENTITY_TYPE_MAP.get(info.get("entity_type", "unknown"), "unknown")
                    })
                else:
                    missing_values.append(v)

            value_coverage_pct = 100 * len(covered_values) / total_values if total_values > 0 else 0

        if field_mapped:
            # For mapped fields, show full details
            field_entry = {
                "field": field_name,
                "field_mapped": True,
                "field_metpo_id": field_metpo_id,
                "field_metpo_label": field_metpo_label,
                "field_entity_type": field_entity_type,
                "total_values": total_values,
                "covered_values_count": len(covered_values),
                "missing_values_count": len(missing_values),
                "value_coverage_percentage": round(value_coverage_pct, 1),
                "covered_values": covered_values if len(covered_values) <= 20 else covered_values[:20],
                "missing_values": missing_values if len(missing_values) <= 20 else missing_values[:20],
                "values_truncated": len(covered_values) > 20 or len(missing_values) > 20
            }
        else:
            # For unmapped fields, just show field name and unique value count
            field_entry = {
                "field": field_name,
                "field_mapped": False,
                "unique_values": total_values
            }

        field_analysis.append(field_entry)

    # Identify false claims (METPO synonyms not in Madin data)
    # Build set of normalized field names to exclude from false claims
    normalized_field_names = set()
    for field_name in madin_fields:
        normalized_field_names.add(normalize_whitespace(field_name))
        normalized_field_names.add(normalize_whitespace(field_name.replace("_", " ")))

    false_claims = []
    verified_synonyms = []

    for syn_value, info in madin_synonyms.items():
        metpo_curie = get_entity_curie(info["entity"])
        entity_type = ENTITY_TYPE_MAP.get(info.get("entity_type", "unknown"), "unknown")
        label = info.get("label", "")

        # If synonym not found in field values AND not a field name itself, it's a false claim
        if syn_value not in value_to_fields:
            if syn_value not in normalized_field_names:
                false_claims.append({
                    "synonym": syn_value,
                    "metpo_id": metpo_curie,
                    "entity_type": entity_type,
                    "label": label
                })
        else:
            verified_synonyms.append({
                "synonym": syn_value,
                "metpo_id": metpo_curie,
                "entity_type": entity_type,
                "label": label,
                "found_in_fields": value_to_fields[syn_value]
            })

    # Generate output
    if output_format == "yaml":
        result = {
            "madin_metpo_reconciliation": {
                "summary": {
                    "total_fields": len(madin_fields),
                    "fields_with_name_mapping": sum(1 for f in field_analysis if f["field_mapped"]),
                    "fields_with_full_value_coverage": sum(1 for f in field_analysis if f.get("value_coverage_percentage") == 100),
                    "total_metpo_madin_synonyms": len(madin_synonyms),
                    "verified_synonyms": len(verified_synonyms),
                    "false_synonym_claims": len(false_claims)
                },
                "fields": field_analysis,
                "high_value_unmapped_fields": [
                    {"field": f["field"], "unique_values": f["unique_values"]}
                    for f in field_analysis
                    if not f["field_mapped"] and 2 <= f["unique_values"] <= 20
                ],
                "false_synonym_claims": false_claims
            }
        }
        output_content = yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)

        if output_file:
            with Path(output_file).open( "w") as f:
                f.write(output_content)
            print(f"Report written to {output_file}")
        else:
            print(output_content)
    else:
        print(f"\n{'='*80}")
        print("Integrated Madin-METPO Reconciliation Report")
        print(f"{'='*80}\n")

        total_fields = len(madin_fields)
        fields_mapped = sum(1 for f in field_analysis if f["field_mapped"])
        fields_full_coverage = sum(1 for f in field_analysis if f.get("value_coverage_percentage") == 100)

        print("SUMMARY:")
        print(f"  Total Madin fields: {total_fields}")
        print(f"  Fields with name mapping: {fields_mapped} ({100*fields_mapped/total_fields:.1f}%)")
        print(f"  Fields with 100% value coverage: {fields_full_coverage} ({100*fields_full_coverage/total_fields:.1f}%)")
        print(f"  Total METPO Madin synonyms: {len(madin_synonyms)}")
        print(f"  Verified synonyms: {len(verified_synonyms)} ({100*len(verified_synonyms)/len(madin_synonyms):.1f}%)")
        print(f"  False synonym claims: {len(false_claims)} ({100*len(false_claims)/len(madin_synonyms):.1f}%)\n")

        print("FIELD ANALYSIS:")
        print("-" * 80)
        for field in field_analysis:
            status = "✓ MAPPED" if field["field_mapped"] else "✗ UNMAPPED"
            print(f"\n{status}: {field['field']}")

            if field["field_mapped"]:
                coverage = f"{field['value_coverage_percentage']:.1f}%"
                print(f"  → {field['field_metpo_id']} ({field['field_metpo_label']}) [{field['field_entity_type']}]")
                print(f"  Values: {field['covered_values_count']}/{field['total_values']} covered ({coverage})")

                if field["covered_values"] and len(field["covered_values"]) <= 10:
                    print("  Covered values:")
                    for val in field["covered_values"][:5]:
                        print(f"    • {val['value']} → {val['metpo_id']}")

                if field["missing_values"] and len(field["missing_values"]) <= 10:
                    print(f"  Missing values: {', '.join(str(v) for v in field['missing_values'][:5])}")
            else:
                print(f"  Unique values: {field['unique_values']}")

        if false_claims:
            print(f"\n\nFALSE SYNONYM CLAIMS ({len(false_claims)}):")
            print("-" * 80)
            for claim in false_claims:
                print(f"  ✗ '{claim['synonym']}' ({claim['metpo_id']} [{claim['entity_type']}] - {claim['label']})")

        print(f"\n{'='*80}\n")


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["values", "field_names", "verify_synonyms", "integrated"], case_sensitive=False),
    default="values",
    help="Reconciliation mode: 'values' checks field values, 'field_names' checks ALL field names, 'verify_synonyms' verifies METPO synonyms exist in Madin data, 'integrated' shows comprehensive analysis"
)
@click.option(
    "--field",
    type=str,
    help="MongoDB field path to reconcile (e.g., 'gram_stain', 'metabolism'). Required for 'values' mode."
)
@click.option(
    "--tsv",
    type=click.Path(exists=True),
    default="reports/synonym-sources.tsv",
    help="Path to synonym-sources.tsv report"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "yaml"], case_sensitive=False),
    default="text",
    help="Output format: 'text' for console output, 'yaml' for structured YAML"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout."
)
def main(mode, field, tsv, output_format, output):
    """Reconcile Madin MongoDB field values against METPO synonyms."""
    try:
        if mode == "field_names":
            reconcile_all_field_names(tsv, output_format, output)
        elif mode == "verify_synonyms":
            verify_madin_synonyms(tsv, output_format, output)
        elif mode == "integrated":
            generate_integrated_report(tsv, output_format, output)
        else:  # values mode
            if not field:
                raise click.UsageError("--field is required for 'values' mode")
            reconcile_coverage(field, tsv, output_format, output)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
