#!/usr/bin/env python
"""
parse_salinity_llm.py
=====================

Deduplicate (raw_text, predicate) pairs, send each unique pair to an LLM
(OpenAI o‑series via LiteLLM / Pydantic‑AI), validate into SalinityRecord
objects, expand back to the full table, and write a TSV.

Improvements v1.2 (2025‑05‑02)
• --max-rows option for quick test runs
• tqdm progress bar
• Pre‑clean thin‑space, “g 1^-1” → g/L, normalize ASW ↔ artificial sea water
• Qualifier map: wt/vol, v/w → w/v
• Added 'broth' to chemical_entities
• Validator log for soft issues → salinity_validation_errors.tsv
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import click
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from tqdm import trange


###############################################################################
# Pydantic schema
###############################################################################


class SalinityRecord(BaseModel):
    raw_text: str
    concentration_value: Optional[float] = Field(None, ge=0)
    concentration_range_min: Optional[float] = Field(None, ge=0)
    concentration_range_max: Optional[float] = Field(None, ge=0)
    concentration_unit: str
    concentration_qualifier: Optional[str] = None
    growth_qualifier: Optional[str] = None
    chemical_entities: Optional[str] = None
    growth_response: Optional[str] = None
    categorical_description: Optional[str] = None
    taxon_constraints: Optional[str] = None
    unparsed_text: Optional[str] = None


###############################################################################
# Prompt
###############################################################################

SYSTEM_GUIDANCE = """
Return ONLY a JSON dict that fits the SalinityRecord schema.

Core rules
----------
• Units: %, g/L, mM, M, µM, ppm; none → concentration_unit="unknown".
• Ranges: X–Y, X to Y, between X and Y.
  Relational: >X (lower‑bound); <X or up to X (upper‑bound).
• Lists or 'or' clauses → split into SEPARATE JSON rows.

Qualifiers
----------
• Normalize wt/vol, vol/vol, v/w → w/v   (store in concentration_qualifier)
• Growth qualifiers include: weak, lag phase, exponential growth, stationary
  phase.  Words 'optimum', 'range', 'most', 'all', 'near' are NOT qualifiers.

Chemical entities
-----------------
Allowed list (case‑insensitive):
  NaCl, KCl, LiCl, MgCl₂, CaCl₂, MgSO₄, NaBr, NaNO₃,
  broth, artificial sea water (ASW), marine salts, brine, sea water
  OR a salt formula like LiCl.
– If NONE of these appear in raw_text leave chemical_entities blank.
– Never combine multiple salts in one row; split mixed statements.

Normalisations
--------------
• ASW ↔ artificial sea water  → string exactly "artificial sea water".
• Normalize thin spaces and "g 1^-1" → g/L.

Field placement
---------------
• 'halophilic', 'slightly halophilic' → categorical_description.
• 'optimum' is ignored (do NOT place in any field).
• Parenthetical phrases like "(most strains)", "(some isolates)"
  → taxon_constraints.
• Any leftover tokens that don't fit the schema → unparsed_text.

If NONE of the allowed chemical terms are present, leave chemical_entities
blank.  Do NOT guess NaCl.

Capture parenthetical phrases containing the word "strain" or "isolate"
(e.g. "(most strains)") and copy to taxon_constraints.

If you cannot map a token, copy it to unparsed_text so reviewers can see it.

Split comma‑ or "or"‑separated numeric parts into separate rows even
inside relational phrases (e.g. "below 3 %, above 18 %").

Return valid JSON only; do not add prose.
"""

###############################################################################
# Helper functions
###############################################################################

GROW_HINTS = {"grows", "(grows)"}
NO_GROW_HINTS = {"does_not_grow", "no_growth", "(does_not_grow)"}

QUAL_MAP = {
    "wt/vol": "w/v",
    "w/v": "w/v",
    "vol/vol": "w/v",
    "v/w": "w/v",
}

CHEM_NORMALISE = {
    "asw": "artificial sea water",
    "artificial sea water": "artificial sea water",
}

THIN_SPACE_RE = re.compile(r"[\u2009\u202f]")
G1_RE = re.compile(r"g\s*1\^?-?l", flags=re.I)


def pre_clean(text: str) -> str:
    text = THIN_SPACE_RE.sub(" ", text)
    text = G1_RE.sub("g/L", text)
    return text.strip()


def normalise_qualifier(q: Optional[str]) -> Optional[str]:
    if not q:
        return None
    parts = [QUAL_MAP.get(p.strip().lower(), p.strip().lower())
             for p in re.split(r"[|,]", q)]
    return "|".join(sorted(set(parts)))


def normalise_chem(chem: Optional[str]) -> Optional[str]:
    if not chem:
        return None
    parts = [CHEM_NORMALISE.get(p.strip().lower(), p.strip().lower())
             for p in re.split(r"[|,]", chem)]
    return "|".join(sorted(set(parts)))


def growth_from_predicate(predicate: str) -> Optional[str]:
    frag = predicate.split("/")[-1].lower()
    if any(k in frag for k in GROW_HINTS):
        return "grows"
    if any(k in frag for k in NO_GROW_HINTS):
        return "does not grow"
    return None


###############################################################################
# CLI
###############################################################################


@click.command()
@click.option("--input-csv", "-i",
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              required=True, help="CSV with 'raw_text' and 'predicate'.")
@click.option("--output-tsv", "-o",
              type=click.Path(dir_okay=False, path_type=Path),
              default="salinity_parsed_llm.tsv", show_default=True,
              help="Destination TSV.")
@click.option("--llm-model", default=None,
              help="Provider/model string (default from LITELLM_MODEL).")
@click.option("--env-file",
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              default=None, help="Path to .env with API keys.")
@click.option("--batch-size", default=40, show_default=True,
              help="Unique pairs per LLM call.")
@click.option("--max-rows", default=None, type=int,
              help="Process only first N dedup rows (debug).")
def main(input_csv: Path, output_tsv: Path, llm_model: Optional[str],
         env_file: Optional[Path], batch_size: int,
         max_rows: Optional[int]) -> None:
    """Parse salinity data through an LLM and emit a validated TSV."""
    if env_file:
        load_dotenv(env_file)

    model_name = llm_model or os.getenv("LITELLM_MODEL") or "o4-mini"

    agent = Agent(model=model_name,
                  output_type=list[SalinityRecord],
                  instructions=SYSTEM_GUIDANCE)

    df = pd.read_csv(input_csv)
    if not {"raw_text", "predicate"}.issubset(df.columns):
        click.echo("❌ CSV missing 'raw_text' or 'predicate'.", err=True)
        sys.exit(1)

    df["raw_text"] = df["raw_text"].astype(str).map(pre_clean)
    dedup_df = df.drop_duplicates(subset=["raw_text", "predicate"])
    if max_rows:
        dedup_df = dedup_df.head(max_rows)
    click.echo(f"Rows: {len(df):,}  •  Unique pairs: {len(dedup_df):,}")

    parsed: List[SalinityRecord] = []
    n_batches = (len(dedup_df) + batch_size - 1) // batch_size

    for b in trange(n_batches, desc="LLM"):
        start = b * batch_size
        batch = dedup_df.iloc[start:start + batch_size]
        prompt = "\n".join(
            json.dumps({"raw_text": r.raw_text,
                        "predicate": r.predicate.split("/")[-1]},
                       ensure_ascii=False)
            for r in batch.itertuples())
        try:
            result = asyncio.run(agent.run(user_prompt=prompt))
            batch_recs: List[SalinityRecord] = result.output  # type: ignore
        except Exception as exc:  # noqa: BLE001
            click.echo(f"\n⚠️  Batch {b} failed: {exc}", err=True)
            continue

        for inp_json, rec in zip(prompt.splitlines(), batch_recs):
            # ── 1 Qualifier normalisation ───────────────────────────────────────────
            rec.concentration_qualifier = normalise_qualifier(
                rec.concentration_qualifier)

            # ── 2 Chemical entity cleanup / ASW ↔ artificial sea water ─────────────
            if rec.chemical_entities:
                ent_list = [e.strip() for e in re.split(r"[|,]", rec.chemical_entities)]
                ent_list = [CHEM_NORMALISE.get(e.lower(), e) for e in ent_list]
                raw_lower = rec.raw_text.lower()
                ent_list = [e for e in ent_list if e.lower() in raw_lower]  # tighter match
                rec.chemical_entities = "|".join(sorted(set(ent_list))) or None

            # ── 3 Taxon constraint fallback (parenthetical) ────────────────────────
            if not rec.taxon_constraints:
                m = re.search(r"\(([^)]*strain[s]?[^)]*)\)", rec.raw_text, flags=re.I)
                if m:
                    rec.taxon_constraints = m.group(1).strip()

            # ── 4 Growth_response fallback from predicate ───────────────────────────
            if rec.growth_response is None:
                pred = json.loads(inp_json)["predicate"]
                rec.growth_response = growth_from_predicate(pred)

            # ── 5 Split comma‑lists the model missed (simple heuristic) ────────────
            added_rows: list[SalinityRecord] = []
            if "," in rec.raw_text or " or " in rec.raw_text.lower():
                values = re.findall(r"\d+\.?\d*", rec.raw_text)
                if len(values) > 1 and rec.concentration_value is not None:
                    for v in values[1:]:
                        clone = rec.model_copy()
                        clone.concentration_value = float(v)
                        added_rows.append(clone)

            parsed.append(rec)
            parsed.extend(added_rows)

    click.echo(f"\nParsed {len(parsed):,} unique records.")

    # Soft‑issue validator
    errors = [r.model_dump() for r in parsed
              if (r.concentration_unit == "unknown"
                  and r.concentration_value is None
                  and r.concentration_range_min is None)
              or (r.concentration_value is None
                  and r.concentration_range_min is None)
              or r.unparsed_text]

    if errors:
        err_path = output_tsv.with_name("salinity_validation_errors.tsv")
        pd.DataFrame(errors).to_csv(err_path, sep="\t", index=False)
        click.echo(f"⚠️  Wrote {len(errors):,} validator rows → {err_path}")

    parsed_df = pd.DataFrame([r.model_dump() for r in parsed])
    merged = df.merge(parsed_df, on="raw_text", how="left",
                      suffixes=("", "_parsed"))
    merged.to_csv(output_tsv, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)
    click.echo(f"✅ Wrote {output_tsv} ({len(merged):,} rows).")


if __name__ == "__main__":
    main()
