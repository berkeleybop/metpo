# Metabolite Utilization

**Path:** `Physiology and metabolism.metabolite utilization`

**Status:** ✅ DONE (per Google Doc)

---

## Schema

```json
{
  "@ref": integer,                    // Literature reference ID
  "Chebi-ID": integer,                // optional (97.8% present) - 777 unique values
  "metabolite": string,               // REQUIRED (100%) - 953 unique values
  "utilization activity": string,     // optional (99.996% present) - 4 unique values
  "kind of utilization tested": string // optional (99.0% present) - 26 unique values
}
```

## Data Shape Distribution

| Shape | Count | Percentage |
|-------|-------|------------|
| Array (list of objects) | 29,901 | 99.0% |
| Single object | 298 | 1.0% |
| **Total strains** | 30,199 | 100% |

### Array Statistics
- Min length: 2
- Max length: 261
- Average length: ~29.5 entries per strain
- **Total entries: ~881,958**

---

## MongoDB Queries

### Find strains with metabolite utilization data
```javascript
db.strains_api.find(
  { 'Physiology and metabolism.metabolite utilization': { $exists: true } }
).count()
// Returns: 30199
```

### Get a sample record (array shape)
```javascript
db.strains_api.findOne(
  { 'Physiology and metabolism.metabolite utilization': { $exists: true, $type: 'array' } },
  { 'Physiology and metabolism.metabolite utilization': 1, 'General.NCBI tax id': 1, 'General.BacDive-ID': 1 }
)
```

### Get a sample record (single object shape)
```javascript
db.strains_api.findOne(
  { 'Physiology and metabolism.metabolite utilization': { $exists: true, $not: { $type: 'array' } } },
  { 'Physiology and metabolism.metabolite utilization': 1, 'General.BacDive-ID': 1 }
)
```

### Get distinct utilization types
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.metabolite utilization': { $exists: true } } },
  { $project: {
      utilization: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.metabolite utilization' },
          then: '$Physiology and metabolism.metabolite utilization',
          else: ['$Physiology and metabolism.metabolite utilization']
        }
      }
    }
  },
  { $unwind: '$utilization' },
  { $group: { _id: '$utilization.kind of utilization tested', count: { $sum: 1 } } },
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
    "metabolite utilization": [
      {
        "@ref": 22965,
        "Chebi-ID": 24996,
        "metabolite": "lactate",
        "utilization activity": "-",
        "kind of utilization tested": "growth"
      },
      {
        "@ref": 22965,
        "Chebi-ID": 17632,
        "metabolite": "nitrate",
        "utilization activity": "-",
        "kind of utilization tested": "reduction"
      },
      {
        "@ref": 22965,
        "Chebi-ID": 29985,
        "metabolite": "L-glutamate",
        "utilization activity": "+",
        "kind of utilization tested": "fermentation"
      }
    ]
  }
}
```

### Single Object Example (BacDive-ID: 4)
```json
{
  "General": { "BacDive-ID": 4 },
  "Physiology and metabolism": {
    "metabolite utilization": {
      "@ref": 22886,
      "Chebi-ID": 17790,
      "metabolite": "methanol",
      "utilization activity": "-",
      "kind of utilization tested": "growth"
    }
  }
}
```

---

## Utilization Types

| Type | Description |
|------|-------------|
| `reduction` | Metabolite reduction (e.g., nitrate → nitrite) |
| `fermentation` | Fermentation of substrate |
| `degradation` | Breakdown/catabolism of compound |
| `hydrolysis` | Hydrolytic cleavage |
| `growth` | Growth on substrate as carbon/energy source |
| `energy source` | Use as energy source |

---

## METPO Predicate Mapping

Based on the Google Doc, the mapping follows this pattern:

### Positive Activity (+)
| Utilization Type | METPO Predicate |
|-----------------|-----------------|
| reduction | `METPO:reduces` |
| fermentation | `METPO:ferments` |
| degradation | `METPO:degrades` |
| hydrolysis | `METPO:hydrolyzes` |
| growth | `METPO:grows_on` |
| energy source | `METPO:uses_as_energy_source` |

### Negative Activity (-)
| Utilization Type | METPO Predicate |
|-----------------|-----------------|
| reduction | `METPO:does_not_reduce` |
| fermentation | `METPO:does_not_ferment` |
| degradation | `METPO:does_not_degrade` |
| hydrolysis | `METPO:does_not_hydrolyze` |
| growth | `METPO:does_not_grow_on` |
| energy source | `METPO:does_not_use_as_energy_source` |

---

## Edge Generation

Each entry generates a triple:

```
NCBITaxon:{tax_id} → {METPO_predicate} → CHEBI:{chebi_id}
```

### Example Edges
```
NCBITaxon:187327 → METPO:does_not_reduce → CHEBI:17632  # nitrate reduction -
NCBITaxon:187327 → METPO:ferments → CHEBI:29985         # L-glutamate fermentation +
```

---

## Processing Notes

1. **Handle both shapes:** Check if value is array or single object
2. **Missing ChEBI IDs:** Some entries may lack `Chebi-ID` - need mapping from metabolite name
3. **Activity values:** Primary values are `+` and `-`, but check for other values like `+/-`, `weak`, etc.
4. **Multiple tax IDs:** Strains may have both strain-level and species-level NCBI tax IDs
