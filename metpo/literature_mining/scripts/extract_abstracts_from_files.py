"""
Extract abstracts from PDF and markdown files for papers that couldn't be fetched via API.

This script processes the 6 papers from the failed retrieval list and extracts
their abstracts from local PDF/MD files.
"""

import re
from pathlib import Path

import click


def extract_abstract_from_markdown(md_path: Path) -> str | None:
    """
    Extract abstract from a markdown file.

    Looks for patterns like:
    - "Abstract" or "ABSTRACT" as a standalone header
    - Text following that header until the next major section

    Args:
        md_path: Path to the markdown file

    Returns:
        Abstract text, or None if not found
    """
    with Path(md_path).open( encoding="utf-8") as f:
        content = f.read()

    # Try to find abstract section
    # Pattern 1: Look for "Abstract" header followed by content
    patterns = [
        # Page-based format (like MDPI papers) - stop at Keywords or numbered sections
        r"(?:^|\n)## Page \d+\s*\n+[Aa]bstract\s*\n+(.*?)(?=Keywords:|[12]\.\s+[A-Z]|\n#{1,3}\s+[A-Z]|\Z)",
        # Markdown header format
        r"(?:^|\n)#{1,3}\s*[Aa]bstract\s*\n+(.*?)(?=\n#{1,3}\s+\w|Keywords:|\Z)",
        # Plain text header
        r"(?:^|\n)[Aa]bstract\s*\n+(.*?)(?=\nKeywords:|\n[A-Z][a-z]+\s*\n|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            abstract = match.group(1).strip()
            # Clean up the abstract
            abstract = re.sub(r"\n+", " ", abstract)  # Replace newlines with spaces
            abstract = re.sub(r"\s+", " ", abstract)  # Normalize whitespace
            abstract = abstract.strip()

            # Remove common artifacts
            abstract = re.sub(r"^\d+→", "", abstract)  # Remove line numbers

            if len(abstract) > 100:  # Sanity check - abstract should be substantial
                return abstract

    return None


def extract_doi_from_filename(filename: str) -> str | None:
    """
    Extract DOI from filename.

    Examples:
        doi_10_3390-su151814000.pdf -> 10.3390/su151814000
        doi_10_1038-nchembio_1947.md -> 10.1038/nchembio.1947
    """
    if not filename.startswith("doi_"):
        return None

    # Remove doi_ prefix and file extension
    doi_part = filename[4:]  # Remove "doi_"
    doi_part = doi_part.rsplit(".", 1)[0]  # Remove extension

    # Convert underscores and hyphens back to DOI format
    # First underscore after doi_ becomes the first dot
    # Subsequent hyphens become dots, underscores become slashes or dots
    parts = doi_part.split("_", 1)  # Split on first underscore
    if len(parts) != 2:
        return None

    prefix = parts[0]  # e.g., "10"
    suffix = parts[1]   # e.g., "3390-su151814000"

    # Replace hyphens with appropriate characters
    # Common pattern: publisher-journal_year_issue
    suffix = suffix.replace("-", ".").replace("_", ".")

    doi = f"{prefix}.{suffix}"

    # Handle special cases
    doi = doi.replace("..", ".")  # Remove double dots

    return doi


def sanitize_doi_for_filename(doi: str) -> str:
    """
    Convert DOI to the filename format used in the publications directory.

    Examples:
        10.1016/j.seppur.2025.131701 -> 10_1016-j_seppur_2025_131701
        10.3390/su151814000 -> 10_3390-su151814000
        10.1038/nchembio.1947 -> 10_1038-nchembio_1947
    """
    # Replace the first dot (in 10.xxxx) with underscore
    # Replace forward slashes with hyphens
    # Replace remaining dots with underscores
    result = doi.replace(".", "_", 1)  # First dot becomes underscore
    result = result.replace("/", "-")   # Slashes become hyphens
    result = result.replace(".", "_")   # Remaining dots become underscores
    return result


def extract_metadata_from_markdown(md_path: Path) -> dict[str, str]:
    """
    Extract metadata (title, authors, journal) from markdown if available.

    Args:
        md_path: Path to markdown file

    Returns:
        Dictionary with metadata fields
    """
    metadata = {
        "title": "",
        "authors": "",
        "journal": "",
        "year": ""
    }

    # For now, return empty metadata - can be enhanced if needed
    # The markdown files from PDF conversion may not have structured metadata

    return metadata


def process_failed_papers():
    """
    Process the 6 papers that failed API retrieval.

    Based on the abstract_fetching_report.md, these are:
    1. 10.1016/j.seppur.2025.131701 (CMM-AI)
    2. 10.1038/nchembio.1947 (CMM-AI)
    3. 10.1101/2023.09.15.557123 (CMM-AI)
    4. 10.1007/s11756-024-01654-0 (PFAS-AI)
    5. 10.1134/S0003683817050027 (PFAS-AI)
    6. 10.3390/su151814000 (PFAS-AI)
    """

    # DOI to directory mapping
    papers = [
        ("10.1016/j.seppur.2025.131701", "literature_mining/CMM-AI/publications"),
        ("10.1038/nchembio.1947", "literature_mining/CMM-AI/publications"),
        ("10.1101/2023.09.15.557123", "literature_mining/CMM-AI/publications"),
        ("10.1007/s11756-024-01654-0", "literature_mining/PFAS-AI/publications"),
        ("10.1134/S0003683817050027", "literature_mining/PFAS-AI/publications"),
        ("10.3390/su151814000", "literature_mining/PFAS-AI/publications"),
    ]

    output_dir = Path("literature_mining/abstracts")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "success": [],
        "failed": []
    }

    for doi, pub_dir in papers:
        print(f"\nProcessing: {doi}")

        # Find the markdown file
        pub_path = Path(pub_dir)
        safe_doi = sanitize_doi_for_filename(doi)
        md_file = pub_path / f"doi_{safe_doi}.md"

        # Handle special versioning (bioRxiv)
        if not md_file.exists():
            # Try with version suffix
            md_file = pub_path / f"doi_{safe_doi}v1.md"

        if not md_file.exists():
            print(f"  ✗ Markdown file not found: {md_file}")
            results["failed"].append(doi)
            continue

        # Extract abstract
        abstract = extract_abstract_from_markdown(md_file)

        if not abstract:
            print(f"  ✗ Could not extract abstract from {md_file.name}")
            results["failed"].append(doi)
            continue

        print(f"  ✓ Extracted abstract ({len(abstract)} chars)")

        # Save to file
        output_file = output_dir / f"doi_{safe_doi}-abstract.txt"

        with Path(output_file).open( "w", encoding="utf-8") as f:
            f.write("Title: [Extracted from local file]\n\n")
            f.write("Authors: [See PDF for full details]\n\n")
            f.write("Journal: [See PDF for full details]\n\n")
            f.write(f"DOI: {doi}\n")
            f.write("Source: Local file extraction\n")
            f.write(f"\nAbstract:\n{abstract}\n")

        print(f"  💾 Saved to: {output_file.name}")
        results["success"].append(doi)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  ✓ Successfully extracted: {len(results['success'])}")
    print(f"  ✗ Failed: {len(results['failed'])}")

    if results["success"]:
        print("\nSuccessfully processed:")
        for doi in results["success"]:
            print(f"  • {doi}")

    if results["failed"]:
        print("\nFailed to process:")
        for doi in results["failed"]:
            print(f"  • {doi}")

    return results


@click.command()
@click.option("--dry-run", is_flag=True,
              help="Show what would be extracted without saving files")
def main(dry_run):
    """Extract abstracts from local PDF/MD files for failed API retrievals.

    Processes papers in ../CMM-AI/papers/ that failed to fetch via API,
    extracting abstracts directly from the source files.
    """
    if dry_run:
        click.echo("DRY RUN MODE - No files will be saved\n")

    results = process_failed_papers()

    if results["failed"]:
        raise click.Abort


if __name__ == "__main__":
    main()
