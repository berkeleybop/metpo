"""
Analyze the unique value provided by each ontology source.

Distinguishes between:
- Ontology FILE (object_source): Which ChromaDB collection returned the match
- Term SOURCE: The actual defining ontology of the term (extracted from IRI)

This helps identify:
1. Ontologies that only contribute imported terms (available elsewhere)
2. Ontologies providing unique native terms
3. Redundant sources that could be removed
"""

import re
from collections import defaultdict

import click
import pandas as pd


def extract_term_source(iri: str) -> str:
    """
    Extract the defining ontology from an IRI.

    Examples:
    - http://purl.obolibrary.org/obo/PATO_0000001 → PATO
    - http://purl.obolibrary.org/obo/GO_0008150 → GO
    - https://w3id.org/biolink/vocab/phenotype → biolink
    """
    # OBO pattern: .../obo/PREFIX_ID
    obo_match = re.search(r"/obo/([A-Za-z]+)_\d+", iri)
    if obo_match:
        return obo_match.group(1).upper()

    # Biolink pattern
    if "biolink" in iri:
        return "biolink"

    # DOI pattern
    if "doi.org" in iri:
        doi_match = re.search(r"doi\.org/[^/]+/([A-Za-z]+)", iri)
        if doi_match:
            return doi_match.group(1)

    # Default: return as-is
    return "unknown"


@click.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Input SSSOM TSV file"
)
def main(input):
    """Analyze unique value of each ontology source."""

    print(f"Loading mappings from: {input}")
    df = pd.read_csv(input, sep="\t", comment="#")

    # Extract term source from IRI
    df["term_source"] = df["object_id"].apply(extract_term_source)

    print(f"\nLoaded {len(df)} mappings")
    print(f"Unique ontology files (object_source): {df['object_source'].nunique()}")
    print(f"Unique term sources (from IRI): {df['term_source'].nunique()}")

    # Analysis 1: Native vs Imported terms per ontology file
    print("\n" + "=" * 100)
    print("NATIVE vs IMPORTED TERMS BY ONTOLOGY FILE")
    print("=" * 100)

    ontology_analysis = []
    for ont_file in sorted(df["object_source"].dropna().unique()):
        ont_df = df[df["object_source"] == ont_file]

        # Count native (term_source matches object_source, case-insensitive)
        native = ont_df[ont_df["term_source"].str.lower() == ont_file.lower()]
        imported = ont_df[ont_df["term_source"].str.lower() != ont_file.lower()]

        # Get unique term sources provided
        term_sources = ont_df["term_source"].value_counts().to_dict()

        ontology_analysis.append({
            "ontology_file": ont_file,
            "total_matches": len(ont_df),
            "native_matches": len(native),
            "imported_matches": len(imported),
            "native_pct": 100 * len(native) / len(ont_df) if len(ont_df) > 0 else 0,
            "term_sources": term_sources,
            "unique_metpo_terms": ont_df["subject_id"].nunique()
        })

    ont_df = pd.DataFrame(ontology_analysis).sort_values("total_matches", ascending=False)

    print(f"\n{'Ontology':<15} {'Total':<8} {'Native':<8} {'Imported':<10} {'Native %':<10} {'METPO Terms':<12} {'Provides'}")
    print("-" * 100)

    for _, row in ont_df.iterrows():
        # Show top 3 term sources provided
        top_sources = sorted(row["term_sources"].items(), key=lambda x: x[1], reverse=True)[:3]
        sources_str = ", ".join([f"{src}({cnt})" for src, cnt in top_sources])

        print(f"{row['ontology_file']:<15} {row['total_matches']:<8} {row['native_matches']:<8} "
              f"{row['imported_matches']:<10} {row['native_pct']:<10.1f} {row['unique_metpo_terms']:<12} {sources_str}")

    # Analysis 2: Term source redundancy
    print("\n" + "=" * 100)
    print("TERM SOURCE REDUNDANCY: Which term sources appear in multiple ontology files?")
    print("=" * 100)

    term_source_availability = defaultdict(set)
    for _, row in df.iterrows():
        term_source_availability[row["term_source"]].add(row["object_source"])

    print(f"\n{'Term Source':<15} {'Available in N files':<25} {'Ontology Files'}")
    print("-" * 100)

    for term_src, ont_files in sorted(term_source_availability.items(),
                                      key=lambda x: len(x[1]), reverse=True):
        if len(ont_files) > 1:  # Only show redundant sources
            len(df[df["term_source"] == term_src])
            # Filter out NaN values from ont_files
            ont_files_clean = [f for f in ont_files if pd.notna(f)]
            if ont_files_clean:
                print(f"{term_src:<15} {len(ont_files_clean):<25} {', '.join(sorted(ont_files_clean))}")

    # Analysis 3: Ontologies providing ONLY imported terms
    print("\n" + "=" * 100)
    print("ONTOLOGIES PROVIDING ONLY IMPORTED TERMS")
    print("=" * 100)
    print("These might be redundant if their terms are available from native sources.\n")

    only_imported = ont_df[ont_df["native_matches"] == 0]
    if len(only_imported) > 0:
        print(f"{'Ontology':<15} {'Total Matches':<15} {'Provides (all imported)'}")
        print("-" * 80)
        for _, row in only_imported.iterrows():
            top_sources = sorted(row["term_sources"].items(), key=lambda x: x[1], reverse=True)
            sources_str = ", ".join([f"{src}({cnt})" for src, cnt in top_sources])
            print(f"{row['ontology_file']:<15} {row['total_matches']:<15} {sources_str}")

            # Check if these terms are available natively elsewhere
            for term_src, _count in top_sources:
                native_available = df[(df["term_source"] == term_src) &
                                     (df["object_source"].str.lower() == term_src.lower())]
                if len(native_available) > 0:
                    print(f"  └─ {term_src}: {len(native_available)} matches available natively from {term_src.lower()}")
    else:
        print("None - all ontologies provide at least some native terms.")

    # Analysis 4: Unique contributions
    print("\n" + "=" * 100)
    print("UNIQUE NATIVE CONTRIBUTIONS")
    print("=" * 100)
    print("Terms that ONLY appear from their native ontology (not imported elsewhere).\n")

    unique_contributions = []
    for term_src in df["term_source"].unique():
        # Get all matches for this term source
        term_matches = df[df["term_source"] == term_src]

        # Check how many ontology files provide it
        providing_files = term_matches["object_source"].unique()

        # Get native matches
        native_matches = term_matches[term_matches["object_source"].str.lower() == term_src.lower()]

        if len(native_matches) > 0 and len(providing_files) == 1:
            unique_contributions.append({
                "term_source": term_src,
                "ontology_file": providing_files[0],
                "match_count": len(native_matches),
                "metpo_terms": native_matches["subject_id"].nunique()
            })

    if unique_contributions:
        unique_df = pd.DataFrame(unique_contributions).sort_values("match_count", ascending=False)
        print(f"{'Term Source':<15} {'Ontology File':<15} {'Matches':<10} {'METPO Terms'}")
        print("-" * 60)
        for _, row in unique_df.iterrows():
            print(f"{row['term_source']:<15} {row['ontology_file']:<15} {row['match_count']:<10} {row['metpo_terms']}")
    else:
        print("All term sources appear in multiple ontology files.")

    # Analysis 5: Removal candidates
    print("\n" + "=" * 100)
    print("REMOVAL CANDIDATES: Ontologies that might be redundant")
    print("=" * 100)
    print("Criteria: Only imported terms AND all terms available from native sources.\n")

    removal_candidates = []
    for _, row in only_imported.iterrows():
        ont_file = row["ontology_file"]
        df[df["object_source"] == ont_file]

        # Check if ALL terms are available natively elsewhere
        all_redundant = True
        for term_src in row["term_sources"]:
            native_available = df[(df["term_source"] == term_src) &
                                 (df["object_source"].str.lower() == term_src.lower())]
            if len(native_available) == 0:
                all_redundant = False
                break

        if all_redundant:
            removal_candidates.append({
                "ontology": ont_file,
                "matches": row["total_matches"],
                "metpo_terms": row["unique_metpo_terms"],
                "provides": ", ".join([f"{src}({cnt})" for src, cnt in
                                      sorted(row["term_sources"].items(), key=lambda x: x[1], reverse=True)])
            })

    if removal_candidates:
        print(f"Found {len(removal_candidates)} candidates:\n")
        for c in removal_candidates:
            print(f"• {c['ontology']}: {c['matches']} matches to {c['metpo_terms']} METPO terms")
            print(f"  Provides: {c['provides']}")
            print("  → All terms available from native sources\n")
    else:
        print("No clear removal candidates found.")
        print("All ontologies either provide native terms or unique imported terms.")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
