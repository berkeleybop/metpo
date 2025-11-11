# Integration Notes for Main Slides

**Quick reference for weaving backup content into main presentation**

---

## Slide 5: "The Gap in the Ontology Landscape"

**Current:** Shows revision dates
**Add lightweight mention:**
> "Beyond outdated revisions, technical issues limit their use: MicrO has 7,130 validation errors and 60 unsatisfiable classes when imported; MPO has strong embeddings but definitions are just label repetitions"

**Backup slide reference:** → Slide 6 for full technical details

---

## Slide 7: Data Sources

**Current:** Shows three sources
**Add:**
> "Integrated into KG-Microbe: 328K nodes, 1.86M edges from **observation-based** phenotypes (not genome predictions)"

**Emphasize word:** "integration" (per Marcin)

---

## Slide 8/9: Embeddings/Mappings  

**Current:** Shows match counts
**Add highlight:**
> "Note: Only 19.6% exact matches - embeddings alone insufficient for precise integration"

**Backup slide reference:** → Slide 2 for distribution details

---

## Slide 13: Methods/Workflow

**Add AI usage transparency:**
> "AI used for: literature extraction (OntoGPT/GPT-4o), definition quality assessment (Claude 3.5). NOT used for: class design, final definitions, hierarchy (all human-curated)"

**Backup slide reference:** → Slide 7 for complete AI usage breakdown

---

## New Backup Slides for Q&A

**Quick answers ready:**
1. **"Do you have qualifier classes?"** → No, fully pre-composed (Slide 4)
2. **"Why not import existing ontologies?"** → 60 unsatisfiable classes, conflicting hierarchies (Slide 3)
3. **"What does 21% grounding mean?"** → Context: extraction rate from abstracts (Slide 9)
4. **"Why can't MicrO convert to semsql?"** → Technical details (Slide 10)
5. **"How does this relate to KG-Microbe paper?"** → We add semantic layer (Slide 5)
6. **"ML requirements?"** → Consistent hierarchies for classification (Slide 4)

---

## Key Stats to Memorize

- **328K nodes, 1.86M edges** (KG-Microbe from 3 sources)
- **255 METPO classes, 3,019 mappings**
- **Only 19.6% exact matches** via embeddings
- **182 excellent matches** (≥0.75 similarity)
- **MicrO: 21% vs METPO: 26%** grounding rate
- **60 unsatisfiable classes** when importing MicrO
- **All observation-based** (not genome predictions)

---

## Marcin's Anticipated Questions - Quick Answers

**Q: Qualifier classes?**
A: No - "facultatively aerobic" is ONE pre-composed class, not "facultative" + "aerobic"

**Q: Why not merge ontologies?**
A: Creates 60 unsatisfiable classes, conflicting hierarchies break ML requirements

**Q: KG-Microbe comparison?**
A: We add semantic harmonization layer on top of their graph construction

**Q: AI usage?**
A: Extraction & quality assessment only; all design/curation human-done

**Q: Definition sources?**
A: Only 15.6% of foreign definitions follow OBO guidelines; we wrote custom ones

**Q: MicrO problems?**
A: 7,130 ROBOT violations, missing critical terms (motile, methylotroph)

---
