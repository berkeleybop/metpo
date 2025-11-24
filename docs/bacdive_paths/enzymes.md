# Enzymes

**Path:** `Physiology and metabolism.enzymes`

**Status:** Documented in Google Doc

---

## Schema

```json
{
  "@ref": integer,     // Literature reference ID
  "value": string,     // REQUIRED (100%) - 191 unique values
  "activity": string,  // optional (99.98% present) - 4 unique values
  "ec": string         // optional (75.5% present) - 104 unique values
}
```

## Data Shape Distribution

| Shape | Count | Percentage |
|-------|-------|------------|
| Array (list of objects) | 28,660 | 97.8% |
| Single object | 659 | 2.2% |
| **Total strains** | 29,319 | 100% |

### Array Statistics
- Min length: 2
- Max length: 106
- Average length: ~20.2 entries per strain
- Total entries from arrays: 577,932
- Total entries from single objects: 659
- **Total entries: ~578,591**

### Activity Values Distribution
| Value | Count | Percentage |
|-------|-------|------------|
| `-` (negative) | 369,367 | 63.8% |
| `+` (positive) | 207,154 | 35.8% |
| `+/-` (variable) | 1,939 | 0.3% |
| `null` | 131 | <0.1% |

### EC Number Coverage
| Status | Count | Percentage |
|--------|-------|------------|
| Has EC number | 436,608 | 75.4% |
| No EC number | 141,983 | 24.6% |

---

## MongoDB Queries

### Find strains with enzyme data
```javascript
db.strains_api.find(
  { 'Physiology and metabolism.enzymes': { $exists: true } }
).count()
// Returns: 29319
```

### Get shape distribution
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.enzymes': { $exists: true } } },
  { $project: {
      shape: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.enzymes' },
          then: 'array',
          else: { $type: '$Physiology and metabolism.enzymes' }
        }
      }
    }
  },
  { $group: { _id: '$shape', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Get activity value distribution
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.enzymes': { $exists: true } } },
  { $project: {
      enzymes: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.enzymes' },
          then: '$Physiology and metabolism.enzymes',
          else: ['$Physiology and metabolism.enzymes']
        }
      }
    }
  },
  { $unwind: '$enzymes' },
  { $group: { _id: '$enzymes.activity', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Count entries with/without EC numbers
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.enzymes': { $exists: true } } },
  { $project: {
      enzymes: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.enzymes' },
          then: '$Physiology and metabolism.enzymes',
          else: ['$Physiology and metabolism.enzymes']
        }
      }
    }
  },
  { $unwind: '$enzymes' },
  { $group: {
      _id: { $cond: { if: { $ifNull: ['$enzymes.ec', false] }, then: 'has_ec', else: 'no_ec' } },
      count: { $sum: 1 }
    }
  }
])
```

---

## Example Data

### Array Example (BacDive-ID: 99)
```json
{
  "General": {
    "BacDive-ID": 99,
    "NCBI tax id": [
      { "NCBI tax id": 1120921, "Matching level": "strain" },
      { "NCBI tax id": 187327, "Matching level": "species" }
    ]
  },
  "Physiology and metabolism": {
    "enzymes": [
      {
        "@ref": 22965,
        "value": "catalase",
        "activity": "-",
        "ec": "1.11.1.6"
      },
      {
        "@ref": 22965,
        "value": "cytochrome oxidase",
        "activity": "-",
        "ec": "1.9.3.1"
      },
      {
        "@ref": 22965,
        "value": "gelatinase",
        "activity": "-"
      },
      {
        "@ref": 68382,
        "value": "alkaline phosphatase",
        "activity": "-",
        "ec": "3.1.3.1"
      },
      {
        "@ref": 68382,
        "value": "acid phosphatase",
        "activity": "+",
        "ec": "3.1.3.2"
      }
    ]
  }
}
```

### Single Object Example (BacDive-ID: 45)
```json
{
  "General": { "BacDive-ID": 45 },
  "Physiology and metabolism": {
    "enzymes": {
      "@ref": 30251,
      "value": "catalase",
      "activity": "+",
      "ec": "1.11.1.6"
    }
  }
}
```

---

## METPO Predicate Mapping

Based on the Google Doc:

| Activity | METPO Predicate |
|----------|-----------------|
| `+` | `METPO:demonstrates_activity_of` |
| `-` | `METPO:does_not_demonstrate_activity_of` |
| `+/-` | (exclude or handle specially) |

---

## Edge Generation

Each entry generates a triple using EC number when available:

```
NCBITaxon:{tax_id} → {METPO_predicate} → EC:{ec_number}
```

### Example Edges
```
NCBITaxon:187327 → METPO:does_not_demonstrate_activity_of → EC:1.11.1.6  # catalase -
NCBITaxon:187327 → METPO:demonstrates_activity_of → EC:3.1.3.2          # acid phosphatase +
```

### For entries without EC numbers
Option 1: Skip (lose 24.6% of data)
Option 2: Map enzyme name to EC number via external resource
Option 3: Create enzyme name nodes (e.g., `METPO:gelatinase`)

---

## Common Enzymes in Dataset

Some frequently tested enzymes:
- Catalase (EC:1.11.1.6)
- Oxidase / Cytochrome oxidase (EC:1.9.3.1)
- β-galactosidase (EC:3.2.1.23)
- Alkaline phosphatase (EC:3.1.3.1)
- Acid phosphatase (EC:3.1.3.2)
- Urease (EC:3.5.1.5)
- Various arylamidases
- Various glycosidases

---

## Processing Notes

1. **Handle both shapes:** Arrays are dominant (97.8%)
2. **EC number mapping:** 24.6% lack EC numbers - need strategy for these
3. **Variable activity (`+/-`):** ~1,939 entries - decide whether to include
4. **Null activity:** 131 entries have null activity - skip these
5. **Duplicate enzymes:** Same enzyme may appear multiple times per strain from different references
6. **Enzyme name normalization:** Names vary (e.g., "oxidase" vs "cytochrome oxidase") - may need standardization
