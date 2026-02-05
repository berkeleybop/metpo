# Why We Created METPO: A Fact-Based Justification

## Executive Summary

METPO was created not because existing microbial phenotype ontologies don't exist, but because **none provide adequate coverage, structural coherence, or are actively maintained** for our use case: annotating microbial ecophysiological trait data from databases like BacDive and BactoTraits for use in KG-Microbe.

---

## The Landscape: Existing Microbial Phenotype Ontologies

### Available Ontologies (from Issue #222 survey)

| Ontology | Domain | Status | Issues |
|----------|--------|--------|--------|
| **MicrO** | Prokaryotic phenotypes, media, assays | Low/unknown activity | No recent updates visible; 103 ROBOT validation errors; last updated 2018 |
| **OMP** | Microbial phenotypes (bacteria, archaea, protists, fungi, viruses) | Production | Last BioPortal upload 2024-03-25; available in OLS |
| **MCO** | Microbial growth/experimental conditions | Production | Initial release 2019; used in RegulonDB |
| **APO** | Ascomycete (fungal) phenotypes | Active | BioPortal 2025-08-12; fungal-focused |
| **FYPO** | Fission yeast phenotypes | Active | Ontobee 2025-05-09; eukaryotic microbe |
| **DDPHENO** | Dictyostelium phenotypes | Active | Amoebozoan; limited bacterial relevance |
| **PHIPO** | Pathogen-host interaction phenotypes | Production | Specific interaction focus |
| **OHMI** | Host-microbiome interactions | Production | Last upload 2019-09-23 |
| **PATO** | General phenotypic qualities | Very active | Cross-species; abstract qualities not specific traits |
| **CMPO** | Cellular microscopy phenotypes | Active | Microscopy-focused |
| **ARO** | Antibiotic resistance | Very active | Narrow domain (AMR genes/mechanisms) |

---

## Our Requirements vs. Available Ontologies

### What We Need:
1. **Bacterial ecophysiological traits** - temperature preferences, pH ranges, NaCl optima, oxygen requirements, cell morphology, metabolic capabilities
2. **Numerical phenotypes** - delta/range/optimum classes for quantitative traits
3. **~250 core classes** covering database benchmarks
4. **Active maintenance** - responsive to literature mining needs
5. **Structural coherence** - clean hierarchies for KG reasoning
6. **ROBOT validation** - no critical errors

### Coverage Analysis (Benchmark Domains)

We evaluated ontologies against domains like:
- Temperature preference (optimum, range, delta)
- pH tolerance (optimum, range, delta)
- NaCl/salinity (optimum, range, delta)
- Oxygen requirements
- Cell morphology
- Metabolic pathways

**From ICBO abstract**: "MicrO covers only 4 of our benchmark domains at ≥80% classes per domain, but has 103 validation errors and hasn't been updated since 2018."

### Structural Coherence Analysis (This Session)

We analyzed sibling coherence between METPO and external ontologies using embedding-based matching and hierarchical structure comparison:

**Results**:
- **Mean coherence: 8.2%** across all ontologies (very low!)
- **Only 6/250 terms (2.4%)** achieved ≥50% structural coherence
- Best case: MCO for NaCl terms (100% coherence for 1 term, 67% for 5 terms)
  - BUT: High semantic distances (0.82-0.95) = poor quality matches
- **No ontology** showed both high coherence AND low semantic distance for substantial term sets

**Ontology Performance**:
| Ontology | Mean Coherence | Terms Analyzed | Match Quality |
|----------|----------------|----------------|---------------|
| MCO | 48.7% | 10 | Poor (0.87 avg dist) |
| OBA | 4.1% | 7 | Poor (0.91) |
| OMP | 3.6% | 3 | Poor (0.80) |
| All others | 0% | 21 | No alignment |

**Interpretation**: METPO's classification structure is **novel** - not well-represented in existing ontologies. We cannot simply import existing hierarchies.

---

## Specific Problems with Candidate Ontologies

### MicrO (Most Promising, But...)
**✓ Pros:**
- Explicitly prokaryotic phenotype & metabolic character focus
- Covers media, assays, experimental conditions

**✗ Cons:**
- **103 ROBOT validation errors** (from abstract)
- **Not updated since 2018** (7 years!)
- **Unknown maintenance status** (Issue #222: "Unknown/low visible recent activity")
- **Only 4/N domains at ≥80% coverage** in our benchmarks

### OMP (Ontology of Microbial Phenotypes)
**✓ Pros:**
- Production status
- Recent update (2024-03-25)
- Broad microbial scope

**✗ Cons:**
- **Only 3.6% structural coherence** with METPO (our analysis)
- **281 matches but mostly poor quality** (distance 0.80+)
- Coverage gaps in numerical phenotypes (delta/range classes)

### MCO (Microbial Conditions Ontology)
**✓ Pros:**
- Good domain fit (growth conditions)
- Best coherence score (48.7%)
- Used in RegulonDB

**✗ Cons:**
- **Poor semantic match quality** (0.87 avg distance)
- **Only 10 terms analyzed** - limited overlap
- Focused on experimental *conditions* not organism *traits*

### PATO (Phenotype And Trait Ontology)
**✓ Pros:**
- Very actively maintained
- High-level phenotypic qualities

**✗ Cons:**
- **Too abstract** - "increased temperature" not "thermophilic"
- **Generic cross-species** - not microbial-specific
- **0% structural coherence** in our analysis

### Other Ontologies:
- **APO, FYPO, DDPHENO**: Eukaryotic microbes (fungi, yeast, amoeba) - not bacterial
- **PHIPO, OHMI**: Interaction phenotypes, not intrinsic traits
- **ARO**: Antibiotic resistance only
- **CMPO**: Microscopy phenotypes only

---

## Why the Low Coherence Matters

Our sibling coherence analysis revealed:

1. **Coverage ≠ Structural Alignment**
   - An ontology might *have terms* for concepts we need (coverage)
   - But those terms might be in **different hierarchical arrangements** (structure)
   - Example: METPO groups all "NaCl optimum" variants under one parent; external ontologies scatter them

2. **Implications for KG-Microbe**:
   - We need coherent hierarchies for **reasoning** ("all thermophiles" queries)
   - We need stable **parent-child relationships** for inference
   - We need **sibling consistency** for clustering similar phenotypes

3. **Low coherence = Cannot Import**:
   - 8.2% mean coherence means we **cannot wholesale import** any existing ontology
   - We'd need to restructure ~92% of mappings - defeating the purpose

---

## METPO's Advantages

### 1. **Pragmatic Scope**
- 250 core classes (manageable, focused)
- Driven by actual database content (BacDive, BactoTraits)
- Coverage optimized for bacterial ecophysiology

### 2. **Literature-Driven Development**
From README: "METPO contributes to and learns from literature mining: if an abstract states 'Microbe X has phenotype Y' but Y lacks representation in METPO, the manual addition of Y to METPO is triggered."

### 3. **KG-Optimized**
- Designed for KG-Microbe integration
- Reification classes for complex relations ("reduction of X to Y")
- Clean hierarchies for SPARQL reasoning
- Uses ChEBI CURIEs externally (doesn't reimport chemicals)

### 4. **Active Maintenance**
- Responsive to use case needs
- ROBOT validation clean (0 errors)
- Integration with OntoGPT pipelines

### 5. **Acknowledges Precedent**
From README: "Annotations like IAO:0000119 (definition source) and skos:closeMatch are used to acknowledge precedent while maintaining simplicity, stability and a focused scope."

We're not **ignoring** existing ontologies - we're **mapping to them** where appropriate while keeping our structure clean.

---

## The Multi-Ontology Problem

### Why Not Just Use Multiple Ontologies Together?

From alignment handoff doc (Section 6):

**The Noise Problem**:
- Huge ontologies add noise
- NCBITaxon (~2.65M terms) matches species names like "thermophilicus" that *look* phenotype-y but aren't trait classes
- Clinical/mammalian ontologies (HP, MP, UBERON) return irrelevant matches
- Chemical ontologies (ChEBI 221K terms) inflate search space

**Empirical Evidence**:
- Initial "all ontologies" approach returned absurd matches (e.g., "vaginal neoplasia" for bacterial morphology)
- OBA-only subset: 33% good matches (<0.9 distance)
- Full corpus: much worse signal-to-noise

**Integration Complexity**:
- Different structural philosophies
- Overlapping/conflicting hierarchies
- Maintenance burden tracking 10+ ontologies
- No single ontology provides >50% high-quality coverage

---

## BioPortal Ontologies (Issue #222 Analysis)

Additional ontologies available on BioPortal but not OLS:

| Ontology | Status | Relevance | Why Not Used |
|----------|--------|-----------|--------------|
| MPO (RIKEN) | Alpha (2014-2020) | Microbial phenotypes | Old (2014); alpha version 0.74; no recent updates |
| OPL | Low-change | Parasite lifecycle | Lifecycle stages, not traits |
| EuPathDB | Active | Eukaryotic pathogens | Eukaryotic focus |
| YPO | Deprecated | Yeast phenotypes | Superseded by APO |

**Conclusion**: No additional BioPortal-only ontologies fill the METPO niche.

---

## Quantitative Summary

### Ontology Landscape Gaps (Fact-Based):

1. **Maintenance Gap**:
   - MicrO: No updates since 2018 (7 years)
   - MPO: Last update 2014-2020 (alpha status)
   - OHMI: Last update 2019

2. **Validation Gap**:
   - MicrO: 103 ROBOT errors
   - METPO: 0 errors

3. **Coverage Gap** (from abstract):
   - MicrO: 4/N domains at ≥80%
   - Needed: All domains at ≥80%

4. **Structural Gap** (from our analysis):
   - Mean coherence: 8.2%
   - High coherence terms: 2.4%
   - Best ontology (MCO): 48.7% but poor match quality

5. **Domain Focus Gap**:
   - Bacterial-specific: Only MicrO (unmaintained), OMP (low coherence)
   - Others: Fungi (APO, FYPO), Generic (PATO), Conditions (MCO), Interactions (PHIPO, OHMI)

---

## Conclusion: Why METPO Was Necessary

**METPO wasn't created because we didn't look at existing ontologies.**

METPO was created because:

1. ✗ **No single ontology** covers bacterial ecophysiological traits adequately (≥80% across all domains)
2. ✗ **Best candidate (MicrO)** has 103 validation errors and 7 years without updates
3. ✗ **Available alternatives** are unmaintained, eukaryote-focused, or structurally incompatible (8.2% mean coherence)
4. ✗ **Multi-ontology integration** introduces noise, conflicts, and maintenance burden
5. ✓ **METPO provides**: Focused scope, clean structure, active maintenance, KG-optimization, and acknowledges precedent via mappings

**We use existing ontologies strategically** (via skos:closeMatch, definition sources) while maintaining structural independence for our knowledge graph use case.

---

## Related Documentation

- **[Merge Scenario Analysis](../../literature_mining/docs/metpo-justification/MERGE_SCENARIO_ANALYSIS.md)** - Empirical evaluation of whether merging MicrO + OMP + PATO could replace METPO (conclusion: no - technical problems and 13% fewer groundings)
- **[MicrO Technical Problems](../../literature_mining/docs/metpo-justification/MICRO_PROBLEMS_ANALYSIS.md)** - Detailed analysis of MicrO's 477 property punning violations and 103 ROBOT errors
- **[Alignment Handoff](../alignment/metpo_alignment_handoff.md)** - ChromaDB semantic alignment pipeline and ontology selection strategy

## References

- ICBO 2025 Abstract: "METPO: A Pragmatic Ontology for Microbial Ecophysiological Traits"
- METPO Alignment Handoff Document (metpo_alignment_handoff.md)
- Issue #222: "revisit other ontologies for definitions"
- Sibling Coherence Analysis (this session): full_coherence_results.csv
- OBA-only validation: oba_matches.csv (~33% good matches, 44% fair, 23% poor)

---

**Last Updated**: 2025-10-27
**Analysis Data**: Based on 250 METPO terms, 13 OLS/BioPortal ontologies, 1250 embedding matches, structural coherence metrics
