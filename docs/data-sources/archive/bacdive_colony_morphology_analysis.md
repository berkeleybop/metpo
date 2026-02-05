# BacDive Colony Morphology Analysis

**Path:** `Morphology.colony morphology`

**Coverage:** 10,573 / 99,393 strains (10.6%)

---

## Structure

Colony morphology is stored as either:
- Single object with `@ref` and optional fields
- Array of objects (multiple observations on different media)

**Example:**
```json
{
  "@ref": 22965,
  "type of hemolysis": "gamma",
  "colony size": "0.3-0.5 mm",
  "colony color": "whitish",
  "colony shape": "circular",
  "incubation period": "2 days",
  "medium used": "Columbia sheep blood agar"
}
```

---

## Fields and Coverage

| Field | Strains | Description |
|-------|---------|-------------|
| **incubation period** | 6,379 | Time to develop colonies (e.g., "1-2 days", "2 days") |
| **colony color** | 4,586 | Color descriptions (RAL codes, descriptive names) |
| **medium used** | 4,430 | Growth medium (e.g., "ISP 2", "Marine agar") |
| **colony shape** | 2,688 | Morphological shape (circular, irregular, rhizoid, etc.) |
| **colony size** | 1,876 | Diameter measurements (e.g., "1-2 mm", "0.5-1.0 mm") |
| **type of hemolysis** | 849 | Hemolysis on blood agar (alpha, beta, gamma, CAMP test) |

**Note:** Not all strains have all fields. Some only have `@ref` (reference to literature source).

---

## Colony Shape

**Unique values:** 15 distinct shapes

**Common shapes:**
- circular (most common)
- irregular
- round
- punctiform
- rhizoid
- filamentous
- oval
- fried-egg-shaped

**Complex descriptive shapes:**
- "swarms structured by radial veining, containing rudimentarily developed fruiting bodies"
- "circular, convex with entire margins"
- "circular, highly cohesive"

---

## Colony Color

**Coverage:** 4,586 strains

**Color encoding:**
- RAL color codes (e.g., "Beige (1001)", "Sand yellow (1002)")
- Descriptive names (e.g., "white", "yellow", "translucent")
- Both (e.g., "Beige (1001)" vs "beige")

**Top 20 colors:**

| Color | Count | Notes |
|-------|-------|-------|
| Beige (1001) | 776 | RAL code |
| Beige | 531 | Without RAL code |
| white | 480 | |
| Ivory (1014) | 409 | RAL code |
| yellow | 351 | |
| Light ivory (1015) | 340 | RAL code |
| Sand yellow (1002) | 298 | RAL code |
| Colorless | 297 | |
| Yellow | 257 | Capitalized variant |
| translucent | 204 | |
| Lemon yellow (1012) | 178 | RAL code |
| Zinc yellow (1018) | 172 | RAL code |
| Brown | 167 | |
| cream | 150 | |
| Pastel yellow (1034) | 144 | RAL code |
| orange | 132 | |
| Cream (9001) | 115 | RAL code |
| Ivory | 112 | Without RAL code |
| beige | 111 | Lowercase variant |

**Key observations:**
- Both capitalized and lowercase variants exist
- RAL color codes provide standardized color references
- Many descriptive variations (e.g., "Beige (1001)" vs "beige")

---

## Colony Size

**Coverage:** 1,876 strains

**Format:** Diameter in millimeters (mm)

**Common values:**

| Size | Count |
|------|-------|
| 1-2 mm | 270 |
| 1 mm | 166 |
| 0.5-1.0 mm | 115 |
| 1.0-2.0 mm | 99 |
| 2-3 mm | 98 |
| 0.5-1 mm | 94 |
| 2 mm | 86 |
| 1-3 mm | 57 |
| 0.5 mm | 52 |

**Range:** From ~0.3 mm (punctiform) to several mm

**Format variations:**
- "1-2 mm" (most common)
- "1.0-2.0 mm" (with decimal)
- "1 mm" (single value)

---

## Type of Hemolysis

**Coverage:** 849 strains

**Values:**
- **gamma** - no hemolysis (most common on blood agar)
- **alpha** - partial hemolysis (greenish discoloration)
- **beta** - complete hemolysis (clear zone)
- **alpha/beta** - mixed pattern
- **CAMP test** - specific hemolysis test for Streptococcus agalactiae

**Medical relevance:** Hemolysis patterns help identify pathogenic bacteria, especially streptococci.

---

## Medium Used

**Coverage:** 4,430 strains

**Top 15 media:**

| Medium | Count | Description |
|--------|-------|-------------|
| ISP 2 | 1,374 | International Streptomyces Project medium 2 |
| ISP 3 | 1,306 | ISP medium 3 |
| ISP 4 | 1,284 | ISP medium 4 |
| ISP 7 | 1,279 | ISP medium 7 |
| ISP 5 | 1,277 | ISP medium 5 |
| ISP 6 | 1,211 | ISP medium 6 |
| suter without tyrosine | 274 | |
| suter with tyrosine | 273 | |
| R2A agar | 222 | Reasoner's 2A agar (low nutrient) |
| Trypticase Soy Agar | 193 | General purpose medium |
| Marine agar (MA) | 173 | For marine bacteria |
| Reasoner's 2A agar (R2A) | 161 | Alternative name for R2A |
| De Man, Rogosa and Sharpe Agar | 122 | For lactobacilli |
| R2A | 118 | Short name |
| MA agar | 76 | Marine agar variant |

**Key observations:**
- ISP media dominate (designed for actinomycetes characterization)
- Multiple name variants for same media (e.g., "R2A agar", "Reasoner's 2A agar", "R2A")
- Medium type affects colony appearance

---

## Incubation Period

**Coverage:** 6,379 strains (most common field)

**Format:** Time duration

**Common values:**
- "1-2 days"
- "2 days"
- "3 days"
- "24 h"
- "48 h"

**Variability:** Depends on organism growth rate and medium

---

## Data Quality Issues

1. **Inconsistent capitalization:**
   - "yellow" vs "Yellow"
   - "beige" vs "Beige"

2. **Multiple naming conventions:**
   - With/without RAL codes
   - Different abbreviations for same media

3. **Incomplete records:**
   - Many strains only have `@ref` without descriptive fields
   - Not all fields populated for each observation

4. **Free-text descriptions:**
   - Colony shape can be very descriptive/specific
   - Hard to standardize

---

## Potential Use Cases

### For METPO/kg-microbe:

1. **Colony color → pigmentation phenotype**
   - RAL codes could map to standardized color ontology
   - Could complement `Morphology.pigmentation.color` field

2. **Colony shape → morphological phenotype**
   - Circular vs irregular vs filamentous growth patterns
   - Relevant for identification

3. **Hemolysis → virulence indicator**
   - Beta-hemolysis associated with pathogenicity
   - Could inform pathogen keywords

4. **Colony size → growth characteristics**
   - Large colonies = fast growth
   - Punctiform = slow growth

5. **Medium specificity → growth requirements**
   - If colonies only form on specific media
   - Indicates nutritional requirements

### Challenges:

1. **Context-dependent:** Colony morphology varies by medium and incubation conditions
2. **Multiple observations per strain:** Arrays complicate extraction
3. **Free-text fields:** Harder to map to ontology terms
4. **Incomplete data:** Only 10.6% of strains have this data

---

## Relationship to Keywords

**"colony-forming" keyword:**
- 2,582 strains with keyword
- 10,573 strains with structured colony morphology data
- **73%** of strains with keyword have NO colony morphology details
- Keyword is just a flag, structured path has phenotypic detail

**Recommendation:** Don't rely on "colony-forming" keyword for phenotype extraction. Use structured colony morphology when available, but recognize limited coverage.

---

## Extraction Strategy for kg-microbe

**If pursuing colony morphology extraction:**

1. **High priority:**
   - Type of hemolysis (medical relevance, controlled vocabulary)
   - Colony shape (when standardized terms like "circular", "irregular")

2. **Medium priority:**
   - Colony color (after normalizing RAL codes and case)
   - Colony size (quantitative, useful for growth rate inference)

3. **Lower priority:**
   - Medium used (useful for growth requirements but highly variable)
   - Incubation period (context-dependent)

4. **Normalization needed:**
   - Map RAL codes to standard color terms
   - Consolidate media name variants
   - Standardize size format (ranges vs single values)

**Note:** Multiple observations per strain (array) requires aggregation strategy (use most common? most recent? keep all with provenance?).
