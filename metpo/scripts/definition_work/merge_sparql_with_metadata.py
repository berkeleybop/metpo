#!/usr/bin/env python3
"""
Merge SPARQL query results with fetched API metadata.
"""

import csv

# Read source metadata
source_metadata = {}
with open("/tmp/source_metadata_complete.tsv", "r") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        source_iri = row["source_iri"]
        source_metadata[source_iri] = {
            "label": row.get("label", ""),
            "definition": row.get("definition", ""),
            "synonyms": row.get("synonyms", ""),
            "api_source": row.get("api_source", "")
        }

# Read SPARQL results and merge
with open("/tmp/metpo_sources_current.tsv", "r") as f_in:
    with open("/tmp/metpo_sources_with_metadata.tsv", "w", newline="") as f_out:
        reader = csv.DictReader(f_in, delimiter="\t")

        fieldnames = ["metpo_id", "metpo_label", "metpo_definition", "definition_source_iri",
                      "source_label", "source_definition", "source_synonyms", "source_api"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()

        for row in reader:
            metpo_id = row["?metpo_id"].strip('"')
            metpo_label = row["?label"].strip('"')
            metpo_def = row.get("?definition", "").strip('"')
            source_iri = row.get("?definition_source", "").strip("<>").strip('"')

            # Look up source metadata
            if source_iri in source_metadata:
                meta = source_metadata[source_iri]
                writer.writerow({
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "metpo_definition": metpo_def,
                    "definition_source_iri": source_iri,
                    "source_label": meta["label"],
                    "source_definition": meta["definition"],
                    "source_synonyms": meta["synonyms"],
                    "source_api": meta["api_source"]
                })
            else:
                # Source not found in metadata (shouldn't happen)
                writer.writerow({
                    "metpo_id": metpo_id,
                    "metpo_label": metpo_label,
                    "metpo_definition": metpo_def,
                    "definition_source_iri": source_iri,
                    "source_label": "",
                    "source_definition": "",
                    "source_synonyms": "",
                    "source_api": "NOT_FOUND"
                })

print("✓ Created integrated output: /tmp/metpo_sources_with_metadata.tsv")
