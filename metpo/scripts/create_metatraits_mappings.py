#!/usr/bin/env python3
"""
Create SSSOM mappings between MetaTraits trait cards, METPO terms, and KG-Microbe nodes.

This script implements multiple mapping strategies:
1. Direct label matching (exactMatch)
2. Synonym matching (closeMatch)
3. Shared ontology reference matching (relatedMatch)
4. Fuzzy string matching (closeMatch with confidence scores)

Outputs formal SSSOM TSV files following the SSSOM standard.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import click
import pandas as pd
from rapidfuzz import fuzz
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDFS, SKOS, OWL


def normalize_string(s: str) -> str:
    """Normalize strings for comparison by lowercasing and replacing separators."""
    if pd.isna(s) or not s:
        return ""
    s = str(s).lower().strip()
    s = re.sub(r"[-_\s]+", " ", s)
    return s


def parse_ontology_curies(curie_string: str) -> set[str]:
    """Parse semicolon-separated ontology CURIEs into a set."""
    if pd.isna(curie_string) or not curie_string:
        return set()
    return {c.strip() for c in str(curie_string).split(";")}


def parse_xrefs(xref_string: str) -> set[str]:
    """Parse pipe-separated xrefs into a set of CURIEs."""
    if pd.isna(xref_string) or not xref_string:
        return set()
    return {x.strip() for x in str(xref_string).split("|")}


def parse_synonyms(synonym_string: str) -> set[str]:
    """Parse pipe-separated synonyms into a set."""
    if pd.isna(synonym_string) or not synonym_string:
        return set()
    return {s.strip() for s in str(synonym_string).split("|")}


def load_metatraits(path: str) -> pd.DataFrame:
    """Load MetaTraits trait cards from TSV."""
    click.echo(f"Loading MetaTraits data from {path}...")
    df = pd.read_csv(path, sep="\t")
    click.echo(f"  Loaded {len(df)} MetaTraits trait cards")
    return df


def load_metpo_from_owl(path: str) -> pd.DataFrame:
    """Load METPO terms from OWL file using rdflib."""
    click.echo(f"Loading METPO terms from OWL: {path}...")

    # Load OWL file
    g = Graph()
    g.parse(path, format="xml")
    click.echo(f"  Loaded {len(g)} triples from OWL file")

    # Define namespaces
    METPO_NS = Namespace("https://w3id.org/metpo/")
    IAO = Namespace("http://purl.obolibrary.org/obo/IAO_")
    OBO = Namespace("http://purl.obolibrary.org/obo/")
    OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

    # Extract METPO terms
    terms = []

    for subject in g.subjects(predicate=RDFS.label):
        # Only process METPO terms (using w3id.org namespace)
        subject_str = str(subject)
        if not subject_str.startswith("https://w3id.org/metpo/"):
            continue

        # Skip ontology metadata and just get numbered terms
        term_id = subject_str.replace("https://w3id.org/metpo/", "")
        if not term_id[0].isdigit():
            continue

        # Extract ID (convert URI to CURIE)
        metpo_id = f"METPO:{term_id}"

        # Extract label
        label = str(g.value(subject, RDFS.label))

        # Extract synonyms (using different properties)
        synonyms = set()
        for syn_prop in [OBOINOWL.hasExactSynonym, OBOINOWL.hasRelatedSynonym,
                         OBOINOWL.hasBroadSynonym, OBOINOWL.hasNarrowSynonym]:
            for syn in g.objects(subject, syn_prop):
                synonyms.add(str(syn))

        # Extract xrefs (database cross-references)
        xrefs = set()

        # hasDbXref
        for xref in g.objects(subject, OBOINOWL.hasDbXref):
            xrefs.add(str(xref))

        # IAO:0000119 is 'definition source' - often contains xrefs
        # These can be on the subject directly OR in axiom annotations
        for source in g.objects(subject, IAO["0000119"]):
            source_str = str(source)
            # Convert OBO URIs to CURIEs
            if "obolibrary.org/obo/" in source_str:
                curie = source_str.split("/obo/")[-1].replace("_", ":")
                xrefs.add(curie)
            elif source_str.startswith("http"):
                # Keep other URLs as-is
                xrefs.add(source_str)
            else:
                xrefs.add(source_str)

        # Also check axiom annotations (OWL2 annotation on annotation)
        # Find axioms where this subject is the annotatedSource
        for axiom in g.subjects(OWL.annotatedSource, subject):
            # Get IAO_0000119 from the axiom
            for source in g.objects(axiom, IAO["0000119"]):
                source_str = str(source)
                if "obolibrary.org/obo/" in source_str:
                    curie = source_str.split("/obo/")[-1].replace("_", ":")
                    xrefs.add(curie)
                elif source_str.startswith("http"):
                    xrefs.add(source_str)
                else:
                    xrefs.add(source_str)

        # skos:exactMatch and skos:closeMatch
        for match in g.objects(subject, SKOS.exactMatch):
            match_str = str(match)
            if "obolibrary.org/obo/" in match_str:
                curie = match_str.split("/obo/")[-1].replace("_", ":")
                xrefs.add(curie)
            else:
                xrefs.add(match_str)

        for match in g.objects(subject, SKOS.closeMatch):
            match_str = str(match)
            if "obolibrary.org/obo/" in match_str:
                curie = match_str.split("/obo/")[-1].replace("_", ":")
                xrefs.add(curie)
            else:
                xrefs.add(match_str)

        # Extract definition
        definition = g.value(subject, OBO["IAO_0000115"])  # IAO:0000115 is 'definition'

        terms.append({
            "id": metpo_id,
            "name": label,
            "synonym": "|".join(sorted(synonyms)) if synonyms else "",
            "xref": "|".join(sorted(xrefs)) if xrefs else "",
            "description": str(definition) if definition else "",
        })

    df = pd.DataFrame(terms)

    if len(df) == 0:
        click.echo("  WARNING: No METPO terms found in OWL file!")
        return df

    click.echo(f"  Loaded {len(df)} METPO terms from OWL")
    click.echo(f"  Terms with xrefs: {len(df[df['xref'] != ''])}")
    click.echo(f"  Terms with synonyms: {len(df[df['synonym'] != ''])}")

    return df


def load_metpo_from_kg_microbe(path: str) -> pd.DataFrame:
    """Load METPO terms from KG-Microbe nodes.tsv."""
    click.echo(f"Loading METPO terms from KG-Microbe: {path}...")

    # Read full file to get header
    df = pd.read_csv(path, sep="\t", nrows=0)
    click.echo(f"  KG-Microbe columns: {list(df.columns)}")

    # Read only METPO rows
    metpo_df = pd.read_csv(
        path,
        sep="\t",
        usecols=["id", "category", "name", "description", "xref", "synonym"],
        low_memory=False,
        dtype=str,
    )

    # Filter for METPO prefix
    metpo_df = metpo_df[metpo_df["id"].str.startswith("METPO:", na=False)]

    # Filter out rows with missing names
    metpo_df = metpo_df[metpo_df["name"].notna()]

    click.echo(f"  Loaded {len(metpo_df)} METPO terms from KG-Microbe")
    return metpo_df


def create_direct_label_mappings(
    metatraits_df: pd.DataFrame,
    metpo_df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Create exactMatch mappings based on direct label matching."""
    click.echo("\n[Phase 1] Creating direct label mappings...")

    mappings = []

    # Build normalized label index for METPO
    metpo_index = {}
    for _, row in metpo_df.iterrows():
        norm_name = normalize_string(row["name"])
        if norm_name not in metpo_index:
            metpo_index[norm_name] = []
        metpo_index[norm_name].append(row)

    # Match MetaTraits against METPO
    for _, mt_row in metatraits_df.iterrows():
        mt_norm = normalize_string(mt_row["name"])

        if mt_norm in metpo_index:
            for metpo_row in metpo_index[mt_norm]:
                mappings.append({
                    "subject_id": f"metatraits:{mt_row['card_id']}",
                    "subject_label": mt_row["name"],
                    "predicate_id": "skos:exactMatch",
                    "object_id": metpo_row["id"],
                    "object_label": metpo_row["name"],
                    "mapping_justification": "semapv:LexicalMatching",
                    "confidence": 1.0,
                    "comment": "Exact normalized label match",
                })

    click.echo(f"  Created {len(mappings)} direct label mappings")
    return mappings


def create_synonym_mappings(
    metatraits_df: pd.DataFrame,
    metpo_df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Create closeMatch mappings based on synonym matching."""
    click.echo("\n[Phase 2] Creating synonym-based mappings...")

    mappings = []

    # Build synonym index for METPO
    synonym_index = defaultdict(list)
    for _, row in metpo_df.iterrows():
        synonyms = parse_synonyms(row.get("synonym", ""))
        for syn in synonyms:
            norm_syn = normalize_string(syn)
            if norm_syn:
                synonym_index[norm_syn].append(row)

    click.echo(f"  Indexed {len(synonym_index)} unique normalized METPO synonyms")

    # Match MetaTraits names against METPO synonyms
    for _, mt_row in metatraits_df.iterrows():
        mt_norm = normalize_string(mt_row["name"])

        if mt_norm in synonym_index:
            for metpo_row in synonym_index[mt_norm]:
                mappings.append({
                    "subject_id": f"metatraits:{mt_row['card_id']}",
                    "subject_label": mt_row["name"],
                    "predicate_id": "skos:closeMatch",
                    "object_id": metpo_row["id"],
                    "object_label": metpo_row["name"],
                    "mapping_justification": "semapv:LexicalMatching",
                    "confidence": 0.95,
                    "comment": "MetaTraits name matches METPO synonym",
                })

    click.echo(f"  Created {len(mappings)} synonym-based mappings")
    return mappings


def create_shared_ontology_mappings(
    metatraits_df: pd.DataFrame,
    metpo_df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Create relatedMatch mappings based on shared ontology references."""
    click.echo("\n[Phase 3] Creating shared ontology reference mappings...")

    mappings = []

    # Build xref index for METPO
    xref_index = defaultdict(list)
    for _, row in metpo_df.iterrows():
        xrefs = parse_xrefs(row.get("xref", ""))
        for xref in xrefs:
            xref_index[xref].append(row)

    click.echo(f"  Indexed {len(xref_index)} unique METPO xrefs")

    # Match MetaTraits ontology refs against METPO xrefs
    matches_by_ontology = defaultdict(int)

    for _, mt_row in metatraits_df.iterrows():
        mt_curies = parse_ontology_curies(mt_row.get("ontology_curies", ""))

        for curie in mt_curies:
            if curie in xref_index:
                matches_by_ontology[curie.split(":")[0]] += 1
                for metpo_row in xref_index[curie]:
                    mappings.append({
                        "subject_id": f"metatraits:{mt_row['card_id']}",
                        "subject_label": mt_row["name"],
                        "predicate_id": "skos:relatedMatch",
                        "object_id": metpo_row["id"],
                        "object_label": metpo_row["name"],
                        "mapping_justification": "semapv:MappingChaining",
                        "confidence": 0.85,
                        "comment": f"Both reference {curie}",
                    })

    click.echo(f"  Created {len(mappings)} shared ontology mappings")
    click.echo(f"  Matches by ontology prefix: {dict(matches_by_ontology)}")
    return mappings


def create_fuzzy_mappings(
    metatraits_df: pd.DataFrame,
    metpo_df: pd.DataFrame,
    threshold: int = 85,
) -> list[dict[str, Any]]:
    """Create closeMatch mappings based on fuzzy string matching."""
    click.echo(f"\n[Phase 4] Creating fuzzy string mappings (threshold={threshold})...")

    mappings = []

    # For each MetaTraits term, find best fuzzy matches in METPO
    for _, mt_row in metatraits_df.iterrows():
        mt_name = mt_row["name"]
        mt_norm = normalize_string(mt_name)

        best_matches = []

        for _, metpo_row in metpo_df.iterrows():
            metpo_name = metpo_row["name"]
            metpo_norm = normalize_string(metpo_name)

            # Skip if already exact match
            if mt_norm == metpo_norm:
                continue

            # Calculate fuzzy similarity
            similarity = fuzz.ratio(mt_norm, metpo_norm)

            if similarity >= threshold:
                best_matches.append((similarity, metpo_row))

        # Keep only top 3 fuzzy matches per MetaTraits term
        best_matches.sort(reverse=True, key=lambda x: x[0])
        for similarity, metpo_row in best_matches[:3]:
            confidence = similarity / 100.0
            mappings.append({
                "subject_id": f"metatraits:{mt_row['card_id']}",
                "subject_label": mt_row["name"],
                "predicate_id": "skos:closeMatch",
                "object_id": metpo_row["id"],
                "object_label": metpo_row["name"],
                "mapping_justification": "semapv:LexicalMatching",
                "confidence": round(confidence, 3),
                "comment": f"Fuzzy string similarity: {similarity}%",
            })

    click.echo(f"  Created {len(mappings)} fuzzy mappings")
    return mappings


def deduplicate_mappings(mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate mappings, keeping highest confidence for each subject-object pair."""
    click.echo("\n[Deduplication] Removing duplicate mappings...")

    # Group by subject-object pair
    pairs = {}
    for m in mappings:
        key = (m["subject_id"], m["object_id"])
        if key not in pairs or m["confidence"] > pairs[key]["confidence"]:
            pairs[key] = m

    deduped = list(pairs.values())
    click.echo(f"  Reduced from {len(mappings)} to {len(deduped)} mappings")
    return deduped


def write_sssom_tsv(mappings: list[dict[str, Any]], output_path: str):
    """Write mappings to SSSOM TSV format."""
    click.echo(f"\nWriting SSSOM file to {output_path}...")

    outpath = Path(output_path)
    outpath.parent.mkdir(parents=True, exist_ok=True)

    with open(outpath, "w", newline="") as f:
        # Write SSSOM metadata header
        f.write("# curie_map:\n")
        f.write("#   METPO: http://purl.obolibrary.org/obo/METPO_\n")
        f.write("#   metatraits: https://metatraits.embl.de/traits#\n")
        f.write("#   skos: http://www.w3.org/2004/02/skos/core#\n")
        f.write("#   semapv: https://w3id.org/semapv/vocab/\n")
        f.write("# mapping_set_id: metatraits-metpo-2026-02-03\n")
        f.write("# mapping_date: 2026-02-03\n")
        f.write("# mapping_tool: metpo/scripts/create_metatraits_mappings.py\n")
        f.write("# mapping_provider: https://github.com/berkeleybop/metpo\n")
        f.write("# license: https://creativecommons.org/publicdomain/zero/1.0/\n")
        f.write("# comment: Mappings between MetaTraits trait cards and METPO terms (from OWL ontology)\n")
        f.write("#\n")

        # Write mappings
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subject_id",
                "subject_label",
                "predicate_id",
                "object_id",
                "object_label",
                "mapping_justification",
                "confidence",
                "comment",
            ],
            delimiter="\t",
        )
        writer.writeheader()

        # Sort by subject_id, then confidence (descending)
        sorted_mappings = sorted(
            mappings,
            key=lambda m: (m["subject_id"], -m["confidence"]),
        )

        writer.writerows(sorted_mappings)

    click.echo(f"  Wrote {len(mappings)} mappings to {outpath}")


def generate_summary_report(
    mappings: list[dict[str, Any]],
    metatraits_df: pd.DataFrame,
    metpo_df: pd.DataFrame,
) -> str:
    """Generate a summary report of the mapping results."""
    from collections import Counter

    report = []
    report.append("# MetaTraits → METPO Mapping Summary\n")
    report.append(f"**Date**: 2026-02-03\n")
    report.append(f"**Total mappings**: {len(mappings)}\n\n")

    # Coverage stats
    mapped_subjects = len(set(m["subject_id"] for m in mappings))
    total_subjects = len(metatraits_df)
    coverage_pct = (mapped_subjects / total_subjects * 100) if total_subjects > 0 else 0

    report.append("## Coverage\n")
    report.append(f"- **MetaTraits terms mapped**: {mapped_subjects} / {total_subjects} ({coverage_pct:.1f}%)\n")
    report.append(f"- **METPO terms matched**: {len(set(m['object_id'] for m in mappings))}\n\n")

    # Predicate distribution
    predicate_counts = Counter(m["predicate_id"] for m in mappings)
    report.append("## Mapping Types\n")
    for pred, count in predicate_counts.most_common():
        pct = (count / len(mappings) * 100) if mappings else 0
        report.append(f"- **{pred}**: {count} ({pct:.1f}%)\n")
    report.append("\n")

    # Justification distribution
    just_counts = Counter(m["mapping_justification"] for m in mappings)
    report.append("## Mapping Strategies\n")
    for just, count in just_counts.most_common():
        pct = (count / len(mappings) * 100) if mappings else 0
        report.append(f"- **{just}**: {count} ({pct:.1f}%)\n")
    report.append("\n")

    # Confidence distribution
    confidences = [m["confidence"] for m in mappings]
    report.append("## Confidence Distribution\n")
    report.append(f"- **Mean**: {sum(confidences)/len(confidences):.3f}\n")
    report.append(f"- **Median**: {sorted(confidences)[len(confidences)//2]:.3f}\n")
    report.append(f"- **High confidence (≥0.95)**: {sum(1 for c in confidences if c >= 0.95)}\n")
    report.append(f"- **Medium confidence (0.85-0.94)**: {sum(1 for c in confidences if 0.85 <= c < 0.95)}\n")
    report.append(f"- **Low confidence (<0.85)**: {sum(1 for c in confidences if c < 0.85)}\n\n")

    # Example mappings
    report.append("## Example Mappings\n\n")
    report.append("### High Confidence (exactMatch)\n")
    exact_matches = [m for m in mappings if m["predicate_id"] == "skos:exactMatch"][:5]
    for m in exact_matches:
        report.append(f"- `{m['subject_label']}` → `{m['object_label']}` (confidence: {m['confidence']})\n")

    report.append("\n### Shared Ontology References\n")
    shared_matches = [m for m in mappings if m["mapping_justification"] == "semapv:SharedOntologyReference"][:5]
    for m in shared_matches:
        report.append(f"- `{m['subject_label']}` → `{m['object_label']}` ({m['comment']})\n")

    return "".join(report)


@click.command()
@click.option(
    "--metatraits-input",
    "-m",
    required=True,
    type=click.Path(exists=True),
    help="Path to MetaTraits cards TSV file",
)
@click.option(
    "--metpo-owl",
    "-p",
    required=True,
    type=click.Path(exists=True),
    help="Path to METPO OWL file",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output SSSOM TSV file path",
)
@click.option(
    "--fuzzy-threshold",
    "-t",
    default=85,
    type=int,
    help="Minimum similarity score (0-100) for fuzzy matching",
)
@click.option(
    "--include-fuzzy/--no-fuzzy",
    default=True,
    help="Include fuzzy string matching (slower but more comprehensive)",
)
@click.option(
    "--report",
    "-r",
    type=click.Path(),
    help="Optional output path for summary report (markdown)",
)
def main(
    metatraits_input: str,
    metpo_owl: str,
    output: str,
    fuzzy_threshold: int,
    include_fuzzy: bool,
    report: str | None,
):
    """
    Create SSSOM mappings between MetaTraits and METPO.

    Implements multiple mapping strategies:
    - Direct label matching (exactMatch)
    - Synonym matching (closeMatch)
    - Shared ontology references (relatedMatch)
    - Fuzzy string matching (closeMatch)
    """
    click.echo("=" * 70)
    click.echo("MetaTraits → METPO Mapping Pipeline")
    click.echo("=" * 70)

    # Load data
    metatraits_df = load_metatraits(metatraits_input)
    metpo_df = load_metpo_from_owl(metpo_owl)

    # Create mappings using different strategies
    all_mappings = []

    all_mappings.extend(create_direct_label_mappings(metatraits_df, metpo_df))
    all_mappings.extend(create_synonym_mappings(metatraits_df, metpo_df))
    all_mappings.extend(create_shared_ontology_mappings(metatraits_df, metpo_df))

    if include_fuzzy:
        all_mappings.extend(
            create_fuzzy_mappings(metatraits_df, metpo_df, threshold=fuzzy_threshold)
        )

    # Deduplicate
    final_mappings = deduplicate_mappings(all_mappings)

    # Write output
    write_sssom_tsv(final_mappings, output)

    # Generate and write report if requested
    if report:
        report_text = generate_summary_report(final_mappings, metatraits_df, metpo_df)
        report_path = Path(report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text)
        click.echo(f"\nWrote summary report to {report}")

    click.echo("\n" + "=" * 70)
    click.echo("✓ Mapping pipeline complete!")
    click.echo("=" * 70)


if __name__ == "__main__":
    main()
