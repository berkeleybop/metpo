"""Generate a ROBOT template for all burned (historically used but no longer active) METPO IDs.

Each burned ID gets proper OBO deprecation axioms:
- owl:deprecated true
- rdfs:label prefixed with "obsolete "
- IAO:0000231 (has obsolescence reason)

The output TSV is consumed by ROBOT to produce components/deprecated.owl,
which is merged into the ontology during prepare_release.

See https://github.com/berkeleybop/metpo/issues/374
"""

import re
import subprocess
from pathlib import Path

import click

TEMPLATE_PATHS = [
    "src/templates/metpo_sheet.tsv",
    "src/templates/metpo-properties.tsv",
]

# Obsolescence reasons (IAO individuals)
REASON_PLACEHOLDER_REMOVED = "IAO:0000226"
REASON_OUT_OF_SCOPE = "OMO:0001000"


def extract_ids_from_tsv(path: Path) -> set[str]:
    """Extract METPO numeric IDs from a TSV file."""
    ids = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            match = re.match(r"METPO:(\d+)", line)
            if match:
                ids.add(match.group(1))
    return ids


def extract_ids_from_entity_extract(path: Path) -> set[str]:
    """Extract METPO numeric IDs from a BioPortal entity extract TSV."""
    ids = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            for match in re.finditer(r"w3id\.org/metpo/(\d+)", line):
                ids.add(match.group(1))
    return ids


def extract_ids_from_git_ref(ref: str, template_path: str, *, cwd: Path | None = None) -> set[str]:
    """Extract METPO numeric IDs from a template at a given git ref."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{template_path}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
    except subprocess.CalledProcessError:
        return set()
    ids = set()
    for line in result.stdout.splitlines():
        match = re.match(r"METPO:(\d+)", line)
        if match:
            ids.add(match.group(1))
    return ids


def collect_all_ids(repo_root: Path) -> tuple[set[str], set[str]]:
    """Collect current and all-ever IDs. Returns (current_ids, all_ids)."""
    current_ids: set[str] = set()
    for tmpl in TEMPLATE_PATHS:
        current_ids |= extract_ids_from_tsv(repo_root / tmpl)

    all_ids = set(current_ids)

    # BioPortal entity extracts
    extracts_dir = repo_root / "metadata/ontology/historical_submissions/entity_extracts"
    if extracts_dir.is_dir():
        for f in sorted(extracts_dir.glob("metpo_submission_*_all_entities.tsv")):
            all_ids |= extract_ids_from_entity_extract(f)

    # Tagged releases
    tags_out = subprocess.run(
        ["git", "tag", "--sort=creatordate"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_root,
    )
    for raw_tag in tags_out.stdout.strip().splitlines():
        tag = raw_tag.strip()
        if not tag:
            continue
        for tmpl in TEMPLATE_PATHS:
            all_ids |= extract_ids_from_git_ref(tag, tmpl, cwd=repo_root)

    return current_ids, all_ids


def _labels_from_extracts(extracts_dir: Path) -> dict[str, tuple[str, str, str]]:
    """Collect labels from BioPortal entity extracts (lower priority)."""
    labels: dict[str, tuple[str, str, str]] = {}
    if not extracts_dir.is_dir():
        return labels
    for f in sorted(extracts_dir.glob("metpo_submission_*_all_entities.tsv")):
        sub_num = re.search(r"submission_(\d+)", f.name)
        source = f"sub{sub_num.group(1)}" if sub_num else f.name
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                id_match = re.search(r"metpo/(\d+)", parts[0])
                if not id_match:
                    continue
                numeric_id = id_match.group(1)
                label = parts[2].strip().strip('"')
                owl_type = _normalize_type(parts[1]) if len(parts) > 1 else "owl:Class"
                if label and numeric_id not in labels:
                    labels[numeric_id] = (label, owl_type, source)
    return labels


def _labels_from_tags(repo_root: Path) -> dict[str, tuple[str, str | None, str]]:
    """Collect labels from tagged releases (higher priority — overwrites).

    Returns owl_type=None when the template column is not a real owl: type
    (e.g., old templates had parent CURIEs in column 3).
    """
    labels: dict[str, tuple[str, str | None, str]] = {}
    tags_out = subprocess.run(
        ["git", "tag", "--sort=creatordate"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_root,
    )
    for raw_tag in tags_out.stdout.strip().splitlines():
        tag = raw_tag.strip()
        if not tag:
            continue
        for tmpl in TEMPLATE_PATHS:
            try:
                result = subprocess.run(
                    ["git", "show", f"{tag}:{tmpl}"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=repo_root,
                )
            except subprocess.CalledProcessError:
                continue
            for line in result.stdout.splitlines():
                parts = line.split("\t")
                if not parts or not parts[0].strip().startswith("METPO:"):
                    continue
                numeric_id = parts[0].strip().replace("METPO:", "")
                label = parts[1].strip() if len(parts) > 1 else ""
                raw_type = parts[2].strip() if len(parts) > 2 else ""
                # Old templates had parent CURIEs in column 3, not owl:Type.
                # Return None so collect_labels can preserve the extract's type.
                owl_type = raw_type if raw_type.startswith("owl:") else None
                if label:
                    labels[numeric_id] = (label, owl_type, f"tag:{tag}")
    return labels


def collect_labels(repo_root: Path) -> dict[str, tuple[str, str, str]]:
    """Collect last-known label, OWL type, and source for every METPO ID.

    Returns dict of numeric_id → (label, owl_type, source).
    Tagged release labels take priority over BioPortal entity extract labels.
    """
    extracts_dir = repo_root / "metadata/ontology/historical_submissions/entity_extracts"
    labels = _labels_from_extracts(extracts_dir)
    # Tag labels take priority, but only update type if the tag provides a real owl: type
    for numeric_id, (label, owl_type, source) in _labels_from_tags(repo_root).items():
        if numeric_id in labels and owl_type is None:
            # Keep the extract's type, just update label and source
            _, existing_type, _ = labels[numeric_id]
            labels[numeric_id] = (label, existing_type, source)
        else:
            resolved_type = owl_type if owl_type is not None else "owl:Class"
            labels[numeric_id] = (label, resolved_type, source)
    return labels


def _normalize_type(raw_type: str) -> str:
    """Normalize OWL type from entity extract format to ROBOT template format."""
    raw = raw_type.strip().strip("<>")
    if "ObjectProperty" in raw:
        return "owl:ObjectProperty"
    if "DatatypeProperty" in raw or "DataProperty" in raw:
        return "owl:DataProperty"
    if "AnnotationProperty" in raw:
        return "owl:AnnotationProperty"
    return "owl:Class"


def classify_reason(numeric_id: str) -> str:
    """Determine the obsolescence reason for a burned ID."""
    n = int(numeric_id)
    # Era 1/2 IDs — numbering scheme abandoned
    if len(numeric_id) in (6, 7) and numeric_id.startswith("0"):
        return REASON_OUT_OF_SCOPE
    # Test ID
    if numeric_id == "9999999":
        return REASON_PLACEHOLDER_REMOVED
    # Era 3 literature-mining terms (1000001-1000327, retired in sub 9)
    if 1000001 <= n <= 1000327:
        return REASON_OUT_OF_SCOPE
    # Properties removed without deprecation (PR #317)
    if 2000200 <= n <= 2000299:
        return REASON_PLACEHOLDER_REMOVED
    return REASON_PLACEHOLDER_REMOVED


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False),
    required=True,
    help="Output ROBOT template TSV path",
)
def main(output: str) -> None:
    """Generate ROBOT template for all deprecated METPO IDs."""
    repo_root = Path(__file__).resolve().parent.parent.parent

    click.echo("Collecting IDs from all sources...", err=True)
    current_ids, all_ids = collect_all_ids(repo_root)
    burned_ids = all_ids - current_ids

    click.echo(f"Found {len(burned_ids)} burned IDs", err=True)

    click.echo("Collecting labels...", err=True)
    labels = collect_labels(repo_root)

    # Build ROBOT template rows
    rows: list[list[str]] = []
    for numeric_id in sorted(burned_ids):
        label, owl_type, _source = labels.get(numeric_id, ("", "owl:Class", "unknown"))

        # Format the CURIE correctly for the era
        if len(numeric_id) <= 7 and numeric_id.startswith("0"):
            curie = f"METPO:{numeric_id}"
        else:
            curie = f"METPO:{numeric_id}"

        obsolete_label = f"obsolete {label}" if label else f"obsolete METPO:{numeric_id}"
        reason = classify_reason(numeric_id)

        rows.append([curie, obsolete_label, owl_type, "true", reason])

    # Write ROBOT template
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        # Row 1: human-readable headers
        f.write("ID\tlabel\tTYPE\tdeprecated\tobsolescence reason\n")
        # Row 2: ROBOT directives
        f.write("ID\tLABEL\tTYPE\tA owl:deprecated\tAI IAO:0000231\n")
        for row in rows:
            f.write("\t".join(row) + "\n")

    click.echo(f"Wrote {len(rows)} deprecated terms to {output}", err=True)


if __name__ == "__main__":
    main()
