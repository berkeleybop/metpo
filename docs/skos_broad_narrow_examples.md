# SKOS broadMatch and narrowMatch Examples

**Source:** W3C SKOS Specification

## Key Insight

`skos:broadMatch` and `skos:narrowMatch` express **hierarchical scope relationships**, not similarity strength.

**Cannot be determined from embedding distance** - requires knowledge of concept hierarchy.

## Public Examples

### Example 1: Platypus (W3C SKOS Primer)

```turtle
ex1:platypus skos:broadMatch ex2:eggLayingAnimals .
```

**Interpretation:** "Platypus" is a **subset** of "egg-laying animals"
- Direction: narrow → broad
- Relationship: platypus ⊂ egg-laying animals

### Example 2: Apple Variety (SSSOM Documentation)

```
subject_id: KF_FOOD:F004
subject_label: braeburn
predicate_id: skos:broadMatch
object_id: FOODON:00002473
object_label: apple whole
```

**Interpretation:** "Braeburn" is a **subset** of "apple whole"
- Direction: narrow → broad
- Relationship: braeburn ⊂ apple

## Contrast with Similarity Predicates

**Hierarchical (require structural knowledge):**
- `skos:broadMatch` - subject is subset of object
- `skos:narrowMatch` - subject is superset of object

**Similarity (can use distance):**
- `skos:exactMatch` - interchangeable (distance < 0.10)
- `skos:closeMatch` - highly similar (distance < 0.35)
- `skos:relatedMatch` - moderately similar (distance ≥ 0.35)

## References

- [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- [W3C SKOS Primer](https://www.w3.org/TR/skos-primer/)
