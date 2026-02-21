# MetaTraits In-Sheet Resolution Report

## Summary

- Total cards: 2860
- Base cards: 81
- Composed cards: 2779
- Fully resolved (METPO): 2316
- Cards with usable external CURIEs (CHEBI/GO/EC): 2750
- **Effective KGX coverage: 2801/2860 (97%)**
- Truly unmapped (no METPO, no external CURIEs): 59

## Trait Format Breakdown

| Format | Cards | METPO resolved | Effective KGX | KGX mapping strategy |
|--------|-------|---------------|--------------|---------------------|
| `composed_boolean` | 2779 | 2258 | 2721 | METPO predicate + CHEBI/GO/EC object |
| `uncomposed_boolean` | 47 | 24 | 46 | has_phenotype / capable_of + METPO class |
| `uncomposed_factor` | 9 | 9 | 9 | has_phenotype + METPO value class |
| `uncomposed_numeric` | 25 | 25 | 25 | METPO data property + xsd:decimal |

## CURIE Pattern Distribution

- 0 CURIEs: 1
- 1 CURIE: 524
- 2 CURIEs: 2249
- 3+ CURIEs: 86

## METPO Resolution Status Counts

- `resolved_with_notes`: 2048
- `missing_chebi; missing_process_term`: 521
- `resolved`: 250
- `missing_process_term`: 23
- `resolved_nonchebi_with_notes`: 18

## Unresolved Composed Categories

| Category | Unresolved | Have predicates | Have ext CURIEs | Blocker |
|----------|-----------|----------------|----------------|--------|
| `produces` | 232 | 232 | 231 | missing CHEBI |
| `enzyme activity` | 132 | 132 | 77 | missing CHEBI |
| `assimilation` | 29 | 29 | 29 | missing CHEBI (ext CURIEs usable) |
| `growth` | 27 | 27 | 26 | missing CHEBI |
| `carbon source` | 20 | 20 | 20 | missing CHEBI (ext CURIEs usable) |
| `builds acid from` | 16 | 16 | 16 | missing CHEBI (ext CURIEs usable) |
| `degradation` | 13 | 13 | 12 | missing CHEBI |
| `hydrolysis` | 13 | 13 | 13 | missing CHEBI (ext CURIEs usable) |
| `utilizes` | 12 | 12 | 12 | missing CHEBI (ext CURIEs usable) |
| `energy source` | 6 | 6 | 6 | missing CHEBI (ext CURIEs usable) |
| `nitrogen source` | 6 | 6 | 6 | missing CHEBI (ext CURIEs usable) |
| `oxidation` | 6 | 6 | 6 | missing CHEBI (ext CURIEs usable) |
| `reduction` | 4 | 4 | 4 | missing CHEBI (ext CURIEs usable) |
| `aerobic growth` | 2 | 2 | 2 | missing CHEBI (ext CURIEs usable) |
| `anaerobic growth with light` | 2 | 2 | 2 | missing CHEBI (ext CURIEs usable) |
| `anaerobic growth` | 1 | 1 | 1 | missing CHEBI (ext CURIEs usable) |

## Truly Unmapped Cards

59 cards have no METPO resolution and no usable external CURIEs (CHEBI, GO, EC):

- `enzyme activity`: 55
- `base`: 1
- `degradation`: 1
- `growth`: 1
- `produces`: 1
