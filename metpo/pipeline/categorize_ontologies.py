#!/usr/bin/env python
"""
Categorize ontologies by relevance to microbial phenotypes and size.

Uses keyword-based scoring learned from domain expert feedback patterns.
"""

import csv

import click

from metpo.cli_common import input_csv_option


def score_ontology(onto):
    """
    Score ontology relevance to microbial phenotypes.
    Returns: (category, score, reason)

    Scoring patterns learned from expert feedback:
    - Bacterial/prokaryotic focus = highest priority
    - Phenotype/trait/quality = core relevance
    - Resistance/interaction/microscopy = highly relevant
    - Environmental/flora = useful for conditions
    - Fungal = lower priority but still relevant if small
    - Anatomy/clinical/taxonomy/chemical = not relevant
    - Size matters but can be overridden by high relevance
    """
    title_desc = (onto["title"] + " " + onto["description"]).lower()
    count = onto["count"]

    score = 0
    reasons = []

    # HIGHEST PRIORITY: Bacterial/prokaryotic/microbial phenotypes
    if any(kw in title_desc for kw in ["microb", "prokaryot", "bacteri", "archae"]):
        score += 15
        reasons.append("bacterial/microbial")

    if any(kw in title_desc for kw in ["phenotype", "trait", "character"]) and "microb" in title_desc:
        score += 10
        reasons.append("microbial phenotype focus")

    # HIGH PRIORITY: Phenotype/trait/quality/attribute ontologies
    phenotype_terms = ["phenotype", "trait", "quality", "attribute", "character"]
    if any(kw in title_desc for kw in phenotype_terms):
        score += 12
        reasons.append("phenotype-centric")

    # HIGH PRIORITY: Resistance, host-microbe interaction, pathogen
    if any(kw in title_desc for kw in ["resistance", "antibiotic", "antimicrob"]):
        score += 14
        reasons.append("antimicrobial resistance")

    if any(kw in title_desc for kw in ["pathogen", "host", "interaction"]):
        score += 12
        reasons.append("pathogen/host interaction")

    # MODERATE-HIGH: Microscopy, cellular phenotypes
    if any(kw in title_desc for kw in ["microscopy", "cellular microscopy"]):
        score += 13
        reasons.append("cellular microscopy")

    if "cell" in title_desc and "phenotype" in title_desc:
        score += 11
        reasons.append("cellular phenotype")

    # MODERATE: Environmental/ecological (useful for growth conditions)
    if any(kw in title_desc for kw in ["environment", "ecology", "flora", "habitat"]):
        score += 9
        reasons.append("environmental conditions")

    # MODERATE: Population, community, biolink
    if any(kw in title_desc for kw in ["population", "community", "biolink"]):
        score += 9
        reasons.append("population/community")

    # MODERATE: Experimental conditions, evidence
    if any(kw in title_desc for kw in ["experimental", "condition", "evidence", "conclusion"]):
        score += 8
        reasons.append("experimental/evidence")

    # MODERATE: Unified/integrated phenotype ontologies
    if "unified" in title_desc and "phenotype" in title_desc:
        score += 10
        reasons.append("unified phenotype coverage")

    # SIZE ADJUSTMENT: Lower priority for very large ontologies unless highly relevant
    if count > 200000:
        if score >= 14:
            reasons.append("large but highly relevant")
        else:
            score -= 5
            reasons.append("very large")

    if count > 500000:
        if score >= 15:
            reasons.append("huge but critically relevant")
        else:
            score -= 10
            reasons.append("too large")

    # FUNGAL: Lower priority than bacterial
    if any(kw in title_desc for kw in ["yeast", "fungi", "fungal", "ascomycete"]):
        if count < 5000:
            score -= 1
            reasons.append("fungal (small, acceptable)")
        else:
            score -= 6
            reasons.append("fungal (lower priority than bacterial)")

    # ANATOMY: Not phenotype-centric
    if "anatomy" in title_desc and "phenotype" not in title_desc:
        score -= 8
        reasons.append("anatomy not phenotype")

    # STRONGLY NEGATIVE: Clearly unrelated domains
    irrelevant = [
        "disease", "drug", "clinical", "human phenotype", "mammal",
        "zebrafish", "geographic", "lipid", "chemical entities",
        "protein ontology", "food", "taxonomy", "genes and genomes",
        "transcription", "cell line", "developmental stages"
    ]
    if any(kw in title_desc for kw in irrelevant):
        score -= 12
        reasons.append("unrelated domain")

    # Categorize based on score
    if score >= 10:
        category = "very_appealing"
    elif score <= -5:
        category = "not_appealing"
    else:
        category = "in_between"

    return category, score, "; ".join(reasons) if reasons else "no keywords matched"


@click.command()
@input_csv_option(required=False, help_text="Input ontology catalog CSV")
@click.option("--output-prefix", default="ontologies", help="Output file prefix")
def main(input_file, output_prefix):
    """Categorize ontologies by relevance to microbial phenotypes."""
    input_csv = input_file or "ontology_catalog.csv"

    # Read ontology catalog
    ontologies = []
    with open(input_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ontologyId"] and row["count"]:
                ontologies.append({
                    "id": row["ontologyId"],
                    "title": row["title"],
                    "count": int(row["count"]),
                    "description": row["description"]
                })

    # Score and categorize all ontologies
    categorized = {
        "very_appealing": [],
        "in_between": [],
        "not_appealing": []
    }

    for onto in ontologies:
        category, score, reason = score_ontology(onto)
        onto["score"] = score
        onto["reason"] = reason
        categorized[category].append(onto)

    # Sort by score within category, then by size
    for category in categorized:
        categorized[category].sort(key=lambda x: (-x["score"], x["count"]))

    # Print results
    print("=" * 100)
    print("VERY APPEALING: Microbial/Phenotype-Centric")
    print("=" * 100)
    print(f"{'ID':<15} {'Count':>10}  {'Score':>5}  {'Title'}")
    print("-" * 100)
    total = 0
    for onto in categorized["very_appealing"]:
        print(f"{onto['id']:<15} {onto['count']:>10,}  {onto['score']:>5}  {onto['title']}")
        total += onto["count"]
    print(f"\nSubtotal: {len(categorized['very_appealing'])} ontologies, {total:,} records")

    print("\n" + "=" * 100)
    print("IN-BETWEEN: Potentially Useful or Unclear Relevance")
    print("=" * 100)
    print(f"{'ID':<15} {'Count':>10}  {'Score':>5}  {'Title'}")
    print("-" * 100)
    total = 0
    for onto in categorized["in_between"][:40]:
        print(f"{onto['id']:<15} {onto['count']:>10,}  {onto['score']:>5}  {onto['title']}")
        total += onto["count"]
    if len(categorized["in_between"]) > 40:
        remaining = sum(o["count"] for o in categorized["in_between"][40:])
        print(f"... and {len(categorized['in_between']) - 40} more ontologies ({remaining:,} records)")
        total += remaining
    print(f"\nSubtotal: {len(categorized['in_between'])} ontologies, {total:,} records")

    print("\n" + "=" * 100)
    print("NOT APPEALING: Unrelated to Microbial Phenotypes or Too Large")
    print("=" * 100)
    print(f"{'ID':<15} {'Count':>10}  {'Score':>5}  {'Title'}")
    print("-" * 100)
    total = 0
    for onto in categorized["not_appealing"][:30]:
        print(f"{onto['id']:<15} {onto['count']:>10,}  {onto['score']:>5}  {onto['title']}")
        total += onto["count"]
    if len(categorized["not_appealing"]) > 30:
        remaining = sum(o["count"] for o in categorized["not_appealing"][30:])
        print(f"... and {len(categorized['not_appealing']) - 30} more ontologies ({remaining:,} records)")
        total += remaining
    else:
        total = sum(o["count"] for o in categorized["not_appealing"])
    print(f"\nSubtotal: {len(categorized['not_appealing'])} ontologies, {total:,} records")

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Very Appealing:  {len(categorized['very_appealing']):>3} ontologies, {sum(o['count'] for o in categorized['very_appealing']):>10,} records")
    print(f"In-Between:      {len(categorized['in_between']):>3} ontologies, {sum(o['count'] for o in categorized['in_between']):>10,} records")
    print(f"Not Appealing:   {len(categorized['not_appealing']):>3} ontologies, {sum(o['count'] for o in categorized['not_appealing']):>10,} records")
    print(f"Total:           {len(ontologies):>3} ontologies, {sum(o['count'] for o in ontologies):>10,} records")

    # Write to CSV files
    for category_name in ["very_appealing", "in_between", "not_appealing"]:
        output_file = f"{output_prefix}_{category_name}.csv"
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ontologyId", "title", "count", "score", "reason", "description"])
            writer.writeheader()
            for onto in categorized[category_name]:
                writer.writerow({
                    "ontologyId": onto["id"],
                    "title": onto["title"],
                    "count": onto["count"],
                    "score": onto["score"],
                    "reason": onto["reason"],
                    "description": onto["description"]
                })

    print("\n✓ Created categorized CSV files:")
    print(f"  - {output_prefix}_very_appealing.csv")
    print(f"  - {output_prefix}_in_between.csv")
    print(f"  - {output_prefix}_not_appealing.csv")


if __name__ == "__main__":
    main()
