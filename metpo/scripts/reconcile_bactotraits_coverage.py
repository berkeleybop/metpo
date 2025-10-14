#!/usr/bin/env python3
"""
Reconcile BactoTraits MongoDB field values against METPO synonyms attributed to BactoTraits source.

This script:
1. Connects to MongoDB and extracts unique values from specified BactoTraits fields
2. Reads the SPARQL synonym-sources.tsv report
3. Filters for synonyms attributed to BactoTraits (ORDaR repository)
4. Reports which BactoTraits values are covered/missing in METPO

BactoTraits specifics:
- Uses different field naming conventions than Madin (e.g., pHO_0_to_6, GC_<=42_65)
- Underscores are used in field names, BUT they were converted from periods for MongoDB compatibility
- Original BactoTraits used periods in bin names (e.g., GC_<=42.65)
- We need to handle both underscore and period variations when matching
"""

import click
import csv
import re
import sys
import yaml
from typing import Dict, List, Set

from pymongo import MongoClient


BACTOTRAITS_SOURCE_URI = "https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/BactoTraits_databaseV2_Jun2022.csv"

# Entity type mappings to OWL CURIEs
ENTITY_TYPE_MAP = {
    'class': 'owl:Class',
    'property': 'owl:ObjectProperty'  # Default for properties
}

def get_entity_curie(entity_uri: str) -> str:
    """
    Convert entity URI to CURIE format.

    :param entity_uri: Full URI like 'https://w3id.org/metpo/1000602'
    :return: CURIE like 'METPO:1000602'
    """
    if entity_uri.startswith('https://w3id.org/metpo/'):
        return 'METPO:' + entity_uri.split('/')[-1]
    return entity_uri


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace: trim left/right and collapse internal whitespace.

    :param text: Input text
    :return: Normalized text
    """
    return re.sub(r'\s+', ' ', text.strip())


def normalize_punctuation_variants(text: str) -> List[str]:
    """
    Generate punctuation variants for BactoTraits field names.

    BactoTraits originally used periods in field names (e.g., GC_<=42.65)
    but these were converted to underscores for MongoDB compatibility (GC_<=42_65).

    This function generates both variants to match against METPO synonyms.

    :param text: Input text (e.g., "GC_<=42_65" or "GC_<=42.65")
    :return: List of variants including original and period/underscore swaps
    """
    variants = [text]

    # Convert underscores to periods in numeric contexts
    # Pattern: digit_digit -> digit.digit
    period_variant = re.sub(r'(\d)_(\d)', r'\1.\2', text)
    if period_variant != text:
        variants.append(period_variant)

    # Convert periods to underscores in numeric contexts
    # Pattern: digit.digit -> digit_digit
    underscore_variant = re.sub(r'(\d)\.(\d)', r'\1_\2', text)
    if underscore_variant != text:
        variants.append(underscore_variant)

    return list(set(variants))  # Remove duplicates


def get_bactotraits_field_values(field_path: str, db_name: str = "bactotraits", collection_name: str = "bactotraits") -> Dict[str, str]:
    """
    Extract unique values from a BactoTraits MongoDB field.

    :param field_path: MongoDB field path (e.g., 'Ox_anaerobic', 'G_negative')
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
        # BactoTraits uses 0/1 for binary traits, NA for missing, and actual values for categories
        # Filter out: 0 (false values), empty strings, and 'NA'
        if v and v != "NA" and v != "" and v != 0 and v != "0":
            normalized = normalize_whitespace(str(v))
            value_map[normalized] = v

    return value_map


def load_bactotraits_synonyms(tsv_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load synonyms attributed to BactoTraits source from synonym-sources.tsv.

    :param tsv_path: Path to reports/synonym-sources.tsv
    :return: Dictionary mapping normalized synonym values to their METPO entity and predicate info
    """
    bactotraits_synonyms = {}
    entity_labels = {}

    with open(tsv_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            entity = row.get('?entity', '').strip('<>')
            entity_type = row.get('?entityType', '').strip('"')
            pred = row.get('?synonymPred', '').strip('<>')
            syn_value = row.get('?synValue', '').strip('"')
            src = row.get('?src', '').strip('<>')

            if entity and pred and syn_value:
                if pred == 'http://www.w3.org/2000/01/rdf-schema#label':
                    entity_labels[entity] = syn_value

                if src == BACTOTRAITS_SOURCE_URI:
                    normalized_syn = normalize_whitespace(syn_value)
                    # Generate punctuation variants for this synonym
                    variants = normalize_punctuation_variants(normalized_syn)

                    for variant in variants:
                        if variant not in bactotraits_synonyms:
                            bactotraits_synonyms[variant] = {
                                'entity': entity,
                                'entity_type': entity_type,
                                'predicate': pred,
                                'source': src,
                                'label': None,
                                'original_synonym': normalized_syn  # Track original form
                            }

    for syn_value, info in bactotraits_synonyms.items():
        entity = info['entity']
        if entity in entity_labels:
            info['label'] = entity_labels[entity]

    return bactotraits_synonyms


def load_all_metpo_synonyms(tsv_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load ALL synonyms from METPO regardless of source attribution.

    :param tsv_path: Path to reports/synonym-sources.tsv
    :return: Dictionary mapping normalized synonym values to their METPO entity and predicate info
    """
    all_synonyms = {}
    entity_labels = {}

    with open(tsv_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            entity = row.get('?entity', '').strip('<>')
            entity_type = row.get('?entityType', '').strip('"')
            pred = row.get('?synonymPred', '').strip('<>')
            syn_value = row.get('?synValue', '').strip('"')
            src = row.get('?src', '').strip('<>')

            if entity and pred and syn_value:
                if pred == 'http://www.w3.org/2000/01/rdf-schema#label':
                    entity_labels[entity] = syn_value

                normalized_syn = normalize_whitespace(syn_value)
                # Generate punctuation variants for this synonym
                variants = normalize_punctuation_variants(normalized_syn)

                for variant in variants:
                    if variant not in all_synonyms:
                        all_synonyms[variant] = {
                            'entity': entity,
                            'entity_type': entity_type,
                            'predicate': pred,
                            'source': src,
                            'label': None,
                            'original_synonym': normalized_syn
                        }

    for syn_value, info in all_synonyms.items():
        entity = info['entity']
        if entity in entity_labels:
            info['label'] = entity_labels[entity]

    return all_synonyms


def get_all_bactotraits_fields(db_name: str = "bactotraits", collection_name: str = "bactotraits") -> List[str]:
    """
    Get all field names from the BactoTraits MongoDB collection.

    :param db_name: MongoDB database name
    :param collection_name: MongoDB collection name
    :return: List of all field names
    """
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    sample_doc = collection.find_one()

    if sample_doc:
        return [key for key in sample_doc.keys() if key != '_id']
    return []


def get_all_bactotraits_values_with_fields(db_name: str = "bactotraits", collection_name: str = "bactotraits") -> Dict[str, List[str]]:
    """
    Get ALL unique values from ALL fields in the BactoTraits MongoDB collection.

    :param db_name: MongoDB database name
    :param collection_name: MongoDB collection name
    :return: Dict mapping normalized values to list of field names where they appear
    """
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    value_to_fields = {}
    fields = get_all_bactotraits_fields(db_name, collection_name)

    for field in fields:
        values = collection.distinct(field)
        for v in values:
            # Filter out binary 0/1 values, empty strings, and 'NA'
            if v and v != "NA" and v != "" and v != 0 and v != "0" and v != 1 and v != "1":
                normalized = normalize_whitespace(str(v))
                if normalized not in value_to_fields:
                    value_to_fields[normalized] = []
                value_to_fields[normalized].append(field)

    return value_to_fields


def reconcile_all_field_names(tsv_path: str, output_format: str = "text", output_file: str = None) -> None:
    """
    Check if ALL BactoTraits field names are synonyms in METPO.

    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    """
    # Taxonomic and identifier fields that should be excluded from trait reconciliation
    TAXONOMIC_ID_FIELDS = {
        'Bacdive_ID', 'culture collection codes', 'Full_name', 'ncbitaxon_id',
        'Species', 'Genus', 'Family', 'Order', 'Class', 'Phylum', 'Kingdom'
    }

    bactotraits_fields = get_all_bactotraits_fields()
    bactotraits_synonyms = load_bactotraits_synonyms(tsv_path)
    all_metpo_synonyms = load_all_metpo_synonyms(tsv_path)

    # Get value counts for each field
    client = MongoClient()
    db = client["bactotraits"]
    collection = db["bactotraits"]

    field_value_counts = {}
    field_value_distributions = {}
    for field in bactotraits_fields:
        # Count non-NA, non-empty, non-0 values for the summary stats
        values = collection.distinct(field)
        non_na_count = sum(1 for v in values if v and v != "NA" and v != "" and v != 0 and v != "0")
        field_value_counts[field] = non_na_count

        # Only get value distribution for fields with reasonable cardinality (1-20 unique non-empty values)
        # This excludes taxonomic/ID fields with thousands of unique values
        if 1 <= non_na_count <= 20:
            pipeline = [
                {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            distribution = list(collection.aggregate(pipeline))

            # Store distribution with ALL values (including empty, NA, 0) converted to strings
            field_value_distributions[field] = [
                {"value": str(d["_id"]) if d["_id"] is not None else "null", "count": d["count"]}
                for d in distribution
            ]

    covered_entries = []
    missing_entries = []

    for field_path in sorted(bactotraits_fields):
        # Strip leading whitespace from field name
        field_path_clean = field_path.strip()

        # Generate variants for field name matching
        field_variants = normalize_punctuation_variants(field_path_clean)
        # Also try space-separated variant
        field_name_spaced = normalize_whitespace(field_path_clean.replace('_', ' '))
        field_variants.extend(normalize_punctuation_variants(field_name_spaced))

        # For one-hot encoded fields, also check the VALUE part after splitting on underscore
        # E.g., "TT_heterotroph" -> check "heterotroph", "Pigment_yellow" -> check "yellow"
        if '_' in field_path_clean:
            parts = field_path_clean.split('_', 1)  # Split on first underscore only
            if len(parts) == 2:
                prefix = parts[0]
                value_part = parts[1]
                field_variants.extend(normalize_punctuation_variants(value_part))
                # Also try with spaces instead of underscores in multi-word values
                value_part_spaced = value_part.replace('_', ' ')
                field_variants.extend(normalize_punctuation_variants(value_part_spaced))

                # For shape fields (S_ prefix), also try with "-shaped" and " shaped" suffixes
                # E.g., "S_rod" -> check "rod", "rod-shaped", "rod shaped"
                if prefix == 'S':
                    field_variants.append(value_part + '-shaped')
                    field_variants.append(value_part + ' shaped')
                    field_variants.append(value_part_spaced + '-shaped')
                    field_variants.append(value_part_spaced + ' shaped')

        value_count = field_value_counts[field_path]

        matched = False
        matched_info = None
        matched_variant = None
        matched_source = None

        # First check BactoTraits-attributed synonyms
        for variant in field_variants:
            if variant in bactotraits_synonyms:
                matched = True
                matched_info = bactotraits_synonyms[variant]
                matched_variant = variant
                matched_source = "bactotraits"
                break

        # If not found in BactoTraits synonyms, check ALL METPO synonyms
        if not matched:
            for variant in field_variants:
                if variant in all_metpo_synonyms:
                    matched = True
                    matched_info = all_metpo_synonyms[variant]
                    matched_variant = variant
                    matched_source = matched_info.get('source', 'unknown')
                    break

        if matched:
            metpo_curie = get_entity_curie(matched_info['entity'])
            label = matched_info.get('label', '')
            entity_type_raw = matched_info.get('entity_type', 'unknown')
            entity_type = ENTITY_TYPE_MAP.get(entity_type_raw, entity_type_raw)

            entry = {
                'field': field_path,
                'matched_as': matched_variant if matched_variant != field_path_clean else None,
                'metpo_id': metpo_curie,
                'label': label,
                'entity_type': entity_type,
                'unique_values': value_count,
                'matched_from_source': matched_source if matched_source != "bactotraits" else None
            }
            # Add value distribution if available
            if field_path in field_value_distributions:
                entry['value_distribution'] = field_value_distributions[field_path]
            covered_entries.append(entry)
        else:
            entry = {
                'field': field_path,
                'unique_values': value_count
            }
            # Add value distribution if available
            if field_path in field_value_distributions:
                entry['value_distribution'] = field_value_distributions[field_path]
            missing_entries.append(entry)

    # Sort missing entries by value count (descending) to highlight high-value missing fields
    missing_entries.sort(key=lambda x: x['unique_values'], reverse=True)

    # Separate taxonomic/ID fields from trait fields
    missing_taxonomic = [e for e in missing_entries if e['field'] in TAXONOMIC_ID_FIELDS]
    missing_traits = [e for e in missing_entries if e['field'] not in TAXONOMIC_ID_FIELDS]

    total = len(bactotraits_fields)
    total_traits = total - len(TAXONOMIC_ID_FIELDS)
    covered_count = len(covered_entries)
    missing_count = len(missing_entries)
    missing_traits_count = len(missing_traits)
    coverage_pct = 100 * covered_count / total if total > 0 else 0
    traits_coverage_pct = 100 * covered_count / total_traits if total_traits > 0 else 0

    if output_format == "yaml":
        # High-value = fields with small controlled vocabularies (2-20 values) that could be ontology classes
        high_value_missing = [
            {'field': e['field'], 'unique_values': e['unique_values']}
            for e in missing_entries if 2 <= e['unique_values'] <= 20
        ]

        result = {
            'field_name_reconciliation': {
                'summary': {
                    'total_fields': total,
                    'total_trait_fields': total_traits,
                    'covered': covered_count,
                    'missing': missing_count,
                    'missing_traits': missing_traits_count,
                    'coverage_percentage': round(coverage_pct, 1),
                    'traits_coverage_percentage': round(traits_coverage_pct, 1)
                },
                'covered_fields': covered_entries,
                'missing_trait_fields': missing_traits,
                'missing_taxonomic_id_fields': missing_taxonomic,
                'high_value_missing_fields': high_value_missing
            }
        }
        output_content = yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_content)
            print(f"Report written to {output_file}")
        else:
            print(output_content)
    else:
        print(f"\n{'='*80}")
        print(f"Checking ALL BactoTraits field names against METPO synonyms")
        print(f"{'='*80}\n")
        print(f"Total BactoTraits fields: {total}")
        print(f"Trait fields (excluding taxonomic/ID): {total_traits}\n")
        print(f"COVERED ({covered_count}/{total_traits} trait fields = {traits_coverage_pct:.1f}%):")
        print("-" * 80)
        for entry in covered_entries:
            matched_note = f" [matched as '{entry['matched_as']}']" if entry['matched_as'] else ""
            if entry['label']:
                print(f"  ✓ '{entry['field']}' → {entry['metpo_id']} ({entry['label']}){matched_note} [{entry['unique_values']} unique values]")
            else:
                print(f"  ✓ '{entry['field']}' → {entry['metpo_id']}{matched_note} [{entry['unique_values']} unique values]")

        if missing_traits:
            print(f"\nMISSING TRAIT FIELDS ({missing_traits_count}/{total_traits} = {100*missing_traits_count/total_traits:.1f}%):")
            print("-" * 80)
            for entry in missing_traits:
                print(f"  ✗ '{entry['field']}' [{entry['unique_values']} unique values]")

            # High-value = small controlled vocabularies (2-20 values) that could be ontology classes
            high_value_missing = [e for e in missing_traits if 2 <= e['unique_values'] <= 20]
            if high_value_missing:
                print(f"\nHIGH-VALUE MISSING FIELDS ({len(high_value_missing)} fields with 2-20 unique values - good ontology class candidates):")
                print("-" * 80)
                for entry in high_value_missing:
                    print(f"  ⚠ '{entry['field']}' [{entry['unique_values']} unique values]")

        if missing_taxonomic:
            print(f"\nMISSING TAXONOMIC/ID FIELDS ({len(missing_taxonomic)} fields - excluded from coverage %):")
            print("-" * 80)
            for entry in missing_taxonomic:
                print(f"  ℹ '{entry['field']}' [{entry['unique_values']} unique values]")

        print(f"\n{'='*80}\n")


def reconcile_coverage(field_path: str, tsv_path: str, output_format: str = "text", output_file: str = None) -> None:
    """
    Reconcile BactoTraits field values against METPO synonyms.

    :param field_path: MongoDB field path to check
    :param tsv_path: Path to synonym-sources.tsv report
    :param output_format: Output format ('text' or 'yaml')
    """
    bactotraits_value_map = get_bactotraits_field_values(field_path)
    bactotraits_synonyms = load_bactotraits_synonyms(tsv_path)

    covered_entries = []
    missing_entries = []

    for normalized_value in sorted(bactotraits_value_map.keys()):
        original_value = bactotraits_value_map[normalized_value]
        was_normalized = (normalized_value != str(original_value))

        # Check variants
        value_variants = normalize_punctuation_variants(normalized_value)
        matched = False
        matched_info = None
        matched_variant = None

        for variant in value_variants:
            if variant in bactotraits_synonyms:
                matched = True
                matched_info = bactotraits_synonyms[variant]
                matched_variant = variant
                break

        if matched:
            metpo_curie = get_entity_curie(matched_info['entity'])
            label = matched_info.get('label', '')
            entity_type_raw = matched_info.get('entity_type', 'unknown')
            entity_type = ENTITY_TYPE_MAP.get(entity_type_raw, entity_type_raw)

            covered_entries.append({
                'value': normalized_value,
                'original_value': original_value if was_normalized else None,
                'matched_as': matched_variant if matched_variant != normalized_value else None,
                'metpo_id': metpo_curie,
                'label': label,
                'entity_type': entity_type
            })
        else:
            missing_entries.append({
                'value': normalized_value,
                'original_value': original_value if was_normalized else None
            })

    total = len(bactotraits_value_map)
    covered_count = len(covered_entries)
    missing_count = len(missing_entries)
    coverage_pct = 100 * covered_count / total if total > 0 else 0

    if output_format == "yaml":
        result = {
            'field_value_reconciliation': {
                'field': field_path,
                'summary': {
                    'total_values': total,
                    'covered': covered_count,
                    'missing': missing_count,
                    'coverage_percentage': round(coverage_pct, 1)
                },
                'covered_values': covered_entries,
                'missing_values': missing_entries
            }
        }
        print(yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True))
    else:
        print(f"\n{'='*80}")
        print(f"Reconciling BactoTraits field: {field_path}")
        print(f"{'='*80}\n")
        print(f"MongoDB values found: {total} (excluding 0, 1, NA, empty)")
        print(f"BactoTraits synonyms in METPO: {len(bactotraits_synonyms)}\n")
        print(f"COVERED ({covered_count}/{total} = {coverage_pct:.1f}%):")
        print("-" * 80)
        for entry in covered_entries:
            normalization_note = f" [NORMALIZED from '{entry['original_value']}']" if entry['original_value'] else ""
            matched_note = f" [matched as '{entry['matched_as']}']" if entry['matched_as'] else ""
            if entry['label']:
                print(f"  ✓ '{entry['value']}' → {entry['metpo_id']} ({entry['label']}){normalization_note}{matched_note}")
            else:
                print(f"  ✓ '{entry['value']}' → {entry['metpo_id']}{normalization_note}{matched_note}")

        if missing_entries:
            print(f"\nMISSING ({missing_count}/{total} = {100*missing_count/total:.1f}%):")
            print("-" * 80)
            for entry in missing_entries:
                normalization_note = f" [NORMALIZED from '{entry['original_value']}']" if entry['original_value'] else ""
                print(f"  ✗ '{entry['value']}'{normalization_note}")

        print(f"\n{'='*80}\n")


@click.command()
@click.option(
    '--mode',
    type=click.Choice(['values', 'field_names'], case_sensitive=False),
    default='values',
    help="Reconciliation mode: 'values' checks field values, 'field_names' checks ALL field names"
)
@click.option(
    '--field',
    type=str,
    help="MongoDB field path to reconcile (e.g., 'Ox_anaerobic', 'G_negative'). Required for 'values' mode."
)
@click.option(
    '--tsv',
    type=click.Path(exists=True),
    default='reports/synonym-sources.tsv',
    help="Path to synonym-sources.tsv report"
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['text', 'yaml'], case_sensitive=False),
    default='text',
    help="Output format: 'text' for console output, 'yaml' for structured YAML"
)
@click.option(
    '--output',
    type=click.Path(),
    help="Output file path. If not specified, prints to stdout."
)
def main(mode, field, tsv, output_format, output):
    """Reconcile BactoTraits MongoDB field values against METPO synonyms."""
    try:
        if mode == "field_names":
            reconcile_all_field_names(tsv, output_format, output)
        else:  # values mode
            if not field:
                raise click.UsageError("--field is required for 'values' mode")
            reconcile_coverage(field, tsv, output_format, output)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
