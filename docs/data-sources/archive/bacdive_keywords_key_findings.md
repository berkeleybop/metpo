# BacDive Keywords: Key Findings Summary

**Date:** 2025-10-22
**Dataset:** BacDive MongoDB (bacdive.strains_api), 99,393 strains, 88 unique keywords

---

## Executive Summary

Complete analysis of all 88 BacDive General.keywords mapped against structured JSON paths. Found that most keywords (71/88) have structured alternatives, with 3 critical synonym gaps affecting kg-microbe extraction.

---

## Critical Findings

### 1. Synonym Gaps in METPO (Affects kg-microbe extraction)

**Must fix - these affect data extraction:**

| Keyword | Strains | Structured Path | Issue |
|---------|---------|----------------|-------|
| Gram-negative | 12,842 | Morphology.cell morphology.gram stain | Path has "negative", METPO needs "Gram-negative" synonym |
| Gram-positive | 6,690 | Morphology.cell morphology.gram stain | Path has "positive", METPO needs "Gram-positive" synonym |
| Gram-variable | 101 | Morphology.cell morphology.gram stain | Path has "variable", METPO needs "Gram-variable" synonym |
| motile | 5,457 | Morphology.cell morphology.motility | Path has "yes", METPO needs "motile" synonym |
| spore-forming | 3,359 | Physiology and metabolism.spore formation.spore formation | Path has "yes", METPO needs "spore-forming" synonym |

**Total affected:** 28,449 strains (28.6% of dataset)

**Solution:** Add these 5 synonyms to metpo_sheet.tsv in appropriate parent classes

### 2. Culture Temperature and pH NOT Being Extracted

**CRITICAL - documented in CRITICAL_FINDING_culture_temp_ph.md**

- **Temperature:** 49,507 strains (49.8%) have `Culture and growth conditions.culture temp` data
  - Constants exist in kg-microbe but NOT extracted
  - Currently only extracting keywords (mesophilic, etc.)
  - Structured path has: specific °C values, type (growth/optimum/min/max), ranges

- **pH:** 6,796 strains (6.8%) have `Culture and growth conditions.culture pH` data
  - No constants in kg-microbe
  - NOT extracted at all
  - Structured path has: pH values, type, categories (acidophile/alkaliphile)

**Recommendation:** Extract BOTH keywords (categorical) AND structured paths (quantitative)

---

## Keyword Categories

### A. Keywords with Direct Structured Paths (71 keywords)

**Perfect matches** - value in keyword matches value in path:
- Cell shapes (17): rod-shaped, coccus-shaped, oval-shaped, etc.
- Oxygen tolerance (9): aerobe, anaerobe, microaerophile, etc.
- Nutrition types (22): chemoorganotroph, autotroph, etc.
- Halophily (7): halophilic, halotolerant, etc.
- Temperature preference (4): mesophilic, thermophilic, psychrophilic, hyperthermophilic

**Format mismatches** - data exists but format differs (5):
- Gram stain (3): Gram-negative, Gram-positive, Gram-variable
- Motility (1): motile
- Spore formation (1): spore-forming

**Availability flags** - keyword indicates data presence (2):
- 16S sequence → `Sequence information.16S sequences.accession` (27,045/27,058 strains)
- genome sequence → `Sequence information.Genome sequences[].accession` (17,606/17,617 strains)

### B. Keywords with Partial Structured Paths (6 keywords)

Path exists but at different granularity:

| Keyword | Path | Issue |
|---------|------|-------|
| antibiotic compound production | compound production.compound | Path has specific compounds, not category |
| pigmented | Morphology.pigmentation.color | Path has specific colors, keyword is flag |
| toxin production | compound production.compound | Path has "toxin" (33 strains), keyword broader (53 strains) |
| alcohol production | compound production.compound | Path has "ethanol" (19 strains), keyword broader (30 strains) |
| amino acid production | compound production.compound | Path has specific amino acids, keyword is category |
| polysaccharide production | metabolite production | Path has "cellulose" (7/26 strains) - keyword is broad category |

### C. Keywords with NO Structured Path (2 keywords)

**Actually no structured path:**
- diazotroph (2 strains) - nitrogen fixation capability, no nitrogen fixation fields found
- other (49 strains) - uninformative catch-all

**Pathogenicity (ML-predicted):**
- human pathogen (1,607 strains)
- animal pathogen (700 strains)
- plant pathogen (376 strains)

*Note: Isolation source categories exist (`Isolation, sampling and environmental information.isolation source categories`) with 63-78% coverage. Categories like "#Host > #Mammals" or "#Host > #Plants" provide indirect evidence but don't prove pathogenicity.*

**Production (has structured data):**
- lactate production (34 strains) - metabolite production path with metabolite="lactate" (34 strains, 100% match)
- methane production (5 strains) - metabolite production path with metabolite="methane" (11 strains, better coverage)
- polysaccharide production (26 strains) - partial match via metabolite="cellulose" (7 strains)

**Colony morphology:**
- colony-forming (2,582 strains) - has structured path `Morphology.colony morphology` (10,573 strains) with detailed data (size, color, shape, hemolysis type)

**Other:**
- antibiotic resistance (157 strains) - has structured path but much more detailed than keyword
- other (49 strains) - uninformative catch-all, appears alongside other keywords
- diazotroph (2 strains) - nitrogen fixation capability, NO structured path
- organotroph|photoautotroph (1 strain) - malformed keyword

---

## Structured Paths Used by kg-microbe

Current kg-microbe implementation extracts from these paths:

1. **Morphology.cell morphology** - gram stain, cell shape, motility
2. **Physiology and metabolism.oxygen tolerance** - aerobe/anaerobe types
3. **Physiology and metabolism.nutrition type** - trophic types
4. **Physiology and metabolism.halophily** - salt tolerance
5. **Physiology and metabolism.spore formation** - spore formation capability
6. **General.keywords** - fallback for unmatched keywords

**NOT extracted (but should be):**
- `Culture and growth conditions.culture temp` - 49,507 strains
- `Culture and growth conditions.culture pH` - 6,796 strains

---

## Coverage Statistics

**Overall keyword coverage:**
- 76/88 (86.4%) have direct structured paths (includes taxonomy, sequence accessions, colony morphology, metabolite production)
- 6/88 (6.8%) have partial structured paths
- 2/88 (2.3%) have truly no structured paths (diazotroph, other)
- 4/88 (4.5%) are pathogen keywords (ML-predicted, indirect evidence only)

**Strain coverage (for keywords with paths):**
- Most structured paths have better coverage than keywords
- Example: oxygen tolerance path covers 23,254 strains vs 21,191 keyword strains
- Temperature: path covers 49,507 vs keywords 45,135

---

## Pathogen Keywords Investigation

**Finding:** Pathogen keywords (human/animal/plant pathogen) appear to be ML-predicted rather than from direct experimental evidence.

**Evidence:**
1. Reference @id 125438 (Koblitz et al. 2024): "Predicting bacterial phenotypic traits through improved machine learning"
2. Multiple strains have "Automatically annotated from API" references
3. No strain-specific pathogenicity papers in references
4. Isolation source categories exist but only indicate WHERE isolated, not IF pathogenic

**Isolation source categories:**
- Path: `Isolation, sampling and environmental information.isolation source categories`
- Coverage: human pathogen (63%), animal pathogen (72%), plant pathogen (78%)
- Structure: hierarchical (Cat1: #Host, Cat2: #Mammals, Cat3: #Suidae)
- Relationship: indirect - source location implies but doesn't prove pathogenicity

---

## Taxonomy Keywords (Bacteria/Archaea)

**Keywords:** Bacteria (97,270 strains), Archaea (1,125 strains)

**Source:** `Name and taxonomic classification.domain` field

**Taxonomic information structure:**

BacDive provides **two sources** of taxonomy:

1. **LPSN (List of Prokaryotic names with Standing in Nomenclature)** - updated taxonomy
   - Nested in `LPSN` object with @ref to LPSN paper (20215)
   - Example: phylum "Bacillota" (new nomenclature)

2. **Legacy/original taxonomy** - at root level
   - Example: phylum "Firmicutes" (old nomenclature)
   - May differ from LPSN

**Ranks provided (textual labels):**
- domain (Bacteria, Archaea)
- phylum
- class
- order
- family
- genus
- species
- full scientific name (with authors and year)
- strain designation
- type strain (yes/no)

**NCBI Taxonomy IDs:**
- **NOT in General or Name and taxonomic classification sections**
- **Only associated with sequences:**
  - `Sequence information.16S sequences.NCBI tax ID` - 26,231 strains
  - `Sequence information.Genome sequences[].NCBI tax ID` - 17,606 strains
- These link sequence accessions to NCBI Taxonomy database entries

**Keyword source:**
- Bacteria/Archaea keywords derived from `domain` field
- 100% match between keyword and domain field value
- Keywords are redundant with structured data

---

## Metabolite and Compound Production

**Discovery:** BacDive has TWO structured paths for production data:

1. **`Physiology and metabolism.metabolite production`** - structured with ChEBI IDs
2. **`Physiology and metabolism.compound production`** - text-based compound names

### Metabolite Production Structure

```json
{
  "@ref": 22893,
  "Chebi-ID": 24996,
  "metabolite": "lactate",
  "production": "yes"
}
```

**Metabolite keywords with structured paths:**

| Keyword | Metabolite Value | Coverage |
|---------|-----------------|----------|
| lactate production | "lactate" | 34/34 (100%) - perfect match |
| methane production | "methane" | 11/5 (220%) - path has BETTER coverage than keyword |
| polysaccharide production | "cellulose" | 7/26 (27%) - cellulose is one type of polysaccharide |

**Key insight:** Metabolite production path uses ChEBI IDs, making it ideal for semantic integration.

### Colony Morphology

**Path:** `Morphology.colony morphology`

**Structure includes:**
- colony size (e.g., "0.3-0.5 mm")
- colony color (e.g., "whitish")
- colony shape (e.g., "circular")
- type of hemolysis (e.g., "gamma")
- incubation period (e.g., "2 days")
- medium used (e.g., "Columbia sheep blood agar")

**Coverage:** 10,573 strains have colony morphology data vs 2,582 with "colony-forming" keyword

**Key insight:** The keyword is just a flag indicating colony formation, while the structured path provides rich phenotypic detail about colony characteristics.

---

## Sequence Accession Paths

Keywords serve as **availability flags** with actual accessions in structured paths:

**16S sequences:**
- Keyword: `General.keywords` = "16S sequence" (27,058 strains)
- Accession: `Sequence information.16S sequences.accession` (27,045 strains, 99.95%)
- Fields: accession, database (e.g., "nuccore"), description, length, NCBI tax ID

**Genome sequences:**
- Keyword: `General.keywords` = "genome sequence" (17,617 strains)
- Accession: `Sequence information.Genome sequences[].accession` (17,606 strains, 99.94%)
- Array of genomes with: accession, database (ncbi/patric/img), assembly level, description
- Example accessions: GCA_003269275 (NCBI), 1122957.3 (PATRIC), 2756170237 (IMG)

---

## Reference Structure

BacDive documents contain full citation details in `Reference` array:

**Fields:**
- `@id` - reference ID (matches `@ref` fields elsewhere in document)
- `authors` - full author list
- `title` - paper title
- `journal` - journal and publication details
- `doi/url` - DOI or URL
- `pubmed` - PubMed ID (when available)
- `catalogue` - for strain collection references

**Reference types observed:**
- Taxonomic papers (LPSN, species descriptions)
- Database/infrastructure papers (StrainInfo, MicrobeAtlas, BRENDA)
- Genome projects (GEBA, DiASPora)
- ML prediction papers (phenotype prediction models)
- Strain collection catalogs (DSMZ, CCUG, CIP)
- Automatic annotations (API-based)

---

## Value Diversity in Structured Paths

**Summary of unique values across all structured paths:**

| Path | Unique Values | Key Observations |
|------|--------------|------------------|
| **Compound production.compound** | 2,568 | Most diverse - highly varied compound names |
| **Genome sequences.accession** | 50,587 | Multiple genome assemblies per strain |
| **16S sequences.accession** | 27,045 | One per strain typically |
| **Culture temp.temperature** | 1,268 | Degrees Celsius values + ranges |
| **Metabolite production** | 505 | With ChEBI IDs for semantic integration |
| **Antibiotic resistance.metabolite** | 206 | Unique antibiotics tested (with ChEBI IDs, resistance/sensitivity data) |
| **Pigmentation.color** | 63 | From generic (yellow) to specific (RAL codes, absorption spectra) |
| **Nutrition type** | 22 | Base trophic types (41 combinations with comma-separated values) |
| **Cell shape** | 19 | Base terms (127 combinations due to multiple observations) |
| **Oxygen tolerance** | 9 | Base terms (206 combinations due to multiple observations) |
| **Halophily level** | 7 | Base terms (19 combinations due to multiple observations) |
| **Gram stain** | 3 | Base terms: negative/positive/variable (26 combinations due to multiple observations) |
| **Motility** | 2 | Base terms: yes/no (17 combinations due to multiple observations) |
| **Spore formation** | 2 | Base terms: yes/no (9 combinations due to multiple observations) |
| **Domain** | 2 | Bacteria, Archaea |

**Key insights:**

1. **Multiple observations are common:** Many fields store multiple observations per strain using arrays or array-valued fields. BacDive uses two patterns:
   - **Array of observation objects:** Parent is array (e.g., cell morphology contains multiple observations, each with @ref)
   - **Array-valued fields:** Field value itself is array (e.g., oxygen tolerance can be ["aerobe", "facultative anaerobe"])

2. **Temperature diversity:** 1,268 unique temperature values include:
   - Single values (37°C)
   - Ranges (30-37°C)
   - Multiple measurement types (growth, optimum, minimum, maximum)

3. **Compound/metabolite production highly specific:**
   - 2,568 unique compounds (text-based)
   - 505 unique metabolites (with ChEBI IDs)
   - Much more granular than keyword categories

4. **Array inflation effect:** Many "unique value" counts are inflated by array combinations:
   - Oxygen tolerance: 9 base terms → 206 combinations (23x inflation)
   - Cell shape: 19 base terms → 127 combinations (6.7x inflation)
   - Gram stain: 3 base terms → 26 combinations (8.7x inflation)
   - Multiple observations per strain create array combinations that count as "unique" when not properly unwound

5. **Sequence accessions are maximally diverse:**
   - 27,045 unique 16S accessions
   - 50,587 unique genome accessions (multiple assemblies per strain from different databases)

**Data file:** Complete counts saved in `bacdive_structured_path_value_counts.tsv`

---

## Recommendations

### High Priority

1. **Add 5 missing synonyms to metpo_sheet.tsv:**
   - "Gram-negative", "Gram-positive", "Gram-variable" to gram stain parent
   - "motile" to motility parent
   - "spore-forming" to spore formation parent

2. **Extract culture temperature data:**
   - Add extraction from `Culture and growth conditions.culture temp`
   - Extract by type: growth, optimum, minimum, maximum
   - Keep keyword extraction as complementary categorical data

3. **Extract culture pH data:**
   - Add extraction from `Culture and growth conditions.culture pH`
   - Use `PH range` field (acidophile/alkaliphile) for validation
   - Add constants to kg-microbe/constants.py

### Medium Priority

4. **Consider extracting sequence accessions:**
   - Currently keywords are just flags
   - Could link to INSDC accessions for data integration

5. **Document partial matches:**
   - Antibiotic resistance keyword vs detailed structured data
   - Production keywords vs specific compound data

### Low Priority

6. **Pathogen keywords:**
   - Current approach (using custom_curies.yaml) is appropriate
   - No better alternative in structured data
   - Isolation source categories could be extracted separately if useful

---

## Files Generated

1. `bacdive_keywords_analysis.md` - initial comprehensive MongoDB analysis
2. `kg_microbe_bacdive_implementation_analysis.md` - kg-microbe code review
3. `CRITICAL_FINDING_culture_temp_ph.md` - temperature/pH discovery
4. `keywords_without_structured_paths.md` - detailed gap analysis
5. `bacdive_keywords_inventory.tsv` - clean machine-readable table
6. `bacdive_keywords_key_findings.md` - this summary

---

## Validation Queries Used

Key MongoDB queries for validation:

```javascript
// Check keyword coverage
db.strains_api.countDocuments({ "General.keywords": "keyword_value" })

// Check structured path coverage
db.strains_api.countDocuments({ "path.to.field": { $exists: true } })

// Check overlap
db.strains_api.countDocuments({
  "General.keywords": "keyword_value",
  "path.to.field": { $exists: true }
})

// Sample structure
db.strains_api.findOne(
  { "General.keywords": "keyword_value" },
  { "General.BacDive-ID": 1, "path.to.field": 1 }
)
```

All findings validated against live MongoDB data (port 27017, database: bacdive, collection: strains_api).
