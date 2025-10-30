#!/usr/bin/env python3
"""
OntoGPT extraction benchmark script with comprehensive metrics.

Runs OntoGPT extraction on a set of abstracts and tracks:
- Cost (total, per abstract, per 1K input chars)
- Time (total, per abstract, per 1K input chars)
- Extraction quality (entities, relationships, density)
- Input size (abstracts vs actual prompts sent to LLM)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_cborg_info(api_key: str) -> Dict:
    """Get CBORG account info and spend."""
    result = subprocess.run(
        ["curl", "-s", "https://api.cborg.lbl.gov/user/info",
         "-H", f"Authorization: Bearer {api_key}"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def count_abstracts(input_dir: Path) -> Tuple[int, int, int]:
    """Count abstracts and calculate total chars/words."""
    files = list(input_dir.glob("*.txt"))
    total_chars = 0
    total_words = 0

    for f in files:
        content = f.read_text()
        total_chars += len(content)
        total_words += len(content.split())

    return len(files), total_chars, total_words


def parse_log_for_input_size(log_file: Path) -> Tuple[int, int]:
    """Parse log file to extract total input chars across all API calls."""
    if not log_file.exists():
        return 0, 0

    total_input = 0
    num_calls = 0

    # Look for lines like: "INFO:ontogpt.clients.llm_client:Complete: engine=gpt-4o, prompt[4241]=..."
    pattern = r'prompt\[(\d+)\]='

    with open(log_file) as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                total_input += int(match.group(1))
                num_calls += 1

    return total_input, num_calls


def count_entities_relationships(output_file: Path) -> Tuple[int, int]:
    """Count entities and relationships from output YAML."""
    if not output_file.exists():
        return 0, 0

    content = output_file.read_text()

    # Approximate counts
    entities = content.count("NamedEntity")
    relationships = content.count("CompoundExpression")

    return entities, relationships


def run_extraction(
    template: str,
    model: str,
    input_dir: Path,
    template_file: Path,
    output_file: Path,
    log_file: Path
) -> int:
    """Run OntoGPT extraction and return duration in seconds."""
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Suppress LiteLLM cost estimation errors
    env = os.environ.copy()
    env["LITELLM_LOG"] = "ERROR"

    system_message = (
        "You are a precise data extraction system. Output ONLY the requested fields "
        "in the exact format specified. Do not add explanations, preambles, notes, "
        "or any other text. If a field has no value, write 'none' after the colon. "
        "Never leave a field completely empty."
    )

    start = time.time()

    cmd = [
        "ontogpt", "extract",
        "-t", str(template_file),
        "-i", str(input_dir),
        "-o", str(output_file),
        "-m", model,
        "-vv",
        "--set-slot-value", "source_text=",
        "--system-message", system_message
    ]

    with open(log_file, 'w') as log:
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)

    duration = int(time.time() - start)

    if result.returncode != 0:
        print(f"WARNING: ontogpt exited with code {result.returncode}", file=sys.stderr)

    return duration


def main():
    parser = argparse.ArgumentParser(description="Benchmark OntoGPT extraction")
    parser.add_argument("template", help="Template name (e.g., 'taxa')")
    parser.add_argument("model", help="Model name (e.g., 'gpt-4o')")
    parser.add_argument("input_dir", help="Directory containing abstracts")
    parser.add_argument("log_file", help="TSV file to log results")

    args = parser.parse_args()

    # Setup paths
    template = args.template
    model = args.model
    input_dir = Path(args.input_dir)
    tsv_file = Path(args.log_file)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    template_file = Path(f"templates/{template}_template_base.yaml")
    output_file = Path(f"outputs/{template}_{model.replace('/', '_')}_{timestamp}.yaml")
    log_file = Path(f"logs/{template}_{model.replace('/', '_')}_{timestamp}.log")

    # Validate
    if not template_file.exists():
        print(f"ERROR: Template file not found: {template_file}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Print header
    print("=" * 42)
    print("OntoGPT Extraction Benchmark")
    print("=" * 42)
    print(f"Template: {template}")
    print(f"Model: {model}")
    print(f"Input: {input_dir}")
    print(f"Timestamp: {timestamp}")
    print()

    # Collect input statistics
    print("Collecting input statistics...")
    num_abstracts, total_chars, total_words = count_abstracts(input_dir)
    avg_chars = total_chars // num_abstracts if num_abstracts > 0 else 0
    avg_words = total_words // num_abstracts if num_abstracts > 0 else 0

    print(f"  Abstracts: {num_abstracts}")
    print(f"  Total chars: {total_chars:,}")
    print(f"  Avg chars/abstract: {avg_chars:,}")
    print(f"  Total words: {total_words:,}")
    print(f"  Avg words/abstract: {avg_words:,}")
    print()

    # Get CBORG info before
    print("Querying CBORG account info (before)...")
    info_before = get_cborg_info(api_key)
    spend_before = info_before.get("user_info", {}).get("spend", 0)
    max_budget = info_before.get("user_info", {}).get("max_budget", 0)
    key_owner = info_before.get("user_info", {}).get("user_email", "unknown")

    print(f"  Key owner: {key_owner}")
    print(f"  Max budget: ${max_budget}")
    print(f"  Spend before: ${spend_before:.4f}")
    print(f"  Budget remaining: ${max_budget - spend_before:.2f}")
    print()

    # Run extraction
    print("Running extraction...")
    duration = run_extraction(template, model, input_dir, template_file, output_file, log_file)
    print()
    print(f"Extraction completed in {duration}s")
    print()

    # Get CBORG info after
    print("Querying CBORG spend (after)...")
    info_after = get_cborg_info(api_key)
    spend_after = info_after.get("user_info", {}).get("spend", 0)
    budget_remaining = max_budget - spend_after

    print(f"  Spend after: ${spend_after:.4f}")

    # Calculate costs
    cost = spend_after - spend_before
    cost_per_abstract = cost / num_abstracts if num_abstracts > 0 else 0
    cost_per_1k_abstract_chars = (cost / total_chars) * 1000 if total_chars > 0 else 0

    # Parse log for actual input size
    total_input_chars, num_api_calls = parse_log_for_input_size(log_file)
    cost_per_1k_input_chars = (cost / total_input_chars) * 1000 if total_input_chars > 0 else 0

    # Calculate time metrics
    time_per_abstract = duration / num_abstracts if num_abstracts > 0 else 0
    time_per_1k_input_chars = (duration / total_input_chars) * 1000 if total_input_chars > 0 else 0

    print(f"  Cost: ${cost:.6f}")
    print(f"  Cost/abstract: ${cost_per_abstract:.6f}")
    print(f"  Cost/1K abstract chars: ${cost_per_1k_abstract_chars:.6f}")
    print(f"  Cost/1K input chars: ${cost_per_1k_input_chars:.6f}")
    print(f"  Time/abstract: {time_per_abstract:.1f}s")
    print(f"  Time/1K input chars: {time_per_1k_input_chars:.1f}s")
    print(f"  Total input chars: {total_input_chars:,} (across {num_api_calls} API calls)")
    print()

    # Count extracted entities and relationships
    print("Analyzing extraction results...")
    if output_file.exists():
        entities, relationships = count_entities_relationships(output_file)

        # Calculate density
        entities_per_1k = (entities / total_input_chars) * 1000 if total_input_chars > 0 else 0
        relationships_per_1k = (relationships / total_input_chars) * 1000 if total_input_chars > 0 else 0

        print(f"  Total entities (approx): {entities}")
        print(f"  Total relationships (approx): {relationships}")
        print(f"  Extraction density:")
        print(f"    - {entities_per_1k:.2f} entities/1K input chars")
        print(f"    - {relationships_per_1k:.2f} relationships/1K input chars")
    else:
        print("  WARNING: Output file not found!")
        entities = 0
        relationships = 0
        entities_per_1k = 0
        relationships_per_1k = 0
    print()

    # Log to TSV
    print(f"Logging results to {tsv_file}...")

    # Create header if file doesn't exist
    if not tsv_file.exists():
        header = [
            "timestamp", "template", "model", "key_owner", "max_budget", "budget_remaining",
            "num_abstracts", "total_abstract_chars", "avg_abstract_chars", "total_words", "avg_words",
            "total_input_chars", "num_api_calls", "total_cost", "cost_per_abstract",
            "cost_per_1k_abstract_chars", "cost_per_1k_input_chars", "total_time_sec",
            "time_per_abstract", "time_per_1k_input_chars", "entities", "relationships",
            "entities_per_1k_input", "relationships_per_1k_input", "output_file", "log_file"
        ]
        tsv_file.write_text("\t".join(header) + "\n")

    # Append results
    row = [
        timestamp, template, model, key_owner, f"{max_budget}", f"{budget_remaining:.2f}",
        f"{num_abstracts}", f"{total_chars}", f"{avg_chars}", f"{total_words}", f"{avg_words}",
        f"{total_input_chars}", f"{num_api_calls}", f"{cost:.6f}", f"{cost_per_abstract:.6f}",
        f"{cost_per_1k_abstract_chars:.6f}", f"{cost_per_1k_input_chars:.6f}", f"{duration}",
        f"{time_per_abstract:.1f}", f"{time_per_1k_input_chars:.1f}", f"{entities}", f"{relationships}",
        f"{entities_per_1k:.2f}", f"{relationships_per_1k:.2f}", str(output_file), str(log_file)
    ]

    with open(tsv_file, 'a') as f:
        f.write("\t".join(row) + "\n")

    # Print summary
    print("✅ Benchmark complete!")
    print()
    print("Summary:")
    print(f"  Abstracts: {num_abstracts} ({total_chars:,} chars, {total_input_chars:,} input chars across {num_api_calls} API calls)")
    print(f"  Cost: ${cost:.6f}")
    print(f"    - ${cost_per_abstract:.6f}/abstract")
    print(f"    - ${cost_per_1k_abstract_chars:.6f}/1K abstract chars")
    print(f"    - ${cost_per_1k_input_chars:.6f}/1K input chars (template + abstract)")
    print(f"  Time: {duration}s")
    print(f"    - {time_per_abstract:.1f}s/abstract")
    print(f"    - {time_per_1k_input_chars:.1f}s/1K input chars")
    print(f"  Extraction: {entities} entities, {relationships} relationships")
    print(f"    - {entities_per_1k:.2f} entities/1K input chars")
    print(f"    - {relationships_per_1k:.2f} relationships/1K input chars")
    print()
    print(f"Results logged to: {tsv_file}")
    print(f"Output: {output_file}")
    print(f"Log: {log_file}")


if __name__ == "__main__":
    main()
