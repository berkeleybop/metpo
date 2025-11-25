# Metabolite Production

**Path:** `Physiology and metabolism.metabolite production`

**Status:** Documented in Google Doc (not marked as DONE)

---

## Schema

```json
{
  "@ref": integer,           // Literature reference ID
  "Chebi-ID": integer,       // optional (98.8% present) - 260 unique values
  "metabolite": string,      // REQUIRED (100%) - 505 unique values
  "production": string,      // optional (99.99% present) - 3 unique values
  "excretion": string        // optional (0.005% present, very rare) - 3 unique values
}
```

## Data Shape Distribution

| Shape | Count | Percentage |
|-------|-------|------------|
| Single object | 15,933 | 67.7% |
| Array (list of objects) | 7,587 | 32.3% |
| **Total strains** | 23,520 | 100% |

### Array Statistics
- Min length: 2
- Max length: 13
- Average length: ~3.1 entries per strain
- Total entries from arrays: 23,157
- Total entries from single objects: 15,933
- **Total entries: ~39,090**

### Production Values Distribution
| Value | Count | Percentage |
|-------|-------|------------|
| `no` | 29,419 | 75.3% |
| `yes` | 9,668 | 24.7% |
| `null` | 3 | <0.1% |

---

## MongoDB Queries

### Find strains with metabolite production data
```javascript
db.strains_api.find(
  { 'Physiology and metabolism.metabolite production': { $exists: true } }
).count()
// Returns: 23520
```

### Get shape distribution
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.metabolite production': { $exists: true } } },
  { $project: {
      shape: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.metabolite production' },
          then: 'array',
          else: { $type: '$Physiology and metabolism.metabolite production' }
        }
      }
    }
  },
  { $group: { _id: '$shape', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Get distinct production values
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.metabolite production': { $exists: true } } },
  { $project: {
      production: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.metabolite production' },
          then: '$Physiology and metabolism.metabolite production',
          else: ['$Physiology and metabolism.metabolite production']
        }
      }
    }
  },
  { $unwind: '$production' },
  { $group: { _id: '$production.production', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
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
    "metabolite production": [
      {
        "@ref": 22965,
        "Chebi-ID": 17272,
        "metabolite": "propionate",
        "production": "yes"
      },
      {
        "@ref": 22965,
        "Chebi-ID": 17968,
        "metabolite": "butyrate",
        "production": "yes"
      },
      {
        "@ref": 22965,
        "Chebi-ID": 30089,
        "metabolite": "acetate",
        "production": "yes"
      },
      {
        "@ref": 68380,
        "Chebi-ID": 35581,
        "metabolite": "indole",
        "production": "no"
      }
    ]
  }
}
```

### Single Object Example (BacDive-ID: 98)
```json
{
  "General": { "BacDive-ID": 98 },
  "Physiology and metabolism": {
    "metabolite production": {
      "@ref": 68380,
      "Chebi-ID": 35581,
      "metabolite": "indole",
      "production": "no"
    }
  }
}
```

---

## METPO Predicate Mapping

Based on the Google Doc:

| Production Value | METPO Predicate |
|-----------------|-----------------|
| `yes` | `METPO:produces` |
| `no` | `METPO:does_not_produce` |

---

## Edge Generation

Each entry generates a triple:

```
NCBITaxon:{tax_id} → {METPO_predicate} → CHEBI:{chebi_id}
```

### Example Edges
```
NCBITaxon:187327 → METPO:produces → CHEBI:17272      # propionate production yes
NCBITaxon:187327 → METPO:produces → CHEBI:17968      # butyrate production yes
NCBITaxon:187327 → METPO:does_not_produce → CHEBI:35581  # indole production no
```

---

## Processing Notes

1. **Handle both shapes:** Single objects are MORE common (67.7%) than arrays here
2. **Missing ChEBI IDs:** Some entries may lack `Chebi-ID` - need mapping from metabolite name
3. **Excretion field:** Very rare (only 2 entries) - may want to capture separately
4. **Null production values:** 3 entries have null - skip or handle specially
5. **Common metabolites:** Indole is frequently tested (production of indole is a classic biochemical test)
