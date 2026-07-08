# METPO Development Guide for Claude Code

**Last Updated:** 2026-06-05

---

## Source of truth and project constraints

Read these before editing ontology content or proposing architecture.

- **The Google Sheet is the source of truth for ontology content** (term labels,
  definitions, synonyms, biolink mappings, range bounds, equivalent-class
  formulas): sheet `1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU`
  ("METPO - growth_condition_terms"). The TSVs under `src/templates/` and
  `src/ontology/components/metpo_sheet.owl` are a **build cache generated from the
  sheet**.
- **Never hand-edit the committed `src/templates/*.tsv` or `src/ontology/components/metpo_sheet.owl`**,
  even to "fix" something a reviewer or Copilot flagged — the next sheet sync
  overwrites it. Fix it in the sheet (e.g. `gog sheets update ...`), then rebuild
  so the regenerated TSV/OWL are what you commit. (The `metpo-edit.owl` header
  annotations are the exception: those are edited in-repo.)
- **CI tests the committed snapshot, not the live sheet.** `qc.yml` runs
  `make test ...` without `squeaky-clean`, so sheet edits only reach CI once
  someone runs `squeaky-clean && make all` locally and commits the regenerated
  `src/templates/*.tsv` and `src/ontology/components/*.owl`.
- **ChromaDB is retired** (unpatchable critical CVE, #455/#401, removed in #498).
  Do not propose new ChromaDB-based solutions. Cross-ontology/embedding work uses
  OLS4 + local embeddings (nomic-embed-text via Ollama on the M5 GPU) +
  linkml-store/OAK; see `metpo/pipeline/cross_ontology_search.py`.
- **Scope-narrowing means relocate, not delete** (#433). Do not delete
  non-ontology content (presentations, literature-mining, analysis scripts)
  until its long-term home is decided; extraction PRs stay drafts until then.

---

## Script Development Requirements

All scripts in this project MUST meet these standards:

1. **Use uv or poetry** - consistent environment management
2. **Have Click CLI interfaces** - proper named option parsing, not ad-hoc scripts
3. **Live in scripts directories** - organized in `metpo/scripts/`, not scattered in project root, `notebooks/`, etc.
4. **Have CLI aliases in pyproject.toml** - `[project.scripts]` entries for easy invocation
5. **Be illustrated in Makefile** - integrated into workflow using `$<` and `$@`; avoid phony targets
6. **Meet production standards** - reusable tools, not one-off analysis notebooks

### Example Script Structure

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""
import click

@click.command()
@click.option('--input', '-i', required=True, help='Input file path')
@click.option('--output', '-o', required=True, help='Output file path')
def main(input: str, output: str):
    """Detailed description of the command."""
    # Implementation
    pass

if __name__ == '__main__':
    main()
```

### Adding to pyproject.toml

```toml
[project.scripts]
my-script = "metpo.scripts.my_script:main"
```

### Adding to Makefile

```makefile
output/result.tsv: input/data.tsv metpo/scripts/my_script.py
	uv run my-script --input $< --output $@
```

---

## Repository Cleanup Requirements

When cleaning up or organizing the repository:

1. **Focus on past week's mess first** - recent files (last 7 days) are usually the bloat
2. **Maximize file count reduction** - fewer files, not just disk space
3. **No duplicates** - if superseded or duplicate functionality, delete one
4. **Remove experimental throwaway code** - as many files as possible by count
5. **Clean up documentation sprawl** - consolidate redundant markdown files
6. **Improve, don't just delete** - add Click CLIs to scripts we're keeping
7. **Use discernment** - understand what each script does before deciding its fate
8. **Check automation first** - verify Makefile/imports dependencies before any deletion
9. **Keep automation working** - Makefile targets must continue to function
10. **Ask questions when uncertain** - don't guess if something is needed

### Before Deleting Any File

1. Check if referenced in Makefile: `grep -r "filename" Makefile`
2. Check if imported by other code: `grep -r "import.*filename\|from.*filename" . --include="*.py"`
3. Check git history: `git log --oneline filename`
4. Verify it's truly superseded/duplicate, not just similar

---

## ID Allocation and Term Deprecation

### The invariants — read these before touching any ID

1. **`src/templates/deprecated.tsv` is the source of truth** for all deprecated METPO terms.
   It is committed to the repo and merged into `metpo.owl` on every build. Do not treat it
   as a generated artifact — it is hand-maintained.

2. **Never reuse a burned ID.** An ID is burned if it appears in `deprecated.tsv`, in any
   BioPortal submission extract, or in any tagged release. Check before allocating. This
   spans historical numbering eras (early leading-zero IDs as well as the current
   `1xxxxxx` classes / `2xxxxxx` properties); in particular the literature-mining range
   `1000001`-`1000327` was retired and must not be reused.

3. **The research tools were a one-time bootstrap.** `generate-deprecated-template` and
   `audit-id-allocation` scanned BioPortal submissions and git history in March 2026 (PR #375)
   to produce the initial `deprecated.tsv`. Do not re-run `generate-deprecated-template` as
   part of routine maintenance — you will overwrite any hand-edits made since then. Run it
   only as a recovery tool if `deprecated.tsv` is believed to be corrupt or badly out of sync.

4. **The BioPortal submission extracts under `metadata/ontology/historical_submissions/`
   may eventually be removed.** If they are, `deprecated.tsv` still encodes everything that
   mattered in them.

### Deprecating a term (the normal workflow)

1. Remove the row from `src/templates/metpo_sheet.tsv` or `metpo-properties.tsv`.
2. Add a row to `src/templates/deprecated.tsv` with `owl:deprecated true`, label
   `"obsolete <former label>"`, and an obsolescence reason (`IAO:0000226` or `OMO:0001000`).
3. Commit both changes in the same commit.

Full details, column format, and examples: `docs/deprecation-workflow.md`.

### Allocating a new ID

```bash
make audit-ids          # regenerates reports/id-allocation-audit.md
```

The report's "Safe Ranges" section gives the next available class and property IDs.
Also run a grep sanity-check: `grep "METPO:<candidate>" src/templates/*.tsv src/templates/deprecated.tsv`

### Quick reference

| Task | Command |
|------|---------|
| See all burned IDs | `cat reports/id-allocation-audit.md` |
| Regenerate audit report | `make audit-ids` |
| Rebuild deprecated OWL component | `make -C src/ontology -f metpo.Makefile regenerate-deprecated` |
| Verify an ID is safe to use | `grep "METPO:XXXXXXX" src/templates/*.tsv src/templates/deprecated.tsv reports/id-allocation-audit.md` |

---

## Ontology Development

### Build Commands

**Host vs container targets.** Anything that runs ROBOT needs the ODK container,
invoked with the `sh run.sh make ...` wrapper from `src/ontology/`: `all`, `test`,
`test_fast`, `prepare_release`, `reason_test`, `sparql_test`, `robot_reports`,
`components/*.owl`. Targets that only shell out to host tools (`curl`, `uv`, git)
run faster **directly with `make ...`** (no container spin-up): `clean`,
`squeaky-clean`, the `../templates/*.tsv` sheet downloads, and the `diff-*`
targets. If `uv` isn't on PATH inside the container, resolve sheet URLs on the
host and pass/curl them in.

**Full build:**
```bash
cd src/ontology
sh run.sh make prepare_release
```

**Fast build (no imports):**
```bash
cd src/ontology
sh run.sh make IMP=false prepare_release
```

**Obsolete-term emission toggle (#378):** deprecated/obsolete terms come only from
`src/templates/deprecated.tsv`. `INCLUDE_OBSOLETE` controls whether they are built
into the release OWL. Default is `true` (current behaviour; the committed artifacts
and the artifact-freshness check reproduce with the default). To produce an
obsolete-free build:
```bash
cd src/ontology
sh run.sh make INCLUDE_OBSOLETE=false prepare_release
```

**Test:**
```bash
cd src/ontology
sh run.sh make test          # Full test
sh run.sh make test_fast     # Quick test
```

**Validation:**
```bash
cd src/ontology
sh run.sh make reason_test sparql_test
```

> **QC SPARQL checks must be provable.** The `sparql_test` violation queries in
> `src/sparql/*-violation.sparql` filter on the METPO namespace; a wrong filter
> once matched nothing and reported "0 violations" while CI stayed green (#487).
> Every `*-violation.sparql` therefore needs a seeded case in
> `tests/sparql_qc/qc-positive-fixture.ttl`; the meta-test
> (`.github/workflows/sparql-metatest.yml`) fails if any query matches zero rows.
> When you add or edit a check, add/adjust its fixture case in the same PR. The
> harness lives under `tests/` (not the ODK-managed `src/` tree); see
> `tests/sparql_qc/README.md`.

### GitHub Actions workflow tooling

The CI workflows are linted and security-audited in GitHub Actions (deliberately
not wired into local pre-commit hooks):

- **actionlint** (`.github/workflows/actionlint.yml`) checks workflow syntax and
  runs shellcheck on every `run:` block. It would have caught the `set -o
  pipefail` that fails under the odk container's default dash shell.
- **zizmor** (`.github/workflows/zizmor.yml`, config `.github/zizmor.yml`) is a
  static security auditor for the workflows (unpinned actions, excessive
  permissions, credential persistence, Dependabot cooldown, ...).

**Run these locally, do not wait for CI.** Whenever you are developing on a
machine where the tools are in the active environment (the M5 has Docker for
actionlint and `uvx` for zizmor), run BOTH after editing any workflow or
`dependabot.yml`, and again before pushing a branch that touches `.github/`:

```bash
# from the repo root
docker run --rm -v "$PWD":/repo:ro --workdir /repo rhysd/actionlint:1.7.12
GH_TOKEN=$(gh auth token) uvx zizmor@1.25.2 --config .github/zizmor.yml .github/
```

Both must be clean (actionlint exits 0; zizmor reports "No findings"). Fix
findings before pushing; CI is the backstop, not the first line of defense. If
the tools are not installed, do not block, but say so rather than skipping
silently. After a `pinact` upgrade or a manual workflow change, re-run them.

Actions are pinned to full commit SHAs (with a `# vX.Y.Z` comment) via
`pinact run --update --min-age 7`, following the NMDC convention; Dependabot keeps
them current. The ODK-generated `qc.yml` is excluded from both tools because
`sh run.sh make update_repo` regenerates it, so hardening there would not persist.

**Maintenance:**
```bash
cd src/ontology
sh run.sh make clean              # Clean build artifacts
sh run.sh make refresh-imports    # Update imported ontologies
sh run.sh make squeaky-clean      # Deep clean
```

### Typical Local Build Workflow

```bash
cd src/ontology/
sh run.sh make squeaky-clean
sh run.sh make update_repo
sh run.sh make refresh-imports
sh run.sh make prepare_release
```

### Ontology Structure

**Key files:**
- **Edit file:** `src/ontology/metpo-edit.owl` - primary ontology editing file
- **Templates:** `src/templates/metpo_sheet.tsv` - term templates
- **Imports:** `src/ontology/imports/` - imported ontologies (bfo, obi, omp, pato, so, micro, mpo)
- **Release files:** `metpo.owl`, `metpo.obo`, `metpo.json` - generated release formats

### IRI and namespace scheme (read before touching any IRI)

METPO term IRIs are **bare-numeric under w3id**: `https://w3id.org/metpo/<digits>`
(e.g. `https://w3id.org/metpo/1000602`). There is **no `METPO_` infix**. The
`METPO:` CURIE prefix is notation only; it expands to `https://w3id.org/metpo/`
(declared in `metpo-odk.yaml` `namespaces:` and the template `--add-prefix`).

- w3id delegates only the `/metpo/` path, so the resolvable base, the ontology
  IRI, the version IRI, and all products must sit under `https://w3id.org/metpo/`.
- The **main ontology IRI must be `https://w3id.org/metpo/metpo.owl`**.
  `https://w3id.org/metpo.owl` is outside the delegation and 404s (#435, #465).
- Do not introduce `http://purl.obolibrary.org/obo/METPO_...` PURLs — obolibrary
  is not registered for METPO and those 404.
- This is the exact scheme the QC SPARQL filters key on
  (`STRSTARTS(str(?term), "https://w3id.org/metpo/")`); a wrong prefix silently
  matches nothing (see the meta-test note above).

### OBO Foundry Coding Guidelines

1. **Use the IRI scheme above** - bare-numeric `https://w3id.org/metpo/<digits>`,
   written `METPO:<digits>` in templates/sheets.
2. **Include labels for all entities** - Every term must have rdfs:label
3. **Use standard OWL Manchester syntax** - Follow OWL conventions
4. **Aristotelian definitions** - `IAO:0000115` definitions follow "A ⟨genus⟩ that
   ⟨differentia⟩", where **the genus is literally the parent class's label** (not a
   free-text noun phrase, not a non-existent class). This is enforced
   deterministically by `metpo-proposal-lint` (DEF-FORM check, baseline ratchet);
   accepted genus/differentia connectors include `that`, `in which`, `where`,
   `characterized by`, `describing` (not `with`/`having`).
5. **Follow naming patterns** - Consistent with existing terms in the ontology
6. **Place imports appropriately** - Keep imported terms in imports directory

### Synonym Column Conventions (source-bound vs ontology-native)

The classes-tab template has two kinds of synonym columns; they have different editing rules.

**Source-bound columns** (always paired with a source URL column):

| Column | Source column | Holds |
|---|---|---|
| `madin synonym or field` | `Madin synonym source` | Verbatim field name or value from Madin et al. |
| `bacdive keyword synonym` | `Bacdive synonym source` | Verbatim keyword from BacDive |
| `bactotraits related synonym` | `Bactotraits synonym source` | Verbatim column name from the BactoTraits CSV |
| `metatraits synonym` | `MetaTraits synonym source` | Verbatim term from MetaTraits |

**Rule:** values in source-bound columns are verbatim from the named source. Do **not** normalize them, even when the source contains:

- typos (BactoTraits `Ox_microerophile` for microaerophile)
- inconsistent prefixes (BactoTraits header has `pHR_8_to_10` then `10_to_14` for the next bin, no `pHR_` prefix)
- non-English forms
- unusual capitalization or punctuation

The implicit contract is that downstream consumers (e.g. `kg-microbe`'s BactoTraits transformer) match on the exact source string. Normalizing breaks matching.

**Source-bound synonyms are reified, and duplicates across bins are intentional.** Each source-bound value is asserted as an `oboInOwl:hasRelatedSynonym` and reified on an `owl:Axiom` carrying the provenance source (`IAO:0000119` -> e.g. `https://bacdive.dsmz.de/`). The **same related synonym appearing on several classes (e.g. across temperature/pH/oxygen bins) is deliberate** - it maps distinct external-system values to METPO entities. Do **not** "de-duplicate" them. (The known *defect* is the separate `confirmed exact synonym` overload in #444, not these.)

**How `kg-microbe` consumes METPO (why the verbatim rule matters):** it reads (1) `metpo.owl` from `main` for ontology nodes/edges, and (2) the ROBOT-template TSVs **pinned to a git tag** for its BacDive/BactoTraits/Madin/MetaTraits synonym-to-predicate mappings. So when METPO removes or renames a property, the pinned tag in kg-microbe must be bumped or the old mapping keeps being used. Treat source-bound synonym strings and property IRIs as a downstream contract.

**Ontology-native columns:**

| Column | Holds |
|---|---|
| `confirmed exact synonym` | Clean US English synonyms curated for METPO itself (`oboInOwl:hasExactSynonym`) |
| `literature mining related synonyms` | OntoGPT-derived candidates (`oboInOwl:hasRelatedSynonym`) |
| `biolink close match` | `skos:closeMatch` to a Biolink class |
| `biolink broad match` *(added to sheet 2026-05-18; appears in `src/templates/metpo_sheet.tsv` after any build that re-fetches; not in the committed snapshot at this PR's HEAD)* | `skos:broadMatch` to a Biolink class (when METPO term is more specific) |

**Important nuance about the committed TSV vs the Google Sheet (today's flow):** the Google Sheet is the conceptual source of truth for ontology content. `src/templates/metpo_sheet.tsv` in the repo is a build cache. The Makefile rule `../templates/metpo_sheet.tsv:` has *no* prerequisites, so Make re-fetches from the sheet **only when the local file is missing**. Three concrete cases:

| Invocation | TSV state | Uses sheet? |
|---|---|---|
| `make all` after `make squeaky-clean` (or otherwise missing TSV) | absent → re-fetched via curl | yes (live sheet) |
| `make all` on a fresh clone / CI run | present (committed snapshot) | no — uses committed TSV as-is |
| `make all` after local edits to the TSV | present (locally edited) | no — local edits survive until next `squeaky-clean` |

CI runs `make test IMP=false PAT=false MIR=false` from `.github/workflows/qc.yml` (no `squeaky-clean`), so CI tests against the **committed** TSV and the **committed** `components/metpo_sheet.owl`, not the live sheet. To get sheet edits into CI, someone has to run `squeaky-clean && make all`, then commit the regenerated `src/templates/*.tsv` and `src/ontology/components/*.owl`. Until then the committed snapshot is what gets tested.

This is mostly fine because the cadence of sheet edits is "edit then run a verifying build then commit," not "edit and forget." But it does mean contributors browsing the repo via GitHub see whatever was last committed, and that's also what CI is checking.

**Rule:** ontology-native columns use normal, consistent US English orthography. Foreign-language forms, source typos, and one-off transcriptions belong in source-bound columns or in `literature mining related synonyms`, not here.

When a source value happens to coincide with the desired ontology-native synonym, write it in *both* columns; do not rely on the source-bound column carrying English semantics.

---

## Project Organization

### Directory Structure

```
metpo/
├── metpo/                    # Python package
│   ├── scripts/             # Production CLI scripts (with Click, pyproject.toml entries)
│   └── *.py                 # Core module code
├── src/
│   ├── ontology/            # ODK ontology development
│   └── templates/           # ROBOT templates
├── notebooks/               # Analysis notebooks (should have minimal .py files)
├── literature_mining/       # OntoGPT extraction and analysis
├── docs/                    # Documentation
└── reports/                 # Generated reports
```

### What Belongs Where

**metpo/scripts/:**
- ✅ Production CLI tools with Click interfaces
- ✅ Scripts with pyproject.toml entries
- ✅ Scripts used in Makefile
- ❌ One-off analysis scripts
- ❌ Experimental/throwaway code

**notebooks/:**
- ✅ Jupyter notebooks (.ipynb)
- ✅ Analysis results (.tsv, .csv)
- ✅ ChromaDB analysis outputs
- ⚠️ Python scripts (should be minimal, prefer moving to metpo/scripts/)

**literature_mining/:**
- ✅ OntoGPT templates (.yaml)
- ✅ Extraction outputs (.yaml)
- ✅ Analysis results (.md, .tsv)
- ⚠️ Utility scripts (consider moving to metpo/scripts/)

**Root directory:**
- ✅ README.md, LICENSE, pyproject.toml, Makefile
- ✅ CLAUDE.md (this file)
- ❌ Analysis scripts (.py)
- ❌ Cleanup planning docs (.md)
- ❌ Data files (.tsv, .csv)

---

## Common Tasks

### Running a Script

**With CLI alias:**
```bash
uv run my-script --input data.tsv --output result.tsv
```

**Direct invocation:**
```bash
uv run python metpo/scripts/my_script.py --input data.tsv --output result.tsv
```

### Adding a New Production Script

1. Create script in `metpo/scripts/new_script.py` with Click CLI
2. Add entry to `pyproject.toml`:
   ```toml
   [project.scripts]
   new-script = "metpo.scripts.new_script:main"
   ```
3. Add Makefile target if part of workflow:
   ```makefile
   output/new-result.tsv: input/data.tsv metpo/scripts/new_script.py
       uv run new-script --input $< --output $@
   ```
4. Test: `uv run new-script --help`

### Checking What Uses a File

```bash
# Check Makefile
grep -n "filename" Makefile

# Check Python imports
grep -r "import.*filename\|from.*filename" . --include="*.py" --exclude-dir=.venv

# Check git history
git log --oneline --all -- path/to/filename

# Check references in all files
grep -r "filename" . --exclude-dir=.venv --exclude-dir=.git
```

---

## Environment Setup

**Install dependencies:**
```bash
uv sync
```

**Run with uv:**
```bash
uv run python script.py
uv run my-cli-command
```

**ODK container:**
```bash
cd src/ontology
sh run.sh make <target>
```

---

## Git Workflow

**Before committing:**
1. Run tests if available
2. Check ontology builds: `cd src/ontology && sh run.sh make test_fast`
3. Verify no broken imports/references
4. Clean up any temporary files

**Commit messages:**
- Use conventional commit format
- Be specific about what changed
- Reference issues when applicable

---

## Notes

- **Always use `uv run`** for Python execution
- **Check automation before deleting** any file
- **Scripts without Click CLIs** are analysis notebooks, not production tools
- **Past week files** (check with `find . -newermt "7 days ago"`) are prime cleanup candidates
- **Ask before deleting** if unsure about a file's purpose

---

## QC, release-diff, and BioPortal mechanics

### ROBOT report: run the default profile for the true dashboard state

The repo's custom ROBOT report profile can report "No violations" while the
**default** ROBOT profile still flags thousands of findings. Typing
`owl:deprecated` as `^^xsd:boolean` (issue #467) let ROBOT recognize the
deprecated terms and cleared most of them, but to see the true OBO-dashboard
state run `robot report` with the DEFAULT profile, not the custom one.

### Scope: exactly four source-bound databases

METPO harmonizes exactly four source-bound databases, the only `IAO:0000119`
synonym sources in `metpo.owl`: BacDive, BactoTraits, Madin
(`jmadin/bacteria_archaea_traits`), and MetaTraits. kg-microbe is the downstream
consumer. Do not name NMDC or BugSigDB in any METPO description or scope text
(NMDC was removed from `dcterms:description` in PR #532). BugSigDB and MicroTrait
are broader-landscape context, not source-bound.

### Diff targets and the pre-PR release-diff workflow

- `make release_diff` (generated Makefile): a ROBOT diff of the OWL currently
  served at `https://w3id.org/metpo/metpo.owl` (GitHub main via w3id) against the
  locally built `metpo.owl`, OWL-level. Output: `reports/release-diff.md`.
- `make diff-sheets` (metpo.Makefile): live Google Sheet vs committed TSV at HEAD.
- `make diff-release`: TSV at the last git tag vs HEAD.
- `make diff-drafts`: saved drafts vs current templates.

Before opening a significant PR, show the OWL-level delta vs main:

    sh run.sh make squeaky-clean
    sh run.sh make prepare_release   # re-fetches the Sheet, rebuilds artifacts
    sh run.sh make release_diff      # diffs the new build vs current w3id/main

`squeaky-clean` alone is not enough: `release_diff` needs a locally built
`metpo.owl`, so `prepare_release` must run first.

### BioPortal is pull-based

BioPortal is configured with
`pullLocation: https://raw.githubusercontent.com/berkeleybop/metpo/refs/heads/main/metpo.owl`.
Its poller runs nightly and creates a new submission whenever that content
changes, so a tagged release propagates within about 24 hours with no manual
web-UI re-submission. The default
`data.bioontology.org/ontologies/METPO/latest_submission` response omits
`pullLocation` and similar infrastructure fields; query with `?display=all` to
see the pull config.

---

## Quick Reference

| Task | Command |
|------|---------|
| Build ontology | `cd src/ontology && sh run.sh make prepare_release` |
| Test ontology | `cd src/ontology && sh run.sh make test_fast` |
| Run script | `uv run script-name --help` |
| Install deps | `uv sync` |
| Check Makefile usage | `grep "filename" Makefile` |
| Find recent files | `find . -newermt "7 days ago" -type f` |
| List CLI scripts | `grep "project.scripts" -A 20 pyproject.toml` |

---

**Remember:** Scripts without Click CLIs and pyproject.toml entries are analysis notebooks, not production tools. They should live in analysis directories or be upgraded to production standards.
