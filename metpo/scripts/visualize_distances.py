"""
Visualize cosine distance and similarity score distributions from SSSOM file.
"""

from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@click.command()
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input SSSOM TSV file with cosine_distance and similarity_score columns",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default="reports/figures/cosine_distance_distributions.png",
    help="Output PNG visualization file",
)
@click.option(
    "--show-plot",
    is_flag=True,
    help="Display plot interactively (in addition to saving)",
)
def main(input_file: Path, output_file: Path, show_plot: bool):
    """
    Visualize cosine distance and similarity score distributions from SSSOM file.

    Generates statistical summaries and visualizations including:
    - Distribution histograms for cosine distance and similarity scores
    - Formula verification (similarity = 1 - distance/2)
    - Scatter plot showing distance vs similarity relationship
    - Cumulative distribution functions
    """
    # Read SSSOM file (skip comment lines starting with #)
    df = pd.read_csv(input_file, sep="\t", comment="#")

    click.echo(f"Total mappings: {len(df):,}")
    click.echo(f"\nColumns: {', '.join(df.columns)}")

    # Extract distance and similarity columns
    distances = df["cosine_distance"].values
    similarities = df["similarity_score"].values

    # Statistics
    click.echo(f"\n{'=' * 70}")
    click.echo("COSINE DISTANCE STATISTICS")
    click.echo(f"{'=' * 70}")
    click.echo(f"Min:    {distances.min():.6f}")
    click.echo(f"Max:    {distances.max():.6f}")
    click.echo(f"Mean:   {distances.mean():.6f}")
    click.echo(f"Median: {np.median(distances):.6f}")
    click.echo(f"Std:    {distances.std():.6f}")

    click.echo(f"\n{'=' * 70}")
    click.echo("SIMILARITY SCORE STATISTICS")
    click.echo(f"{'=' * 70}")
    click.echo(f"Min:    {similarities.min():.6f}")
    click.echo(f"Max:    {similarities.max():.6f}")
    click.echo(f"Mean:   {similarities.mean():.6f}")
    click.echo(f"Median: {np.median(similarities):.6f}")
    click.echo(f"Std:    {similarities.std():.6f}")

    # Verify formula: similarity = 1 - (distance / 2)
    computed_sim = 1 - (distances / 2)
    formula_check = np.allclose(similarities, computed_sim)
    click.echo(f"\n{'=' * 70}")
    click.echo("FORMULA VERIFICATION")
    click.echo(f"{'=' * 70}")
    click.echo(f"similarity = 1 - (distance / 2): {formula_check}")
    if formula_check:
        click.echo("✓ Formula is correct!")
    else:
        max_diff = np.abs(similarities - computed_sim).max()
        click.echo(f"✗ Formula mismatch! Max difference: {max_diff:.10f}")

    # Distribution bins
    click.echo(f"\n{'=' * 70}")
    click.echo("COSINE DISTANCE DISTRIBUTION")
    click.echo(f"{'=' * 70}")
    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0]
    for i in range(len(bins) - 1):
        count = ((distances >= bins[i]) & (distances < bins[i + 1])).sum()
        pct = 100 * count / len(distances)
        bar = "█" * int(pct / 2)
        click.echo(f"[{bins[i]:.1f}, {bins[i + 1]:.1f}): {count:5d} ({pct:5.1f}%) {bar}")

    click.echo(f"\n{'=' * 70}")
    click.echo("SIMILARITY SCORE DISTRIBUTION")
    click.echo(f"{'=' * 70}")
    sim_bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for i in range(len(sim_bins) - 1):
        count = ((similarities >= sim_bins[i]) & (similarities < sim_bins[i + 1])).sum()
        pct = 100 * count / len(similarities)
        bar = "█" * int(pct / 2)
        click.echo(f"[{sim_bins[i]:.1f}, {sim_bins[i + 1]:.1f}): {count:5d} ({pct:5.1f}%) {bar}")

    # Predicate distribution
    click.echo(f"\n{'=' * 70}")
    click.echo("PREDICATE DISTRIBUTION")
    click.echo(f"{'=' * 70}")
    pred_counts = df["predicate_id"].value_counts()
    for pred, count in pred_counts.items():
        pct = 100 * count / len(df)
        click.echo(f"{pred:20s}: {count:5d} ({pct:5.1f}%)")

    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Cosine distance histogram
    ax1 = axes[0, 0]
    ax1.hist(distances, bins=50, color="steelblue", alpha=0.7, edgecolor="black")
    ax1.axvline(
        distances.mean(),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {distances.mean():.3f}",
    )
    ax1.axvline(
        np.median(distances),
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Median: {np.median(distances):.3f}",
    )
    ax1.set_xlabel("Cosine Distance", fontsize=12)
    ax1.set_ylabel("Count", fontsize=12)
    ax1.set_title("Cosine Distance Distribution", fontsize=14, fontweight="bold")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # 2. Similarity score histogram
    ax2 = axes[0, 1]
    ax2.hist(similarities, bins=50, color="forestgreen", alpha=0.7, edgecolor="black")
    ax2.axvline(
        similarities.mean(),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {similarities.mean():.3f}",
    )
    ax2.axvline(
        np.median(similarities),
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Median: {np.median(similarities):.3f}",
    )
    ax2.set_xlabel("Similarity Score", fontsize=12)
    ax2.set_ylabel("Count", fontsize=12)
    ax2.set_title("Similarity Score Distribution", fontsize=14, fontweight="bold")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    # 3. Distance vs Similarity scatter
    ax3 = axes[1, 0]
    ax3.scatter(distances, similarities, alpha=0.3, s=10, color="purple")
    # Plot theoretical line: sim = 1 - (dist / 2)
    x_theory = np.linspace(0, 2, 100)
    y_theory = 1 - (x_theory / 2)
    ax3.plot(x_theory, y_theory, "r--", linewidth=2, label="sim = 1 - (dist/2)")
    ax3.set_xlabel("Cosine Distance", fontsize=12)
    ax3.set_ylabel("Similarity Score", fontsize=12)
    ax3.set_title("Distance vs Similarity (Formula Check)", fontsize=14, fontweight="bold")
    ax3.legend()
    ax3.grid(alpha=0.3)
    ax3.set_xlim(0, max(2, distances.max() * 1.1))
    ax3.set_ylim(0, 1)

    # 4. Cumulative distributions
    ax4 = axes[1, 1]
    sorted_dist = np.sort(distances)
    cumulative_dist = np.arange(1, len(sorted_dist) + 1) / len(sorted_dist)
    ax4.plot(sorted_dist, cumulative_dist, linewidth=2, label="Cosine Distance", color="steelblue")

    sorted_sim = np.sort(similarities)
    cumulative_sim = np.arange(1, len(sorted_sim) + 1) / len(sorted_sim)
    ax4_twin = ax4.twinx()
    ax4_twin.plot(sorted_sim, cumulative_sim, linewidth=2, label="Similarity Score", color="forestgreen")

    ax4.set_xlabel("Cosine Distance", fontsize=12)
    ax4.set_ylabel("Cumulative Probability", fontsize=12, color="steelblue")
    ax4_twin.set_ylabel("Cumulative Probability", fontsize=12, color="forestgreen")
    ax4.set_title("Cumulative Distribution Functions", fontsize=14, fontweight="bold")
    ax4.tick_params(axis="y", labelcolor="steelblue")
    ax4_twin.tick_params(axis="y", labelcolor="forestgreen")
    ax4.grid(alpha=0.3)
    ax4.legend(loc="upper left")
    ax4_twin.legend(loc="lower right")

    # Save plot
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")

    click.echo(f"\n{'=' * 70}")
    click.echo("VISUALIZATION SAVED")
    click.echo(f"{'=' * 70}")
    click.echo(f"Saved to: {output_file}")

    # Show plot if requested
    if show_plot:
        plt.show()


if __name__ == "__main__":
    main()
