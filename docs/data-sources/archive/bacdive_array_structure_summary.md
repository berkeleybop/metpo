# BacDive Array Structure Patterns Summary

**Key Finding:** BacDive uses **two different patterns** for storing multiple observations:

1. **Parent object is array** - Multiple observation objects, each with different fields
2. **Field value is array** - Single parent object with array-valued field

---

## Pattern 1: Array of Observation Objects

**Parent objects that are arrays:**

| Parent Path | Contains Fields | Base Terms | Pattern |
|-------------|-----------------|------------|---------|
| **Morphology.cell morphology** | gram stain, cell shape, motility, cell length, etc. | gram stain: 3<br>motility: 2<br>cell shape: 19 | Each array element is an observation with `@ref` |
| **Physiology and metabolism.spore formation** | spore formation | 2 (yes, no) | Each array element is an observation with `@ref` |
| **Physiology and metabolism.halophily** | halophily level | 7 | Each array element is an observation with `@ref` |

**Example structure:**
```json
"cell morphology": [
  {
    "@ref": 22965,
    "gram stain": "negative",
    "cell shape": "coccus-shaped",
    "motility": "no"
  },
  {
    "@ref": 67771,
    "gram stain": "negative",
    "cell shape": "coccus-shaped"
  },
  {
    "@ref": 120258,
    "gram stain": "negative",
    "cell shape": "coccus-shaped",
    "motility": "no"
  }
]
```

**Why this creates "extra" unique values:**

When querying `Morphology.cell morphology.gram stain`, MongoDB aggregation returns the value from **each array element**, so you get:
- `"negative"` (from element 0)
- `"negative"` (from element 1)
- `"negative"` (from element 2)

When grouped, if you don't unwind properly, the **entire array** becomes the group key, creating combinations like:
- `["negative", "negative", "negative"]`
- `["positive", "positive"]`
- `["negative", "positive"]`

This is why:
- **Gram stain:** 3 base terms → 26 "unique" combinations
- **Motility:** 2 base terms → 17 "unique" combinations
- **Cell shape:** 19 base terms → 127 "unique" combinations

---

## Pattern 2: Array-Valued Fields

**Fields where the value itself is an array:**

| Field Path | Base Terms | Array Pattern |
|------------|------------|---------------|
| **Physiology and metabolism.oxygen tolerance.oxygen tolerance** | 9 | Value is array or string |
| **Physiology and metabolism.nutrition type.type** | 22 | Value is comma-separated string |

**Example structure:**
```json
"oxygen tolerance": {
  "@ref": 5523,
  "oxygen tolerance": ["aerobe", "facultative anaerobe", "microaerophile"]
}
```

**Why this creates "extra" unique values:**

Each unique **array combination** (including order and duplicates) counts as a separate value:
- `["aerobe", "obligate aerobe"]` ≠ `["obligate aerobe", "aerobe"]`
- `["aerobe", "aerobe"]` ≠ `["aerobe"]`

This is why:
- **Oxygen tolerance:** 9 base terms → 206 "unique" combinations
- **Nutrition type:** 22 base terms → 41 "unique" combinations (mostly comma-separated strings)

---

## Detailed Statistics

### Morphology.cell morphology (Array of Objects)

**Strains with cell morphology data:** 16,032

**Field: gram stain**
- Base terms: 3 (negative, positive, variable)
- Total observations: 5,339 (across all array elements)
- Unique "combinations": 26 (when array treated as single value)
- Coverage: ~33% of strains have this field filled in array elements

**Field: motility**
- Base terms: 2 (yes, no)
- Total observations: 4,498
- Unique "combinations": 17
- Coverage: ~28% of strains have this field filled

**Field: cell shape**
- Base terms: 19
- Total observations: 4,961
- Unique "combinations": 127
- Coverage: ~31% of strains have this field filled

**Observation:** Most strains have 2-4 array elements in cell morphology, but not all elements have all fields filled.

### Physiology and metabolism.spore formation (Array of Objects)

**Strains with spore formation data:** 5,443

**Field: spore formation**
- Base terms: 2 (yes, no)
- Total observations: 797 (only 15% of arrays have this field)
- Unique "combinations": 9
- Pattern: `["yes", "yes"]`, `["no", "no"]`, `["yes", "no"]`, etc.

### Physiology and metabolism.halophily (Array of Objects)

**Strains with halophily data:** 9,687

**Field: halophily level**
- Base terms: 7
- Total observations: 355 (only 4% of arrays have this field)
- Unique "combinations": 19
- Pattern: Most arrays are short (1-2 elements)

### Physiology and metabolism.oxygen tolerance (Array-Valued Field)

**Strains with oxygen tolerance data:** 23,254

**Distribution:**
- Single string: 18,654 strains (80%)
- Array: 4,600 strains (20%)

**Array details:**
- Base terms: 9
- Array sizes: 1-6 values
- Unique combinations: 206

### Physiology and metabolism.nutrition type (Mixed Pattern)

**Strains with nutrition type data:** 490

**Pattern:** Mostly single strings, some comma-separated
- Base terms: 22
- Unique combinations: 41 (includes comma-separated variants)

---

## Why This Matters for Data Extraction

### Challenge: Multiple Observations Per Strain

**Same strain can have:**
- 3 different gram stain observations from 3 different papers
- 4 different cell shape observations
- Multiple oxygen tolerance classifications

**Questions for extraction:**
1. Which observation to use?
2. How to handle conflicts?
3. How to represent uncertainty?

### Extraction Strategies

**Option 1: Take first observation**
```python
value = array[0] if array else None
```
- ✅ Simple
- ❌ Arbitrary
- ❌ May not be most reliable

**Option 2: Take most common (consensus)**
```python
from collections import Counter
value = Counter(array).most_common(1)[0][0]
```
- ✅ Democratic
- ✅ Reduces noise
- ❌ Loses minority reports
- ⚠️ Ties are ambiguous

**Option 3: Take most specific**
```python
# For oxygen tolerance: obligate > facultative > general
hierarchy = ["obligate aerobe", "aerobe", "facultative anaerobe"]
value = min(array, key=lambda x: hierarchy.index(x) if x in hierarchy else 999)
```
- ✅ Maximizes information
- ❌ Requires domain knowledge
- ❌ May not apply to all fields

**Option 4: Extract all with provenance**
```python
for item in array:
    create_edge(strain, phenotype=item['gram stain'], source=item['@ref'])
```
- ✅ Maximum information retention
- ✅ Tracks provenance
- ❌ Creates many edges
- ❌ More complex queries

**Option 5: Aggregate to certainty level**
```python
if len(set(array)) == 1:
    certainty = "confirmed"  # All sources agree
elif len(set(array)) == 2:
    certainty = "conflicting"
else:
    certainty = "highly variable"
```
- ✅ Captures uncertainty
- ✅ Useful for data quality assessment
- ❌ Requires additional metadata fields

### Recommendation for kg-microbe

**Current approach:** Uses METPO tree traversal with parent-child matching, likely handles arrays implicitly.

**Suggested enhancement:**
1. **For high-confidence fields (gram stain, motility):** Use consensus
2. **For variable fields (cell shape, oxygen tolerance):** Extract all with provenance
3. **Track observation count** as metadata (more observations = more reliable)
4. **Flag conflicts** when observations disagree

---

## Summary Table

| Field | Parent Type | Base Terms | Unique Combos | Strains | Observations | Obs/Strain |
|-------|-------------|------------|---------------|---------|--------------|------------|
| **Gram stain** | Array of objects | 3 | 26 | 16,032 | 5,339 | 0.33 |
| **Motility** | Array of objects | 2 | 17 | 16,032 | 4,498 | 0.28 |
| **Cell shape** | Array of objects | 19 | 127 | 16,032 | 4,961 | 0.31 |
| **Spore formation** | Array of objects | 2 | 9 | 5,443 | 797 | 0.15 |
| **Halophily level** | Array of objects | 7 | 19 | 9,687 | 355 | 0.04 |
| **Oxygen tolerance** | Array-valued field | 9 | 206 | 23,254 | ~29,000 | 1.25 |
| **Nutrition type** | Comma-separated | 22 | 41 | 490 | ~490 | 1.0 |

**Key insight:** "Observations per strain" shows how often the field is populated within array elements. Low values (<1.0) indicate sparse data within arrays.

---

## Impact on Value Counts

**Original naive counts were inflated because:**

1. **Array of objects pattern** (gram stain, motility, cell shape):
   - Querying returns array of values from all elements
   - Each unique array becomes a "value"
   - Creates combinations like `["negative", "negative", "positive"]`

2. **Array-valued field pattern** (oxygen tolerance):
   - Field value is literally an array
   - Each unique array combination is a "value"
   - Order and duplicates create variants

**Corrected counts:**

| Field | Naive Count | Actual Base Terms | Inflation Factor |
|-------|-------------|-------------------|------------------|
| Oxygen tolerance | 206 | 9 | 23x |
| Cell shape | 127 | 19 | 6.7x |
| Gram stain | 26 | 3 | 8.7x |
| Motility | 17 | 2 | 8.5x |
| Spore formation | 9 | 2 | 4.5x |
| Halophily | 19 | 7 | 2.7x |
| Nutrition type | 41 | 22 | 1.9x |

**Lesson:** When counting "unique values" in BacDive, always check if you're counting array combinations vs base terms!
