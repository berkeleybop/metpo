# METPO Development Guide for Claude Code

**Last Updated:** 2025-11-10

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
   BioPortal submission extract, or in any tagged release. Check before allocating.

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

### OBO Foundry Coding Guidelines

1. **Follow OBO Foundry ID formats** - Use METPO:XXXXXXX format
2. **Include labels for all entities** - Every term must have rdfs:label
3. **Use standard OWL Manchester syntax** - Follow OWL conventions
4. **Document definitions** - Use IAO:0000115 for term definitions
5. **Follow naming patterns** - Consistent with existing terms in the ontology
6. **Place imports appropriately** - Keep imported terms in imports directory

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
