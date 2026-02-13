"""Demo: map MetaTraits MongoDB records to KGX using official KGX sinks.

Reads from local MongoDB `metatraits.genome_traits` and resolves trait names through
`data/mappings/metatraits_in_sheet_resolution.tsv`.

This is a demonstration utility for external implementers. It intentionally does not
call the MetaTraits API.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Literal

import click
from kgx.sink import JsonlSink, TsvSink
from kgx.transformer import Transformer
from pymongo import MongoClient


def load_resolution_table(path: Path) -> dict[str, dict[str, str]]:
    table: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            trait = (row.get("trait_name") or "").strip()
            if trait:
                table[trait] = row
    return table


def parse_boolean_from_majority_label(label: str) -> bool | None:
    lower = label.strip().lower()
    if lower.startswith("true"):
        return True
    if lower.startswith("false"):
        return False
    return None


def choose_object_curie(ontologies: list[str], row: dict[str, str]) -> str:
    if row.get("mapping_kind") == "composed":
        chebis = [
            curie.strip()
            for curie in (row.get("substrate_chebi_ids") or "").split(";")
            if curie.strip()
        ]
        if chebis:
            return chebis[0]
        for curie in ontologies:
            if curie.startswith("CHEBI:"):
                return curie

    matched = [x.strip() for x in (row.get("matched_process_metpo") or "").split(";") if x.strip()]
    if matched:
        return matched[0].split("|", 1)[0]

    for curie in ontologies:
        if re.match(r"^[A-Za-z][A-Za-z0-9_]+:\S+$", curie):
            return curie
    return ""


def map_record_to_edge(record: dict, row: dict[str, str]) -> dict[str, str] | None:
    majority_label = str(record.get("majority_label", ""))
    bool_value = parse_boolean_from_majority_label(majority_label)
    if bool_value is None:
        return None

    ontologies = [str(x).strip() for x in record.get("ontologies", []) if str(x).strip()]
    mapping_kind = row.get("mapping_kind", "")

    if mapping_kind == "composed":
        predicate = (
            row.get("predicate_positive_id", "")
            if bool_value
            else row.get("predicate_negative_id", "")
        )
    else:
        # Demo fallback for base terms: emit has_phenotype if we have a METPO class match.
        predicate = "biolink:has_phenotype"

    if not predicate:
        return None

    obj = choose_object_curie(ontologies, row)
    if not obj:
        return None

    subject = f"assembly:{record.get('genome_accession', 'unknown')}"
    return {
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "trait_name": str(record.get("name", "")),
        "majority_label": majority_label,
        "knowledge_level": "knowledge_assertion",
        "agent_type": "automated_agent" if record.get("is_ai") else "manual_agent",
        "primary_knowledge_source": ["infores:metatraits"],
    }


def object_category(curie: str) -> list[str]:
    if curie.startswith("CHEBI:"):
        return ["biolink:ChemicalEntity"]
    if curie.startswith("GO:"):
        return ["biolink:BiologicalProcess"]
    if curie.startswith("EC:"):
        return ["biolink:MolecularActivity"]
    if curie.startswith("METPO:"):
        return ["biolink:PhenotypicFeature"]
    return ["biolink:NamedThing"]


def write_kgx(
    nodes: dict[str, dict[str, object]],
    edges: list[dict[str, object]],
    output_prefix: Path,
    output_format: Literal["tsv", "jsonl"],
) -> tuple[Path, Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    transformer = Transformer()
    if output_format == "jsonl":
        sink = JsonlSink(owner=transformer, filename=str(output_prefix))
        nodes_path = output_prefix.with_name(f"{output_prefix.name}_nodes.jsonl")
        edges_path = output_prefix.with_name(f"{output_prefix.name}_edges.jsonl")
    else:
        sink = TsvSink(
            owner=transformer,
            filename=str(output_prefix),
            format="tsv",
            node_properties={"id", "category", "name"},
            edge_properties={
                "subject",
                "predicate",
                "object",
                "trait_name",
                "majority_label",
                "knowledge_level",
                "agent_type",
                "primary_knowledge_source",
            },
        )
        nodes_path = output_prefix.with_name(f"{output_prefix.name}_nodes.tsv")
        edges_path = output_prefix.with_name(f"{output_prefix.name}_edges.tsv")

    for node in nodes.values():
        sink.write_node(node)
    for edge in edges:
        sink.write_edge(edge)
    sink.finalize()

    return nodes_path, edges_path


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017", show_default=True)
@click.option("--db", "db_name", default="metatraits", show_default=True)
@click.option("--collection", default="genome_traits", show_default=True)
@click.option(
    "--resolution-table",
    type=click.Path(path_type=Path, exists=True),
    default=Path("data/mappings/metatraits_in_sheet_resolution.tsv"),
    show_default=True,
)
@click.option("--limit", type=int, default=50, show_default=True)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["tsv", "jsonl"]),
    default="tsv",
    show_default=True,
)
@click.option(
    "--output-prefix",
    type=click.Path(path_type=Path),
    default=Path("data/mappings/demo_metatraits_mongo_kgx"),
    show_default=True,
)
def main(
    mongo_uri: str,
    db_name: str,
    collection: str,
    resolution_table: Path,
    limit: int,
    output_format: Literal["tsv", "jsonl"],
    output_prefix: Path,
) -> None:
    table = load_resolution_table(resolution_table)

    client = MongoClient(mongo_uri)
    coll = client[db_name][collection]

    cursor = coll.find(
        {},
        {
            "_id": 0,
            "name": 1,
            "majority_label": 1,
            "percentages": 1,
            "ontologies": 1,
            "is_ai": 1,
            "genome_accession": 1,
        },
    ).limit(limit)

    edges: list[dict[str, object]] = []
    nodes: dict[str, dict[str, object]] = {}
    missing_mapping = 0
    dropped = 0

    for record in cursor:
        name = str(record.get("name", "")).strip()
        row = table.get(name)
        if not row:
            missing_mapping += 1
            continue
        edge = map_record_to_edge(record, row)
        if edge is None:
            dropped += 1
            continue
        edges.append(edge)
        subject = str(edge["subject"])
        obj = str(edge["object"])
        if subject not in nodes:
            nodes[subject] = {"id": subject, "category": ["biolink:Genome"]}
        if obj not in nodes:
            nodes[obj] = {"id": obj, "category": object_category(obj)}

    nodes_path, edges_path = write_kgx(
        nodes=nodes,
        edges=edges,
        output_prefix=output_prefix,
        output_format=output_format,
    )

    click.echo(f"Read up to {limit} records from {db_name}.{collection}")
    click.echo(f"Mapped nodes: {len(nodes)}")
    click.echo(f"Mapped edges: {len(edges)}")
    click.echo(f"Missing trait mapping rows: {missing_mapping}")
    click.echo(f"Dropped after mapping (no predicate/object): {dropped}")
    click.echo(f"Wrote nodes: {nodes_path}")
    click.echo(f"Wrote edges: {edges_path}")


if __name__ == "__main__":
    main()
