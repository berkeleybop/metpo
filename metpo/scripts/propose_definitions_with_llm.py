"""
Use LLM to propose definitions for all METPO classes.

Follows Seppälä-Ruttenberg-Smith guidelines:
- Genus-differentia form: "A [genus] that [differentia]"
- Genus = parent class (genus proximus)
- Each part serves as necessary condition
- No circularity, examples, or generalizing expressions

For each METPO term:
1. Load parent classes from hierarchy
2. Check for matched definitions from multiple sources
3. Check current METPO definition
4. Use LLM to synthesize best definition following guidelines
5. Track all source terms used
"""

import csv
import os
from pathlib import Path

import click
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()


DEFINITION_GUIDELINES = """
You are an expert ontology curator creating OBO Foundry-compliant definitions.

CRITICAL GUIDELINES (Seppälä-Ruttenberg-Smith):
1. Use genus-differentia form: "A [genus] that [differentia]"
2. The genus MUST be the parent class provided
3. Each part is a necessary condition (avoid "usually", "generally")
4. NO examples ("such as", "e.g.")
5. NO circularity (don't use the term being defined)
6. Be specific and concise (aim for 50-200 characters)
7. Focus on WHAT it is, not how to measure it

STRUCTURE:
- Start with "A [parent class]" or "An [parent class]"
- Follow with "that", "which", "where", or "in which"
- State the essential differentiating characteristics
- Keep it genus-differentia, not descriptive prose

EXAMPLES:
GOOD: "A cell shape phenotype where the cell is roughly spherical."
BAD: "Describes a cell that looks like a sphere." (no genus, descriptive)

GOOD: "A temperature phenotype that represents the optimal growth condition."
BAD: "The temperature at which growth is best." (no genus)

GOOD: "A trophic process where energy is obtained from light."
BAD: "Organisms that use light for energy." (wrong form, uses examples)
"""


def load_metpo_terms(template_path: Path) -> dict[str, dict]:
    """Load METPO terms with parents and current definitions."""
    terms = {}

    with Path(template_path).open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip row 1
        next(reader)  # Skip row 2

        for row in reader:
            if len(row) < 5:
                continue

            metpo_id = row[0].strip()
            label = row[1].strip()
            parent_str = row[3].strip() if len(row) > 3 else ""
            current_def = row[4].strip() if len(row) > 4 else ""

            if metpo_id:
                parents = [p.strip() for p in parent_str.split("|") if p.strip()]
                terms[metpo_id] = {
                    "label": label,
                    "parents": parents,
                    "current_definition": current_def,
                }

    return terms


def load_matched_definitions(matched_path: Path) -> dict[str, dict]:
    """Load matched definitions from foreign ontologies."""
    matched = {}

    if not matched_path.exists():
        return matched

    with Path(matched_path).open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            metpo_id = row["metpo_id"]
            matched[metpo_id] = row

    return matched


def load_all_candidates(candidates_path: Path) -> dict[str, list[dict]]:
    """Load all candidate definitions (top 5 per term)."""
    candidates = {}

    if not candidates_path.exists():
        return candidates

    with Path(candidates_path).open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            metpo_id = row["metpo_id"]
            if metpo_id not in candidates:
                candidates[metpo_id] = []
            candidates[metpo_id].append(row)

    return candidates


def build_prompt(
    metpo_id: str,
    label: str,
    parents: list[str],
    current_def: str,
    matched_def: dict | None,
    all_candidates: list[dict],
) -> str:
    """Build LLM prompt for definition proposal."""

    prompt = f"""Create an OBO Foundry-compliant definition for this ontology term.

TERM: {metpo_id} "{label}"

PARENT CLASS(ES): {", ".join(parents) if parents else "[ROOT CLASS]"}
(Your definition's genus MUST be one of these parents)

"""

    if current_def:
        prompt += f"""CURRENT METPO DEFINITION:
{current_def}

"""

    if matched_def:
        prompt += f"""BEST MATCHED DEFINITION (from {matched_def.get("source_ontology", "unknown")}):
{matched_def.get("definition", "")}
Quality: {matched_def.get("quality_label", "unknown")}

"""

    if all_candidates:
        prompt += "OTHER CANDIDATE DEFINITIONS:\n"
        for i, cand in enumerate(all_candidates[:3], 1):
            prompt += (
                f"{i}. [{cand.get('source_ontology', '?')}] {cand.get('definition', '')[:100]}...\n"
            )
        prompt += "\n"

    prompt += """TASK:
Write a NEW definition that:
1. Uses the parent class as genus: "A [parent] that..." or "An [parent] that..."
2. States the essential differentiating characteristics
3. Follows all Seppälä-Ruttenberg-Smith guidelines
4. Is concise (50-200 characters ideal)

If the parent is a multi-word phrase like "temperature phenotype with numerical limits",
you can simplify to just the core concept (e.g., "temperature phenotype") for readability.

Respond with ONLY the definition text, nothing else.
"""

    return prompt


@click.command()
@click.option(
    "--metpo-terms",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    default="src/templates/metpo_sheet.tsv",
    help="Path to METPO terms template",
)
@click.option(
    "--best-definitions",
    "-b",
    type=click.Path(path_type=Path),
    default="reports/best_definition_per_term_final.tsv",
    help="Path to best matched definitions",
)
@click.option(
    "--all-candidates",
    "-c",
    type=click.Path(path_type=Path),
    default="reports/comprehensive_definition_candidates.tsv",
    help="Path to all candidate definitions",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/llm_proposed_definitions.tsv",
    help="Output TSV with proposed definitions",
)
@click.option("--model", "-m", default="gpt-4", help="OpenAI model to use")
@click.option(
    "--limit", type=int, default=None, help="Limit number of terms to process (for testing)"
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def main(
    metpo_terms: Path,
    best_definitions: Path,
    all_candidates: Path,
    output: Path,
    model: str,
    limit: int | None,
    verbose: bool,
):
    """
    Use LLM to propose definitions for all METPO classes.

    Follows Seppälä-Ruttenberg-Smith guidelines and METPO hierarchy.
    """

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        click.echo("Error: OPENAI_API_KEY not found in environment", err=True)
        click.echo("Please set it in your .env file", err=True)
        return 1

    client = OpenAI(api_key=api_key)

    # Load data
    click.echo(f"Loading METPO terms from {metpo_terms}...")
    metpo_data = load_metpo_terms(metpo_terms)
    click.echo(f"Loaded {len(metpo_data)} METPO terms")

    click.echo("\nLoading matched definitions...")
    matched_defs = load_matched_definitions(best_definitions)
    click.echo(f"Loaded {len(matched_defs)} matched definitions")

    click.echo("\nLoading all candidates...")
    all_cands = load_all_candidates(all_candidates)
    click.echo(f"Loaded candidates for {len(all_cands)} terms")

    # Process each term
    results = []
    processed = 0

    click.echo(f"\nProcessing terms with {model}...")
    click.echo("(This may take a few minutes)\n")

    for metpo_id in sorted(metpo_data.keys()):
        if limit and processed >= limit:
            break

        term = metpo_data[metpo_id]
        label = term["label"]
        parents = term["parents"]
        current_def = term["current_definition"]

        matched = matched_defs.get(metpo_id)
        candidates = all_cands.get(metpo_id, [])

        # Build prompt
        prompt = build_prompt(metpo_id, label, parents, current_def, matched, candidates)

        if verbose:
            click.echo(f"\n{metpo_id} ({label})")
            click.echo(f"  Parents: {', '.join(parents) if parents else '[ROOT]'}")

        # Call LLM
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": DEFINITION_GUIDELINES},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=300,
            )

            proposed_def = response.choices[0].message.content.strip()

            # Remove quotes if LLM added them
            if proposed_def.startswith('"') and proposed_def.endswith('"'):
                proposed_def = proposed_def[1:-1]

            if verbose:
                click.echo(f"  Current: {current_def[:60] if current_def else '[NONE]'}...")
                click.echo(f"  Proposed: {proposed_def[:80]}...")
            else:
                status = "✓" if current_def else "+"
                click.echo(f"{status} {metpo_id:20s} {label:40s}")

            # Track sources
            sources_used = []
            if matched:
                sources_used.append(
                    f"{matched.get('source_ontology')}:{matched.get('source_iri', '')}"
                )
            if candidates:
                for cand in candidates[:3]:
                    src = f"{cand.get('source_ontology')}:{cand.get('source_iri', '')}"
                    if src not in sources_used:
                        sources_used.append(src)

            results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": label,
                    "parent_classes": "|".join(parents),
                    "current_definition": current_def,
                    "proposed_definition": proposed_def,
                    "has_current": "yes" if current_def else "no",
                    "sources_consulted": "; ".join(sources_used),
                    "num_sources": len(sources_used),
                    "model_used": model,
                }
            )

            processed += 1

        except Exception as e:
            click.echo(f"✗ {metpo_id:20s} ERROR: {e}", err=True)
            results.append(
                {
                    "metpo_id": metpo_id,
                    "metpo_label": label,
                    "parent_classes": "|".join(parents),
                    "current_definition": current_def,
                    "proposed_definition": f"[ERROR: {e}]",
                    "has_current": "yes" if current_def else "no",
                    "sources_consulted": "",
                    "num_sources": 0,
                    "model_used": model,
                }
            )
            processed += 1

    # Write output
    click.echo(f"\nWriting proposed definitions to {output}...")
    output.parent.mkdir(parents=True, exist_ok=True)

    with Path(output).open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "metpo_id",
            "metpo_label",
            "parent_classes",
            "current_definition",
            "proposed_definition",
            "has_current",
            "sources_consulted",
            "num_sources",
            "model_used",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(results)

    # Summary
    click.echo("\n" + "=" * 70)
    click.echo("SUMMARY")
    click.echo("=" * 70)
    click.echo(f"Total terms processed: {len(results)}")

    had_current = sum(1 for r in results if r["has_current"] == "yes")
    click.echo(f"Had current definition: {had_current} ({had_current / len(results) * 100:.1f}%)")
    click.echo(
        f"Needed definition: {len(results) - had_current} ({(len(results) - had_current) / len(results) * 100:.1f}%)"
    )

    with_sources = sum(1 for r in results if r["num_sources"] > 0)
    click.echo(
        f"\nBased on foreign ontology terms: {with_sources} ({with_sources / len(results) * 100:.1f}%)"
    )
    click.echo(f"Based on parent class only: {len(results) - with_sources}")

    click.echo(f"\nModel used: {model}")
    click.echo(f"Output file: {output}")
    return None


if __name__ == "__main__":
    main()
