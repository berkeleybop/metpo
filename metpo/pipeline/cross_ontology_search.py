"""Find cross-ontology matches for METPO terms using OLS4 search + local embeddings.

This is the working, dependency-light replacement for the removed ChromaDB tooling.
It needs no paid model, no API key, and no 300GB OLS SQLite. The acknowledged future
direction is to lean on established LinkML-ecosystem tools (not blocking, tracked):
OAK/oaklib (#194) for ontology access + SSSOM + similarity, linkml-store (#364) for
embedding indexes with local models via the `llm` library, and the OLS4 embeddings
API for server-side semantic search. For each METPO term it:

1. retrieves candidate classes from the EBI OLS4 search API (covers ~270 ontologies),
2. re-ranks the candidates by semantic similarity using a LOCAL embedding model
   served by Ollama (default: nomic-embed-text, runs on the M5 GPU; no OpenAI, no
   300GB OLS SQLite, no ChromaDB),

and emits, per match: the external IRI/CURIE, label, definition, ontology, and a
cosine-similarity score. Those rows give you three things at once:

* **definition sources / gap-filling** -- the matched term's definition,
* **cross-ontology mappings** -- the matched CURIE (SSSOM candidate),
* **synonym candidates** -- the matched label.

For ontologies OLS does not host (BioPortal-only, e.g. MicrO/MPO/D3O), download
them with `make download-external-bioportal-ontologies` and point a future
linkml-store index at them; the same local-embedding ranking applies.
"""

import csv
import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import click

OLS_SEARCH = "https://www.ebi.ac.uk/ols4/api/search"
# Default embedding backend: free, local, runs on the M5 GPU. Nothing paid, no API
# key. Both the endpoint and the model are CLI-parameterized so anyone can point at
# a different local model, a remote Ollama server, or other hardware.
DEFAULT_EMBED_URL = "http://localhost:11434/api/embeddings"
DEFAULT_EMBED_MODEL = "nomic-embed-text"


def ols_candidates(label, rows=20):
    """Lexical candidate classes from OLS4 for a label (IRI, curie, label, def, ontology)."""
    q = urllib.parse.urlencode({"q": label, "type": "class", "rows": rows})
    req = urllib.request.Request(f"{OLS_SEARCH}?{q}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        docs = json.load(r).get("response", {}).get("docs", [])
    out = []
    for d in docs:
        out.append(
            {
                "iri": d.get("iri", ""),
                "curie": d.get("obo_id") or d.get("short_form", ""),
                "label": d.get("label", ""),
                "definition": (d.get("description") or [""])[0]
                if isinstance(d.get("description"), list)
                else (d.get("description") or ""),
                "ontology": d.get("ontology_name", ""),
            }
        )
    return out


def embed(text, model, embed_url=DEFAULT_EMBED_URL):
    """Embed text via an Ollama-compatible /api/embeddings endpoint.

    Defaults to a free local model on this machine. Pass a different ``embed_url``
    (remote Ollama host, another local server) and/or ``model`` to run elsewhere.
    Returns None if the endpoint/model is unavailable (caller falls back gracefully).
    """
    body = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(
        embed_url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("embedding")
    except Exception:
        return None


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def load_terms(metpo_tsv, label, definition):
    """Build the list of {id,label,definition} terms from a TSV or a single label."""
    if label:
        return [{"id": "", "label": label, "definition": definition}]
    terms = []
    with Path(metpo_tsv).open() as f:
        reader = csv.reader(f, delimiter="\t")
        low = [h.lower() for h in next(reader, [])]
        id_i = low.index("id") if "id" in low else 0
        lbl_i = low.index("label") if "label" in low else 1
        def_i = next((i for i, h in enumerate(low) if "definition" in h), None)
        for row in reader:
            if len(row) <= lbl_i or not row[lbl_i].strip():
                continue
            terms.append(
                {
                    "id": row[id_i].strip() if len(row) > id_i else "",
                    "label": row[lbl_i].strip(),
                    "definition": row[def_i].strip() if def_i is not None and len(row) > def_i else "",
                }
            )
    return terms


def rank_candidates(term, cands, use_embeddings, model, embed_url):
    """Attach a 'similarity' score to each candidate (embedding cosine or lexical order)."""
    if use_embeddings and cands:
        qv = embed((term["label"] + ". " + term["definition"]).strip(". "), model, embed_url)
        for c in cands:
            cv = embed((c["label"] + ". " + c["definition"]).strip(". "), model, embed_url)
            c["similarity"] = round(cosine(qv, cv), 4) if (qv and cv) else 0.0
        cands.sort(key=lambda c: c["similarity"], reverse=True)
    else:
        for rank, c in enumerate(cands):
            c["similarity"] = round(1.0 - rank / max(len(cands), 1), 4)
    return cands


COLS = [
    "metpo_id",
    "metpo_label",
    "match_ontology",
    "match_curie",
    "match_iri",
    "match_label",
    "match_definition",
    "similarity",
]


def _write(fh, rows):
    w = csv.DictWriter(fh, fieldnames=COLS, delimiter="\t")
    w.writeheader()
    w.writerows(rows)


def write_matches(rows, output):
    """Write match rows as TSV to ``output`` (path) or stdout."""
    if output:
        with Path(output).open("w", newline="") as fh:
            _write(fh, rows)
    else:
        _write(sys.stdout, rows)


@click.command()
@click.option("--metpo-tsv", "-i", type=click.Path(exists=True, dir_okay=False), help="TSV with ID,LABEL[,definition] columns.")
@click.option("--label", "-l", help="Single METPO term label (alternative to --metpo-tsv).")
@click.option("--definition", "-d", default="", help="Optional definition for the single-label mode (improves ranking).")
@click.option("--output", "-o", type=click.Path(dir_okay=False), help="Output SSSOM-ish TSV (default: stdout).")
@click.option("--rows", default=20, show_default=True, help="OLS candidate classes to retrieve per term.")
@click.option("--top-n", default=5, show_default=True, help="Top matches to keep per term after re-ranking.")
@click.option("--model", default=DEFAULT_EMBED_MODEL, show_default=True, help="Embedding model (free + local by default; any Ollama-served model works).")
@click.option("--embed-url", default=DEFAULT_EMBED_URL, show_default=True, help="Ollama-compatible /api/embeddings endpoint (point at a remote host or other local server to run elsewhere).")
@click.option("--no-embeddings", is_flag=True, help="Skip embeddings entirely; rank by OLS lexical order only.")
@click.option("--min-similarity", default=0.0, show_default=True, type=float, help="Drop matches below this cosine similarity.")
def main(metpo_tsv, label, definition, output, rows, top_n, model, embed_url, no_embeddings, min_similarity):
    """Find cross-ontology matches (definitions/synonyms/mappings) for METPO terms.

    OLS4 search for candidates + local (free) embeddings for ranking. This is the
    working replacement for the removed ChromaDB tooling; OAK/oaklib (#194) and
    linkml-store (#364) are the acknowledged future direction.
    """
    if not metpo_tsv and not label:
        raise click.UsageError("Provide --metpo-tsv or --label.")

    terms = load_terms(metpo_tsv, label, definition)

    use_embeddings = (not no_embeddings) and embed("test", model, embed_url) is not None
    if not no_embeddings and not use_embeddings:
        click.echo(
            f"WARNING: embedding model '{model}' unavailable at {embed_url}; "
            "falling back to OLS lexical order (no semantic re-ranking). Start Ollama "
            f"and `ollama pull {model}`, point --embed-url elsewhere, or pass "
            "--no-embeddings to silence this.",
            err=True,
        )

    out_rows = []
    for t in terms:
        cands = rank_candidates(t, ols_candidates(t["label"], rows=rows), use_embeddings, model, embed_url)
        for c in cands[:top_n]:
            if c["similarity"] < min_similarity:
                continue
            out_rows.append(
                {
                    "metpo_id": t["id"],
                    "metpo_label": t["label"],
                    "match_ontology": c["ontology"],
                    "match_curie": c["curie"],
                    "match_iri": c["iri"],
                    "match_label": c["label"],
                    "match_definition": c["definition"],
                    "similarity": c["similarity"],
                }
            )

    write_matches(out_rows, output)
    if output:
        click.echo(
            f"Wrote {len(out_rows)} matches for {len(terms)} terms to {output} "
            f"({'local embeddings' if use_embeddings else 'lexical order'}).",
            err=True,
        )


if __name__ == "__main__":
    main()
