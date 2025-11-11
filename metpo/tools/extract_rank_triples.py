"""Extract taxonomy rank triples from NCBI nodes.dmp file.

This tool processes the NCBI taxonomy nodes.dmp file and extracts
taxonomic rank information as RDF triples in Turtle format.
"""

import click
from rdflib import Graph, URIRef, Literal
from tqdm import tqdm

NCBI_TAXON_PREFIX = "http://purl.obolibrary.org/obo/NCBITaxon_"
HAS_RANK_PREDICATE = URIRef("http://purl.obolibrary.org/obo/ncbitaxon#has_rank")


@click.command()
@click.option(
    "--input-file", "-i",
    type=click.Path(exists=True),
    required=True,
    help="Path to nodes.dmp input file"
)
@click.option(
    "--output-file", "-o",
    type=click.Path(writable=True),
    required=True,
    help="Path to output Turtle (.ttl) RDF file"
)
def extract_taxon_ranks(input_file, output_file):
    """Extract RDF triples from NCBI nodes.dmp linking taxon IDs to textual ranks."""
    g = Graph()

    with open(input_file, encoding="utf-8") as f:
        lines = f.readlines()

    for line in tqdm(lines, desc="Processing nodes.dmp"):
        parts = [p.strip() for p in line.split("\t|\t")]
        if len(parts) >= 3:
            tax_id = parts[0]
            rank = parts[2]
            if rank and rank != "no rank":
                subject = URIRef(f"{NCBI_TAXON_PREFIX}{tax_id}")
                g.add((subject, HAS_RANK_PREDICATE, Literal(rank)))

    g.serialize(destination=output_file, format="turtle")
    click.echo(f"✅ RDF triples written to: {output_file}")


if __name__ == "__main__":
    extract_taxon_ranks()
