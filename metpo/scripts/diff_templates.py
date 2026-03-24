"""Structured diff of METPO ROBOT templates across sources.

Compares template TSV files by METPO ID, reporting:
- IDs present in one source but not the other
- Label changes for common IDs
- Cell-level diffs for common IDs (optional)

Sources can be local files, git refs, or the live Google Sheet.
"""

import csv
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import click

SPREADSHEET_ID = "1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU"
SHEET_GIDS = {
    "classes": "121955004",
    "properties": "2094089867",
}
TEMPLATE_PATHS = {
    "classes": "src/templates/metpo_sheet.tsv",
    "properties": "src/templates/metpo-properties.tsv",
}


def resolve_source(source: str, template: str) -> Path:
    """Resolve a source specifier to a local file path.

    Accepts:
        - "gsheet" — download live Google Sheet
        - "HEAD", "main", tag names, commit hashes — extract from git
        - file path — use directly
    """
    if source == "gsheet":
        gid = SHEET_GIDS[template]
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?exportFormat=tsv&gid={gid}"
        tmp = Path(tempfile.mktemp(suffix=".tsv"))
        urllib.request.urlretrieve(url, tmp)
        return tmp

    # Try as git ref
    git_path = TEMPLATE_PATHS[template]
    try:
        result = subprocess.run(
            ["git", "show", f"{source}:{git_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        tmp = Path(tempfile.mktemp(suffix=".tsv"))
        tmp.write_text(result.stdout)
        return tmp
    except subprocess.CalledProcessError:
        pass

    # Try as file path
    p = Path(source)
    if p.exists():
        return p

    raise click.BadParameter(f"Cannot resolve '{source}' as gsheet, git ref, or file path")


def load_ids(path: Path) -> dict[str, str]:
    """Load METPO IDs and labels from a TSV, skipping header rows."""
    ids = {}
    with Path(path).open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row or not row[0].strip().startswith("METPO:"):
                continue
            metpo_id = row[0].strip()
            label = row[1].strip() if len(row) > 1 else ""
            ids[metpo_id] = label
    return ids


def load_full_rows(path: Path) -> dict[str, list[str]]:
    """Load full rows keyed by METPO ID."""
    rows = {}
    with Path(path).open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row or not row[0].strip().startswith("METPO:"):
                continue
            metpo_id = row[0].strip()
            rows[metpo_id] = row
    return rows


def load_headers(path: Path) -> list[str]:
    """Load the human-readable header row (first row)."""
    with Path(path).open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row:
                return [c.strip() for c in row]
    return []


def _print_cell_diffs(path_a: Path, path_b: Path, common: list[str], max_cell_diffs: int) -> None:
    """Print cell-level diffs for common IDs between two template files."""
    headers = load_headers(path_b)
    rows_a = load_full_rows(path_a)
    rows_b = load_full_rows(path_b)
    diffs = []
    for mid in common:
        ra = rows_a.get(mid, [])
        rb = rows_b.get(mid, [])
        max_cols = max(len(ra), len(rb))
        for col in range(max_cols):
            va = ra[col].strip() if col < len(ra) else ""
            vb = rb[col].strip() if col < len(rb) else ""
            if va != vb:
                col_name = headers[col] if col < len(headers) else f"col[{col}]"
                diffs.append((mid, col_name, va[:60], vb[:60]))
    if diffs:
        click.echo(f"\n  ~~~ Cell-level diffs ({len(diffs)} cells across common IDs) ~~~")
        for mid, col_name, va, vb in diffs[:max_cell_diffs]:
            click.echo(f"    {mid} [{col_name}]: '{va}' -> '{vb}'")
        if len(diffs) > max_cell_diffs:
            click.echo(f"    ... and {len(diffs) - max_cell_diffs} more")


def compare(
    name_a: str,
    path_a: Path,
    name_b: str,
    path_b: Path,
    *,
    cell_diffs: bool = False,
    max_cell_diffs: int = 50,
) -> dict:
    """Compare two template files by METPO ID. Returns summary dict."""
    ids_a = load_ids(path_a)
    ids_b = load_ids(path_b)

    only_a = sorted(set(ids_a) - set(ids_b))
    only_b = sorted(set(ids_b) - set(ids_a))
    common = sorted(set(ids_a) & set(ids_b))

    label_changes = [(mid, ids_a[mid], ids_b[mid]) for mid in common if ids_a[mid] != ids_b[mid]]

    click.echo(f"\n{'=' * 70}")
    click.echo(f"  {name_a} ({len(ids_a)} IDs) vs {name_b} ({len(ids_b)} IDs)")
    click.echo(f"{'=' * 70}")
    click.echo(
        f"  Common: {len(common)}  |  Only in {name_a}: {len(only_a)}"
        f"  |  Only in {name_b}: {len(only_b)}"
    )

    if only_a:
        click.echo(f"\n  --- Only in {name_a} ({len(only_a)}) ---")
        for mid in only_a:
            click.echo(f"    {mid}\t{ids_a[mid]}")

    if only_b:
        click.echo(f"\n  +++ Only in {name_b} ({len(only_b)}) ---")
        for mid in only_b:
            click.echo(f"    {mid}\t{ids_b[mid]}")

    if label_changes:
        click.echo(f"\n  ~~~ Label changes ({len(label_changes)}) ~~~")
        for mid, la, lb in label_changes:
            click.echo(f"    {mid}: '{la}' -> '{lb}'")

    if cell_diffs and common:
        _print_cell_diffs(path_a, path_b, common, max_cell_diffs)

    if not only_a and not only_b and not label_changes:
        click.echo("\n  IDs and labels are identical.")

    return {
        "only_a": only_a,
        "only_b": only_b,
        "common": len(common),
        "label_changes": len(label_changes),
    }


@click.command()
@click.option(
    "--source-a",
    "-a",
    default="gsheet",
    help="First source: 'gsheet', git ref (HEAD, main, tag), or file path",
)
@click.option(
    "--source-b",
    "-b",
    default="HEAD",
    help="Second source: 'gsheet', git ref (HEAD, main, tag), or file path",
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["classes", "properties", "both"]),
    default="both",
    help="Which template to diff",
)
@click.option("--cell-diffs/--no-cell-diffs", default=False, help="Show cell-level diffs")
@click.option("--max-cell-diffs", default=50, help="Maximum number of cell diffs to display")
def main(
    source_a: str,
    source_b: str,
    template: str,
    cell_diffs: bool,
    max_cell_diffs: int,
) -> None:
    """Diff METPO ROBOT templates across sources.

    Compare templates between Google Sheets, git refs, and local files.

    Examples:

        # Google Sheet vs current HEAD
        diff-templates

        # Google Sheet vs last release
        diff-templates -a gsheet -b 2025-12-12

        # Current branch vs main
        diff-templates -a HEAD -b main

        # Two local files
        diff-templates -a src/templates/metpo_sheet.tsv -b /tmp/old_sheet.tsv -t classes
    """
    templates = ["classes", "properties"] if template == "both" else [template]

    for tmpl in templates:
        click.echo(f"\n{'#' * 70}")
        click.echo(f"# {tmpl.upper()} TEMPLATE ({TEMPLATE_PATHS[tmpl]})")
        click.echo(f"{'#' * 70}")

        path_a = resolve_source(source_a, tmpl)
        path_b = resolve_source(source_b, tmpl)

        compare(
            source_a,
            path_a,
            source_b,
            path_b,
            cell_diffs=cell_diffs,
            max_cell_diffs=max_cell_diffs,
        )


if __name__ == "__main__":
    main()
