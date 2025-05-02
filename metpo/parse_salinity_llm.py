#!/usr/bin/env python
"""
parse_salinity_llm.py

Deduplicate salinity rows on (raw_text, predicate), pass each unique pair to an
LLM via Pydantic‑AI, validate the reply, then expand back to the full table.

Run:
$ poetry run python parse_salinity_llm.py \
      --input-csv salinity_raw_text_input.csv \
      --output-tsv salinity_parsed_llm.tsv \
      --llm-model openai/gpt-4o-mini \
      --env-file .env \
      --batch-size 20
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
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
# Pydantic schema returned by the LLM
###############################################################################


class SalinityRecord(BaseModel):
    """Structured salinity information extracted from free text."""

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
# Distilled system prompt
###############################################################################

SYSTEM_GUIDANCE = """
You parse salinity descriptions. Return a JSON dict matching SalinityRecord.
• Units: %, g/L, mM, M, µM, ppm; none → "unknown".
• Ranges: X–Y, X to Y, between X and Y. Relational: > X, ≤ X, up to X.
• (w/v), (vol/vol), (wt/vol) → concentration_qualifier.
• (weak), "lag phase", "exponential growth" → growth_qualifier.
• Chemical entities: NaCl, KCl, LiCl, MgCl₂, CaCl₂, MgSO₄, NaBr, NaNO₃,
  artificial sea water, ASW, marine salts, brine, sea water, or salt formulas.
• growth_response: "grows" / "does not grow" (infer from predicate or text).
Return valid JSON only, no commentary.
"""

###############################################################################
# Helper for growth_response inference
###############################################################################

GROW_HINTS = {"grows", "(grows)"}
NO_GROW_HINTS = {"does_not_grow", "no_growth", "(does_not_grow)"}


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
@click.option(
    "--input-csv",
    "-i",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="CSV with 'raw_text' and 'predicate' columns.",
)
@click.option(
    "--output-tsv",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default="salinity_parsed_llm.tsv",
    show_default=True,
    help="Destination TSV path.",
)
@click.option(
    "--llm-model",
    default=None,
    help="Provider/model string (overrides LITELLM_MODEL env var).",
)
@click.option(
    "--env-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to .env containing API keys and default model.",
)
@click.option(
    "--batch-size",
    default=20,
    show_default=True,
    help="How many unique pairs per LLM call.",
)
def main(
        input_csv: Path,
        output_tsv: Path,
        llm_model: Optional[str],
        env_file: Optional[Path],
        batch_size: int,
) -> None:
    """Parse salinity data through an LLM and emit a validated TSV."""
    # Load env if supplied
    if env_file:
        load_dotenv(env_file)

    model_name = llm_model or os.getenv("LITELLM_MODEL")
    if not model_name:
        click.echo("❌ No model specified via --llm-model or LITELLM_MODEL.", err=True)
        sys.exit(1)

    agent = Agent(
        model=model_name,
        output_type=list[SalinityRecord],  # expect JSON array → list[SalinityRecord]
        instructions=SYSTEM_GUIDANCE,
    )

    # Load and dedup
    df = pd.read_csv(input_csv)
    if not {"raw_text", "predicate"}.issubset(df.columns):
        click.echo("❌ CSV must contain 'raw_text' and 'predicate'.", err=True)
        sys.exit(1)

    dedup_df = df.drop_duplicates(subset=["raw_text", "predicate"])
    click.echo(
        f"Rows: {len(df):,}  •  Unique pairs: {len(dedup_df):,}"
    )

    parsed_records: List[SalinityRecord] = []

    n_batches = (len(dedup_df) + batch_size - 1) // batch_size
    for b in trange(n_batches, desc="LLM batches processed"):
        start = b * batch_size
        batch = dedup_df.iloc[start: start + batch_size]
        prompt_lines = [
            json.dumps(
                {
                    "raw_text": rec.raw_text,
                    "predicate": rec.predicate.split("/")[-1],
                },
                ensure_ascii=False,
            )
            for rec in batch.itertuples()
        ]
        prompt = "\n".join(prompt_lines)

        async def _call_llm() -> List[SalinityRecord]:
            result = await agent.run(user_prompt=prompt)
            return getattr(result, "output", result)

        try:
            batch_results: List[SalinityRecord] = asyncio.run(_call_llm())
        except Exception as exc:  # noqa: BLE001
            click.echo(
                f"⚠️  LLM failure on rows {start}-{start + batch_size}: {exc}",
                err=True,
            )
            continue

        for inp_json, rec in zip(prompt_lines, batch_results):
            if rec.growth_response is None:
                payload = json.loads(inp_json)
                rec.growth_response = growth_from_predicate(payload["predicate"])
            parsed_records.append(rec)

    click.echo(f"Parsed {len(parsed_records):,} unique records.")

    # Expand back and save
    parsed_df = pd.DataFrame([r.model_dump() for r in parsed_records])
    merged = df.merge(parsed_df, on="raw_text", how="left", suffixes=("", "_parsed"))
    merged.to_csv(output_tsv, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)
    click.echo(f"✅ Wrote {output_tsv} ({len(merged):,} rows).")


if __name__ == "__main__":
    main()
