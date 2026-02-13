"""
Fetch microbial phenotype trait cards from the MetaTraits database (metatraits.embl.de).

Extracts trait names, types, ontology cross-references, and descriptions
from the /traits page and outputs as TSV or JSON for METPO mapping work.

MetaTraits displays each trait as a Bootstrap card element on its /traits page.
This scraper parses those HTML elements to extract structured data. The website
is the only source that publishes ontology CURIEs per trait; the API and bulk
downloads do not include them.
"""

import csv
import json
import re
from pathlib import Path

import click
import requests


def extract_traits(html: str) -> list[dict]:
    """Extract trait data from the MetaTraits /traits HTML page."""
    card_starts = [m.start() for m in re.finditer(r'<div class="card mb-3" id="', html)]

    traits = []
    for i, start in enumerate(card_starts):
        end = card_starts[i + 1] if i + 1 < len(card_starts) else start + 5000
        section = html[start:end]

        card_id = re.search(r'id="([^"]+)"', section).group(1)
        title = re.search(r"<h4[^>]*>(.*?)</h4>", section).group(1).strip()
        badge = re.search(r'rounded-pill">(.*?)</span>', section)
        badge_val = badge.group(1).strip() if badge else ""

        onto_refs = re.findall(r'class="btn btn-cta" href=([^>]+)>([^<]+)</a>', section)

        desc = re.search(r'<p class="card-text[^"]*">(.*?)</p>', section, re.DOTALL)
        desc_text = re.sub(r"<[^>]+>", "", desc.group(1)).strip() if desc else ""

        traits.append(
            {
                "card_id": card_id,
                "name": title,
                "type": badge_val,
                "ontology_refs": [{"curie": r[1].strip(), "url": r[0].strip()} for r in onto_refs],
                "description": desc_text,
            }
        )

    return traits


@click.command()
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output file path (.tsv or .json)",
)
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["tsv", "json"]),
    default=None,
    help="Output format (inferred from extension if not given)",
)
@click.option(
    "--url",
    default="https://metatraits.embl.de/traits",
    show_default=True,
    help="URL of the MetaTraits traits page",
)
def main(output: str, fmt: str | None, url: str):
    """Fetch and extract microbial phenotype trait cards from MetaTraits."""
    if fmt is None:
        fmt = "json" if output.endswith(".json") else "tsv"

    click.echo(f"Fetching traits from {url}...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    traits = extract_traits(resp.text)
    click.echo(f"Extracted {len(traits)} trait cards")

    outpath = Path(output)
    outpath.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        with outpath.open("w") as f:
            json.dump(traits, f, indent=2)
    else:
        with outpath.open("w", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(
                ["card_id", "name", "type", "ontology_curies", "ontology_urls", "description"]
            )
            for t in traits:
                curies = "; ".join(r["curie"] for r in t["ontology_refs"])
                urls = "; ".join(r["url"] for r in t["ontology_refs"])
                w.writerow([t["card_id"], t["name"], t["type"], curies, urls, t["description"]])

    click.echo(f"Wrote {outpath}")


if __name__ == "__main__":
    main()
