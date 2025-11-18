"""
Compare two extraction outputs to evaluate template improvements.
Usage: python compare_extractions.py <v1.yaml> <v2.yaml>
"""

import sys
from collections import defaultdict
from pathlib import Path

import click
import yaml


def analyze_extraction(yaml_file: Path) -> dict:
    """Analyze an extraction file and return statistics."""
    with Path(yaml_file).open() as f:
        docs = list(yaml.safe_load_all(f))

    stats = {
        "file": yaml_file.name,
        "total_docs": len(docs),
        "total_entities": 0,
        "total_relationships": 0,
        "grounded_entities": 0,
        "auto_entities": 0,
        "namespace_counts": defaultdict(int),
        "predicate_counts": defaultdict(int),
        "per_doc_stats": []
    }

    for doc in docs:
        if not doc or "extracted_object" not in doc:
            continue

        extracted = doc["extracted_object"]
        named_entities = doc.get("named_entities", [])

        # Count entities
        for entity in named_entities:
            if "none" in str(entity.get("id", "")).lower():
                continue
            stats["total_entities"] += 1

            entity_id = str(entity.get("id", ""))
            if ":" in entity_id:
                namespace = entity_id.split(":")[0]
                stats["namespace_counts"][namespace] += 1

                if namespace != "AUTO":
                    stats["grounded_entities"] += 1
                else:
                    stats["auto_entities"] += 1

        # Count relationships
        chem_rels = extracted.get("chemical_utilizations", [])
        if not isinstance(chem_rels, list):
            chem_rels = [chem_rels] if chem_rels else []

        valid_rels = []
        for rel in chem_rels:
            if isinstance(rel, dict) and all(k in rel for k in ["subject", "predicate", "object"]):
                valid_rels.append(rel)
                stats["total_relationships"] += 1

                # Count predicate usage
                predicate = rel.get("predicate", "unknown")
                stats["predicate_counts"][predicate] += 1

        # Per-document stats
        doc_stat = {
            "entities": len([e for e in named_entities if "none" not in str(e.get("id", "")).lower()]),
            "relationships": len(valid_rels),
            "input_len": len(doc.get("input_text", ""))
        }
        stats["per_doc_stats"].append(doc_stat)

    return stats

def print_comparison(v1_stats: dict, v2_stats: dict):
    """Print side-by-side comparison of two extractions."""
    click.echo("=" * 100)
    click.echo("EXTRACTION COMPARISON: V1 vs V2")
    click.echo("=" * 100)
    click.echo()

    # Overall stats
    click.echo(f"{'Metric':<40} | {'V1':>20} | {'V2':>20} | {'Change':>15}")
    click.echo("-" * 100)

    click.echo(f"{'Total documents':<40} | {v1_stats['total_docs']:>20} | {v2_stats['total_docs']:>20} | {'-':>15}")

    # Relationships (most important for KG)
    v1_rels = v1_stats["total_relationships"]
    v2_rels = v2_stats["total_relationships"]
    change = v2_rels - v1_rels
    pct_change = f"+{100*change/v1_rels:.1f}%" if v1_rels > 0 else "N/A"
    emoji = "✅" if change > 0 else ("⚠️" if change == 0 else "❌")
    click.echo(f"{'Total relationships (KG triples)':<40} | {v1_rels:>20} | {v2_rels:>20} | {f'{change:+} ({pct_change})':>15} {emoji}")

    # Entities
    v1_ents = v1_stats["total_entities"]
    v2_ents = v2_stats["total_entities"]
    change = v2_ents - v1_ents
    pct_change = f"+{100*change/v1_ents:.1f}%" if v1_ents > 0 else "N/A"
    click.echo(f"{'Total entities':<40} | {v1_ents:>20} | {v2_ents:>20} | {f'{change:+} ({pct_change})':>15}")

    # Grounding quality (critical for KG)
    v1_grounded = v1_stats["grounded_entities"]
    v2_grounded = v2_stats["grounded_entities"]
    v1_rate = 100*v1_grounded/v1_ents if v1_ents > 0 else 0
    v2_rate = 100*v2_grounded/v2_ents if v2_ents > 0 else 0
    change = v2_grounded - v1_grounded
    rate_change = v2_rate - v1_rate
    emoji = "✅" if change > 0 else ("⚠️" if change == 0 else "❌")
    click.echo(f"{'Grounded entities (non-AUTO)':<40} | {f'{v1_grounded} ({v1_rate:.0f}%)':>20} | {f'{v2_grounded} ({v2_rate:.0f}%)':>20} | {f'{change:+} ({rate_change:+.1f}pp)':>15} {emoji}")

    # AUTO entities (lower is better for KG)
    v1_auto = v1_stats["auto_entities"]
    v2_auto = v2_stats["auto_entities"]
    change = v2_auto - v1_auto
    emoji = "✅" if change < 0 else ("⚠️" if change == 0 else "❌")
    click.echo(f"{'AUTO entities (lower is better)':<40} | {v1_auto:>20} | {v2_auto:>20} | {f'{change:+}':>15} {emoji}")

    click.echo()
    click.echo("-" * 100)
    click.echo("PER-DOCUMENT AVERAGES")
    click.echo("-" * 100)

    v1_avg_rels = sum(d["relationships"] for d in v1_stats["per_doc_stats"]) / v1_stats["total_docs"]
    v2_avg_rels = sum(d["relationships"] for d in v2_stats["per_doc_stats"]) / v2_stats["total_docs"]
    change = v2_avg_rels - v1_avg_rels
    pct_change = f"+{100*change/v1_avg_rels:.1f}%" if v1_avg_rels > 0 else "N/A"
    emoji = "✅" if change > 0 else ("⚠️" if change == 0 else "❌")
    click.echo(f"{'Avg relationships per paper':<40} | {v1_avg_rels:>20.1f} | {v2_avg_rels:>20.1f} | {f'{change:+.1f} ({pct_change})':>15} {emoji}")

    v1_avg_ents = sum(d["entities"] for d in v1_stats["per_doc_stats"]) / v1_stats["total_docs"]
    v2_avg_ents = sum(d["entities"] for d in v2_stats["per_doc_stats"]) / v2_stats["total_docs"]
    click.echo(f"{'Avg entities per paper':<40} | {v1_avg_ents:>20.1f} | {v2_avg_ents:>20.1f} | {f'{v2_avg_ents - v1_avg_ents:+.1f}':>15}")

    # Namespace breakdown
    click.echo()
    click.echo("-" * 100)
    click.echo("NAMESPACE USAGE (for grounding)")
    click.echo("-" * 100)

    all_namespaces = set(v1_stats["namespace_counts"].keys()) | set(v2_stats["namespace_counts"].keys())
    for ns in sorted(all_namespaces):
        v1_count = v1_stats["namespace_counts"].get(ns, 0)
        v2_count = v2_stats["namespace_counts"].get(ns, 0)
        change = v2_count - v1_count
        emoji = "✅" if ns != "AUTO" and change > 0 else ("❌" if ns == "AUTO" and change > 0 else "")
        click.echo(f"  {ns:<20} | {v1_count:>10} | {v2_count:>10} | {f'{change:+}':>10} {emoji}")

    # Predicate usage
    click.echo()
    click.echo("-" * 100)
    click.echo("PREDICATE USAGE (top 10)")
    click.echo("-" * 100)

    all_predicates = set(v1_stats["predicate_counts"].keys()) | set(v2_stats["predicate_counts"].keys())
    top_predicates = sorted(all_predicates,
                           key=lambda p: v1_stats["predicate_counts"].get(p, 0) + v2_stats["predicate_counts"].get(p, 0),
                           reverse=True)[:10]

    for pred in top_predicates:
        v1_count = v1_stats["predicate_counts"].get(pred, 0)
        v2_count = v2_stats["predicate_counts"].get(pred, 0)
        change = v2_count - v1_count
        click.echo(f"  {pred:<35} | {v1_count:>10} | {v2_count:>10} | {f'{change:+}':>10}")

    click.echo()
    click.echo("=" * 100)
    click.echo("SUMMARY")
    click.echo("=" * 100)

    # Determine which is better
    v2_better_count = 0
    if v2_rels > v1_rels:
        v2_better_count += 1
        click.echo(f"✅ V2 extracted {v2_rels - v1_rels} MORE relationships (+{100*(v2_rels-v1_rels)/v1_rels:.1f}%)")
    elif v2_rels < v1_rels:
        click.echo(f"❌ V2 extracted {v1_rels - v2_rels} FEWER relationships ({100*(v1_rels-v2_rels)/v1_rels:.1f}%)")
    else:
        click.echo("⚠️  V2 extracted SAME number of relationships")

    if v2_grounded > v1_grounded:
        v2_better_count += 1
        click.echo(f"✅ V2 grounded {v2_grounded - v1_grounded} MORE entities to ontologies")
    elif v2_grounded < v1_grounded:
        click.echo(f"❌ V2 grounded {v1_grounded - v2_grounded} FEWER entities")

    if v2_rate > v1_rate:
        v2_better_count += 1
        click.echo(f"✅ V2 has BETTER grounding rate ({v2_rate:.1f}% vs {v1_rate:.1f}%)")
    elif v2_rate < v1_rate:
        click.echo(f"❌ V2 has WORSE grounding rate ({v2_rate:.1f}% vs {v1_rate:.1f}%)")

    click.echo()
    if v2_better_count >= 2:
        click.echo("🎉 V2 TEMPLATE SHOWS IMPROVEMENT!")
    elif v2_better_count == 1:
        click.echo("⚠️  V2 shows mixed results")
    else:
        click.echo("❌ V2 did not improve extraction")

    click.echo("=" * 100)


@click.command()
def main():
    if len(sys.argv) < 3:
        click.echo("Usage: python compare_extractions.py <v1.yaml> <v2.yaml>")
        sys.exit(1)

    v1_file = Path(sys.argv[1])
    v2_file = Path(sys.argv[2])

    if not v1_file.exists():
        click.echo(f"Error: V1 file not found: {v1_file}")
        sys.exit(1)

    if not v2_file.exists():
        click.echo(f"Error: V2 file not found: {v2_file}")
        sys.exit(1)

    click.echo(f"Analyzing V1: {v1_file.name}...")
    v1_stats = analyze_extraction(v1_file)

    click.echo(f"Analyzing V2: {v2_file.name}...")
    v2_stats = analyze_extraction(v2_file)

    print_comparison(v1_stats, v2_stats)


if __name__ == "__main__":
    main()
