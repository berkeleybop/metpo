#!/usr/bin/env python3
"""
Pure metric calculator for OntoGPT benchmarks.
Takes numbers in via arguments, outputs JSON metrics to stdout.
No I/O, no subprocess - just pure calculations.
"""

import json
import sys
import click


def calculate_metrics(
    cost: float,
    num_abstracts: int,
    abstract_chars: int,
    input_chars: int,
    duration: int,
    entities: int,
    relationships: int
) -> dict:
    """
    Calculate all benchmark metrics.

    Returns dict with all calculated metrics.
    """
    # Cost metrics
    cost_per_abstract = cost / num_abstracts if num_abstracts > 0 else 0
    cost_per_1k_abstract_chars = (cost / abstract_chars) * 1000 if abstract_chars > 0 else 0
    cost_per_1k_input_chars = (cost / input_chars) * 1000 if input_chars > 0 else 0

    # Time metrics
    time_per_abstract = duration / num_abstracts if num_abstracts > 0 else 0
    time_per_1k_input_chars = (duration / input_chars) * 1000 if input_chars > 0 else 0

    # Extraction density metrics
    entities_per_1k_input = (entities / input_chars) * 1000 if input_chars > 0 else 0
    relationships_per_1k_input = (relationships / input_chars) * 1000 if input_chars > 0 else 0

    return {
        "cost_per_abstract": round(cost_per_abstract, 6),
        "cost_per_1k_abstract_chars": round(cost_per_1k_abstract_chars, 6),
        "cost_per_1k_input_chars": round(cost_per_1k_input_chars, 6),
        "time_per_abstract": round(time_per_abstract, 1),
        "time_per_1k_input_chars": round(time_per_1k_input_chars, 1),
        "entities_per_1k_input": round(entities_per_1k_input, 2),
        "relationships_per_1k_input": round(relationships_per_1k_input, 2)
    }


@click.command()
@click.option('--cost', type=float, required=True, help='Total cost in dollars')
@click.option('--abstracts', type=int, required=True, help='Number of abstracts')
@click.option('--abstract-chars', type=int, required=True, help='Total abstract characters')
@click.option('--input-chars', type=int, required=True, help='Total input characters (template + abstracts)')
@click.option('--duration', type=int, required=True, help='Total duration in seconds')
@click.option('--entities', type=int, required=True, help='Total entities extracted')
@click.option('--relationships', type=int, required=True, help='Total relationships extracted')
def main(cost, abstracts, abstract_chars, input_chars, duration, entities, relationships):
    """Calculate OntoGPT benchmark metrics.

    Takes numbers in via arguments, outputs JSON metrics to stdout.
    No I/O, no subprocess - just pure calculations.

    Example:

        calculate-extraction-metrics --cost 0.05 --abstracts 10 \\
            --abstract-chars 15000 --input-chars 50000 --duration 300 \\
            --entities 45 --relationships 12
    """
    metrics = calculate_metrics(
        cost=cost,
        num_abstracts=abstracts,
        abstract_chars=abstract_chars,
        input_chars=input_chars,
        duration=duration,
        entities=entities,
        relationships=relationships
    )

    # Output JSON to stdout
    json.dump(metrics, sys.stdout, indent=2)
    click.echo()  # Newline for readability


if __name__ == "__main__":
    main()
