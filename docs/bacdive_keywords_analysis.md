# BacDive General.keywords Analysis

**Date:** 2025-10-22
**Database:** Local MongoDB (port 27017), bacdive.strains_api collection
**Total strain documents:** 99,393

## Executive Summary

This analysis examines the use of `General.keywords` in the BacDive dataset and compares it with more specific JSON paths. Key findings:

1. **All General.keywords fields are arrays** (not scalars)
2. **88 unique keyword values** across the entire dataset
3. **Significant redundancy** between keywords and specific paths (e.g., Morphology, Physiology sections)
4. **63 of 88 keywords** are already mapped as synonyms in METPO
5. **Important gaps** exist where specific paths have data but keywords don't, and vice versa

## Complete Keyword Inventory

All 88 unique General.keywords values with occurrence counts:

| Keyword | Count | In METPO? | Specific Path Available? |
|---------|-------|-----------|-------------------------|
| Bacteria | 97,270 | No | N/A (taxonomy) |
| mesophilic | 42,236 | Yes | No (keywords only) |
| 16S sequence | 27,058 | No | N/A (data type) |
| genome sequence | 17,617 | No | N/A (data type) |
| Gram-negative | 12,842 | No* | Yes (Morphology.cell morphology.gram stain) |
| rod-shaped | 11,543 | Yes | Yes (Morphology.cell morphology.cell shape) |
| aerobe | 9,353 | Yes | Yes (Physiology.oxygen tolerance) |
| Gram-positive | 6,690 | No* | Yes (Morphology.cell morphology.gram stain) |
| motile | 5,457 | No* | Yes (Morphology.cell morphology.motility) |
| anaerobe | 4,773 | Yes | Yes (Physiology.oxygen tolerance) |
| microaerophile | 3,986 | Yes | Yes (Physiology.oxygen tolerance) |
| facultative anaerobe | 3,493 | Yes | Yes (Physiology.oxygen tolerance) |
| spore-forming | 3,359 | No* | Yes (Physiology.spore formation) |
| colony-forming | 2,582 | No | N/A |
| obligate aerobe | 2,327 | Yes | Yes (Physiology.oxygen tolerance) |
| coccus-shaped | 1,729 | Yes | Yes (Morphology.cell morphology.cell shape) |
| human pathogen | 1,607 | No | N/A (isolation/ecology) |
| thermophilic | 1,530 | Yes | No (keywords only) |
| psychrophilic | 1,190 | Yes | No (keywords only) |
| Archaea | 1,125 | No | N/A (taxonomy) |
| animal pathogen | 700 | No | N/A (isolation/ecology) |
| antibiotic compound production | 508 | No | N/A (metabolism) |
| oval-shaped | 478 | Yes | Yes (Morphology.cell morphology.cell shape) |
| plant pathogen | 376 | No | N/A (isolation/ecology) |
| ovoid-shaped | 362 | Yes | Yes (Morphology.cell morphology.cell shape) |
| chemoorganotroph | 193 | Yes | Yes (Physiology.nutrition type) |
| hyperthermophilic | 179 | Yes | No (keywords only) |
| pigmented | 166 | No | Possible (various pigment fields) |
| antibiotic resistance | 157 | No | N/A (phenotype) |
| obligate anaerobe | 152 | Yes | Yes (Physiology.oxygen tolerance) |
| Gram-variable | 101 | No* | Yes (Morphology.cell morphology.gram stain) |
| facultative aerobe | 92 | Yes | Yes (Physiology.oxygen tolerance) |
| filament-shaped | 90 | Yes | Yes (Morphology.cell morphology.cell shape) |
| chemoheterotroph | 71 | Yes | Yes (Physiology.nutrition type) |
| heterotroph | 68 | Yes | Yes (Physiology.nutrition type) |
| spiral-shaped | 62 | Yes | Yes (Morphology.cell morphology.cell shape) |
| moderately halophilic | 56 | Yes | Yes (Physiology.halophily) |
| pleomorphic-shaped | 55 | Yes | Yes (Morphology.cell morphology.cell shape) |
| toxin production | 53 | No | N/A (metabolism) |
| flask-shaped | 49 | Yes | Yes (Morphology.cell morphology.cell shape) |
| other | 49 | No | N/A |
| chemoorganoheterotroph | 47 | Yes | Yes (Physiology.nutrition type) |
| chemolithoautotroph | 40 | Yes | Yes (Physiology.nutrition type) |
| halophilic | 37 | Yes | Yes (Physiology.halophily) |
| lactate production | 34 | No | N/A (metabolism) |
| vibrio-shaped | 31 | Yes | Yes (Morphology.cell morphology.cell shape) |
| alcohol production | 30 | No | N/A (metabolism) |
| amino acid production | 28 | No | N/A (metabolism) |
| polysaccharide production | 26 | No | N/A (metabolism) |
| halotolerant | 25 | Yes | Yes (Physiology.halophily) |
| sphere-shaped | 16 | Yes | Yes (Morphology.cell morphology.cell shape) |
| non-halophilic | 16 | Yes | Yes (Physiology.halophily) |
| slightly halophilic | 14 | Yes | Yes (Physiology.halophily) |
| aerotolerant | 13 | Yes | Yes (Physiology.oxygen tolerance) |
| helical-shaped | 12 | Yes | Yes (Morphology.cell morphology.cell shape) |
| curved-shaped | 9 | Yes | Yes (Morphology.cell morphology.cell shape) |
| extremely halophilic | 9 | Yes | Yes (Physiology.halophily) |
| chemoautolithotroph | 8 | Yes | Yes (Physiology.nutrition type) |
| organoheterotroph | 8 | Yes | Yes (Physiology.nutrition type) |
| autotroph | 8 | Yes | Yes (Physiology.nutrition type) |
| organotroph | 7 | Yes | Yes (Physiology.nutrition type) |
| methylotroph | 6 | Yes | Yes (Physiology.nutrition type) |
| chemolithotroph | 6 | Yes | Yes (Physiology.nutrition type) |
| phototroph | 5 | Yes | Yes (Physiology.nutrition type) |
| photoheterotroph | 5 | Yes | Yes (Physiology.nutrition type) |
| methane production | 5 | No | N/A (metabolism) |
| chemolithoheterotroph | 3 | Yes | Yes (Physiology.nutrition type) |
| ellipsoidal | 3 | Yes | Yes (Morphology.cell morphology.cell shape) |
| microaerotolerant | 3 | Yes | Yes (Physiology.oxygen tolerance) |
| spore-shaped | 3 | Yes | Yes (Morphology.cell morphology.cell shape) |
| methanotroph | 2 | Yes | Yes (Physiology.nutrition type) |
| star-shaped | 2 | Yes | Yes (Morphology.cell morphology.cell shape) |
| dumbbell-shaped | 2 | Yes | Yes (Morphology.cell morphology.cell shape) |
| lithotroph | 2 | Yes | Yes (Physiology.nutrition type) |
| haloalkaliphilic | 2 | Yes | Yes (Physiology.halophily) |
| diazotroph | 2 | No | N/A (metabolism) |
| lithoheterotroph | 2 | Yes | Yes (Physiology.nutrition type) |
| crescent-shaped | 1 | Yes | Yes (Morphology.cell morphology.cell shape) |
| photoorganoheterotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| diplococcus-shaped | 1 | Yes | Yes (Morphology.cell morphology.cell shape) |
| chemotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| chemoautotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| lithoautotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| mixotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| organotroph\|photoautotroph | 1 | No | Yes (Physiology.nutrition type) |
| photolithotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| oligotroph | 1 | Yes | Yes (Physiology.nutrition type) |
| ring-shaped | 1 | Yes | Yes (Morphology.cell morphology.cell shape) |

*Note: Gram stain values in keywords are "Gram-positive"/"Gram-negative"/"Gram-variable" but in Morphology path they are "positive"/"negative"/"variable" (without "Gram-" prefix). METPO has synonyms for the shorter forms in the specific paths.

## Redundancy Analysis: Keywords vs. Specific Paths

### 1. Gram Stain
- **Keywords:** 19,633 strains with Gram-positive/-negative/-variable
- **Morphology path:** 15,630 strains with gram stain data
- **Both:** 15,208 strains
- **Keywords only:** 4,425 strains ⚠️
- **Path only:** 422 strains

**Issue:** 4,425 strains have Gram info ONLY in keywords, not in the structured Morphology path. These would be missed if kg-microbe ignores keywords.

### 2. Cell Shape
- **Keywords:** 14,449 strains with shape keywords
- **Morphology path:** 15,182 strains with cell shape data
- **Both:** 14,438 strains
- **Keywords only:** 11 strains
- **Path only:** 744 strains

**Good news:** Strong overlap. Morphology path is more complete.

### 3. Motility
- **Keywords:** 5,457 strains with "motile" keyword
- **Morphology path:** 14,060 strains with motility data
- **Both:** 5,344 strains
- **Keywords only:** 113 strains
- **Path only:** 8,716 strains

**Issue:** Keywords only capture motile strains, missing non-motile ones. Morphology path is much more comprehensive.

### 4. Spore Formation
- **Keywords:** 3,359 strains with "spore-forming"
- **Physiology path:** 5,443 strains with spore formation data
- **Both:** 1,919 strains
- **Keywords only:** 1,440 strains ⚠️
- **Path only:** 3,524 strains

**Issue:** 1,440 strains have spore info ONLY in keywords. Physiology path likely includes "non-spore-forming" data.

### 5. Temperature Preference
- **Keywords:** 45,135 strains with mesophilic/thermophilic/psychrophilic/hyperthermophilic
- **Physiology path:** 0 strains ⚠️⚠️⚠️
- **Both:** 0 strains
- **Keywords only:** 45,135 strains

**CRITICAL:** Temperature preference appears to exist ONLY in keywords. No structured temperature preference path found in Physiology section.

### 6. Oxygen Preference
- **Keywords:** 24,192 strains with oxygen-related keywords
- **Physiology path:** 23,254 strains with oxygen tolerance data
- **Both:** 23,253 strains
- **Keywords only:** 939 strains ⚠️
- **Path only:** 1 strain

**Issue:** 939 strains have oxygen info ONLY in keywords.

### 7. Halophily
- **Keywords:** 159 strains with halophily keywords
- **Physiology path:** 364 strains with halophily data
- **Both:** 159 strains
- **Keywords only:** 0 strains
- **Path only:** 205 strains

**Good news:** All keyword data is also in structured path. Path has more data.

### 8. Trophic Type / Nutrition
- **Keywords:** 475 strains with trophic type keywords
- **Physiology path:** 490 strains with nutrition type data
- **Both:** 474 strains
- **Keywords only:** 1 strain
- **Path only:** 16 strains

**Good news:** Almost perfect overlap. Structured path is slightly more complete.

## METPO Synonym Coverage

**Currently mapped in METPO:** 63 of 88 keywords (72%)

### Keywords MISSING from METPO (should be added):

#### High priority (>1000 occurrences):
1. **Gram-negative** (12,842) - Note: METPO has "negative" but not "Gram-negative"
2. **Gram-positive** (6,690) - Note: METPO has "positive" but not "Gram-positive"
3. **motile** (5,457) - Note: METPO has "yes"/"no" for motility but not "motile"
4. **spore-forming** (3,359) - Note: METPO has "yes"/"no" and "spore" but not "spore-forming"
5. **colony-forming** (2,582)
6. **human pathogen** (1,607)
7. **Archaea** (1,125)

#### Medium priority (100-1000 occurrences):
8. **animal pathogen** (700)
9. **antibiotic compound production** (508)
10. **plant pathogen** (376)
11. **pigmented** (166)
12. **antibiotic resistance** (157)
13. **Gram-variable** (101)

#### Lower priority (<100 occurrences):
14. toxin production (53)
15. other (49)
16. lactate production (34)
17. alcohol production (30)
18. amino acid production (28)
19. polysaccharide production (26)
20. methane production (5)
21. diazotroph (2)
22. organotroph|photoautotroph (1) - malformed, pipe character

#### Metadata/non-phenotypic (probably don't need METPO synonyms):
- Bacteria (97,270) - taxonomy
- 16S sequence (27,058) - data availability
- genome sequence (17,617) - data availability

## Recommendations for kg-microbe

### Priority 1: Critical gaps to address

1. **Temperature preference is ONLY in keywords**
   - 45,135 strains have temperature data
   - No structured Physiology path exists
   - **Must use keywords** for mesophilic/thermophilic/psychrophilic/hyperthermophilic
   - Alternative: map to numerical temperature ranges if available elsewhere

2. **Add missing keyword mappings to METPO**
   - Priority: Gram-negative, Gram-positive, motile, spore-forming
   - These are highly used terms that should have METPO synonym mappings

### Priority 2: Handle both sources to maximize coverage

3. **Gram stain:** Use Morphology path as primary, keywords as fallback
   - 4,425 strains only have Gram data in keywords
   - Morphology path format: "positive"/"negative"/"variable"
   - Keywords format: "Gram-positive"/"Gram-negative"/"Gram-variable"

4. **Spore formation:** Use Physiology path as primary, keywords as fallback
   - 1,440 strains only have spore data in keywords
   - Keywords only have "spore-forming" (positive cases)
   - Physiology path likely has both positive and negative cases

5. **Oxygen preference:** Use Physiology path as primary, keywords as fallback
   - 939 strains only have oxygen data in keywords
   - Physiology path is more comprehensive

### Priority 3: Prefer structured paths when available

6. **Cell shape:** Prefer Morphology.cell morphology.cell shape
   - More complete (744 additional strains)
   - Only 11 strains have shape in keywords but not in path

7. **Motility:** Use Morphology.cell morphology.motility ONLY
   - Much more complete (8,716 additional strains vs 113 in keywords only)
   - Keywords only have "motile" (positive cases), path has yes/no

8. **Halophily:** Use Physiology path ONLY
   - Path is more complete (205 additional strains vs 0 in keywords only)

9. **Trophic type:** Use Physiology.nutrition type path ONLY
   - Nearly complete overlap, path slightly better

### Priority 4: Consider excluding from phenotype extraction

Keywords that are metadata rather than phenotypes:
- Bacteria, Archaea (taxonomy)
- 16S sequence, genome sequence (data availability)
- colony-forming (growth characteristic, low specificity)
- other (uninformative)

Keywords that might need specialized handling:
- Pathogen classifications (human/animal/plant pathogen)
- Production capabilities (antibiotic/toxin/metabolite production)
- Pigmentation (might map to color/pigment fields)

## Implementation Strategy

### Suggested priority order:

1. **Immediate:** Keep using keywords for temperature preference (no alternative)
2. **High priority:** Map keywords → structured paths with fallback for:
   - Gram stain
   - Oxygen preference
   - Spore formation
3. **Medium priority:** Switch to structured paths only for:
   - Cell shape
   - Motility (but add "motile" → "yes" mapping)
   - Halophily
   - Trophic type
4. **Low priority:** Add METPO synonyms for high-value keywords currently missing
5. **Consider:** Separate handling for pathogen/production/resistance keywords

### Code pattern recommendation:

```python
def get_phenotype_value(doc, phenotype_type):
    """
    Get phenotype value with fallback from specific path to keywords.

    Priority order:
    1. Specific structured path (if available)
    2. General.keywords (if no structured path or path is empty)
    """
    value = None

    # Try specific path first
    if phenotype_type == "gram_stain":
        value = get_from_path(doc, "Morphology.cell morphology.gram stain")
        if not value:
            value = extract_from_keywords(doc, ["Gram-positive", "Gram-negative", "Gram-variable"])

    elif phenotype_type == "temperature_preference":
        # Temperature only in keywords
        value = extract_from_keywords(doc, ["mesophilic", "thermophilic", "psychrophilic", "hyperthermophilic"])

    # ... etc

    return value
```

## Data Quality Notes

### Morphology.cell morphology is an array
Example structure:
```json
{
  "Morphology": {
    "cell morphology": [
      {
        "@ref": 22965,
        "gram stain": "negative",
        "cell length": "0.5-0.6 µm",
        "cell shape": "coccus-shaped",
        "motility": "no"
      },
      {
        "@ref": 67771,
        "cell shape": "coccus-shaped"
      }
    ]
  }
}
```

**Implication:** Need to handle multiple measurements/observations per strain. Consider:
- Taking first value
- Taking most recent (@ref might indicate curation version)
- Aggregating if values differ

### Missing alignments between METPO template terms and keywords

METPO uses BacDive *path* values, not *keyword* values, so:
- METPO has "positive" (from path), BacDive keywords have "Gram-positive"
- METPO has "yes"/"no" (from path), BacDive keywords have "motile"/"spore-forming"

This is actually correct design - METPO should align with the structured paths, not the less-structured keywords.

## Questions for Discussion

1. Should we add keyword variants to METPO synonyms (e.g., both "positive" and "Gram-positive")?
2. How should we handle the 4,425 strains with Gram stain only in keywords?
3. For temperature preference with no structured path, should we:
   - Keep using keywords?
   - Try to infer from numerical temperature ranges?
   - Both?
4. Should pathogen types and metabolic production keywords be extracted at all, or handled separately from core phenotypes?
5. For the `organotroph|photoautotroph` malformed keyword, should we report to BacDive or handle specially?

## Next Steps

1. Review with team (Mark, Marcin, Sujay)
2. Prioritize which gaps to address in kg-microbe
3. Decide on METPO synonym additions
4. Implement fallback logic for critical fields (Gram stain, spore formation, oxygen)
5. Update documentation on BacDive data extraction strategy
