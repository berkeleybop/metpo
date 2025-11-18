"""
Comprehensive workflow to fetch definition source metadata from OLS and BioPortal.

Tries multiple strategies:
1. BioPortal D3O ontology direct lookup for DSMZ terms (prioritized)
2. OLS API for standard ontology terms
3. BioPortal search API for terms not in OLS

Usage:
    export BIOPORTAL_API_KEY='your-api-key-here'
    python3 fetch_all_source_metadata_fixed.py <sparql_output.tsv>
"""

import csv
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

BIOPORTAL_API_KEY = os.environ.get("BIOPORTAL_API_KEY", "")


def iri_to_curie(iri: str) -> str:
    """Convert IRI to CURIE if possible."""
    if "purl.obolibrary.org/obo/" in iri:
        local_part = iri.split("purl.obolibrary.org/obo/")[-1]
        if "_" in local_part:
            prefix, local_id = local_part.split("_", 1)
            return f"{prefix}:{local_id}"
    return iri


def curie_to_iri(curie_or_url: str) -> str:
    """Convert CURIE to IRI for OLS lookup."""
    if curie_or_url.startswith(("http://", "https://")):
        return curie_or_url

    if ":" not in curie_or_url:
        return curie_or_url

    prefix, local_id = curie_or_url.split(":", 1)
    prefix_upper = prefix.upper()

    obo_ontologies = [
        "GO",
        "CHEBI",
        "PATO",
        "OBI",
        "UBERON",
        "CL",
        "SO",
        "BFO",
        "IAO",
        "RO",
        "ENVO",
        "HP",
        "MONDO",
        "DOID",
        "NCBITaxon",
        "OMP",
        "MICRO",
        "PHIPO",
        "MPO",
        "OBA",
        "BTO",
        "DDANAT",
        "ECOCORE",
        "MEO",
        "NCIT",
        "OGMS",
        "OHMI",
        "PO",
        "TO",
        "ZFA",
        "APOLLO_SV",
        "FBcv",
        "WBPhenotype",
        "UPHENO",
        "IDO",
    ]

    if prefix_upper in obo_ontologies:
        return f"http://purl.obolibrary.org/obo/{prefix_upper}_{local_id}"

    if prefix == "MetaCyc":
        return f"http://identifiers.org/metacyc.compound/{local_id}"

    if prefix_upper == "WD":
        return f"http://www.wikidata.org/entity/{local_id}"

    return f"http://purl.obolibrary.org/obo/{prefix_upper}_{local_id}"


def get_ontology_from_curie(curie: str) -> str | None:
    """Extract ontology prefix from CURIE for OLS lookup."""
    if ":" not in curie:
        return None

    prefix = curie.split(":", 1)[0].lower()

    ontology_map = {
        "go": "go",
        "chebi": "chebi",
        "pato": "pato",
        "obi": "obi",
        "bfo": "bfo",
        "envo": "envo",
        "omp": "omp",
        "micro": "micro",
        "mpo": "mpo",
        "phipo": "phipo",
        "oba": "oba",
        "bto": "bto",
        "ncit": "ncit",
        "ogms": "ogms",
        "ddanat": "ddanat",
        "ecocore": "ecocore",
        "meo": "meo",
        "ohmi": "ohmi",
        "po": "po",
        "to": "to",
        "zfa": "zfa",
        "apollo_sv": "apollo_sv",
        "fbcv": "fbcv",
        "wbphenotype": "wbphenotype",
        "iao": "iao",
        "ro": "ro",
        "uberon": "uberon",
        "cl": "cl",
        "so": "so",
        "hp": "hp",
        "mondo": "mondo",
        "doid": "doid",
        "ncbitaxon": "ncbitaxon",
        "upheno": "upheno",
        "ido": "ido",
    }

    return ontology_map.get(prefix)


def fetch_metadata_from_bioportal_d3o(iri: str) -> dict | None:
    """Fetch DSMZ term directly from BioPortal D3O ontology."""
    if not BIOPORTAL_API_KEY:
        return None

    # Only try D3O for DSMZ IRIs
    if "purl.dsmz.de" not in iri:
        return None

    try:
        # BioPortal pattern: /ontologies/{ACRONYM}/classes/{encoded_iri}
        # Single encoding - correct domain is data.bioontology.org
        encoded_iri = quote(iri, safe="")
        url = f"https://data.bioontology.org/ontologies/D3O/classes/{encoded_iri}"

        params = {"apikey": BIOPORTAL_API_KEY}
        response = requests.get(url, params=params, timeout=15)

        if response.status_code != 200:
            return None

        data = response.json()
        label = data.get("prefLabel", "")

        # Extract definition
        definition = ""
        if "definition" in data:
            defs = data["definition"]
            if isinstance(defs, list) and defs:
                definition = defs[0]
            elif isinstance(defs, str):
                definition = defs

        # Extract synonyms
        synonyms = []
        if "synonym" in data:
            syns = data["synonym"]
            if isinstance(syns, list):
                synonyms = syns
            elif isinstance(syns, str):
                synonyms = [syns]

        return {
            "label": label,
            "definition": definition,
            "synonyms": synonyms,
            "source": "BioPortal-D3O",
        }

    except Exception:
        return None


def fetch_metadata_from_ols(curie: str, iri: str) -> dict | None:
    """Fetch comprehensive metadata from OLS4 API."""
    try:
        ontology = get_ontology_from_curie(curie)
        if not ontology:
            return None

        encoded_iri = quote(quote(iri, safe=""), safe="")
        url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/{encoded_iri}"

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        label = data.get("label", "")

        # Extract definition
        definition = ""
        if data.get("description"):
            definition = (
                data["description"][0]
                if isinstance(data["description"], list)
                else data["description"]
            )

        if not definition and "annotation" in data:
            annotations = data["annotation"]
            if "definition" in annotations:
                defs = annotations["definition"]
                definition = defs[0] if isinstance(defs, list) and defs else defs
            elif "IAO:0000115" in annotations:
                defs = annotations["IAO:0000115"]
                definition = defs[0] if isinstance(defs, list) and defs else defs

        # Extract synonyms
        synonyms = set()
        if data.get("synonyms"):
            synonyms.update(data["synonyms"])

        if "annotation" in data:
            annotations = data["annotation"]
            for syn_type in [
                "hasExactSynonym",
                "hasRelatedSynonym",
                "hasBroadSynonym",
                "hasNarrowSynonym",
            ]:
                if syn_type in annotations:
                    syns = annotations[syn_type]
                    if isinstance(syns, list):
                        synonyms.update(syns)
                    else:
                        synonyms.add(syns)

        return {
            "label": label,
            "definition": definition,
            "synonyms": sorted(synonyms),
            "source": "OLS",
        }

    except Exception:
        return None


def fetch_metadata_from_bioportal_search(curie: str, iri: str) -> dict | None:
    """Fetch metadata from BioPortal search API."""
    if not BIOPORTAL_API_KEY:
        return None

    try:
        url = "https://data.bioontology.org/search"
        params = {
            "q": iri,
            "apikey": BIOPORTAL_API_KEY,
            "require_exact_match": "true",
            "also_search_properties": "true",
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get("collection"):
            return None

        result = data["collection"][0]
        label = result.get("prefLabel", "")
        definition = ""
        synonyms = []

        # Fetch full term details
        if "@id" in result:
            term_url = result["@id"]
            term_response = requests.get(term_url, params={"apikey": BIOPORTAL_API_KEY}, timeout=15)

            if term_response.status_code == 200:
                term_data = term_response.json()

                # Extract definition
                if "definition" in term_data:
                    defs = term_data["definition"]
                    definition = defs[0] if isinstance(defs, list) and defs else defs

                # Extract synonyms
                if "synonym" in term_data:
                    syns = term_data["synonym"]
                    synonyms = syns if isinstance(syns, list) else [syns]

        return {
            "label": label,
            "definition": definition,
            "synonyms": synonyms,
            "source": "BioPortal-Search",
        }

    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_all_source_metadata_fixed.py <sparql_output.tsv>")
        print()
        print("Set BIOPORTAL_API_KEY environment variable for BioPortal fallback:")
        print("  export BIOPORTAL_API_KEY='your-key-here'")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "/tmp/source_metadata_complete.tsv"

    print("=" * 80)
    print("COMPREHENSIVE SOURCE METADATA FETCHING WORKFLOW")
    print("=" * 80)
    print()
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print()

    if BIOPORTAL_API_KEY:
        print(f"✓ BioPortal API key found ({BIOPORTAL_API_KEY[:10]}...)")
    else:
        print("⚠ No BioPortal API key - only OLS will be used")
        print("  Set with: export BIOPORTAL_API_KEY='your-key-here'")
    print()

    # Load unique sources
    sources = set()
    with Path(input_file).open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            source = row.get("?definition_source", "").strip()
            if source.startswith("<") and source.endswith(">"):
                source = source[1:-1]
            if source and not source.startswith("?"):
                sources.add(source)

    # Sort sources: DSMZ first, then alphabetical
    dsmz_sources = sorted([s for s in sources if "purl.dsmz.de" in s])
    other_sources = sorted([s for s in sources if "purl.dsmz.de" not in s])
    sorted_sources = dsmz_sources + other_sources

    print(f"Total unique sources: {len(sources)}")
    print(f"  - DSMZ sources: {len(dsmz_sources)} (prioritized)")
    print(f"  - Other sources: {len(other_sources)}")
    print()

    # Fetch metadata
    results = []
    bioportal_d3o_success = 0
    ols_success = 0
    bioportal_search_success = 0
    failed = []

    for i, source_iri in enumerate(sorted_sources, 1):
        source_curie = iri_to_curie(source_iri)

        print(f"[{i}/{len(sources)}] {source_curie}")
        if source_iri != source_curie:
            print(f"  IRI: {source_iri}")

        metadata = None

        # Strategy 1: Try BioPortal D3O for DSMZ terms FIRST
        if "purl.dsmz.de" in source_iri:
            metadata = fetch_metadata_from_bioportal_d3o(source_iri)
            if metadata and metadata["label"]:
                bioportal_d3o_success += 1

        # Strategy 2: Try OLS
        if not (metadata and metadata["label"]):
            metadata = fetch_metadata_from_ols(source_curie, source_iri)
            if metadata and metadata["label"]:
                ols_success += 1

        # Strategy 3: Try BioPortal general search
        if not (metadata and metadata["label"]) and BIOPORTAL_API_KEY:
            print("  → Trying BioPortal search...")
            time.sleep(0.5)
            metadata = fetch_metadata_from_bioportal_search(source_curie, source_iri)
            if metadata and metadata["label"]:
                bioportal_search_success += 1

        if metadata and metadata["label"]:
            synonyms_str = "|".join(metadata["synonyms"]) if metadata["synonyms"] else ""

            results.append(
                {
                    "source_curie": source_curie,
                    "source_iri": source_iri,
                    "label": metadata["label"],
                    "definition": metadata["definition"],
                    "synonyms": synonyms_str,
                    "api_source": metadata["source"],
                }
            )

            print(f"  ✓ [{metadata['source']}] {metadata['label']}")
            if metadata["definition"]:
                print(f"    Definition: {metadata['definition'][:80]}...")
            if metadata["synonyms"]:
                print(f"    Synonyms: {len(metadata['synonyms'])} found")
        else:
            failed.append(source_curie)
            results.append(
                {
                    "source_curie": source_curie,
                    "source_iri": source_iri,
                    "label": "",
                    "definition": "",
                    "synonyms": "",
                    "api_source": "NOT_FOUND",
                }
            )
            print("  ✗ Not found in any API")

        time.sleep(0.2)
        print()

    # Save results
    with Path(output_file).open("w", newline="") as f:
        fieldnames = ["source_curie", "source_iri", "label", "definition", "synonyms", "api_source"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(results)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sources: {len(sources)}")
    total_success = ols_success + bioportal_search_success + bioportal_d3o_success
    print(
        f"Successfully resolved: {total_success} ({total_success * 100 // len(sources) if sources else 0}%)"
    )
    print(f"  - via BioPortal D3O: {bioportal_d3o_success}")
    print(f"  - via OLS: {ols_success}")
    print(f"  - via BioPortal search: {bioportal_search_success}")
    print(f"Failed to resolve: {len(failed)}")
    print()
    print(f"✓ Saved results to {output_file}")
    print()

    if failed:
        print("Failed sources:")
        for source in failed[:20]:
            print(f"  - {source}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")


if __name__ == "__main__":
    main()
