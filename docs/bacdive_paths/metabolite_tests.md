# Metabolite Tests

**Path:** `Physiology and metabolism.metabolite tests`

**Status:** TODO (per Google Doc)

---

## Schema

```json
{
  "@ref": integer,                  // Literature reference ID
  "Chebi-ID": integer,              // REQUIRED (100%) - 9 unique values
  "metabolite": string,             // REQUIRED (100%) - 9 unique values
  "voges-proskauer-test": string,   // optional (43.5% present) - 4 unique values
  "methylred-test": string,         // optional (13.8% present) - 4 unique values
  "indole test": string,            // optional (42.3% present) - 3 unique values
  "citrate test": string            // optional (0.4% present) - 4 unique values
}
```

**Note:** Each entry tests ONE metabolite and may have results for multiple test types.

## Data Shape Distribution

| Shape | Count | Percentage |
|-------|-------|------------|
| Single object | 12,093 | 59.9% |
| Array (list of objects) | 8,106 | 40.1% |
| **Total strains** | 20,199 | 100% |

**Total entries: 30,436**

---

## Test Types and Value Distributions

| Test | `+` (positive) | `-` (negative) | `+/-` (variable) | Total |
|------|----------------|----------------|------------------|-------|
| Voges-Proskauer | 4,849 | 8,397 | 4 | 13,250 |
| Indole | 2,454 | 10,415 | 0 | 12,869 |
| Methyl Red | 1,720 | 2,493 | 2 | 4,215 |
| Citrate | 29 | 80 | 2 | 111 |

---

## MongoDB Queries

### Find strains with metabolite tests data
```javascript
db.strains_api.find(
  { 'Physiology and metabolism.metabolite tests': { $exists: true } }
).count()
// Returns: 20199
```

### Get shape distribution
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.metabolite tests': { $exists: true } } },
  { $project: {
      shape: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.metabolite tests' },
          then: 'array',
          else: { $type: '$Physiology and metabolism.metabolite tests' }
        }
      }
    }
  },
  { $group: { _id: '$shape', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Get test value distributions
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.metabolite tests': { $exists: true } } },
  { $project: {
      tests: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.metabolite tests' },
          then: '$Physiology and metabolism.metabolite tests',
          else: ['$Physiology and metabolism.metabolite tests']
        }
      }
    }
  },
  { $unwind: '$tests' },
  { $facet: {
      vp: [
        { $match: { 'tests.voges-proskauer-test': { $exists: true, $ne: null } } },
        { $group: { _id: '$tests.voges-proskauer-test', count: { $sum: 1 } } }
      ],
      mr: [
        { $match: { 'tests.methylred-test': { $exists: true, $ne: null } } },
        { $group: { _id: '$tests.methylred-test', count: { $sum: 1 } } }
      ],
      indole: [
        { $match: { 'tests.indole test': { $exists: true, $ne: null } } },
        { $group: { _id: '$tests.indole test', count: { $sum: 1 } } }
      ],
      citrate: [
        { $match: { 'tests.citrate test': { $exists: true, $ne: null } } },
        { $group: { _id: '$tests.citrate test', count: { $sum: 1 } } }
      ]
    }
  }
])
```

---

## Example Data

### Array Example (BacDive-ID: 73)
```json
{
  "General": {
    "BacDive-ID": 73,
    "NCBI tax id": [
      { "NCBI tax id": 1123064, "Matching level": "strain" },
      { "NCBI tax id": 424704, "Matching level": "species" }
    ]
  },
  "Physiology and metabolism": {
    "metabolite tests": [
      {
        "@ref": 22960,
        "Chebi-ID": 15688,
        "metabolite": "acetoin",
        "voges-proskauer-test": "-"
      },
      {
        "@ref": 22960,
        "Chebi-ID": 17234,
        "metabolite": "glucose",
        "methylred-test": "-"
      }
    ]
  }
}
```

### Single Object Example (BacDive-ID: 99)
```json
{
  "General": { "BacDive-ID": 99 },
  "Physiology and metabolism": {
    "metabolite tests": {
      "@ref": 68380,
      "Chebi-ID": 35581,
      "metabolite": "indole",
      "indole test": "-"
    }
  }
}
```

---

## Test Descriptions

| Test | What it detects | Associated Metabolite |
|------|-----------------|----------------------|
| **Voges-Proskauer** | Acetoin production from glucose fermentation | acetoin (CHEBI:15688) |
| **Methyl Red** | Mixed acid fermentation (pH drop) | glucose (CHEBI:17234) |
| **Indole** | Tryptophan degradation to indole | indole (CHEBI:35581) |
| **Citrate** | Citrate as sole carbon source | citrate |

---

## METPO Predicate Mapping

Based on the Google Doc, the mapping creates test-specific edges:

### Edge Pattern
```
NCBITaxon:{tax_id} → METPO:tests_positive_for → METPO:{test_name}
NCBITaxon:{tax_id} → METPO:tests_negative_for → METPO:{test_name}
METPO:{test_name} → METPO:assesses → CHEBI:{chebi_id}
```

### Test Name Mappings
| BacDive Field | METPO Term |
|---------------|------------|
| `voges-proskauer-test` | `METPO:voges-proskauer-test` |
| `methylred-test` | `METPO:methylred-test` |
| `indole test` | `METPO:indole-test` |
| `citrate test` | `METPO:citrate-test` |

### Example Edges
```
# For voges-proskauer-test: "-" with metabolite acetoin
NCBITaxon:424704 → METPO:tests_negative_for → METPO:voges-proskauer-test
METPO:voges-proskauer-test → METPO:assesses → CHEBI:15688

# For indole test: "+" with metabolite indole
NCBITaxon:424704 → METPO:tests_positive_for → METPO:indole-test
METPO:indole-test → METPO:assesses → CHEBI:35581
```

---

## Processing Notes

1. **Handle both shapes:** Single objects are more common (59.9%)
2. **Multiple tests per entry:** One metabolite entry may have multiple test results
3. **Variable results (`+/-`):** Per Google Doc, these should be EXCLUDED (only 8 total)
4. **Test-metabolite relationship:** Each test type is associated with a specific metabolite
5. **METPO terms needed:** Need to create METPO terms for each test type:
   - `METPO:voges-proskauer-test`
   - `METPO:methylred-test`
   - `METPO:indole-test`
   - `METPO:citrate-test`
6. **Predicates needed:**
   - `METPO:tests_positive_for`
   - `METPO:tests_negative_for`
   - `METPO:assesses`
