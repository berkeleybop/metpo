# METPO Grounding Analysis

Consolidated findings on ontology grounding in OntoGPT extractions.

## Critical Discovery: URI vs CURIE Format

**Problem**: Initial analysis claimed 0% METPO grounding. This was WRONG.

**Root cause**: Searched for CURIE format (`METPO:1000681`) but METPO uses URI format (`<https://w3id.org/metpo/1000681>`).

All other ontologies use CURIE format:
- `CHEBI:17439`
- `NCBITaxon:1355477`
- `OMP:0000001`

**Correct search pattern**:
```bash
# Find ALL METPO terms (both formats)
grep -rE "(METPO:|w3id\.org/metpo/)" literature_mining/outputs/

# Count by file
for f in literature_mining/outputs/*.yaml; do
  count=$(grep -c "w3id.org/metpo/" "$f" || echo 0)
  if [ "$count" -gt 0 ]; then echo "$f: $count"; fi
done

# Extract unique METPO classes
grep -roh "w3id\.org/metpo/[0-9]*" literature_mining/outputs/ | sort -u
```

## Successfully Grounded METPO Classes

8 unique METPO classes found in extractions:

| METPO ID | Label | Domain |
|----------|-------|--------|
| METPO:1000602 | aerobic | oxygen requirement |
| METPO:1000603 | anaerobic | oxygen requirement |
| METPO:1000605 | facultative | oxygen requirement |
| METPO:1000615 | mesophilic | temperature |
| METPO:1000620 | halophilic | salinity |
| METPO:1000681 | rod-shaped | morphology |
| METPO:1000702 | motile | motility |
| METPO:1000703 | non-motile | motility |

**Files with most METPO groundings**:
- `growth_conditions_gpt-4o_20251030_142703.yaml` - 20 URIs
- `morphology_gpt-4o_20251030_180642.yaml` - 22 URIs

## Annotator Configuration: What Works vs Fails

### Working configurations

Templates that successfully ground to METPO:

```yaml
# morphology_template_base.yaml
Motility:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:obo:metpo

# growth_conditions_hybrid.yaml
OxygenRequirement:
  is_a: NamedEntity
  annotations:
    annotators: sqlite:../src/ontology/metpo.owl
```

### Failing configurations

Templates that produce 0% METPO grounding:

```yaml
# biochemical_hybrid.yaml - NO METPO ANNOTATOR
MetabolicPhenotype:
  annotations:
    annotators: sqlite:obo:go, sqlite:obo:chebi
```

**Key insight**: Templates MUST include METPO annotator to ground to METPO.

## Annotator Comparison Results

Fair comparison using identical prompts, different annotators (10 ICBO abstracts):

| Annotator | Phenotype Groundings | Notes |
|-----------|---------------------|-------|
| METPO | 26 | Best coverage |
| MicrO | 23 | 21% grounding rate |
| OMP | 15 | Limited to OMP terms |
| PATO | 8 | General qualities only |

**Location**: `outputs/annotator_comparison_fair/`
**Command**: `make fair-annotator-analyze`

See also: [TEMPLATE_OPTIMIZATION.md](TEMPLATE_OPTIMIZATION.md) for template design patterns.

## MicrO Problems

Despite 22,205 classes, MicrO achieved only 21% grounding vs METPO's 26%.

Issues identified:
- Semsql build failures
- Unmaintained since 2018
- Failed to ground: "motile", "non-motile", "methylotroph", "methanotroph"

Full analysis: [MICRO_PROBLEMS_ANALYSIS.md](../metpo-justification/MICRO_PROBLEMS_ANALYSIS.md)

## Open Questions

1. **Why URI format for METPO only?**
   - OBO library vs local file difference?
   - OntoGPT configuration?

2. **Gram stain grounding failures**
   - Extraction: `AUTO:Gram-stain-negative`
   - METPO has: `METPO:1000702` (label: "Gram-negative")
   - Need synonym mapping

---

## Related Documentation

- **[Alignment Handoff](../../../docs/alignment/metpo_alignment_handoff.md)** - ChromaDB semantic alignment pipeline for METPO
- **[METPO Justification](../../../docs/ontology/METPO_JUSTIFICATION.md)** - Why METPO was created
- **[Merge Scenario Analysis](../metpo-justification/MERGE_SCENARIO_ANALYSIS.md)** - Empirical comparison of MicrO+OMP vs METPO

---

*Consolidated from: SESSION_HANDOFF_2025-11-06.md, METPO_GROUNDING_CORRECTED_ANALYSIS.md*
