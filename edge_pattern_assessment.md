# Edge Pattern Semantic Assessment

Assessment of 65 unique edge patterns in kg-microbe using semantic understanding of Biolink Model.

## Legend
- ✅ **Semantically valid** - appropriate subject/predicate/object combination
- ⚠️ **Questionable** - technically valid but semantically odd or ambiguous
- ❌ **Invalid** - violates semantic expectations or constraints
- 🔧 **Data quality** - missing/unknown categories prevent assessment
- 🔽 **Lower priority** - issues exist but fixing is lower priority

---

## High-Volume Patterns (>10,000 edges)

### 🔽 `assay --assesses--> organism` (522,399 edges)
**Pattern:** `PhenotypicQuality (assay) --assesses--> OrganismTaxon`
- **Note:** Assays typically assess qualities/phenotypes OF organisms rather than organisms directly
- **Current usage acceptable** as shorthand
- **Impact:** 404,550 (bacdive) + 117,849 (bacdive)

### ✅ `organism --consumes--> chemical` (429,233 edges)
**Pattern:** `OrganismTaxon --consumes--> ChemicalEntity`
- **Valid:** Organisms consume chemical substances
- Covers: bacdive (260,019 + 132,698), madin_etal (36,816)

### ✅ `organism --subclass_of--> organism` (172,761 edges)
**Pattern:** `OrganismTaxon (strain) --subclass_of--> OrganismTaxon (NCBITaxon)`
- **Valid:** Strains represent strain types, making this an ontological subclass relationship
- **Impact:** 159,751 (bacdive) + 13,010 with unknown object (bacdive)

### ❌ `organism --capable_of--> quality` (186,197 edges)
**Pattern:** `OrganismTaxon --capable_of--> PhenotypicQuality (EC codes)`
- **Issue:** `capable_of` requires process/activity as object, not quality
- **Root cause:** EC codes miscategorized as PhenotypicQuality (should be MolecularActivity/BiologicalProcess)
- **See:** Issue #438

### 🔽 `organism --has_phenotype--> quality` (209,916 edges)
**Pattern:** `OrganismTaxon --has_phenotype--> PhenotypicQuality (METPO)`
- **Valid:** Canonical pattern for phenotype annotation
- **Note:** Not ideal but acceptable, fixing is lower priority
- Covers: bacdive (92,898 + 26,160), bactotraits (90,768)

### 🔧 `organism --has_phenotype--> (empty)` (44,081 edges)
**Pattern:** `OrganismTaxon --has_phenotype--> (empty category) METPO`
- **Issue:** Missing category on METPO nodes
- **See:** Issue #439

### ✅ `environment --location_of--> organism` (168,375 edges)
**Pattern:** `EnvironmentalFeature --location_of--> OrganismTaxon`
- **Valid:** Environments are locations where organisms are found
- Covers: isolation_source, ENVO, UBERON nodes

### ❌ `organism --occurs_in--> medium` (52,995 edges)
**Pattern:** `OrganismTaxon --occurs_in--> ChemicalEntity (medium)`
- **Issue:** Organisms don't "occur in" media; *growth processes* occur in media
- **Should be:** `GrowthProcess --occurs_in--> medium` with `organism --capable_of--> GrowthProcess`
- **See:** Issue #440

### ✅ `organism --associated_with_sensitivity_to--> chemical` (12,518 edges)
**Pattern:** `OrganismTaxon --associated_with_sensitivity_to--> ChemicalEntity`
- **Valid:** Organisms can be sensitive to chemicals (antimicrobials, etc.)

### ✅ `organism --associated_with_resistance_to--> chemical` (10,297 edges)
**Pattern:** `OrganismTaxon --associated_with_resistance_to--> ChemicalEntity`
- **Valid:** Organisms can be resistant to chemicals
- **Note:** Predicate not in standard Biolink Model but semantically sound

### ⚠️ `organism --produces--> chemical` (12,523 edges)
**Pattern:** `OrganismTaxon --produces--> ChemicalEntity/ChemicalSubstance`
- **Issue:** `produces` not in Biolink Model
- **Should be:** `has_output` (standard predicate)
- **Semantically valid:** Organisms do produce chemical outputs

---

## Medium-Volume Patterns (1,000-10,000 edges)

### 🔧 `(unknown) ENVO --location_of--> organism` (14,888 edges)
**Pattern:** `(unknown category) ENVO --location_of--> OrganismTaxon`
- **Issue:** Missing category on ENVO environmental nodes
- **Should be:** `EnvironmentalFeature`

### 🔧 `(empty) isolation_source --location_of--> organism` (6,775 edges)
**Pattern:** `(empty) isolation_source --location_of--> OrganismTaxon`
- **Issue:** Missing category
- **Should be:** `EnvironmentalFeature`

### ✅ `organism --capable_of--> process` (5,723 edges)
**Pattern:** `OrganismTaxon --capable_of--> BiologicalProcess`
- **Valid:** Organisms are capable of biological processes
- Covers: pathways (4,407), GO terms (1,316)

### ⚠️ `organism --has_phenotype--> quality` (2,676 edges)
**Pattern:** `OrganismTaxon --has_phenotype--> PhenotypicQuality (pathogen)`
- **Issue:** "pathogen" prefix suggests this is a classification/role, not intrinsic phenotype
- **Should clarify:** Is this a categorical assignment or a phenotypic quality?

### 🔧 `organism --capable_of--> (empty)` (1,770 edges)
**Pattern:** `OrganismTaxon --capable_of--> (empty) METPO`
- **Issue:** Missing category on capability objects
- **Ambiguous:** If METPO terms are qualities (current bacdive) or processes

### 🔧 `(unknown) NCBITaxon --has_phenotype--> quality` (1,208 edges)
**Pattern:** `(unknown) NCBITaxon --has_phenotype--> PhenotypicQuality`
- **Issue:** Missing category on organism nodes
- **Should be:** `OrganismTaxon`

---

## Low-Volume Patterns (<1,000 edges)

### ⚠️ `environment CHEBI --location_of--> organism` (910 edges)
**Pattern:** `EnvironmentalFeature (CHEBI) --location_of--> OrganismTaxon`
- **Issue:** CHEBI chemicals categorized as EnvironmentalFeature
- **Semantically odd:** Chemicals aren't typically "environments" unless referring to chemical habitats

### ❌ `chemical --occurs_in--> assay` (340 edges)
**Pattern:** `ChemicalEntity --occurs_in--> PhenotypicQuality (assay)`
- **Issue:** Chemicals don't "occur in" assays; they're *used in* or *consumed by* assays
- **Should be:** `assay --has_input--> chemical` or `assay --uses--> chemical`

### ⚠️ `environment NCBITaxon --location_of--> organism` (624 edges)
**Pattern:** `EnvironmentalFeature (NCBITaxon) --location_of--> OrganismTaxon`
- **Issue:** Organisms (NCBITaxon) categorized as EnvironmentalFeature
- **Probably wrong:** Unless modeling symbiotic relationships where one organism is habitat for another

### ✅ `chemical --has_chemical_role--> role` (357 edges)
**Pattern:** `ChemicalEntity --has_chemical_role--> ChemicalRole`
- **Valid:** Standard chemical role annotation

### 🔧 `(unknown) PATO --location_of--> organism` (569 edges)
**Pattern:** `(unknown) PATO --location_of--> OrganismTaxon`
- **Issue:** PATO terms (qualities) used as locations
- **Problematic:** Qualities aren't locations

### ❌ `enzyme/quality --is_assessed_by--> assay` (112 edges)
**Pattern:** `EC/PhenotypicQuality --is_assessed_by--> assay`
- **Issue:** `is_assessed_by` not in Biolink Model
- **Semantic direction:** Seems backwards from `assay --assesses--> quality`

### 🔽 `enzyme/quality --consumes--> chemical` (47 edges)
**Pattern:** `EC (as Enzyme/Quality) --consumes--> chemical`
- **Issue:** Enzymes don't consume; *enzymatic processes* consume substrates
- **Should be:** `EnzymaticActivity --has_input--> chemical`
- **Lower priority:** Small number of edges

### 🔧 Multiple `(unknown)` patterns
- Various patterns with unknown categories prevent proper assessment
- All need category assignment

---

## Summary by Validity

### ✅ **Clearly Valid** (19 patterns, ~1.1M edges)
- organism --consumes--> chemical
- organism --has_phenotype--> quality (when categories present)
- environment --location_of--> organism
- organism --capable_of--> process
- organism --associated_with_[sensitivity/resistance]_to--> chemical
- chemical --has_chemical_role--> role
- organism --subclass_of--> organism

### ❌ **Invalid - High Priority** (3 patterns, ~239K edges)
- organism --capable_of--> quality (should be process) #438
- organism --occurs_in--> medium (should be process) #440
- chemical --occurs_in--> assay (wrong direction/predicate)

### ❌ **Invalid - Lower Priority** (1 pattern, 112 edges)
- enzyme --is_assessed_by--> assay (non-standard predicate)

### ⚠️ **Questionable** (5 patterns, ~15K edges)
- organism --produces--> chemical (valid semantics, wrong predicate name)
- organism --has_phenotype--> pathogen (classification vs. phenotype)
- environment (chemical) --location_of--> organism (category mismatch)
- environment (organism) --location_of--> organism (category mismatch)
- PATO --location_of--> organism (quality as location)

### 🔽 **Lower Priority Issues** (3 patterns, ~570K edges)
- assay --assesses--> organism (acceptable shorthand)
- organism --has_phenotype--> quality (not ideal but acceptable)
- enzyme --consumes--> chemical (low volume)

### 🔧 **Data Quality Issues** (33 patterns, ~85K edges)
- All patterns with (unknown) or (empty) categories
- Cannot assess semantics without knowing entity types

---

## Recommendations

### Priority 1: Fix High-Impact Invalid Patterns
1. **Organism-medium relationship** (53K edges): Use different predicate or add process nodes → Issue #440
2. **EC code categorization** (186K edges): Recategorize as processes, fix capable_of range → Issue #438
3. **Chemical-assay relationship** (340 edges): Reverse direction or change predicate

### Priority 2: Resolve Ambiguities
1. **Produces predicate** (13K edges): Map to standard `has_output`
2. **Pathogen phenotype** (3K edges): Clarify semantic intent
3. **CHEBI/NCBITaxon as EnvironmentalFeature**: Review categorization

### Priority 3: Fix Data Quality
1. Assign categories to all (unknown) and (empty) nodes → Issue #439
2. Review PATO terms used as locations
3. Add missing categories to ENVO, isolation_source nodes

### Priority 4: Add Missing Predicates
1. Request `associated_with_resistance_to` be added to Biolink Model
2. Consider domain-specific predicates like `cultured_in` for growth media
