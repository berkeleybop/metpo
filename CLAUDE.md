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
- ✅ ICBO_PREP.md (temporary for conference prep)
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

## MetaTraits Mapping Workflow

METPO integrates with the MetaTraits database (metatraits.embl.de), a comprehensive collection of microbial trait data. We maintain formal SSSOM mappings between MetaTraits trait cards, METPO terms, and KG-Microbe nodes.

### Data Sources

1. **MetaTraits Database** - 2,860+ microbial trait cards with ontology cross-references (OMP, PATO, GO, CHEBI, etc.)
2. **METPO in KG-Microbe** - 360+ METPO terms integrated into the KG-Microbe knowledge graph
3. **METPO Ontology** - Primary source ontology with definitions and cross-references

### Fetching MetaTraits Data

```bash
# Fetch latest trait cards from metatraits.embl.de
uv run fetch-metatraits --output data/mappings/metatraits_cards.tsv

# Or use Makefile
make data/mappings/metatraits_cards.tsv
```

### Creating Mappings

The mapping pipeline uses four strategies:

1. **Direct label matching** (exactMatch) - Exact string matches after normalization
2. **Synonym matching** (closeMatch) - MetaTraits names matching METPO synonyms
3. **Shared ontology references** (relatedMatch) - Both reference same OMP/PATO/etc term
4. **Fuzzy string matching** (closeMatch) - Similarity-based matching with configurable threshold

```bash
# Create mappings with all strategies
uv run create-metatraits-mappings \
  --metatraits-input data/mappings/metatraits_cards.tsv \
  --kgmicrobe-nodes /path/to/merged-kg_nodes.tsv \
  --output data/mappings/metatraits_metpo_kgmicrobe.sssom.tsv \
  --report reports/metatraits_mapping_analysis.md \
  --fuzzy-threshold 85

# Or use Makefile (recommended)
make metatraits-mappings
```

### Output Files

- **SSSOM TSV**: `data/mappings/metatraits_metpo_kgmicrobe.sssom.tsv` - Formal mappings following SSSOM standard
- **Summary Report**: `reports/metatraits_mapping_analysis.md` - Coverage statistics and examples

### Mapping Quality

The pipeline produces high-quality mappings with:
- Mean confidence: ~0.95
- exactMatch mappings: 1.0 confidence
- closeMatch (synonyms): 0.95 confidence
- relatedMatch (shared refs): 0.85 confidence
- Fuzzy matches: 0.85-0.95 confidence based on similarity

### Customizing Mapping Parameters

```bash
# Disable fuzzy matching (faster, fewer mappings)
uv run create-metatraits-mappings --no-fuzzy ...

# Adjust fuzzy threshold (higher = stricter)
uv run create-metatraits-mappings --fuzzy-threshold 90 ...
```

### Integration with KG-Microbe

Set the `KGMICROBE_NODES` environment variable or Makefile variable:

```bash
# In .env file
KGMICROBE_NODES=/path/to/merged-kg_nodes.tsv

# Or override in Makefile
make metatraits-mappings KGMICROBE_NODES=/custom/path/merged-kg_nodes.tsv
```

### Validation

SSSOM files can be validated using sssom-py:

```bash
uv run sssom validate data/mappings/metatraits_metpo_kgmicrobe.sssom.tsv
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
| Fetch MetaTraits | `uv run fetch-metatraits --output data/mappings/metatraits_cards.tsv` |
| Create MetaTraits mappings | `make metatraits-mappings` |
| Check Makefile usage | `grep "filename" Makefile` |
| Find recent files | `find . -newermt "7 days ago" -type f` |
| List CLI scripts | `grep "project.scripts" -A 20 pyproject.toml` |

---

**Remember:** Scripts without Click CLIs and pyproject.toml entries are analysis notebooks, not production tools. They should live in analysis directories or be upgraded to production standards.
