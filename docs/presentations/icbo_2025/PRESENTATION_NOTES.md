# ICBO 2025 Presentation Notes

## Slide 1: Title Slide Issues

### METPO Acronym Not Fully Expanded
- **Current:** "METPO: A Pragmatic Ontology for Microbial Ecophysiological Traits"
- **Issue:** Missing the "Phenotype" component
- **Full Expansion:** **M**icrobial **E**cophysiological **T**rait and **P**henotype **O**ntology
- **Source:** See README.md line 5: "Microbial ecophysiological trait and phenotype ontology"

### Key Term to Define: Ecophysiological

**Ecophysiological** (or ecophysiology) refers to the study of how organisms' physiological processes respond to and interact with their environment.

In the microbial context:
- **Ecophysiological traits** are physiological characteristics that determine how microbes function in their ecological niches
- Examples include:
  - Temperature preferences (psychrophile, mesophile, thermophile)
  - pH tolerance (acidophile, neutrophile, alkaliphile)
  - Oxygen requirements (aerobe, anaerobe, facultative)
  - Salinity tolerance (halophile, non-halophile)
  - Metabolic capabilities (carbon sources, electron donors/acceptors)

**Why it matters for METPO:**
- These traits are critical for understanding microbial ecology and biotechnology applications
- They're measured and reported differently across databases (BacDive, BactoTraits, etc.)
- METPO provides semantic standardization for integrating this heterogeneous data

## Suggested Talk Flow
1. Introduce METPO with full acronym expansion
2. Define "ecophysiological" with concrete examples
3. Explain why standardizing these traits matters for data integration

---

## Slide 2: Data Integration Challenge - Authenticity Issue

### Problem
The three data source examples should **faithfully represent** how each source actually encodes "this organism is a mesophile" in their original format.

### Current State
- **BacDive:** Shows nested JSON with `"mesophilic"` - needs verification
- **BactoTraits:** Shows incorrect vertical format - needs actual three-header structure
- **Madin et al.:** Shows simple CSV with `temp_pref,mesophilic` - needs verification

### Required Information
To make these examples authentic, we need:

1. **BacDive (nested JSON format)**
   - Actual JSON structure for temperature trait
   - Exact field names and nesting
   - Actual value used (e.g., "mesophilic", "mesophile", or categorical?)

2. **BactoTraits (three-header CSV)**
   - Row 1: Units
   - Row 2: Descriptions
   - Row 3: Column names
   - Actual column structure for temperature class
   - How "mesophile" appears in the data rows

3. **Madin et al. (flat CSV)**
   - Actual column name for temperature preference
   - Exact value encoding (e.g., "mesophilic", "mesophile", numeric?)

### Goal
Show the **same semantic concept** (mesophile) encoded in **three genuinely different ways** to motivate why ontology-based standardization is essential.

---

## Authentic Data Examples for Slide 2

Based on actual source files in `/Users/MAM/Documents/gitrepos/metpo/local/`:

### 1. BacDive (JSON with keywords)
**Source:** BacDive uses keywords for temperature classification
**Path:** `Keywords` → `mesophilic`
**Format:**
```json
{
  "Keywords": [
    "mesophilic",
    "Gram-negative"
  ]
}
```

**Alternative (structured path - more detailed but longer):**
```json
{
  "Culture and growth conditions": {
    "culture temp": {
      "@ref": 5523,
      "type": "optimum",
      "temperature": "28"
    }
  }
}
```

### 2. BactoTraits (semicolon-delimited, three-header CSV)
**Source:** `/local/bactotraits/BactoTraits_databaseV2_Jun2022.csv`
**Organism:** Acetobacter oeni
**Structure:**
```
Header 1 (category):  ;;;temp_Optimum;;;;;;;
Header 2 (units):     ;;;Celsius degree;;;;;;;
Header 3 (columns):   TO_<=10;TO_10_to_22;TO_22_to_27;TO_27_to_30;TO_30_to_34;...
Data row:             0;0;0;1;0;...
```
Note: Value of `1` in column TO_27_to_30 indicates mesophile

### 3. Madin et al. (comma-separated CSV)
**Source:** `/local/madin/madin_etal.csv`
**Organism:** Acetobacter fabarum
**Format:**
```csv
species,optimum_tmp
Acetobacter fabarum,28
```

### Hybrid Presentation Approach
For the slides, present as:
- **Label with actual format**: "BacDive (JSON)", "BactoTraits (semicolon-delimited, 3-header CSV)", "Madin et al. (CSV)"
- **Show structure authentically but readably**: Use actual delimiters and structure, but format for clarity
- **Emphasize**: Same biological fact (mesophile), three completely different encodings

### Updated Slide 2 (Implemented)
Shows the true diversity of temperature preference encoding:

1. **BacDive**: Categorical keyword "mesophilic" (explicit semantic label)
2. **BactoTraits**: Binary `1` in column `TO_27_to_30` (implicit - we must infer that 27-30°C means mesophilic)
3. **Madin et al.**: Numeric value `28` in `optimum_tmp` (raw measurement - we must interpret)

**Key insight**: BactoTraits doesn't assert "this is a mesophile" - it just marks growth in a 27-30°C range. The semantic interpretation must be inferred. This makes the data integration challenge even more striking!

**Talking point**: "Notice how only BacDive explicitly says 'mesophilic'. The other two require interpretation: is 27-30°C mesophilic? Is 28°C? This is where METPO provides the semantic bridge."

---

## Slide 2 - Second Iteration (Expanded Examples)

Updated to show:
1. **Taxon identifiers** for each source (strain/Full_name/tax_id+species)
2. **All three header rows** for BactoTraits showing the multi-header structure:
   - Row 1: Category/trait group (`strain name`, `temp_Optimum`)
   - Row 2: Units (blank for name, `Celsius` for temperature)
   - Row 3: Column names (`Full_name`, `TO_22_to_27`, `TO_27_to_30`)
   - Row 4: Data values

**Authentic examples from actual files:**
- BacDive: Generic Acetobacter with "mesophilic" keyword
- BactoTraits: *Acetobacter oeni* with value `1` in `TO_27_to_30` column
- Madin et al.: *Acetobacter fabarum* (tax_id: 483199) with optimum temp 28°C

**PDF regenerated:** ✅ (changes applied)

---

## Slide 2 - Third Iteration Requirements

### Issues to address:
1. **Use NCBI taxon ID** for all organisms (not strain names)
2. **Show full JSON path** for BacDive (from MongoDB)
3. **Display tabular sources as tables** (not code blocks)
4. **Space constraints**: May need 2 slides if all details don't fit

### Cross-database organism search:
**Acetobacter fabarum (NCBI tax ID: 483199)** exists in:
- ✅ **BacDive**: Has temp data (28°C growth, "mesophilic" keyword)
- ❌ **BactoTraits**: Present but NO temperature data (all NA)
- ✅ **Madin**: Has temp data (optimum_tmp = 28)

**Problem**: No single organism with temperature data in all three sources!

### Options:
**Option A**: Use different organisms for each source (current approach)
- More authentic - shows what data actually exists
- Can show tax ID for each
- Easier to display

**Option B**: Find a genus/family-level example
- Less precise but shows conceptual point
- May still have data gaps

**Option C**: Split into 2 slides
- Slide 2a: BacDive (full JSON with path)
- Slide 2b: BactoTraits + Madin (as tables)
- More room to show authentic detail

**Recommendation**: Option C (2 slides) OR Option A with compact tables

---

## Slide 2 - FINAL Implementation (3 Slides + Summary)

**Decision**: Use 4 slides total - overview + 3 data source slides + integration summary

### Slide 2 (Overview): The Data Integration Challenge
- Brief intro to the problem
- Lists the three different approaches

### Slide 2a: BacDive Example
- **Organism**: *Acholeplasma laidlawii* (NCBI Tax ID: 2148)
- **Format**: Nested JSON from MongoDB
- **Shows**: Full path to both keyword ("mesophilic") AND structured temp data (37°C)
- **Path shown**: `General.keywords` and `Culture and growth conditions.culture temp`
- **Key feature**: Categorical + numeric in nested structure

### Slide 2b: BactoTraits Example
- **Organism**: *Acetobacter oeni* (NCBI Tax ID: 304077)
- **Format**: Proper markdown table showing 3-header CSV structure
- **Shows**:
  - Header 1: Category/trait group names
  - Header 2: Units (Celsius degree)
  - Header 3: Column names (TO_27_to_30, etc.)
  - Data row: Binary values (1 in TO_27_to_30 column)
- **Key feature**: Binary encoding across temperature bins

### Slide 2c: Madin Example
- **Organism**: *Acetobacter fabarum* (NCBI Tax ID: 483199)
- **Format**: Simple markdown table
- **Shows**: tax_id, species, optimum_tmp columns
- **Key feature**: Raw numeric value (28°C)

### Slide 2d: Integration Problem Summary
- Emphasizes the incompatibility
- Three different organisms, same temp preference (~28°C)
- Questions: How to query across? How to make equivalent?
- Solution: METPO as semantic bridge

**Note for future**: Finding a single organism with temp data in all three sources would strengthen the narrative but requires significant database searching.

**PDF regenerated:** ✅ (4-slide structure implemented)

---

## Data-Driven Development Slide - Moved to Backups

**Action taken:**
- Moved "Data-Driven Ontology Development" slide with diagram to Backup Slides section
- Content IS discussed elsewhere in simpler form:
  - "OntoGPT Grounding: Data-Driven Expansion" slide states: "Failed groundings are features, not bugs—they guide ontology development"
  - Added simple bullet point to "Introducing METPO" slide: "**Data-driven:** Failed groundings guide iterative expansion (literature mining identifies gaps)"

**Rationale:**
- The detailed feedback loop diagram is good backup material for Q&A
- Core concept is now mentioned twice in main presentation (intro + OntoGPT results)
- Keeps main talk focused and moving

**PDF regenerated:** ✅ (data-driven slide moved)

---

## CORRECTED Slide 2 - Exact Authentic Data Structures

**User correctly identified**: I was not being faithful to the exact source structures!

### Fixed Issues:

1. **BactoTraits has NO NCBI tax ID column** - removed incorrect claim
2. **Added exact 3-header CSV structure** from actual file:
   - Row 1: `taxonomy`, `strain name`, `temp_Optimum` (category labels)
   - Row 2: blank except `Celsius degree` (units)
   - Row 3: `Kingdom`, `Phylum`, `Class`, `Order`, `Family`, `Genus`, `Species`, `Full_name`, `TO_22_to_27`, `TO_27_to_30`, etc. (column names)
   - Data row: Actual values from file

3. **BacDive - verified exact JSON paths** from MongoDB:
   - `General.keywords` = ["Bacteria", "mesophilic", "animal pathogen"]
   - `General['NCBI tax id']['NCBI tax id']` = 2148
   - `Culture and growth conditions['culture temp']` with exact fields: `@ref`, `growth`, `type`, `temperature`

4. **Madin - verified exact column headers and values**:
   - Columns: `tax_id`, `species_tax_id`, `data_source`, `species`, `optimum_tmp`
   - Actual row: 483199, 483199, "fierer", "Acetobacter fabarum", "28"
   - Added project name: "Bacteria and Archaea Traits" dataset

5. **Intro slide**: Changed to specify "microbial growth temperature preferences"

**PDF regenerated:** ✅ (with exact authentic structures)

---

## BactoTraits Simplified - Taxonomy Columns Removed

**Change**: Removed Kingdom, Phylum, Class, Order, Family, Genus, Species columns from BactoTraits table

**Now shows**:
- Row 1: `strain name`, `temp_Optimum` (categories)
- Row 2: blank, `Celsius degree` (units)
- Row 3: `Full_name`, `TO_22_to_27`, `TO_27_to_30`, `TO_30_to_34`, `TO_34_to_40`, `TO_>40`
- Data: Acetobacter oeni Silva et al. 2006, 0, **1**, 0, 0, 0

**Benefit**: More focused on temperature data, cleaner slide

**PDF regenerated:** ✅

---

## Final Verification - All Slides Faithful to Source

Each slide now correctly shows:

### Slide 1 (BacDive):
- ✅ NCBI taxon ID: 2148 (from `General['NCBI tax id']['NCBI tax id']`)
- ✅ Species name: "Acholeplasma laidlawii" (from `Name and taxonomic classification.species`)
- ✅ Temperature: "37" + keyword "mesophilic" (from `Culture and growth conditions['culture temp']` and `General.keywords`)
- ✅ Shows exact MongoDB JSON structure with all paths

### Slide 2 (BactoTraits):
- ❌ No NCBI tax ID column exists in dataset (verified all 105 columns - explicitly noted on slide)
- ✅ Organism identifiers: Bacdive_ID=19, Genus=Acetobacter, Species=oeni, Full_name="Acetobacter oeni Silva et al. 2006"
- ✅ Temperature: TO_27_to_30=1 (binary encoding)
- ✅ Shows exact 3-header CSV structure: Row 1 (categories), Row 2 (units), Row 3 (column names)

### Slide 3 (Madin):
- ✅ NCBI taxon ID: tax_id=483199
- ✅ Species name: "Acetobacter fabarum"
- ✅ Temperature: optimum_tmp=28
- ✅ Shows exact CSV columns: tax_id, species_tax_id, data_source, species, optimum_tmp
- ✅ Includes dataset name: "Bacteria and Archaea Traits"

**All structures verified against actual source files**

**Final PDF regenerated:** ✅ (icbo_metpo_slides.pdf)

---

## SLIDE CONSOLIDATION PLAN

### Current Structure Issues:
- Too many slides (~30+ main presentation)
- Redundant content doesn't build on previous material
- LLM-sounding language patterns
- Vertical overflow on several slides
- Not using full slide width

### Proposed Consolidation (Target: ~18-20 main slides):

**MERGE 1: "Gap in Ontology" + "Introducing METPO"** (2 slides → 1)
- Remove Status & Domain columns from table
- Show: Ontology name + Last Updated only
- Text below: "4 of 5 unmaintained since 2014-2019"
- Immediate pivot to: "METPO addresses this: 255 classes, actively maintained, purpose-built"
- Remove buzzwords like "Application-driven development", "Core principle"
- Keep facts: coverage, tooling, active development

**MERGE 2: "METPO's Modern & Pragmatic Design" + next design details** (2+ slides → 1)
- Current slide 1: Synonyms example
- Current slide 2: External mappings
- Consolidate to single slide with two-column layout using full width
- **Critical fix:** Clarify SSSOM mappings early:
  - "3,019 mappings via label/synonym alignment (many low-confidence)"
  - "Used for cross-reference, not imports"
- Add GitHub/Sheets maintainability point clearly

**MERGE 3: Data Integration Slides** (4 slides → 2)
- Current: Overview + BacDive + BactoTraits + Madin + Summary = 5 slides
- New structure:
  - Slide 1: Two-column comparison showing 2 sources (BacDive + BactoTraits)
  - Slide 2: Third source (Madin) + integration challenge
- Use full slide width for tables

**MERGE 4: KG-Microbe Slides** (3 slides → 1-2)
- "METPO in Production" + "METPO in Action" + "KG-Microbe Semantic Backbone"
- Remove repetitive explanations
- Make figures more prominent
- **Fix:** Use consistent language (strains OR taxa, not nodes/edges)
- Remove "Source: Direct analysis..." attributions
- Show 1-2 clear examples max

**MERGE 5: CMM/REE Context** (2 slides → 1 backup slide)
- Move most CMM/REE details to backup
- **Add:** Culturebot content in main presentation (waiting for user's links)
- Keep biorecovery context minimal

**MERGE 6: Interoperability slides** (2-3 slides → 1)
- Combine mapping strategy + structural coherence
- **Define terms:** structural coherence, broadMatch vs exactMatch
- Choose ONE mapping strategy to report (optimized)
- Remove "24 retained, 15 removed" details

**REMOVE/SIMPLIFY:**
- "Sustainability & Governance" - remove "ICBO 2025 Theme" self-referential claim
- "Conclusion" - remove "Transparency" bullet
- "Future Work" - define AUTO terms or say "ungrounded terms" instead
- Multiple backup slides with verbose source attributions
- "Semantic-SQL" full slide → merge into relevant section or remove

**LANGUAGE DE-LLM-ING:**
- Remove: "comprehensive", "significant", "pragmatic", "robust"
- Remove: "Core principle:", "Design philosophy:", "Key findings:"
- Remove: Perfect parallel "**Bold:** description" structures
- Use: Direct statements, specific numbers, actual examples
- Replace abstract claims with concrete facts

### Result:
- **From ~30 slides → ~18-20 slides**
- Less vertical overflow (wider layouts)
- Less redundancy (each slide adds new info)
- Less AI smell (direct, factual language)
- More focus on culturebot application
- Clearer about mapping limitations

---

## MAJOR SLIDE CONSOLIDATION COMPLETE

### Summary of Changes:

**Slides Consolidated (from ~30 → ~18-20):**

1. ✅ **"Gap" + "Introducing METPO"** (2→1)
   - Removed Status/Domain columns
   - Direct problem→solution flow
   - Added GitHub/Sheets maintainability
   - Bold emphasizes facts (**255 classes**, **3 databases**), not vibes

2. ✅ **"Modern & Pragmatic Design"** 
   - **Clarified SSSOM early:** "3,019 mappings via label/synonym alignment, many low-confidence"
   - Emphasized "used for cross-reference, not imports"
   - Added GitHub (code) + Google Sheets (content) = maintainability

3. ✅ **Data Integration** (5→2 slides)
   - Slide 1: BacDive + BactoTraits side-by-side (full width)
   - Slide 2: Madin + integration problem + METPO solution
   - Removed redundant overview and summary

4. ✅ **KG-Microbe** (3→1 slide)
   - Consolidated stats, removed "METPO in Action" redundancy
   - Consistent terminology: "Strains/Taxa" not "nodes/edges"
   - Removed "Source: Direct analysis..."
   - Figure more prominent

5. ✅ **Interoperability** 
   - Reported ONE strategy (optimized: 2,883 mappings)
   - Defined structural coherence (comparing hierarchical positions)
   - Removed redundant content

6. ✅ **Sustainability & Governance**
   - Removed "ICBO 2025 Theme" self-reference
   - Added CultureBot prominence
   - Clear roles: PI vs Maintainer

7. ✅ **Conclusion**
   - Removed "Transparency" bullet
   - Bold on facts not vibes

8. ✅ **Thank You**
   - Separated: "Presenter & METPO Maintainer: Mark Miller" / "PI: Marcin Joachimiak"

9. ✅ **Backup Slides Cleaned**
   - ROBOT: just "passes", no error counts
   - Ontology counts clarified (221K = class count)
   - Removed "CHEBI worst ROI" line
   - Removed ".md" file references
   - Fixed N4L claim (not in BioPortal)
   - Removed entire Semantic-SQL slide

### Language De-LLM'd:
- Removed: "comprehensive", "significant", "Core principle:", "Key findings:", "Design philosophy:"
- Removed: Template-like **Bold:** vibes patterns
- Kept: "pragmatic" (user requested)
- Bold now emphasizes: **Facts, numbers, concrete data**

### Technical Fixes:
- AUTO → "ungrounded terms"
- Consistent "Strains/Taxa" counting
- Defined "structural coherence"
- One mapping strategy reported

**PDF regenerated:** ✅ (icbo_metpo_slides.pdf)

**User reminded:** Need culturebot links/docs to add more culturebot content
