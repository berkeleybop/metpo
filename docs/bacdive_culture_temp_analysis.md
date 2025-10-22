# BacDive Culture Temperature Value Diversity

**Path:** `Culture and growth conditions.culture temp`

**Unique temperature values:** 1,267

**Why so many unique values?**

---

## Breakdown by Format

| Format | Count | Examples |
|--------|-------|----------|
| **Ranges (X-Y)** | 834 (66%) | "30-37", "10-45", "25-41" |
| **Decimal values** | 322 (25%) | "26.5", "39.5", "20.0-37.0" |
| **Single integers** | 106 (8%) | "37", "28", "30", "25" |
| **Negative values** | 5 (<1%) | "-1.8-26" |

---

## Why So Many Unique Values?

### 1. **Ranges are very specific**

Ranges represent the temperature range for growth, and labs report different ranges:

**Common ranges:**
- 30-37°C (951 occurrences)
- 25-41°C (709)
- 10-37°C (607)
- 15-37°C (594)
- 25-37°C (568)

**But also many rare, specific ranges:**
- 8-46°C (1 occurrence)
- 38-41°C (1)
- 22-60°C (1)
- 67.5-75°C (1)
- 02-18°C (1) - with leading zero!

**Result:** Each unique range = unique value

### 2. **Decimal precision varies**

Some labs report decimals, others don't:

**Same temperature, different formats:**
- "37" (21,751 occurrences)
- "37.0" (fewer occurrences)
- "36.5" (specific)

**Decimal ranges:**
- "25.0-37.0"
- "20.0-42.0"
- "8.0-44.6"
- "5.0-7.5" (suspiciously low - pH?)

**Result:** "37" ≠ "37.0" in the data

### 3. **Leading zeros in some entries**

- "02-18" instead of "2-18"
- "04-30" instead of "4-30"
- "07-23" instead of "7-23"

**Result:** More unique string values

### 4. **Unusual formatting**

- "25--30" (double dash!)
- ">34.0" (greater than)
- "<60.0" (less than)

### 5. **Possible data entry errors**

- "5.0-7.5" (likely pH, not temperature)
- "90-95" (very high - thermophile or error?)
- "46-78" (wide range)

---

## Temperature Types

| Type | Occurrences | Description |
|------|-------------|-------------|
| **growth** | 87,461 (91%) | Temperature where growth was observed |
| **optimum** | 7,775 (8%) | Optimal growth temperature |
| **maximum** | 197 (<1%) | Maximum temperature for growth |
| **minimum** | 157 (<1%) | Minimum temperature for growth |
| *(empty)* | 52 (<1%) | Type not specified |
| **other** | 1 (<1%) | Other type |

**Total measurements:** 95,643 (from 49,507 strains)

**Multiple measurements per strain:** Common - strains have growth, optimum, min, max

---

## Top 30 Most Common Temperature Values

| Temperature | Count | Type |
|-------------|-------|------|
| 37 | 21,751 | Human body temperature - medical isolates |
| 28 | 18,377 | Room/environmental temperature |
| 30 | 18,153 | Standard growth temperature |
| 25 | 4,030 | Room temperature |
| 45 | 3,029 | Thermophile |
| 10 | 2,930 | Psychrophile/refrigeration |
| 5 | 1,771 | Psychrophile/cold |
| 41 | 1,676 | Slightly above human temp |
| 15 | 1,105 | Cool temperature |
| **30-37** | **951** | **Human/environmental range** |
| 20 | 855 | Cool room temperature |
| 55 | 784 | Thermophile |
| 35 | 777 | Near human temp |
| **25-41** | **709** | **Broad mesophile range** |
| **10-37** | **607** | **Very broad range** |
| **15-37** | **594** | **Broad range** |
| **25-37** | **568** | **Mesophile range** |
| 22 | 495 | Room temperature |
| **25-30** | **485** | **Narrow mesophile range** |
| **30-41** | **485** | **Elevated temperature range** |

**Pattern:** Single values dominate, but ranges add diversity

---

## Data Quality Issues

### 1. **String matching is fragile**

- "37" ≠ "37.0" ≠ "37.00"
- "2-18" ≠ "02-18"
- "30-37" ≠ "30-37.0" ≠ "30.0-37.0"

### 2. **No standardized format**

- Some use decimals, others don't
- Some use leading zeros, others don't
- Some use comparators (>, <)

### 3. **Possible errors**

- "5.0-7.5" looks like pH
- "25--30" has double dash
- Wide ranges like "8-46" may be data entry errors

### 4. **Ambiguous ranges**

- Does "30-37" mean:
  - Growth observed at 30°C AND 37°C?
  - Growth observed at all temps between 30-37°C?
  - Typical interpretation: growth throughout the range

---

## Why This Matters for kg-microbe

### Current Situation:
- kg-microbe extracts KEYWORDS (mesophilic, thermophilic, etc.)
- kg-microbe does NOT extract structured temperature values
- Keywords: 45,135 strains
- Structured data: 49,507 strains (**4,372 more strains!**)

### Challenge: 1,267 unique values
- Too many to map individually to ontology terms
- Need **numeric parsing** and **range standardization**

### Extraction Strategy Options:

#### Option 1: Parse to numeric ranges
```python
"30-37" → min=30, max=37
"37" → value=37
"25.0-37.0" → min=25.0, max=37.0
```

**Pros:** Enables quantitative queries
**Cons:** Requires parsing logic, handle edge cases

#### Option 2: Bin into temperature categories
```python
if temp < 15: "psychrophilic"
elif temp 15-45: "mesophilic"
elif temp 45-80: "thermophilic"
elif temp > 80: "hyperthermophilic"
```

**Pros:** Maps to existing METPO terms
**Cons:** Loses precision, binning logic needed

#### Option 3: Extract both
- Store numeric values as attributes
- Also infer categorical labels
- Keep keywords as complementary data

**Pros:** Maximum information retention
**Cons:** More complex, more edges in graph

### Recommendation:

**Extract structured temperature data with Option 3:**

1. Parse temperature strings to numeric min/max
2. Store as quantitative attributes (e.g., `growth_temperature_min`, `growth_temperature_max`)
3. Infer categorical labels from numeric values
4. Keep keyword extraction as is (categorical)

**Benefits:**
- 4,372 additional strains get temperature data
- Enables queries like "organisms that grow at 37°C"
- More precise than keywords alone
- Maintains compatibility with existing keyword extraction

**Parsing logic needed:**
- Strip decimals if not meaningful
- Remove leading zeros
- Handle ranges (X-Y)
- Handle single values
- Handle comparators (>, <)
- Flag suspicious values for review

---

## Temperature Distribution Insights

### Single Value Distribution:

**Top 10 single integer values:**
- 37°C (21,751) - human body temperature (medical isolates)
- 28°C (18,377) - typical lab growth temperature
- 30°C (18,153) - standard incubator temperature
- 25°C (4,030) - room temperature
- 45°C (3,029) - moderate thermophiles
- 10°C (2,930) - psychrophiles/food spoilage
- 5°C (1,771) - refrigeration temperature
- 41°C (1,676) - fever temperature
- 15°C (1,105) - cool environment
- 20°C (855) - cool room temperature

**Biological significance:**
- Clustering at 28-30°C (environmental isolates)
- Major peak at 37°C (human pathogens/commensals)
- Psychrophile peak at 5-10°C
- Thermophile representation at 45-60°C

### Range Value Patterns:

**Common patterns:**
- **Broad mesophile:** 10-37, 15-37, 10-45
- **Narrow mesophile:** 25-30, 30-37, 25-37
- **Thermophile:** 45-85, 50-92, 55-80
- **Psychrophile:** 2-18, 4-24, 5-20

---

## Comparison to Keywords

**Keywords provide categories:**
- mesophilic (42,236 strains)
- thermophilic (1,530 strains)
- psychrophilic (1,190 strains)
- hyperthermophilic (179 strains)

**Structured path provides:**
- Specific temperatures: "37°C"
- Growth ranges: "30-37°C"
- Multiple types: growth, optimum, min, max
- Better coverage: 49,507 vs 45,135 strains

### Validation: Do Keywords Match Actual Temperatures?

**Tested 100 strains per keyword category:**

| Keyword | Expected Range | Match Rate | Mismatch Rate |
|---------|---------------|------------|---------------|
| **mesophilic** | 15-45°C | 100% (100/100) | 0% |
| **psychrophilic** | <20°C | 96% (96/100) | 4% |
| **thermophilic** | 45-80°C | 96% (96/100) | 4% |
| **hyperthermophilic** | >80°C | 99% (99/100) | 1% |

**Match criteria:** Strain has optimum temperature OR any growth temperature within expected range

**Mismatch examples:**

*Psychrophilic mismatches (4/100):*
- BacDive-ID 245: growth at 22°C, 30°C, 37°C (no temps <20°C!)
- BacDive-ID 324: growth at 24°C (borderline)
- BacDive-ID 1676: growth at 23°C (borderline)

*Thermophilic mismatches (4/100):*
- BacDive-ID 437: optimum 40°C, growth 15-40°C (below thermophilic range)
- BacDive-ID 506: optimum 42-45°C (borderline)

*Hyperthermophilic mismatch (1/100):*
- BacDive-ID 16897: growth 50-92°C, optimum 74°C (below 80°C threshold)

### Key Findings:

1. **Very high accuracy (96-100%):** Keywords generally match actual temperatures
2. **Borderline cases exist:** Some strains at category boundaries (22°C for psychrophilic, 42-45°C for thermophilic)
3. **Keywords likely ML-predicted or rule-based:** Not from direct curation, but derived from temperature data
4. **Coverage difference meaningful:** 49,507 strains with structured data vs 45,135 with keywords = **4,372 strains (9.7%)** could get temperature categories if we extract from structured path

### Correlation:

**99.9% of keyword strains ALSO have structured data**
- This confirms keywords are DERIVED from structured data
- Structured data is primary source
- Keywords are secondary/inferred
- Small mismatch rate (1-4%) suggests:
  - Automated assignment with occasional errors
  - Borderline cases assigned to nearest category
  - Or rule changes over time

---

## Summary

**Why 1,267 unique values?**

1. **Ranges are hyper-specific** (834 unique ranges)
2. **Decimal precision varies** (322 values with decimals)
3. **Format inconsistencies** (leading zeros, double dashes)
4. **Lab-specific reporting** (different measurement precision)
5. **String matching, not numeric** ("37" ≠ "37.0")

**Bottom line:**
- Temperature data is rich but messy
- Needs parsing for meaningful extraction
- Well worth the effort: 49,507 strains with quantitative temperature data
- Currently being ignored by kg-microbe despite constants being defined
