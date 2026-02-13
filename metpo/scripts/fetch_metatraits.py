"""Fetch MetaTraits trait cards and emit structured TSV/JSON outputs.

This scraper targets the /traits catalog, which exposes ontology CURIE links
that are not present in the MetaTraits API or bulk taxonomy exports.
"""

import csv
import html as html_lib
import json
import re
from pathlib import Path

import click
import requests

CARD_START_PATTERN = r'<div class="card mb-3" id="'


def _extract_first(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_traits(html: str) -> list[dict[str, object]]:
    """Extract trait card content from MetaTraits HTML."""
    card_starts = [m.start() for m in re.finditer(CARD_START_PATTERN, html)]
    traits: list[dict[str, object]] = []

    for idx, start in enumerate(card_starts):
        end = card_starts[idx + 1] if idx + 1 < len(card_starts) else len(html)
        section = html[start:end]

        card_id = _extract_first(r'id="([^"]+)"', section)
        name = _extract_first(r"<h4[^>]*>(.*?)</h4>", section)
        trait_type = _extract_first(r'rounded-pill">(.*?)</span>', section)

        description_html = _extract_first(r'<p class="card-text[^\"]*">(.*?)</p>', section)
        # Strip tags and decode HTML entities so downstream matching uses plain text.
        description = html_lib.unescape(re.sub(r"<[^>]+>", "", description_html)).strip()

        ontology_refs = []
        for href, curie in re.findall(r'class="btn btn-cta" href=([^>]+)>([^<]+)</a>', section):
            ontology_refs.append({"curie": curie.strip(), "url": href.strip()})

        if not card_id or not name:
            continue

        traits.append(
            {
                "card_id": card_id,
                "name": name,
                "type": trait_type,
                "ontology_refs": ontology_refs,
                "description": description,
            }
        )

    return traits


@click.command()
@click.option("--output", "-o", required=True, type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["tsv", "json"]),
    default=None,
    help="Output format (inferred from extension when omitted)",
)
@click.option(
    "--url",
    default="https://metatraits.embl.de/traits",
    show_default=True,
    help="MetaTraits traits catalog URL",
)
def main(output: str, fmt: str | None, url: str) -> None:
    """Fetch and parse MetaTraits trait cards from the traits catalog page."""
    if fmt is None:
        fmt = "json" if output.endswith(".json") else "tsv"

    click.echo(f"Fetching {url} ...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    traits = extract_traits(response.text)
    click.echo(f"Extracted {len(traits)} trait cards")

    outpath = Path(output)
    outpath.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        with outpath.open("w", encoding="utf-8") as stream:
            json.dump(traits, stream, indent=2)
    else:
        with outpath.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, delimiter="\t")
            writer.writerow(
                ["card_id", "name", "type", "ontology_curies", "ontology_urls", "description"]
            )
            for trait in traits:
                refs = trait["ontology_refs"]
                curies = "; ".join(ref["curie"] for ref in refs)
                urls = "; ".join(ref["url"] for ref in refs)
                writer.writerow(
                    [
                        trait["card_id"],
                        trait["name"],
                        trait["type"],
                        curies,
                        urls,
                        trait["description"],
                    ]
                )

    click.echo(f"Wrote {outpath}")


if __name__ == "__main__":
    main()
