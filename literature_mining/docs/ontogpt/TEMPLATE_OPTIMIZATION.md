# Template Optimization Guide

Consolidated learnings on OntoGPT template design for maximum extraction quality.

## The Winning Pattern

The hybrid template pattern achieves 100% ground truth accuracy:

```yaml
annotations:
  prompt: >-
    Extract ALL relationships. Be COMPREHENSIVE - do not omit any.
    Examples: 22A uses_for_growth methanol; MG1655 synthesizes cobalamin
  exclude: 22A, MG1655, methanol, cobalamin
```

**Three key components**:

1. **Inline examples** - Show exact output format in the prompt
2. **`exclude` annotation** - Prevents example entities from appearing in output
3. **Comprehensiveness instructions** - "Extract ALL", "Be COMPREHENSIVE", "do not omit"

## Template Iteration History

### Chemical Utilization Templates

| Version | Result | Problem |
|---------|--------|---------|
| V1 (baseline) | 23 rels, 73% grounding | Missed synthesis relationships |
| V2 (prompt.examples) | 17 rels | `prompt.examples` EXCLUDES entities! |
| V3 (verbose) | 1,748 rels (8 unique) | LLM loop bug from too many examples |
| Enhanced | 15 rels | Over-guidance biased predicate selection |
| CTD-style | 14 rels, 81% grounding | Good synthesis, poor volume |
| **Hybrid** | **34 rels, 100% accuracy** | **Production winner** |

### Morphology Templates

| Version | Grounding | Problem |
|---------|-----------|---------|
| Base | 62.5% | Appropriate for sparse data |
| V2 | 50.0% | Failed |
| V3 | 46.2% | Failed |
| V4 | 54.5% | Failed |
| Hybrid | 36.8% | Severe hallucinations |

**Key finding**: "Extract ALL" pattern FAILS when corpus lacks target data.

## Why Templates Fail

### `prompt.examples` annotation (V2)

```yaml
# WRONG - This EXCLUDES the examples from output
annotations:
  prompt.examples: |
    22A uses_for_growth methanol
```

The `prompt.examples` annotation tells OntoGPT to exclude those entities. Use inline examples with `exclude` instead.

### Verbose prompts (V3)

Too many examples (20+) cause LLM to loop, producing thousands of repeated items.

**Fix**: Keep to 5-8 examples maximum.

### Over-guidance (Enhanced)

Detailed categorical guidance biased the LLM away from appropriate predicates:
- Lost `uses_for_growth` entirely (0 vs 11 in baseline)
- Over-used generic `uses_in_other_way`

**Fix**: Show examples, don't over-explain categories.

### Corpus mismatch (Morphology hybrid)

CMM papers are metabolic/physiological studies, not taxonomic descriptions. Forcing "Extract ALL" on sparse data produces hallucinations:

```yaml
cell_shape:
  - AUTO:Not%20explicitly%20mentioned
motility:
  - AUTO:Not%20mentioned
```

**Fix**: Use conservative base template for sparse data domains.

## Model and Temperature Effects

### Temperature

Tested on 3 papers with GPT-4o:

| Temperature | Relationships | Accuracy |
|-------------|---------------|----------|
| 0.0 | 34 | 100% |
| 0.1 | 22 | 100% |
| 0.3 | 6 | 100% |

**Finding**: Lower temperature = more relationships, same accuracy.

**Recommendation**: Use temperature 0.0 for production.

### Model comparison

| Model | Relationships | Ground Truth |
|-------|---------------|--------------|
| GPT-4o | 22 | 5/5 (100%) |
| Claude Sonnet 4.5 | 31 | 1/5 (20%) |

**Recommendation**: Use GPT-4o for production extractions.

## Domain-Specific Recommendations

### Chemical utilization
- Use hybrid template with "Extract ALL"
- Papers have dense chemical interaction data
- Production: 1,214 relationships from 24 papers

### Morphology
- Use base template (conservative)
- CMM corpus lacks taxonomic descriptions
- For morphology-rich papers: test IJSEM novel species descriptions

### Growth conditions
- Use hybrid template
- Intermediate data density

## Checklist for New Templates

1. Include inline examples with `exclude` annotation
2. Add comprehensiveness instructions ("Extract ALL", "Be COMPREHENSIVE")
3. Keep examples to 5-8 max
4. Include METPO annotator for phenotype grounding
5. Test on 3 papers before full corpus
6. Validate against ground truth
7. Match optimization level to corpus data density

## Production Templates

Current production-ready templates:

```
templates/
├── chemical_utilization_hybrid.yaml   # 100% accuracy
├── growth_conditions_hybrid.yaml      # Testing complete
├── morphology_template_base.yaml      # Optimal for CMM
├── strain_phenotype_metpo.yaml        # ICBO comparisons
├── strain_phenotype_omp.yaml          # ICBO comparisons
├── strain_phenotype_pato.yaml         # ICBO comparisons
└── strain_phenotype_micro.yaml        # ICBO comparisons
```

See also: [GROUNDING_ANALYSIS.md](GROUNDING_ANALYSIS.md) for annotator configuration.

---

*Consolidated from: SESSION_NOTES.md, HYBRID_TEMPLATE_OPTIMIZATION_GUIDE.md, MORPHOLOGY_EXTRACTION_ANALYSIS.md*
