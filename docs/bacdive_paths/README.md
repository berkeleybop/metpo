# BacDive Metabolic Assay Paths

Documentation for extracting metabolic phenotype data from BacDive for the KG-Microbe knowledge graph.

**Source:** Google Doc "bacdive metabolic assays" + MongoDB `bacdive.strains_api` collection

---

## Quick Reference

| Path | Entries | Status | Predicate Type |
|------|---------|--------|----------------|
| [metabolite_utilization](metabolite_utilization.md) | ~882K | ✅ DONE | reduces, ferments, degrades, etc. |
| [metabolite_production](metabolite_production.md) | ~39K | Documented | produces |
| [metabolite_tests](metabolite_tests.md) | ~30K | TODO | tests_positive_for |
| [enzymes](enzymes.md) | ~579K | Documented | demonstrates_activity_of |
| [API tests](api_tests_overview.md) | ~1.5M | Documented | demonstrates_activity_of, catabolizes |
| [antibiotic_resistance](antibiotic_resistance.md) | ~21K | Bonus | resistant_to, sensitive_to |

**Total potential edges: ~3M+**

---

## Data Shapes

BacDive data comes in two formats:

### Long Format (row-per-test)
Used by: `metabolite utilization`, `metabolite production`, `metabolite tests`, `enzymes`, `antibiotic resistance`

```json
[
  { "metabolite": "glucose", "activity": "+" },
  { "metabolite": "lactose", "activity": "-" }
]
```

### Wide Format (column-per-test)
Used by: All API tests (`API zym`, `API 20E`, `API biotype100`, etc.)

```json
{
  "GLU": "+",
  "LAC": "-",
  "MAL": "+"
}
```

Both formats can be either:
- **Single object** (one test result)
- **Array** (multiple test results from different references)

---

## METPO Predicates Needed

### Metabolite Utilization
| Predicate | Description |
|-----------|-------------|
| `METPO:reduces` / `does_not_reduce` | Reduction (e.g., nitrate → nitrite) |
| `METPO:ferments` / `does_not_ferment` | Fermentation |
| `METPO:degrades` / `does_not_degrade` | Degradation/catabolism |
| `METPO:hydrolyzes` / `does_not_hydrolyze` | Hydrolysis |
| `METPO:grows_on` / `does_not_grow_on` | Growth on substrate |

### Metabolite Production
| Predicate | Description |
|-----------|-------------|
| `METPO:produces` / `does_not_produce` | Metabolite production |

### Metabolite Tests
| Predicate | Description |
|-----------|-------------|
| `METPO:tests_positive_for` | Positive test result |
| `METPO:tests_negative_for` | Negative test result |
| `METPO:assesses` | Test → metabolite relationship |

### Enzyme Activity
| Predicate | Description |
|-----------|-------------|
| `METPO:demonstrates_activity_of` | Enzyme activity present |
| `METPO:does_not_demonstrate_activity_of` | Enzyme activity absent |

### Carbon Source Utilization (API tests)
| Predicate | Description |
|-----------|-------------|
| `METPO:catabolizes` | Can use as carbon source |
| `METPO:does_not_catabolize` | Cannot use as carbon source |

### Antibiotic Resistance
| Predicate | Description |
|-----------|-------------|
| `METPO:resistant_to` | Resistant to antibiotic |
| `METPO:sensitive_to` | Sensitive to antibiotic |

---

## MongoDB Connection

```python
from pymongo import MongoClient

client = MongoClient()  # localhost, no auth
db = client.bacdive
collection = db.strains_api
```

Schema documentation available in `bacdive_meta.property_schemas`.

---

## Processing Pipeline

1. **Query strains** with target path
2. **Handle shapes** (array vs object)
3. **Map identifiers** (ChEBI, EC numbers)
4. **Generate triples** (NCBITaxon → predicate → object)
5. **Add provenance** (BacDive ID, reference ID)

---

## Files in This Directory

| File | Description |
|------|-------------|
| [README.md](README.md) | This overview |
| [metabolite_utilization.md](metabolite_utilization.md) | Metabolite utilization path |
| [metabolite_production.md](metabolite_production.md) | Metabolite production path |
| [metabolite_tests.md](metabolite_tests.md) | Biochemical tests (VP, MR, etc.) |
| [enzymes.md](enzymes.md) | Direct enzyme activity |
| [api_zym.md](api_zym.md) | API ZYM enzyme panel |
| [api_biotype100.md](api_biotype100.md) | API biotype100 carbon sources |
| [api_tests_overview.md](api_tests_overview.md) | All API tests summary |
| [antibiotic_resistance.md](antibiotic_resistance.md) | Antibiotic resistance |

---

## External Resources

- **Assay kit mappings:** https://github.com/CultureBotAI/assay-metadata/blob/main/data/assay_kits_simple.json
- **BacDive API:** https://bacdive.dsmz.de/api/
- **Google Doc:** "bacdive metabolic assays" (internal)
