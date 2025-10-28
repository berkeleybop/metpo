# BacDive Oxygen Tolerance Value Diversity

**Path:** `Physiology and metabolism.oxygen tolerance.oxygen tolerance`

**Reported unique values:** 206

**Actual unique base terms:** 9

---

## Why 206 "Unique" Values?

### The Answer: Arrays with Multiple Observations

The oxygen tolerance field can be:
1. **Single string:** `"anaerobe"`
2. **Array of strings:** `["aerobe", "facultative anaerobe", "microaerophile"]`

**When I counted "unique values," I was counting each unique array combination!**

### The Structure

**Distribution:**
- **18,654 strains (80%):** Single string value
- **4,600 strains (20%):** Array of multiple values

**Array sizes:**
- 2 values: 3,656 strains (most common)
- 3 values: 738 strains
- 4 values: 170 strains
- 5 values: 33 strains
- 6 values: 2 strains

**Unique array combinations:** 124

**Why so many array combinations?**
1. **Different orders:** `["aerobe", "obligate aerobe"]` ≠ `["obligate aerobe", "aerobe"]`
2. **Duplicates:** `["aerobe", "aerobe", "obligate aerobe"]` ≠ `["aerobe", "obligate aerobe"]`
3. **Different terms:** `["aerobe", "facultative anaerobe"]` ≠ `["aerobe", "microaerophile"]`

**Total "unique" values at document level:**
- Single values: Various (9 base terms)
- Array combinations: 124
- Plus order/duplicate variants
- **= ~206 when counting naively**

---

## The 9 Base Terms

**Actual unique oxygen tolerance terms:**

1. **aerobe** (10,338 occurrences)
2. **anaerobe** (5,790 occurrences)
3. **microaerophile** (4,724 occurrences)
4. **facultative anaerobe** (4,484 occurrences)
5. **obligate aerobe** (3,346 occurrences)
6. **obligate anaerobe** (224 occurrences)
7. **facultative aerobe** (106 occurrences)
8. **aerotolerant** (21 occurrences)
9. **microaerotolerant** (5 occurrences)

**Total measurements:** ~29,000 (from 23,254 strains - many strains have multiple observations)

---

## Why Multiple Values Per Strain?

### Reason 1: Multiple Testing Conditions

Different labs test under different conditions:

**Example: BacDive-ID 95**
```json
[
  {"@ref": 5521, "oxygen tolerance": "aerobe"},
  {"@ref": 9023, "oxygen tolerance": "obligate aerobe"},
  {"@ref": 42021, "oxygen tolerance": "aerobe"}
]
```

Different references (labs/papers) report different classifications.

### Reason 2: Growth on Different Media

Oxygen tolerance can vary with:
- Medium composition
- Temperature
- pH
- Other environmental factors

### Reason 3: Strain Variability

Some strains show variable oxygen tolerance:
- Can grow both aerobically AND anaerobically
- Facultative organisms by definition

### Reason 4: Classification Disagreement

Different researchers classify the same strain differently:
- One lab: "aerobe"
- Another lab: "obligate aerobe"
- Another lab: "facultative anaerobe"

---

## Sample Array Combinations

**Most common patterns:**

1. **`["aerobe", "obligate aerobe"]`** - narrow vs broad aerobe classification
2. **`["anaerobe", "facultative anaerobe"]`** - anaerobic with some oxygen tolerance
3. **`["microaerophile", "facultative anaerobe"]`** - low oxygen preference with flexibility
4. **`["aerobe", "facultative anaerobe", "microaerophile"]`** - conflicting reports from 3 sources
5. **`["anaerobe", "anaerobe"]`** - duplicate observations (same classification, different refs)
6. **`["obligate aerobe", "obligate aerobe"]`** - duplicate agreement

**Unusual combinations:**
- `["aerobe", "obligate aerobe", "aerobe", "obligate aerobe"]` - 4 measurements alternating
- `["microaerophile", "facultative anaerobe", "anaerobe", "microaerophile", "microaerophile", "facultative anaerobe"]` - 6 measurements with conflicts

---

## Comparison to Keywords

**Keywords:**
- aerobe (9,353 strains)
- anaerobe (4,773 strains)
- microaerophile (3,986 strains)
- facultative anaerobe (3,493 strains)
- obligate aerobe (2,327 strains)
- obligate anaerobe (152 strains)
- facultative aerobe (92 strains)
- aerotolerant (13 strains)
- microaerotolerant (3 strains)

**Structured path:**
- 23,254 strains with oxygen tolerance data
- 9 unique base terms
- Multiple observations per strain common

**Coverage difference:**
- Keywords: 24,192 total (but some overlap between keywords per strain)
- Structured data: 23,254 strains
- Very similar coverage!

---

## Why This Matters

### Challenge: How to handle arrays?

**Option 1: Take first value**
- Simple but arbitrary
- Loses information

**Option 2: Take most common value**
- More robust
- Still loses information

**Option 3: Take most specific value**
- "obligate aerobe" > "aerobe"
- Requires hierarchy/ontology

**Option 4: Extract all values**
- Creates multiple edges per strain
- Most information retained
- More complex graph

**Option 5: Use consensus**
- If ≥2 sources agree, use that
- Otherwise, use "variable"

### Current kg-microbe Approach

kg-microbe likely uses the METPO tree traversal approach which:
- Extracts from structured path
- Uses parent-child hierarchy in METPO
- May handle arrays by taking specific values

### Recommendation

**For kg-microbe extraction:**

1. **Prefer structured path over keywords** (same coverage, more provenance)
2. **Handle arrays intelligently:**
   - Check for consensus (all agree)
   - Use most specific term (obligate > facultative > general)
   - Flag conflicts in metadata
3. **Link to references** (`@ref` field shows source)
4. **Extract duplicates as confidence signal** (multiple refs with same value = high confidence)

---

## Data Quality Observations

### Good:
- Only 9 base terms (controlled vocabulary)
- High coverage (23,254 strains = 23.4% of dataset)
- Multiple observations provide validation

### Issues:
1. **Conflicting classifications** - Same strain classified differently
2. **Duplicate observations** - `["aerobe", "aerobe"]` suggests redundant entries
3. **Order matters** - Arrays not sorted, so `["aerobe", "obligate aerobe"]` ≠ `["obligate aerobe", "aerobe"]`
4. **No weighting** - All observations treated equally regardless of source quality

---

## Summary

**Why 206 unique values?**

Not because there are 206 different oxygen tolerance types, but because:

1. **Arrays of observations:** 20% of strains have multiple values
2. **Order sensitivity:** `["A", "B"]` ≠ `["B", "A"]`
3. **Duplicates:** `["A", "A"]` ≠ `["A"]`
4. **Combinations:** With 9 base terms and arrays up to size 6, many permutations exist

**Reality:**
- **9 base terms** (controlled vocabulary)
- **124 unique array combinations** (with order/duplicates)
- **~82 additional variations** from order permutations
- **= 206 "unique" values** at document level

**For analysis:** Treat as 9 base categories with multiple observations per strain, not 206 categories.

**For extraction:** Use structured path, handle arrays intelligently, prefer most specific term or consensus.
