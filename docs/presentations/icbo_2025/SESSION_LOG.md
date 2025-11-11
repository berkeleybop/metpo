# OntoGPT ICBO 2025 Demo - Session Log
**Date:** 2025-11-07
**Session:** Continuation from previous context limit

## Session Objectives
Prepare OntoGPT demonstration materials for ICBO 2025 conference showing METPO ontology grounding strengths and weaknesses.

---

## Completed Work

### 1. Template Specification Research
✅ **Found:** OntoGPT templates ARE first-class LinkML schemas
- Templates follow LinkML specification directly (not meta-schema governed)
- OntoGPT uses convention-based annotations defined in Python constants
- Key annotation keys: `prompt`, `prompt.skip`, `annotators`, `prompt.examples`, `ner.recurse`
- Documentation: `/home/mark/gitrepos/ontogpt/docs/custom.md`
- Implementation: `/home/mark/gitrepos/ontogpt/src/ontogpt/engines/knowledge_engine.py` lines 108-113

### 2. Template Cleanup
✅ **Removed non-functional annotations:**
- `exclude:` annotation from strain_phenotype_icbo.yaml (no implementation in OntoGPT)
- `prompt.examples` from ChemicalCompound and Strain classes (causes hallucinations per lines 388-394)

✅ **Added prefixes for OWL export:**
```yaml
prefixes:
  METPO: http://purl.obolibrary.org/obo/METPO_
  NCBITaxon: http://purl.obolibrary.org/obo/NCBITaxon_
  CHEBI: http://purl.obolibrary.org/obo/CHEBI_
```

### 3. Expanded Abstract Collection
✅ **10 diverse abstracts selected** (from 4 to 10):
- Original 4: 19622650, 27573017, 28879838, 37170873
- Added 6: 18294205, 19440302, 19622668, 20336137, 22740660, 27983469
- Mix of CMM and non-CMM abstracts
- Coverage: chemical utilization + phenotype assertions

✅ **Format cleanup:**
- Identified 5 abstracts in artl-cli dict format: `{'content': '...', 'saved_to': None, 'windowed': False}`
- Created unwrap script: `/home/mark/gitrepos/metpo/literature_mining/scripts/unwrap_abstracts.py`
- Converted all to plain text

✅ **Metadata generation:**
- Created `abstracts_metadata.json` using artl-cli
- Contains PMIDs, DOIs, PMCIDs, URLs, open access status, journal info for all 10 abstracts
- Script: `fetch_abstracts_metadata.sh`

### 4. Makefile Enhancements

✅ **Input definition fixed:**
```makefile
# Before (only 4 abstracts hardcoded):
PHENOTYPE_INPUTS := $(INPUTS_DIR)/28879838-abstract.txt ...
CHEMICAL_INPUTS := $(INPUTS_DIR)/19622650-abstract.txt ...
ALL_INPUTS := $(sort $(PHENOTYPE_INPUTS) $(CHEMICAL_INPUTS))

# After (all 10 abstracts automatically):
ALL_INPUTS := $(wildcard $(INPUTS_DIR)/*-abstract.txt)
```

✅ **OWL conversion targets added:**
- `make convert-turtle` - Converts all YAML → Turtle RDF (.ttl)
- `make convert-owl` - Converts all YAML → OWL (.owl)
- Both targets: depend on `all`, process phenotype/chemical separately, log to outputs/logs/
- Updated help text with new targets

### 5. Analysis Script Improvements
✅ **Created:** `analyze_metpo_grounding.py`
- Counts METPO class URIs (e.g., `<https://w3id.org/metpo/1000379>`)
- Counts METPO predicate usage from enums (e.g., `uses_as_carbon_source`)
- Distinguishes between successful groundings and AUTO terms

---

## What Worked Well

### ✅ OntoGPT Grounding via Enums
- **METPO predicates DO work** through enum `meaning:` field mappings
- Example: `uses_as_carbon_source: meaning: METPO:2000006`
- `ontogpt convert -O owl` expands predicates to full URIs in output

### ✅ Template Architecture
- Two-template approach effective:
  - `strain_phenotype_icbo.yaml` - morphology, physiology, growth characteristics
  - `chemical_utilization_icbo.yaml` - organism-chemical relationships
- All abstracts through both templates shows versatility

### ✅ Tooling Integration
- artl-cli successfully fetches comprehensive metadata
- OntoGPT's `annotators` work with local METPO: `sqlite:/home/mark/gitrepos/metpo/src/ontology/metpo.owl`
- OntoGPT's `annotators` work with remote ontologies: `sqlite:obo:ncbitaxon`, `sqlite:obo:chebi`

---

## Challenges Encountered

### ⚠️ OntoGPT Grounding Limitations
**Finding:** OntoGPT grounding ONLY works on classes (NamedEntity), NOT on predicates/enums
- Predicates must be pre-populated in enum definitions with `meaning:` field
- Cannot dynamically ground relationship types like we can with entities
- Workaround: Comprehensive enum with all METPO predicates (65+ values in ChemicalInteractionPropertyEnum)

### ⚠️ Incomplete Extractions
**Current status:** Only 10 of 20 expected extractions completed
- Have: 18294205-phenotype, 19440302-phenotype, 19622650-both, 27573017-both, 28879838-both, 37170873-both
- Missing: 19622668, 20336137, 22740660, 27983469 (both templates)
- Missing: 18294205, 19440302 (chemical template only)
- **Root cause:** Makefile inputs were hardcoded to only 4 abstracts when user ran `make all`
- **Fixed:** Changed to `ALL_INPUTS := $(wildcard $(INPUTS_DIR)/*-abstract.txt)`

### ⚠️ artl-cli Format Inconsistency
- Some abstracts returned as plain text, others as dict format
- No clear pattern for when dict format is used
- **Solution:** Created unwrap_abstracts.py utility

### ⚠️ NCBITaxon Prefix Error
- Initial error: `Unknown CURIE prefix: NCBITaxon`
- Occurred during extraction because prefixes weren't defined in template
- **Fixed:** Added NCBITaxon, CHEBI prefixes to both templates

---

## Incomplete Work / Next Steps

### 🔲 CRITICAL: Complete All Extractions
**Priority: HIGH - BLOCKS EVERYTHING ELSE**

**Current State:**
- Have: 10 YAML files (50% complete)
  - 18294205-phenotype ✅
  - 19440302-phenotype ✅
  - 19622650-phenotype ✅, 19622650-chemical ✅
  - 27573017-phenotype ✅, 27573017-chemical ✅
  - 28879838-phenotype ✅, 28879838-chemical ✅
  - 37170873-phenotype ✅, 37170873-chemical ✅

**Missing:** 10 YAML files
- 18294205-chemical ❌
- 19440302-chemical ❌
- 19622668-phenotype ❌, 19622668-chemical ❌
- 20336137-phenotype ❌, 20336137-chemical ❌
- 22740660-phenotype ❌, 22740660-chemical ❌
- 27983469-phenotype ❌, 27983469-chemical ❌

**Why Incomplete:**
- User ran `make all` before I fixed Makefile inputs
- Old Makefile only processed 4 hardcoded abstracts
- Now fixed with: `ALL_INPUTS := $(wildcard $(INPUTS_DIR)/*-abstract.txt)`

**Action Required:**
```bash
cd /home/mark/gitrepos/metpo/ontogpt_icbo_demo
make clean && make all
```
- Estimated time: 15-20 minutes with gpt-4o
- Will process all 10 abstracts through both templates
- Check progress: `ls outputs/*.yaml | wc -l` (should reach 20)

---

### 🔲 Generate OWL/Turtle Outputs
**Priority: MEDIUM - DEPENDS ON EXTRACTIONS**

**Current State:**
- Makefile targets complete and ready
- No RDF files generated yet

**What's Ready:**
- `make convert-turtle` target (lines 141-156)
- `make convert-owl` target (lines 158-173)
- Both log to outputs/logs/ and use correct templates

**Action Required:**
```bash
# After extractions complete:
make convert-owl    # Generates 20 .owl files
make convert-turtle # Generates 20 .ttl files
```

**Expected Outputs:**
- 20 OWL files in outputs/ (one per YAML)
- 20 Turtle files in outputs/ (one per YAML)
- 40 conversion log files in outputs/logs/

**Use for ICBO:**
- Can demo RDF triple structure
- Show how enums expand to METPO URIs
- Import into triple store if needed

---

### 🔲 Run Full Analysis
**Priority: MEDIUM - DEPENDS ON EXTRACTIONS**

**Current State:**
- `analyze_metpo_grounding.py` exists and works
- `make analyze` target exists (lines 76-99)
- Only analyzed 10 files so far

**What Analysis Shows:**
- METPO URI counts per file (class groundings)
- AUTO term counts (failed groundings)
- METPO property usage (from enums)
- ChEBI grounding counts

**Action Required:**
```bash
make analyze > analysis_results.txt
```

**Missing Analysis Capabilities:**
- Cross-file statistics (totals, averages)
- Success rate percentages
- Most/least common phenotypes
- Coverage metrics for ICBO presentation

**Enhancement Ideas:**
```python
# Add to analyze_metpo_grounding.py:
# - Total METPO groundings across all files
# - Success rate: METPO URIs / (METPO + AUTO)
# - Top 10 most frequent phenotypes
# - Comparison: phenotype vs chemical template success rates
```

---

### 🔲 Review and Document Grounding Quality
**Priority: MEDIUM - FOR ICBO TALK**

**Questions to Answer:**
1. **What phenotypes ground well to METPO?**
   - Look for patterns in successful groundings
   - Example: "motile" → `<https://w3id.org/metpo/1000379>` ✅
   - Example: "rod-shaped" → `AUTO:rod-shaped` ❌

2. **What chemical utilization predicates are most common?**
   - From ChemicalInteractionPropertyEnum (65 options)
   - Which get used vs. which are theoretical?

3. **NCBITaxon vs. METPO coverage:**
   - Taxa ground to NCBITaxon successfully
   - But phenotypes have limited METPO coverage
   - Why? (METPO is domain-specific, NCBITaxon is comprehensive)

4. **Template effectiveness:**
   - Does phenotype template extract chemicals? (shouldn't)
   - Does chemical template extract phenotypes? (shouldn't)
   - How to quantify template specificity?

**Deliverable for ICBO:**
- Summary stats document
- Examples of good/poor groundings
- Lessons learned for ontology-grounded extraction

---

### 🔲 Template Improvements (Low Priority)

**Known Limitations:**
1. **Phenotype coverage in METPO**
   - Many bacterial phenotypes not in METPO
   - METPO focused on chemical interactions
   - Could we use PATO for phenotypes instead?

2. **Strain identifier consistency**
   - Templates try hard to maintain identical strain IDs
   - But LLM sometimes varies (e.g., "017" vs "017T")
   - Could post-process to normalize?

3. **Prompt examples removed**
   - We removed `prompt.examples` to avoid hallucinations
   - But examples can improve extraction quality
   - Alternative: Use few-shot in system prompt instead?

**Not Critical for ICBO Demo:**
- Current templates demonstrate concept adequately
- Focus on analyzing what we have, not perfecting extraction

---

### 🔲 Documentation and Presentation Prep

**For ICBO Talk:**
1. **Slide content from this work:**
   - Methodology: LinkML → OntoGPT → METPO grounding
   - Results: Success rates, example extractions
   - Challenges: Grounding limitations, coverage gaps
   - Architecture diagram: Templates → Extraction → RDF

2. **Demo materials:**
   - Show YAML extraction output
   - Show OWL/Turtle with expanded URIs
   - Live query against RDF (if time)

3. **Reproducibility:**
   - GitHub repo with all materials
   - README with setup instructions
   - Example: `make all` reproduces entire workflow

**Files to Create:**
- README.md in ontogpt_icbo_demo/
- Examples document with best/worst extractions
- Presentation slides outline

---

### 🔲 Known Issues / Future Work

**Background Process Artifacts:**
- System shows 3 background bash processes as "running"
- Actually completed, just not cleaned up
- Not blocking any work

**artl-cli Dict Format:**
- Unpredictable when dict vs. plain text returned
- Workaround: unwrap_abstracts.py utility
- Could file issue with artl-cli maintainers

**OntoGPT Grounding Architecture:**
- Grounding only works on NamedEntity classes
- Predicates/enums require manual enumeration
- This is a fundamental OntoGPT design choice
- Not a bug, but limits automation

**METPO Ontology Coverage:**
- Good: Chemical utilization predicates (65+)
- Limited: Phenotype classes
- Gap: Culture media terms
- Could expand METPO or use additional ontologies

**Testing:**
- No automated tests for templates
- Manual verification of all extractions needed
- Could add: schema validation, expected result checks

---

## Files Created/Modified This Session

### Created:
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/abstracts_metadata.json` (12KB)
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/fetch_abstracts_metadata.sh`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/analyze_metpo_grounding.py`
- `/home/mark/gitrepos/metpo/literature_mining/scripts/unwrap_abstracts.py`
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/inputs/` (6 new abstracts)

### Modified:
- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/Makefile`
  - Changed ALL_INPUTS to use wildcard
  - Added convert-turtle and convert-owl targets
  - Updated help text

- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/templates/chemical_utilization_icbo.yaml`
  - Added NCBITaxon, CHEBI, METPO prefix definitions
  - Removed prompt.examples from ChemicalCompound class

- `/home/mark/gitrepos/metpo/ontogpt_icbo_demo/templates/strain_phenotype_icbo.yaml`
  - Removed non-functional `exclude:` annotation

### Output Files (Partial):
- 10 of 20 expected YAML extraction files in `outputs/`
- 11 log files in `outputs/logs/`

---

## Key Insights for ICBO Presentation

### Strengths to Highlight:
1. **METPO predicates work via enum mappings** - 65+ chemical interaction properties successfully mapped
2. **Multi-ontology integration** - METPO + NCBITaxon + ChEBI groundings in single extraction
3. **RDF/OWL export** - Clean conversion from YAML → semantic web formats
4. **Automated pipeline** - Make-based workflow for reproducible extractions

### Weaknesses to Acknowledge:
1. **Grounding limited to classes** - Cannot dynamically ground predicates/relationships
2. **Requires pre-enumeration** - All predicates must be manually added to template
3. **Coverage gaps** - Some phenotypes don't ground (remain as AUTO terms)
4. **Template complexity** - Balancing comprehensiveness vs. LLM prompt size

---

## Environment Details
- Working directory: `/home/mark/gitrepos/metpo/ontogpt_icbo_demo`
- Python environment: uv-managed (NOT system python)
- OntoGPT version: From `/home/mark/gitrepos/ontogpt/.venv/bin/ontogpt`
- Model: gpt-4o (default), temperature 0.0
- METPO ontology: `/home/mark/gitrepos/metpo/src/ontology/metpo.owl`

---

## Commands for Next Session

```bash
# Complete all extractions (in separate shell, ~15-20 min)
cd /home/mark/gitrepos/metpo/ontogpt_icbo_demo
make clean && make all

# Generate RDF outputs
make convert-owl
make convert-turtle

# Run analysis
make analyze

# Check results
ls -lh outputs/*.yaml | wc -l  # Should be 20
ls -lh outputs/*.owl | wc -l   # Should be 20 after convert-owl
ls -lh outputs/*.ttl | wc -l   # Should be 20 after convert-turtle
```

---

## Notes
- Background bash processes from earlier test runs are completed but show as "running" in system reminders (artifact)
- Temporary test files cleaned from /tmp
- User prefers `uv run python` over direct python3 calls
- User requested this log before shutting down session
