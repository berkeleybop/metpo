"""Audit all METPO IDs ever allocated across templates, releases, and BioPortal submissions.

Produces a comprehensive report of active, burned, and historical IDs to prevent
ID reuse. See https://github.com/berkeleybop/metpo/issues/374
"""

import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import click

TEMPLATE_PATHS = [
    "src/templates/metpo_sheet.tsv",
    "src/templates/metpo-properties.tsv",
]


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


def get_label_from_git(
    ref: str, template_path: str, metpo_id: str, *, cwd: Path | None = None
) -> str:
    """Look up a label for a METPO ID from a template at a given git ref."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{template_path}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
    except subprocess.CalledProcessError:
        return ""
    prefix = f"METPO:{metpo_id}"
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if parts and parts[0].strip() == prefix and len(parts) > 1:
            return parts[1].strip()
    return ""


@dataclass
class AuditResult:
    """Results of an ID allocation audit."""

    current_class_ids: set[str] = field(default_factory=set)
    current_prop_ids: set[str] = field(default_factory=set)
    submission_ids: dict[str, set[str]] = field(default_factory=dict)
    release_ids: dict[str, set[str]] = field(default_factory=dict)
    all_ids: set[str] = field(default_factory=set)
    burned_ids: set[str] = field(default_factory=set)

    @property
    def current_ids(self) -> set[str]:
        return self.current_class_ids | self.current_prop_ids


def collect_ids(repo_root: Path) -> AuditResult:
    """Collect all METPO IDs from every known source."""
    result = AuditResult()

    # Current templates
    click.echo("Scanning current templates...", err=True)
    result.current_class_ids = extract_ids_from_tsv(repo_root / "src/templates/metpo_sheet.tsv")
    result.current_prop_ids = extract_ids_from_tsv(repo_root / "src/templates/metpo-properties.tsv")

    # BioPortal entity extracts
    click.echo("Scanning BioPortal entity extracts...", err=True)
    extracts_dir = repo_root / "metadata/ontology/historical_submissions/entity_extracts"
    if extracts_dir.is_dir():
        for f in sorted(extracts_dir.glob("metpo_submission_*_all_entities.tsv")):
            sub_num = re.search(r"submission_(\d+)", f.name)
            if sub_num:
                result.submission_ids[sub_num.group(1)] = extract_ids_from_entity_extract(f)

    # Tagged releases
    click.echo("Scanning tagged releases...", err=True)
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
        ids = set()
        for tmpl in TEMPLATE_PATHS:
            ids |= extract_ids_from_git_ref(tag, tmpl, cwd=repo_root)
        if ids:
            result.release_ids[tag] = ids

    # Compute union and burned
    result.all_ids = set(result.current_ids)
    for ids in result.submission_ids.values():
        result.all_ids |= ids
    for ids in result.release_ids.values():
        result.all_ids |= ids
    result.burned_ids = result.all_ids - result.current_ids

    return result


def classify_burned(burned_ids: set[str]) -> dict[str, list[str]]:
    """Classify burned IDs by era."""
    return {
        "era1": sorted(i for i in burned_ids if len(i) == 6 and i.startswith("0")),
        "era2": sorted(i for i in burned_ids if len(i) == 7 and i.startswith("0")),
        "era3_classes": sorted(i for i in burned_ids if i.startswith("1")),
        "era3_props": sorted(i for i in burned_ids if i.startswith("2")),
        "test": sorted(i for i in burned_ids if i.startswith("9")),
    }


def resolve_burned_prop_labels(
    era3_props: list[str],
    release_ids: dict[str, set[str]],
    *,
    cwd: Path | None = None,
) -> dict[str, str]:
    """Find the last known label for each burned property ID."""
    labels: dict[str, str] = {}
    for pid in era3_props:
        for tag in reversed(list(release_ids.keys())):
            if pid in release_ids[tag]:
                label = get_label_from_git(tag, "src/templates/metpo-properties.tsv", pid, cwd=cwd)
                if label:
                    labels[pid] = f"{label} (last in {tag})"
                    break
    return labels


def build_provenance(
    burned_ids: set[str],
    submission_ids: dict[str, set[str]],
    release_ids: dict[str, set[str]],
) -> dict[str, list[str]]:
    """Build provenance chains for burned IDs."""
    prov: dict[str, list[str]] = defaultdict(list)
    for sub, ids in sorted(submission_ids.items(), key=lambda item: int(item[0])):
        for i in ids & burned_ids:
            prov[i].append(f"sub{sub}")
    for tag, ids in release_ids.items():
        for i in ids & burned_ids:
            prov[i].append(f"tag:{tag}")
    return dict(prov)


def format_report(audit: AuditResult, *, cwd: Path | None = None) -> str:
    """Format the audit result as a markdown report."""
    classified = classify_burned(audit.burned_ids)
    prop_labels = resolve_burned_prop_labels(classified["era3_props"], audit.release_ids, cwd=cwd)
    provenance = build_provenance(audit.burned_ids, audit.submission_ids, audit.release_ids)

    highest_class = max((i for i in audit.current_ids if i.startswith("1")), default="?")
    highest_prop = max((i for i in audit.current_ids if i.startswith("2")), default="?")

    lines = [
        "# METPO ID Allocation Audit",
        "",
        f"**Generated:** {datetime.now(tz=UTC).date().isoformat()}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Active IDs (current templates) | {len(audit.current_ids)} |",
        f"| Active classes | {len(audit.current_class_ids)} |",
        f"| Active properties | {len(audit.current_prop_ids)} |",
        f"| Burned IDs (ever used, not currently active) | {len(audit.burned_ids)} |",
        f"| Total unique IDs ever allocated | {len(audit.all_ids)} |",
        f"| Highest active class ID | METPO:{highest_class} |",
        f"| Highest active property ID | METPO:{highest_prop} |",
        f"| BioPortal submissions scanned | {len(audit.submission_ids)} |",
        f"| Tagged releases scanned | {len(audit.release_ids)} |",
        "",
        "## Burned Era 3 Property IDs (never reuse)",
        "",
        "These properties appeared in tagged releases or BioPortal submissions but are no longer in the templates.",
        "",
        "| ID | Label | Provenance |",
        "|---|---|---|",
    ]
    for pid in classified["era3_props"]:
        label = prop_labels.get(pid, "unknown")
        prov = ", ".join(provenance.get(pid, ["git-only"]))
        lines.append(f"| METPO:{pid} | {label} | {prov} |")

    lines += [
        "",
        "## Burned ID Counts by Era",
        "",
        "| Era | Description | Burned IDs |",
        "|-----|-------------|-----------|",
        f"| Era 1 | 6-digit (000xxx), submissions 2-3 | {len(classified['era1'])} |",
        f"| Era 2 | 7-digit (0000xxx), submissions 3-5 | {len(classified['era2'])} |",
        f"| Era 3 classes | 1xxxxxx, retired literature-mining terms | {len(classified['era3_classes'])} |",
        f"| Era 3 properties | 2xxxxxx, removed without deprecation | {len(classified['era3_props'])} |",
        f"| Test | 9999999 | {len(classified['test'])} |",
        "",
        "## Safe Ranges for New Terms",
        "",
        "| Type | Next safe ID | Based on |",
        "|------|-------------|----------|",
        f"| Classes | METPO:{int(highest_class) + 1} | highest active + 1 |",
        f"| Properties | METPO:{int(highest_prop) + 1} | highest active + 1 |",
        "",
        "## Sources Scanned",
        "",
        "| Source | IDs found |",
        "|--------|----------|",
        f"| `src/templates/metpo_sheet.tsv` | {len(audit.current_class_ids)} |",
        f"| `src/templates/metpo-properties.tsv` | {len(audit.current_prop_ids)} |",
    ]
    for sub in sorted(audit.submission_ids.keys(), key=int):
        lines.append(f"| BioPortal submission {sub} | {len(audit.submission_ids[sub])} |")
    for tag, ids in audit.release_ids.items():
        lines.append(f"| Tag `{tag}` | {len(ids)} |")

    return "\n".join(lines) + "\n"


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output file path (default: stdout)",
)
def main(output: str | None) -> None:
    """Audit all METPO IDs ever allocated and report active vs burned."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    audit = collect_ids(repo_root)
    report = format_report(audit, cwd=repo_root)

    if output:
        Path(output).write_text(report, encoding="utf-8")
        click.echo(f"Report written to {output}", err=True)
    else:
        click.echo(report)


if __name__ == "__main__":
    main()
