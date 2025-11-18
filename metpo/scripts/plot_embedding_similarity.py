#!/usr/bin/env python3
"""
Plot distribution of best embedding similarity scores for METPO terms.

This helps assess the overall quality of SSSOM mappings by showing:
1. Distribution of best similarity scores per METPO term
2. Breakdown by match type (exactMatch, closeMatch, relatedMatch)
3. Comparison across source ontologies
"""
import csv
import click
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def read_best_matches(sssom_path: Path) -> Dict[str, Dict]:
    """Read SSSOM mappings and get best match per METPO term."""
    best_matches = {}

    with open(sssom_path, "r", encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, delimiter="\t")

        for row in reader:
            subject_id = row.get("subject_id", "").strip()
            if not subject_id.startswith("METPO:"):
                continue

            similarity = float(row.get("similarity_score", 0))
            confidence = float(row.get("confidence", 0))

            # Keep only the best match per term
            if subject_id not in best_matches or similarity > best_matches[subject_id]["similarity"]:
                predicate = row.get("predicate_id", "")
                match_type = "other"
                if "exactMatch" in predicate:
                    match_type = "exactMatch"
                elif "closeMatch" in predicate:
                    match_type = "closeMatch"
                elif "relatedMatch" in predicate:
                    match_type = "relatedMatch"

                best_matches[subject_id] = {
                    "subject_id": subject_id,
                    "subject_label": row.get("subject_label", "").strip(),
                    "similarity": similarity,
                    "confidence": confidence,
                    "match_type": match_type,
                    "object_source": row.get("object_source", "").strip(),
                    "object_label": row.get("object_label", "").strip(),
                }

    return best_matches


@click.command()
@click.option(
    "--mappings",
    "-m",
    type=click.Path(exists=True, path_type=Path),
    default="data/mappings/metpo_mappings_combined_relaxed.sssom.tsv",
    help="Path to SSSOM mappings file"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/embedding_similarity_distribution.png",
    help="Output PNG file"
)
@click.option(
    "--stats-output",
    type=click.Path(path_type=Path),
    default="reports/embedding_similarity_stats.tsv",
    help="Output TSV file with statistics"
)
def main(mappings: Path, output: Path, stats_output: Path):
    """
    Plot distribution of best embedding similarity scores for METPO terms.
    """
    click.echo(f"Reading SSSOM mappings from {mappings}...")
    best_matches = read_best_matches(mappings)

    click.echo(f"Found best matches for {len(best_matches)} METPO terms")

    # Extract data for plotting
    similarities = [m["similarity"] for m in best_matches.values()]
    confidences = [m["confidence"] for m in best_matches.values()]

    # Group by match type
    by_match_type = defaultdict(list)
    for match in best_matches.values():
        by_match_type[match["match_type"]].append(match["similarity"])

    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("METPO Embedding Similarity Distribution", fontsize=16, fontweight="bold")

    # 1. Overall distribution (histogram)
    ax1 = axes[0, 0]
    ax1.hist(similarities, bins=50, edgecolor="black", alpha=0.7)
    ax1.axvline(np.median(similarities), color="red", linestyle="--",
                label=f"Median: {np.median(similarities):.3f}")
    ax1.axvline(np.mean(similarities), color="orange", linestyle="--",
                label=f"Mean: {np.mean(similarities):.3f}")
    ax1.set_xlabel("Similarity Score", fontsize=12)
    ax1.set_ylabel("Number of METPO Terms", fontsize=12)
    ax1.set_title("Distribution of Best Similarity Scores", fontsize=13, fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. By match type (box plot)
    ax2 = axes[0, 1]
    match_types = ["exactMatch", "closeMatch", "relatedMatch", "other"]
    data_by_type = [by_match_type.get(mt, []) for mt in match_types]

    bp = ax2.boxplot(data_by_type, labels=match_types, patch_artist=True)
    colors = ["#2ecc71", "#3498db", "#f39c12", "#95a5a6"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax2.set_ylabel("Similarity Score", fontsize=12)
    ax2.set_title("Similarity by Match Type", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.tick_params(axis="x", rotation=15)

    # 3. Cumulative distribution
    ax3 = axes[1, 0]
    sorted_sims = np.sort(similarities)
    cumulative = np.arange(1, len(sorted_sims) + 1) / len(sorted_sims) * 100
    ax3.plot(sorted_sims, cumulative, linewidth=2, color="#3498db")

    # Add reference lines
    for threshold, label in [(0.5, "50%"), (0.7, "70%"), (0.9, "90%")]:
        ax3.axvline(threshold, color="red", linestyle=":", alpha=0.5)
        count = sum(1 for s in similarities if s >= threshold)
        pct = count / len(similarities) * 100
        ax3.text(threshold, 50, f"{pct:.1f}%\n≥{threshold}",
                ha="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    ax3.set_xlabel("Similarity Score", fontsize=12)
    ax3.set_ylabel("Cumulative Percentage (%)", fontsize=12)
    ax3.set_title("Cumulative Distribution of Similarity Scores", fontsize=13, fontweight="bold")
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 1])

    # 4. Top source ontologies
    ax4 = axes[1, 1]
    ontology_counts = defaultdict(lambda: {"count": 0, "avg_sim": []})
    for match in best_matches.values():
        ont = match["object_source"]
        ontology_counts[ont]["count"] += 1
        ontology_counts[ont]["avg_sim"].append(match["similarity"])

    # Get top 10 ontologies by count
    top_onts = sorted(ontology_counts.items(),
                     key=lambda x: x[1]["count"], reverse=True)[:10]

    ont_names = [ont for ont, _ in top_onts]
    ont_counts = [data["count"] for _, data in top_onts]
    ont_avg_sims = [np.mean(data["avg_sim"]) for _, data in top_onts]

    x_pos = np.arange(len(ont_names))
    bars = ax4.bar(x_pos, ont_counts, color="#3498db", alpha=0.7, edgecolor="black")

    # Color bars by average similarity
    norm = plt.Normalize(min(ont_avg_sims), max(ont_avg_sims))
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=norm)
    for bar, avg_sim in zip(bars, ont_avg_sims):
        bar.set_color(sm.to_rgba(avg_sim))

    ax4.set_ylabel("Number of Best Matches", fontsize=12)
    ax4.set_title("Top 10 Source Ontologies (colored by avg similarity)", fontsize=13, fontweight="bold")
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(ont_names, rotation=45, ha="right")
    ax4.grid(True, alpha=0.3, axis="y")

    # Add colorbar
    cbar = plt.colorbar(sm, ax=ax4, orientation="vertical", pad=0.01)
    cbar.set_label("Avg Similarity", fontsize=10)

    plt.tight_layout()

    # Save figure
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=300, bbox_inches="tight")
    click.echo(f"✓ Plot saved to {output}")

    # Calculate and save statistics
    stats = []

    # Overall statistics
    stats.append({
        "metric": "Overall",
        "category": "All terms",
        "count": len(similarities),
        "min": f"{np.min(similarities):.4f}",
        "max": f"{np.max(similarities):.4f}",
        "mean": f"{np.mean(similarities):.4f}",
        "median": f"{np.median(similarities):.4f}",
        "std": f"{np.std(similarities):.4f}",
        "q25": f"{np.percentile(similarities, 25):.4f}",
        "q75": f"{np.percentile(similarities, 75):.4f}",
    })

    # By match type
    for match_type in ["exactMatch", "closeMatch", "relatedMatch", "other"]:
        sims = by_match_type.get(match_type, [])
        if sims:
            stats.append({
                "metric": "By match type",
                "category": match_type,
                "count": len(sims),
                "min": f"{np.min(sims):.4f}",
                "max": f"{np.max(sims):.4f}",
                "mean": f"{np.mean(sims):.4f}",
                "median": f"{np.median(sims):.4f}",
                "std": f"{np.std(sims):.4f}",
                "q25": f"{np.percentile(sims, 25):.4f}",
                "q75": f"{np.percentile(sims, 75):.4f}",
            })

    # Thresholds
    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        count = sum(1 for s in similarities if s >= threshold)
        pct = count / len(similarities) * 100
        stats.append({
            "metric": f"≥ {threshold} threshold",
            "category": f"Similarity ≥ {threshold}",
            "count": count,
            "min": f"{pct:.1f}%",
            "max": "",
            "mean": "",
            "median": "",
            "std": "",
            "q25": "",
            "q75": "",
        })

    # Write statistics
    stats_output.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_output, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["metric", "category", "count", "min", "max", "mean", "median", "std", "q25", "q75"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(stats)

    click.echo(f"✓ Statistics saved to {stats_output}")

    # Print summary
    click.echo("\n" + "="*60)
    click.echo("SUMMARY STATISTICS")
    click.echo("="*60)
    click.echo(f"Total METPO terms with mappings: {len(best_matches)}")
    click.echo(f"Mean similarity: {np.mean(similarities):.4f}")
    click.echo(f"Median similarity: {np.median(similarities):.4f}")
    click.echo(f"Std deviation: {np.std(similarities):.4f}")
    click.echo(f"\nThreshold breakdown:")
    for threshold in [0.9, 0.8, 0.7, 0.6, 0.5]:
        count = sum(1 for s in similarities if s >= threshold)
        pct = count / len(similarities) * 100
        click.echo(f"  ≥ {threshold}: {count:4d} terms ({pct:5.1f}%)")

    click.echo(f"\nMatch type breakdown:")
    for match_type in ["exactMatch", "closeMatch", "relatedMatch", "other"]:
        count = len(by_match_type.get(match_type, []))
        if count > 0:
            pct = count / len(similarities) * 100
            avg = np.mean(by_match_type[match_type])
            click.echo(f"  {match_type:15s}: {count:4d} terms ({pct:5.1f}%) - avg sim: {avg:.4f}")


if __name__ == "__main__":
    main()
