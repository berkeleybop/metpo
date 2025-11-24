# Antibiotic Resistance

**Path:** `Physiology and metabolism.antibiotic resistance`

**Status:** Not explicitly in Google Doc, but related to metabolic phenotypes

---

## Schema

```json
{
  "@ref": integer,              // Literature reference ID
  "ChEBI": integer,             // optional (97.5% present) - 194 unique values
  "metabolite": string,         // REQUIRED (100%) - 206 unique values
  "is antibiotic": string,      // REQUIRED (100%) - 1 unique value ("yes")
  "is resistant": string,       // optional (50.1% present) - 3 unique values
  "is sensitive": string,       // optional (65.2% present) - 3 unique values
  "is intermediate": string,    // optional (0.2% present) - 2 unique values
  "resistance conc.": string,   // optional (2.7% present) - 142 unique values
  "sensitivity conc.": string,  // optional (5.9% present) - 192 unique values
  "intermediate conc.": string, // optional (0.06% present) - 14 unique values
  "group ID": integer           // optional (0.5% present) - 29 unique values
}
```

## Data Shape Distribution

| Shape | Count | Percentage |
|-------|-------|------------|
| Single object | 4,163 | 63.5% |
| Array (list of objects) | 2,397 | 36.5% |
| **Total strains** | 6,560 | 100% |

**Total entries: 21,177**

---

## Value Distributions

### Resistance Status
| Field | `yes` | `no` | `null` |
|-------|-------|------|--------|
| `is resistant` | 9,303 | 1,312 | 10,562 |
| `is sensitive` | 11,642 | 2,155 | 7,380 |
| `is intermediate` | 33 | 0 | 21,144 |

**Note:** Most entries have either `is resistant` OR `is sensitive` set, not both.

---

## MongoDB Queries

### Find strains with antibiotic resistance data
```javascript
db.strains_api.find(
  { 'Physiology and metabolism.antibiotic resistance': { $exists: true } }
).count()
// Returns: 6560
```

### Get shape distribution
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.antibiotic resistance': { $exists: true } } },
  { $project: {
      shape: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.antibiotic resistance' },
          then: 'array',
          else: { $type: '$Physiology and metabolism.antibiotic resistance' }
        }
      }
    }
  },
  { $group: { _id: '$shape', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Get resistance/sensitivity distributions
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.antibiotic resistance': { $exists: true } } },
  { $project: {
      abr: {
        $cond: {
          if: { $isArray: '$Physiology and metabolism.antibiotic resistance' },
          then: '$Physiology and metabolism.antibiotic resistance',
          else: ['$Physiology and metabolism.antibiotic resistance']
        }
      }
    }
  },
  { $unwind: '$abr' },
  { $facet: {
      resistant: [
        { $group: { _id: '$abr.is resistant', count: { $sum: 1 } } }
      ],
      sensitive: [
        { $group: { _id: '$abr.is sensitive', count: { $sum: 1 } } }
      ]
    }
  }
])
```

---

## Example Data

### Array Example (BacDive-ID: 82)
```json
{
  "General": {
    "BacDive-ID": 82,
    "NCBI tax id": { "NCBI tax id": 512383, "Matching level": "species" }
  },
  "Physiology and metabolism": {
    "antibiotic resistance": [
      {
        "@ref": 22964,
        "ChEBI": 28971,
        "metabolite": "ampicillin",
        "is antibiotic": "yes",
        "is resistant": "yes"
      },
      {
        "@ref": 22964,
        "ChEBI": 17698,
        "metabolite": "chloramphenicol",
        "is antibiotic": "yes",
        "is resistant": "yes"
      },
      {
        "@ref": 22964,
        "ChEBI": 17833,
        "metabolite": "gentamicin",
        "is antibiotic": "yes",
        "is sensitive": "yes"
      },
      {
        "@ref": 22964,
        "ChEBI": 6104,
        "metabolite": "kanamycin",
        "is antibiotic": "yes",
        "is sensitive": "yes"
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
    "antibiotic resistance": {
      "@ref": 119306,
      "ChEBI": 86455,
      "metabolite": "optochin",
      "is antibiotic": "yes",
      "is sensitive": "no",
      "is resistant": "yes"
    }
  }
}
```

---

## METPO Predicate Mapping

Suggested predicates for antibiotic resistance:

| Condition | METPO Predicate |
|-----------|-----------------|
| `is resistant: "yes"` | `METPO:resistant_to` |
| `is sensitive: "yes"` | `METPO:sensitive_to` |
| `is intermediate: "yes"` | `METPO:intermediate_to` (or skip) |
| `is resistant: "no"` | `METPO:not_resistant_to` OR `METPO:sensitive_to` |
| `is sensitive: "no"` | `METPO:not_sensitive_to` OR `METPO:resistant_to` |

---

## Edge Generation

Each entry generates a triple:

```
NCBITaxon:{tax_id} → {METPO_predicate} → CHEBI:{chebi_id}
```

### Example Edges
```
NCBITaxon:512383 → METPO:resistant_to → CHEBI:28971    # ampicillin resistant
NCBITaxon:512383 → METPO:resistant_to → CHEBI:17698    # chloramphenicol resistant
NCBITaxon:512383 → METPO:sensitive_to → CHEBI:17833    # gentamicin sensitive
NCBITaxon:512383 → METPO:sensitive_to → CHEBI:6104     # kanamycin sensitive
```

---

## Processing Notes

1. **Handle both shapes:** Single objects (63.5%) and arrays (36.5%)
2. **ChEBI IDs present:** Most entries have ChEBI identifiers
3. **Multiple status fields:** Check both `is resistant` and `is sensitive`
4. **Null handling:** Many entries have null for one of resistant/sensitive
5. **Intermediate rare:** Only 33 entries have `is intermediate: "yes"` - may want to skip
6. **Concentration data:** Available but not typically used for KG edges
7. **Conflicting values:** Some entries have both `is resistant: "yes"` and `is sensitive: "no"` - use primary indicator

### Common Antibiotics in Dataset
- Ampicillin (CHEBI:28971)
- Chloramphenicol (CHEBI:17698)
- Gentamicin (CHEBI:17833)
- Kanamycin (CHEBI:6104)
- Streptomycin (CHEBI:17076)
- Penicillin
- Tetracycline
- Vancomycin
