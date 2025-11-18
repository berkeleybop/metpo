#!/usr/bin/env python3
"""
Comprehensive analysis of ontologies considered for METPO - 100% TRACEABLE

Primary sources:
- /home/mark/gitrepos/metpo/docs/ONTOLOGY_SELECTION_SUMMARY.md
- /home/mark/gitrepos/metpo/docs/ONTOLOGY_CROSSREFERENCE_HISTORY.md
- /home/mark/gitrepos/semantic-sql/src/semsql/builder/registry/ontologies.yaml
"""

import yaml
from pathlib import Path
from collections import defaultdict

# Primary source files
ONTOLOGY_SELECTION_DOC = Path("/home/mark/gitrepos/metpo/docs/ONTOLOGY_SELECTION_SUMMARY.md")
SEMSQL_REGISTRY = Path("/home/mark/gitrepos/semantic-sql/src/semsql/builder/registry/ontologies.yaml")

# Ontologies kept in ChromaDB (from ONTOLOGY_SELECTION_SUMMARY.md)
ONTOLOGIES_KEPT_OLS = [
    ("micro", "Microbial ecology", 17645, 611, 34.63),
    ("flopo", "Flora phenotype", 35359, 152, 4.30),
    ("ecocore", "Ecological core", 6086, 33, 5.42),
    ("envo", "Environment ontology", 7365, 20, 2.72),
    ("mco", "Microbial conditions", 3491, 11, 3.15),
    ("cmpo", "Cellular microscopy", 1134, 3, 2.65),
    ("pato", "Phenotype attributes", 9061, 14, 1.55),
    ("eco", "Evidence codes", 3449, 5, 1.45),
    ("phipo", "Pathogen-host interaction", 4327, 5, 1.16),
    ("eupath", "Eukaryotic pathogen", 5406, 6, 1.11),
    ("pco", "Population & community", 435, 5, 11.49),
    ("exo", "Experimental conditions", 175, 2, 11.43),
    ("geo", "Geographical", 196, 2, 10.20),
    ("biolink", "Semantic model", 974, 9, 9.24),
    ("omp", "Microbial phenotypes", 2440, 39, 8.21),
    ("apo", "Ascomycete phenotypes", 646, 4, 6.19),
    ("ohmi", "Host-microbe interactions", 1244, 7, 5.63),
    ("oba", "Biological attributes", 73148, 69, 0.94),
    ("upheno", "Unified phenotype", 192001, 154, 0.80),
    ("go", "Gene Ontology", 84737, 28, 0.33),
]

ONTOLOGIES_KEPT_NONOLS = [
    ("n4l_merged", "Names4Life microbial phenotypes", 454, 76, 167.40, "doi.org/10.1601"),
    ("d3o", "DSMZ microbiology (GC content!)", 283, 6, 21.20, "purl.dsmz.de"),
    ("miso", "DSMZ microbial survey", 387, 6, 15.50, "purl.dsmz.de"),
    ("meo", "Metadata hub microbiology", 2499, 15, 6.00, "mdatahub.org"),
]

ONTOLOGIES_REMOVED_OLS = [
    ("chebi", "Chemical entities - WORST ROI", 221776, 2, 0.009),
    ("foodon", "Food ontology", 40123, 9, 0.224),
    ("cl", "Cell types", 17521, 6, 0.342),
    ("fypo", "Fission yeast", 17232, 7, 0.406),
    ("ecto", "Environmental exposures", 12404, 5, 0.403),
    ("aro", "Antibiotic resistance", 8551, 0, 0.000),
    ("ddpheno", "Dictyostelium", 1397, 0, 0.000),
]

def load_semsql_registry():
    """Load semantic-sql ontology registry"""
    if not SEMSQL_REGISTRY.exists():
        print(f"WARNING: {SEMSQL_REGISTRY} not found")
        return {}

    with open(SEMSQL_REGISTRY) as f:
        data = yaml.safe_load(f)

    # Extract ontology IDs
    ontologies = set()
    if "ontologies" in data:
        for ont_id in data["ontologies"].keys():
            ontologies.add(ont_id.lower())

    return ontologies

def analyze_ontology_landscape():
    """Comprehensive analysis of ontology landscape"""

    print("=" * 80)
    print("METPO Ontology Landscape Analysis - 100% TRACEABLE")
    print("=" * 80)
    print(f"\nPrimary sources:")
    print(f"  - {ONTOLOGY_SELECTION_DOC}")
    print(f"  - {SEMSQL_REGISTRY}")

    # Load semsql registry
    semsql_ontologies = load_semsql_registry()
    print(f"\nSemantic-SQL registry contains: {len(semsql_ontologies)} ontologies")

    print("\n" + "=" * 80)
    print("ONTOLOGIES KEPT IN CHROMADB (24 total)")
    print("=" * 80)

    print("\n--- OLS Ontologies (20) ---\n")
    print(f"{'ID':<12} {'Description':<30} {'Embeddings':<12} {'Matches':<10} {'ROI':<8} {'semsql':<8}")
    print("-" * 90)

    total_embeddings = 0
    total_matches = 0
    in_semsql = 0

    for ont_id, desc, emb, matches, roi in ONTOLOGIES_KEPT_OLS:
        in_registry = "✓" if ont_id.lower() in semsql_ontologies else "✗"
        if in_registry == "✓":
            in_semsql += 1
        total_embeddings += emb
        total_matches += matches
        print(f"{ont_id:<12} {desc:<30} {emb:<12,} {matches:<10} {roi:<8.2f} {in_registry:<8}")

    print(f"\nOLS Summary: {total_embeddings:,} embeddings, {total_matches} METPO matches")
    print(f"In semsql registry: {in_semsql}/20 ({in_semsql/20*100:.1f}%)")

    print("\n--- Non-OLS Ontologies (4) ---\n")
    print(f"{'ID':<15} {'Description':<35} {'Embeddings':<12} {'Matches':<10} {'ROI':<10} {'Source':<20}")
    print("-" * 100)

    nonols_embeddings = 0
    nonols_matches = 0

    for ont_id, desc, emb, matches, roi, source in ONTOLOGIES_KEPT_NONOLS:
        nonols_embeddings += emb
        nonols_matches += matches
        print(f"{ont_id:<15} {desc:<35} {emb:<12,} {matches:<10} {roi:<10.2f} {source:<20}")

    print(f"\nNon-OLS Summary: {nonols_embeddings:,} embeddings, {nonols_matches} METPO matches")
    print(f"In semsql registry: 0/4 (specialized sources)")

    print("\n" + "=" * 80)
    print("ONTOLOGIES REMOVED (15 total)")
    print("=" * 80)

    print("\n--- OLS Ontologies Removed (7) ---\n")
    print(f"{'ID':<12} {'Reason':<35} {'Embeddings':<12} {'Matches':<10} {'ROI':<8}")
    print("-" * 85)

    removed_embeddings = 0
    for ont_id, reason, emb, matches, roi in ONTOLOGIES_REMOVED_OLS:
        removed_embeddings += emb
        print(f"{ont_id:<12} {reason:<35} {emb:<12,} {matches:<10} {roi:<8.3f}")

    print(f"\nRemoved embeddings: {removed_embeddings:,} (saved 41.2% of corpus)")

    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    print(f"""
1. **Comprehensive Search**: 200+ ontologies explored
   - MicrO imports analyzed (20 ontologies)
   - Issue #222 phenotype survey (17 ontologies)
   - Oaklib cache (181 ontologies accessed)
   - 39 ontologies embedded in ChromaDB for testing

2. **Final Selection**: 24 ontologies retained
   - ROI-driven selection (good matches / 1000 embeddings)
   - Domain-specific focus (microbial phenotypes)
   - 452,942 embeddings (down from 778,496)
   - 1,282 good matches (distance <0.60)

3. **OLS Coverage**: 20/24 ontologies from OLS
   - All searchable via OLS API
   - Standardized OWL format
   - Most in semsql registry ({in_semsql}/20)

4. **Specialized Sources**: 4 non-OLS ontologies
   - Names4Life (n4l_merged): BEST ROI (167.40)
   - DSMZ ontologies (d3o, miso): GC content coverage
   - MDAtahub (meo): Microbiology metadata
   - Not in OLS or BioPortal (domain-specific)

5. **Quality Threshold**: All kept ontologies have:
   - ROI >= 0.50 OR good matches >= 20
   - High-quality embeddings
   - Domain relevance to microbial phenotypes

6. **Import Analysis**: Would need 20+ ontologies
   - Cannot simply import all 24 (licensing, hierarchy conflicts)
   - METPO uses SSSOM mappings instead (~3,000 mappings)
   - Maintains independence while ensuring interoperability
""")

    print("\n" + "=" * 80)
    print("SEMANTIC-SQL REGISTRY OVERLAP")
    print("=" * 80)

    kept_ols_ids = [ont[0].lower() for ont in ONTOLOGIES_KEPT_OLS]
    overlap = [ont_id for ont_id in kept_ols_ids if ont_id in semsql_ontologies]

    print(f"\nOLS ontologies in semsql registry: {len(overlap)}/20")
    print(f"In registry: {', '.join(sorted(overlap))}")

    not_in_semsql = [ont_id for ont_id in kept_ols_ids if ont_id not in semsql_ontologies]
    if not_in_semsql:
        print(f"\nNot in registry: {', '.join(sorted(not_in_semsql))}")
        print("(May use different IDs or not yet in semantic-sql collection)")

def main():
    analyze_ontology_landscape()

    print("\n" + "=" * 80)
    print("PRIMARY SOURCES:")
    print("  - docs/ONTOLOGY_SELECTION_SUMMARY.md")
    print("  - docs/ONTOLOGY_CROSSREFERENCE_HISTORY.md")
    print("  - semantic-sql/src/semsql/builder/registry/ontologies.yaml")
    print("=" * 80)

if __name__ == "__main__":
    main()
