# CLI Standardization Assessment and Plan

**Date**: 2025-11-10
**Goal**: Standardize all Python scripts to use Click, register in pyproject.toml, and integrate with Makefile

---

## Current State Summary

### Total Unregistered Scripts: 28 files

**By Category:**
- Literature Mining Analysis: 10 scripts (6.8K total lines)
- Literature Mining Utilities: 8 scripts (1.3K total lines)
- Presentation Scripts: 9 scripts (1.5K total lines)
- Already has Click: 2 scripts (metpo_assessor.py, visualize_ner.py)

**Current CLI Framework Status:**
- ✅ **Using Click**: 2 scripts
- ⚠️ **Using argparse**: 5 scripts (need conversion)
- ❌ **No CLI**: 21 scripts (need full CLI addition)

---

## Effort Estimation by Script Type

### **Category 1: No CLI Framework (21 scripts) - HIGH EFFORT**

**Location**: `metpo/literature_mining/analysis/` (10 files)

| Script | Lines | Effort | Priority | Notes |
|--------|-------|--------|----------|-------|
| analyze_metpo_grounding.py | ~200 | Medium | High | Core analysis script |
| analyze_metpo_grounding_filtered.py | ~180 | Medium | High | Core analysis script |
| extract_metpo_entities.py | ~150 | Medium | High | Entity extraction |
| find_metpo_terms.py | ~120 | Low | High | Term finding utilities |
| analyze_extractions.py | ~250 | Medium | Medium | May be redundant |
| analyze_coverage_by_source_type.py | ~180 | Medium | Low | One-time analysis? |
| analyze_metpo_efficiency.py | ~160 | Medium | Low | One-time metrics? |
| analyze_metpo_database_alignment.py | ~200 | Medium | Low | One-time analysis? |
| compare_extractions.py | ~140 | Low | Low | One-time comparison? |
| validate_extractions.py | ~130 | Low | Low | Validation covered elsewhere? |

**Effort per script**: 2-4 hours
- Add Click decorators and main() function
- Define argument/option parameters
- Add help text and documentation
- Register in pyproject.toml
- Test CLI interface
- Add Makefile target (optional)

**Total for Category 1**: 20-40 hours for 10 high-priority scripts

---

### **Category 2: Argparse Scripts (5 scripts) - MEDIUM EFFORT**

**Location**: `metpo/literature_mining/scripts/`

| Script | Lines | Effort | Priority | Notes |
|--------|-------|--------|----------|-------|
| fetch_abstracts_from_dois.py | 150 | Low | High | Documented in ACKNOWLEDGMENTS |
| extract_abstracts_from_files.py | 254 | Medium | High | File extraction utility |
| dedupe_and_filter_abstracts.py | 154 | Low | High | Deduplication (documented) |
| dedupe_by_content.py | 184 | Low | Medium | Content-based dedup |
| calculate_metrics.py | 88 | Low | Medium | Metrics calculation |

**Effort per script**: 1-2 hours
- Replace argparse with Click
- Convert ArgumentParser → @click.command()
- Convert add_argument() → @click.option()
- Update main() signature
- Register in pyproject.toml
- Test CLI interface

**Total for Category 2**: 5-10 hours for 5 scripts

---

### **Category 3: Already Using Click (2 scripts) - LOW EFFORT**

**Location**: Mixed

| Script | Lines | Status | Effort | Action |
|--------|-------|--------|--------|--------|
| visualize_ner.py | 312 | ✅ Has Click | 15 min | Just register in pyproject.toml |
| metpo_assessor.py | 2094 | ✅ Has Click | 15 min | Just register in pyproject.toml |

**Total for Category 3**: 30 minutes

---

### **Category 4: Presentation Scripts (9 scripts) - OPTIONAL**

**Location**: `metpo/presentations/` (ICBO 2025)

| Script | Lines | Effort | Priority | Notes |
|--------|-------|--------|----------|-------|
| analyze_bactotraits.py | 153 | Low | Optional | One-time figure generation |
| analyze_kg_microbe_metpo.py | 178 | Low | Optional | One-time figure generation |
| analyze_madin_etal.py | 187 | Low | Optional | One-time figure generation |
| analyze_ontogpt_grounding.py | 134 | Low | Optional | One-time figure generation |
| analyze_ontology_landscape.py | 209 | Low | Optional | One-time figure generation |
| analyze_primary_sources.py | 165 | Low | Optional | One-time figure generation |
| analyze_sssom_mappings.py | 71 | Low | Optional | One-time figure generation |
| calculate_minimum_import_set.py | 161 | Low | Optional | One-time figure generation |
| generate_feedback_loop.py | 213 | Low | Optional | One-time figure generation |

**Recommendation**: Leave as-is unless they need to be rerun frequently
- These are research output scripts for a specific presentation
- Already executed and generated figures
- Low value in CLI standardization unless reusability is important

**Total for Category 4**: 9-18 hours if standardized (not recommended)

---

## Recommended Phased Approach

### **Phase 1: Quick Wins (1 hour)**
Register the 2 scripts that already have Click:
- [ ] `visualize-ner` → `metpo.literature_mining.analysis.visualize_ner:main`
- [ ] `metpo-assessor` → `metpo.literature_mining.analysis.metpo_assessor:main`

---

### **Phase 2: High-Priority argparse → Click (5-10 hours)**
Convert the 5 utility scripts documented in ACKNOWLEDGMENTS.md:
- [ ] `fetch-abstracts-from-dois` → `metpo.literature_mining.scripts.fetch_abstracts_from_dois:main`
- [ ] `extract-abstracts-from-files` → `metpo.literature_mining.scripts.extract_abstracts_from_files:main`
- [ ] `dedupe-and-filter-abstracts` → `metpo.literature_mining.scripts.dedupe_and_filter_abstracts:main`
- [ ] `dedupe-by-content` → `metpo.literature_mining.scripts.dedupe_by_content:main`
- [ ] `calculate-extraction-metrics` → `metpo.literature_mining.scripts.calculate_metrics:main`

---

### **Phase 3: Core Analysis Scripts (20-40 hours)**
Add Click CLI to high-value analysis scripts:
- [ ] `analyze-metpo-grounding` → `metpo.literature_mining.analysis.analyze_metpo_grounding:main`
- [ ] `analyze-metpo-grounding-filtered` → `metpo.literature_mining.analysis.analyze_metpo_grounding_filtered:main`
- [ ] `extract-metpo-entities` → `metpo.literature_mining.analysis.extract_metpo_entities:main`
- [ ] `find-metpo-terms` → `metpo.literature_mining.analysis.find_metpo_terms:main`

---

### **Phase 4: Optional - Remaining Scripts (10-20 hours)**
Decide whether to:
- Add CLI to remaining analysis scripts
- Delete one-time analysis scripts
- Archive completed analysis scripts

---

## Detailed Work Breakdown for Each Script Type

### **Type A: No CLI → Add Click (Example: analyze_metpo_grounding.py)**

**Current structure:**
```python
#!/usr/bin/env python3
import yaml
from pathlib import Path

def extract_entities_from_yaml(yaml_path: Path):
    # ... implementation

def main():
    # Hardcoded paths
    yaml_dir = Path("literature_mining/ontogpt_output")
    for yaml_file in yaml_dir.glob("*.yaml"):
        process(yaml_file)

if __name__ == "__main__":
    main()
```

**Changes needed:**
```python
#!/usr/bin/env python3
import click
import yaml
from pathlib import Path

def extract_entities_from_yaml(yaml_path: Path):
    # ... implementation (no changes)

@click.command()
@click.argument('yaml_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path),
              help='Output file for results')
@click.option('--format', type=click.Choice(['tsv', 'json', 'yaml']),
              default='tsv', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(yaml_dir, output, format, verbose):
    """Analyze OntoGPT YAML outputs for METPO grounding coverage."""
    for yaml_file in yaml_dir.glob("*.yaml"):
        if verbose:
            click.echo(f"Processing {yaml_file}")
        process(yaml_file)

    if output:
        save_results(output, format)

if __name__ == "__main__":
    main()
```

**Steps:**
1. Add `import click`
2. Add `@click.command()` decorator to main()
3. Convert hardcoded paths → `@click.argument()`
4. Add useful options with `@click.option()`
5. Replace `print()` with `click.echo()`
6. Add docstring (becomes CLI help text)
7. Register in pyproject.toml

**Time**: 2-3 hours per script

---

### **Type B: argparse → Click (Example: fetch_abstracts_from_dois.py)**

**Current structure:**
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Fetch abstracts from DOIs")
    parser.add_argument('input', help='Input TSV file with DOIs')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--doi-column', default='doi', help='DOI column name')
    args = parser.parse_args()

    fetch_abstracts_from_file(args.input, args.output, args.doi_column)
```

**Changes needed:**
```python
import click

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', type=click.Path(),
              help='Output file for results')
@click.option('--doi-column', default='doi',
              help='Name of column containing DOIs')
def main(input_file, output_file, doi_column):
    """Fetch abstracts from DOIs using artl-mcp's Europe PMC integration."""
    fetch_abstracts_from_file(input_file, output_file, doi_column)
```

**Steps:**
1. Replace `import argparse` → `import click`
2. Replace `ArgumentParser()` → `@click.command()`
3. Replace `add_argument()` → `@click.argument()` or `@click.option()`
4. Update main() signature to accept parameters directly
5. Remove `args = parser.parse_args()` and `args.` prefixes
6. Test that all argument behavior is preserved

**Time**: 1-2 hours per script

---

### **Type C: Already Click → Just Register (Example: visualize_ner.py)**

**Current structure:**
```python
import click

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', default='ner_visualization.html')
def main(input_file, output_file):
    """Visualize NER coverage from OntoGPT output."""
    # ... implementation

if __name__ == '__main__':
    main()
```

**Changes needed:**
Add to `pyproject.toml`:
```toml
visualize-ner = "metpo.literature_mining.analysis.visualize_ner:main"
```

**Steps:**
1. Add entry to `[project.scripts]` section
2. Test: `uv sync && uv run visualize-ner --help`

**Time**: 15 minutes per script

---

## pyproject.toml Registration Template

After adding Click CLI to each script, register in `pyproject.toml`:

```toml
[project.scripts]
# Tools (existing)
extract-rank-triples = "metpo.tools.extract_rank_triples:extract_taxon_ranks"
convert-chem-props = "metpo.tools.convert_chem_props:main"
import-bactotraits = "metpo.tools.import_bactotraits:main"

# Literature Mining - Analysis
analyze-metpo-grounding = "metpo.literature_mining.analysis.analyze_metpo_grounding:main"
analyze-metpo-grounding-filtered = "metpo.literature_mining.analysis.analyze_metpo_grounding_filtered:main"
extract-metpo-entities = "metpo.literature_mining.analysis.extract_metpo_entities:main"
find-metpo-terms = "metpo.literature_mining.analysis.find_metpo_terms:main"
visualize-ner = "metpo.literature_mining.analysis.visualize_ner:main"
metpo-assessor = "metpo.literature_mining.analysis.metpo_assessor:main"

# Literature Mining - Utilities
fetch-abstracts-from-dois = "metpo.literature_mining.scripts.fetch_abstracts_from_dois:main"
extract-abstracts-from-files = "metpo.literature_mining.scripts.extract_abstracts_from_files:main"
dedupe-and-filter-abstracts = "metpo.literature_mining.scripts.dedupe_and_filter_abstracts:main"
dedupe-by-content = "metpo.literature_mining.scripts.dedupe_by_content:main"
calculate-extraction-metrics = "metpo.literature_mining.scripts.calculate_metrics:main"
```

---

## Makefile Integration

Add convenience targets for frequently-used commands:

```makefile
# Literature mining pipeline
.PHONY: fetch-abstracts dedupe-abstracts analyze-grounding

fetch-abstracts:
	uv run fetch-abstracts-from-dois literature_mining/dois.tsv -o literature_mining/abstracts.tsv

dedupe-abstracts:
	uv run dedupe-and-filter-abstracts literature_mining/abstracts.tsv -o literature_mining/abstracts_deduped.tsv

analyze-grounding:
	uv run analyze-metpo-grounding literature_mining/ontogpt_output/ -o data/literature_mining/grounding_analysis.tsv
```

---

## Total Effort Summary

| Phase | Scripts | Hours | Priority |
|-------|---------|-------|----------|
| Phase 1: Register existing Click | 2 | 0.5 | **High** |
| Phase 2: argparse → Click | 5 | 5-10 | **High** |
| Phase 3: Add Click to core analysis | 4 | 8-12 | **Medium** |
| Phase 4: Remaining analysis scripts | 6 | 12-18 | **Low** |
| Phase 5: Presentation scripts | 9 | 9-18 | **Optional** |
| **TOTAL (excluding Phase 5)** | **17** | **25-40 hours** | |
| **TOTAL (all phases)** | **26** | **34-58 hours** | |

---

## Recommendation

**Pragmatic Approach:**

1. **Do Phase 1 now** (30 min) - Quick wins
2. **Do Phase 2 next** (5-10 hrs) - High-value utilities already documented in provenance
3. **Evaluate Phase 3** (8-12 hrs) - Only if analysis scripts are run frequently
4. **Skip Phase 4** - Low-value, possibly redundant
5. **Skip Phase 5** - Research outputs, already executed

**Total realistic effort**: 6-11 hours to standardize the most important 7 scripts

---

## Benefits of Standardization

**After completing Phases 1-2, you get:**
- ✅ Consistent CLI interface across all tools
- ✅ Built-in help text: `uv run <command> --help`
- ✅ Shell completion support (with click-completion)
- ✅ Easy to document in README
- ✅ Integration with Makefile targets
- ✅ Better error handling and validation
- ✅ Testing support with Click's CliRunner

**Questions to Answer Before Proceeding:**
1. Which analysis scripts are run regularly vs one-time?
2. Should presentation scripts be reusable or archived?
3. Are any of the "possibly redundant" scripts actually needed?
4. What's the priority for CLI standardization vs other work?

---

## Next Steps

1. **User decision**: Which phases to tackle?
2. **Create issue**: Track CLI standardization work
3. **Start with Phase 1**: 30-minute quick win
4. **Iterate**: One script at a time, test thoroughly
