# API Tests Overview

This document provides a summary of all API (bioMérieux) biochemical test kits in BacDive.

---

## Key Insight: Uniform Structure

**All 17 API tests share identical structure:**
- `@ref` - the only non-analyte field (literature reference ID)
- All other fields are analyte names with values: `+`, `-`, or `+/-`
- Field names ARE the analyte names (need external mapping to ChEBI/EC)

---

## Summary Table

| API Test | Strains | Field Count | Type |
|----------|---------|-------------|------|
| API zym | 11,747 | 20 | Enzyme |
| API 50CHac | 6,853 | 50 | Carbohydrate acidification |
| API rID32STR | 3,666 | 32 | Streptococcus rapid ID |
| API biotype100 | 3,599 | 99 | Carbohydrate assimilation |
| API 20NE | 3,833 | 21 | Non-Enterobacteriaceae |
| API 20E | 3,452 | 26 | Enterobacteriaceae |
| API coryne | 3,287 | 21 | Corynebacterium |
| API rID32A | 2,198 | 29 | Anaerobes rapid ID |
| API NH | 1,407 | 13 | Neisseria/Haemophilus |
| API ID32E | 1,438 | 32 | Enterobacteriaceae extended |
| API ID32STA | 839 | 26 | Staphylococcus |
| API CAM | 370 | 21 | Campylobacter |
| API 20STR | 311 | 21 | Streptococcus |
| API LIST | 270 | 11 | Listeria |
| API STA | 220 | 21 | Staphylococcus |
| API 20A | 185 | 24 | Anaerobes |
| API 50CHas | 13 | 50 | Carbohydrate assimilation |

**Total: ~43,688 strain records across all API tests**

---

## Structure

### Wide Format
All API tests use a **wide format** where each analyte is a separate field:

```json
{
  "@ref": 12345,
  "Alkaline phosphatase": "+",
  "Esterase": "-",
  "Lipase": "+/-",
  ...
}
```

This differs from `enzymes` and `metabolite utilization` which use **long format** (one row per test).

### Value Vocabulary

| Value | Meaning | Include in KG? |
|-------|---------|----------------|
| `+` | Positive/Present | Yes |
| `-` | Negative/Absent | Yes |
| `+/-` | Variable/Weak | No (exclude) |

These are the **only three values** across all non-@ref fields in all 17 API tests.

---

## Analyte Mapping

The field names in API tests are analyte names that need external mapping to ontology identifiers.

**Reference for well mappings:**
https://github.com/CultureBotAI/assay-metadata/blob/main/data/assay_kits_simple.json

### Edge Generation Pattern

```
NCBITaxon:{tax_id} → {METPO_predicate} → {CHEBI or EC identifier}
```

With source annotation:
```
source: bacdive:{API test name} - {field name}
```

Example:
```
NCBITaxon:225144 → METPO:demonstrates_activity_of → EC:3.1.3.1
source: bacdive:API zym - Alkaline phosphatase
```

---

## API Test Categories

### Enzyme Activity Tests
Test for presence/absence of specific enzymes:
- **API zym** (20 fields) - General enzyme panel
- **API rID32A** (29 fields) - Anaerobe identification (includes arylamidases)

**METPO Predicates:**
- `+` → `METPO:demonstrates_activity_of` → EC:{ec_number}
- `-` → `METPO:does_not_demonstrate_activity_of` → EC:{ec_number}

### Carbohydrate Utilization Tests
Test ability to ferment/assimilate carbon sources:
- **API 50CHac** (50 fields) - Carbohydrate acidification
- **API 50CHas** (50 fields) - Carbohydrate assimilation (identical fields to 50CHac)
- **API biotype100** (99 fields) - Extended carbon source panel

**METPO Predicates:**
- `+` → `METPO:catabolizes` → CHEBI:{chebi_id}
- `-` → `METPO:does_not_catabolize` → CHEBI:{chebi_id}

### Mixed Identification Panels
Combination of enzyme and substrate utilization tests:
- **API 20E** (26 fields) - Enterobacteriaceae
- **API 20NE** (21 fields) - Non-fermentative Gram-negative
- **API 20A** (24 fields) - Anaerobes
- **API 20STR** (21 fields) - Streptococcus
- **API ID32E** (32 fields) - Extended Enterobacteriaceae
- **API ID32STA** (26 fields) - Staphylococcus
- **API rID32STR** (32 fields) - Streptococcus rapid ID
- **API coryne** (21 fields) - Corynebacterium
- **API NH** (13 fields) - Neisseria/Haemophilus
- **API STA** (21 fields) - Staphylococcus
- **API CAM** (21 fields) - Campylobacter
- **API LIST** (11 fields) - Listeria

---

## MongoDB Queries

### Count all API test records
```javascript
const apiTests = [
  'API zym', 'API rID32A', 'API 50CHac', 'API biotype100', 'API 20NE',
  'API 20E', 'API rID32STR', 'API coryne', 'API NH', 'API ID32STA',
  'API ID32E', 'API STA', 'API CAM', 'API LIST', 'API 20A', 'API 20STR', 'API 50CHas'
];

apiTests.forEach(test => {
  const path = 'Physiology and metabolism.' + test;
  const count = db.strains_api.countDocuments({ [path]: { $exists: true } });
  print(test + ': ' + count);
});
```

### Get all field names for an API test
```javascript
db.strains_api.aggregate([
  { $match: { 'Physiology and metabolism.API zym': { $exists: true } } },
  { $project: { data: '$Physiology and metabolism.API zym' } },
  { $limit: 100 },
  { $project: { keys: { $objectToArray: '$data' } } },
  { $unwind: '$keys' },
  { $group: { _id: '$keys.k' } },
  { $sort: { _id: 1 } }
])
```

---

## Processing Strategy

Since all API tests share identical structure, a single generic processing function handles all of them. The only variable is the analyte-to-identifier mapping for each test kit.

### Edge Count Estimates

| API Test | Strains | Fields | Max Edges |
|----------|---------|--------|-----------|
| API zym | 11,747 | 20 | ~234,940 |
| API 50CHac | 6,853 | 50 | ~342,650 |
| API biotype100 | 3,599 | 99 | ~356,301 |
| API 20E | 3,452 | 26 | ~89,752 |
| API rID32STR | 3,666 | 32 | ~117,312 |
| (others) | ... | ... | ... |

**Estimated total: ~1.5-2M potential edges from API tests**
