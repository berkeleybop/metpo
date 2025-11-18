#!/usr/bin/env python3
"""
Deduplicate abstracts and filter for papers mentioning bacterial taxa.

Consolidates abstracts from multiple directories, removes duplicates,
and filters for papers that mention bacterial taxa.
"""

import re
import shutil
import click
from pathlib import Path
from typing import Set, Tuple


def has_bacterial_taxa(content: str) -> Tuple[bool, str]:
    """
    Check if abstract mentions bacterial taxa.

    Returns:
        (has_bacteria, reason) tuple
    """
    # Patterns for bacterial mentions
    patterns = {
        "genus_species": r"\b[A-Z][a-z]+\s+[a-z]+\s+(strain|sp\.|isolate)",
        "bacteria_word": r"\bbacteri(a|um|al|ology)\b",
        "microbe_word": r"\bmicrob(e|ial|iome)\b",
        "specific_genera": r"\b(Pseudomonas|Methylobacterium|Bradyrhizobium|Methylococcus|Methylotroph)\b",
        "strain": r"\bstrain\s+[A-Z0-9]+\b",
    }

    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            return True, pattern_name

    return False, "no_match"


def get_abstract_text(filepath: Path) -> str:
    """Extract just the abstract portion from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract abstract section
    match = re.search(r"Abstract:\n(.+)", content, re.DOTALL)
    if match:
        return match.group(1)
    return content


@click.command()
@click.option("--source-dirs", multiple=True,
              default=["literature_mining/abstracts", "literature_mining/cmm_pfas_abstracts"],
              help="Source directories to scan (can specify multiple)", show_default=True)
@click.option("--output-dir", default="literature_mining/abstracts_filtered",
              help="Output directory for filtered abstracts", show_default=True)
@click.option("--dry-run", is_flag=True,
              help="Show what would be done without copying files")
@click.option("--require-bacteria", is_flag=True,
              help="Only include abstracts mentioning bacterial taxa")
def main(source_dirs, output_dir, dry_run, require_bacteria):
    """Dedupe and filter abstracts for bacterial taxa mentions.

    Consolidates abstracts from multiple directories, removes duplicates,
    and optionally filters for papers mentioning bacterial taxa.
    """
    args = type("Args", (), {
        "source_dirs": source_dirs,
        "output_dir": output_dir,
        "dry_run": dry_run,
        "require_bacteria": require_bacteria
    })()

    # Collect all abstracts
    print("Scanning source directories...")
    all_files = {}  # filename -> filepath mapping

    for source_dir in args.source_dirs:
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"  ⚠ Directory not found: {source_dir}")
            continue

        files = list(source_path.glob("*-abstract.txt"))
        print(f"  {source_dir}: {len(files)} files")

        for file in files:
            # Track first occurrence
            if file.name not in all_files:
                all_files[file.name] = file

    print(f"\nTotal unique files: {len(all_files)}")

    # Filter for bacterial mentions if requested
    if args.require_bacteria:
        print("\nFiltering for bacterial taxa mentions...")
        filtered = {}
        reasons = {}

        for filename, filepath in all_files.items():
            content = get_abstract_text(filepath)
            has_bacteria, reason = has_bacterial_taxa(content)

            if has_bacteria:
                filtered[filename] = filepath
                reasons[filename] = reason

        print(f"  ✓ With bacterial mentions: {len(filtered)}")
        print(f"  ✗ Without bacterial mentions: {len(all_files) - len(filtered)}")

        # Show breakdown by detection reason
        reason_counts = {}
        for reason in reasons.values():
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        print("\n  Detection breakdown:")
        for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
            print(f"    {reason}: {count}")

        files_to_copy = filtered
    else:
        files_to_copy = all_files

    # Copy files
    if args.dry_run:
        print(f"\n[DRY RUN] Would copy {len(files_to_copy)} files to {args.output_dir}")

        # Show sample
        print("\nSample files (first 10):")
        for filename in list(files_to_copy.keys())[:10]:
            print(f"  {filename}")
    else:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nCopying {len(files_to_copy)} files to {args.output_dir}...")

        for filename, filepath in files_to_copy.items():
            dest = output_path / filename
            shutil.copy2(filepath, dest)

        print(f"✓ Done! {len(files_to_copy)} abstracts in {args.output_dir}")


if __name__ == "__main__":
    main()
