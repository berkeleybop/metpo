# Ontology Property Audit Results

Comprehensive audit of label, synonym, and definition properties across non-OLS ontologies.

## Summary

All properties in `sparql/extract_for_embeddings.rq` have been verified against actual ontology files.

### Standard Properties (Used Widely)

✅ **Labels**
- `rdfs:label` - Used by ALL ontologies
- `skos:prefLabel` - Used by SKOS-based ontologies (GMO)

✅ **Synonyms**
- `oboInOwl:hasExactSynonym` - Standard OBO (OMP, BIPON)
- `oboInOwl:hasBroadSynonym` - Standard OBO
- `oboInOwl:hasNarrowSynonym` - Standard OBO
- `oboInOwl:hasRelatedSynonym` - Standard OBO
- `skos:altLabel` - SKOS alternative labels (GMO)

✅ **Definitions**
- `IAO:0000115` - Standard OBO definition property (OMP: 2,110 uses)
- `skos:definition` - SKOS definitions (GMO: 167 uses)
- `rdfs:comment` - Fallback for descriptions (all ontologies)

### Non-Standard Properties (Verified as Used)

⚠️ **BIPON-specific** (non-standard OBO namespace)
- `obo:Synonym` - 617 uses (alternative to oboInOwl properties)
- `obo:Definition` - 158 uses (alternative to IAO:0000115)

⚠️ **FMPM-specific**
- `owl:altLabel` - 152 uses (should be skos:altLabel but owl is used)

⚠️ **N4L-specific**
- `spin:labelTemplate` - 56 uses (template-based labels)

⚠️ **Dublin Core** (rare)
- `dc:title` - D3O: 1 use
- `dcterms:title`, `dc:description`, `dcterms:description` - Minimal use

## Detailed Audit by Ontology

### D3O (309KB, 411 classes)
**Pattern: Simple RDF**
```
rdfs:label:    411 ← Primary labels
rdfs:comment:  409 ← Used for definitions!
dc:title:        1 ← Rare
Synonyms:     NONE
```

### OMP (4.4MB, 2,728 classes)
**Pattern: Standard OBO**
```
rdfs:label:                    2,728 ← Primary labels
IAO:0000115:                   2,110 ← Standard OBO definitions
oboInOwl:hasExactSynonym:        404
rdfs:comment:                    376
oboInOwl:hasNarrowSynonym:       261
oboInOwl:hasRelatedSynonym:      206
oboInOwl:hasBroadSynonym:         21
```

### GMO (615KB, 2,593 classes)
**Pattern: SKOS Heavy**
```
rdfs:label:       2,593 ← Also present
skos:prefLabel:   1,584 ← SKOS preferred labels
skos:altLabel:      504 ← SKOS alternative labels
skos:definition:    167 ← SKOS definitions
rdfs:comment:        48
dcterms:description:  1
dcterms:title:        1
```

### BIPON (3.6MB, 3,073 classes)
**Pattern: Non-standard OBO namespace**
```
rdfs:label:                    3,073 ← Primary labels
obo#Synonym:                     617 ← NON-STANDARD! But verified
oboInOwl:hasRelatedSynonym:      565
oboInOwl:hasExactSynonym:        553
obo#Definition:                  158 ← NON-STANDARD! But verified
rdfs:comment:                     66
oboInOwl:hasBroadSynonym:         41
oboInOwl:hasNarrowSynonym:        39
```

### FMPM (325KB, 155 classes)
**Pattern: OWL instead of SKOS**
```
rdfs:label:   155
owl:altLabel: 152 ← Should be skos:altLabel, but verified as used
```

### N4L (2.8MB, 711 classes)
**Pattern: SPIN templates**
```
rdfs:comment:         982 ← Used for definitions
rdfs:label:           711 ← Primary labels
spin:labelTemplate:    56 ← Template-based labels, verified
```

## Verification Evidence

All properties verified by direct SPARQL queries against ontology files:

```bash
# obo:Synonym verification (BIPON)
?s = <http://purl.obolibrary.org/obo/CHEBI_28846>
?p = <http://purl.obolibrary.org/obo#Synonym>
?o = "2'-Deoxycytidine 5'-diphosphate"

# obo:Definition verification (BIPON)
?s = <http://www.semanticweb.org/BiPON/BiPON_00001404>
?p = <http://purl.obolibrary.org/obo#Definition>
?o = "Recovery of transcription process next to a pause event."

# owl:altLabel verification (FMPM)
?s = <urn:absolute:FMPM#Cured_ham>
?p = <http://www.w3.org/2002/07/owl#altLabel>
?o = "Ham"

# spin:labelTemplate verification (N4L)
?s = <http://doi.org/10.1601/RangeOfGrowthCondition>
?p = <http://spinrdf.org/spin#labelTemplate>
?o = "T14: Strain has observation..."

# Standard IAO definition (OMP)
?s = <http://purl.obolibrary.org/obo/OMP_0008004>
?p = IAO:0000115
?o = "An endospore internal structure phenotype..."

# Standard oboInOwl synonym (OMP)
?s = <http://purl.obolibrary.org/obo/GO_0048519>
?p = oboInOwl:hasExactSynonym
?o = "down regulation of biological process"

# Standard SKOS (GMO)
?s = <http://purl.jp/bio/10/gmo/GMO_001493>
?p = skos:prefLabel
?o = "Malachite green solution"@en
```

## SPARQL Query Coverage

The current query in `sparql/extract_for_embeddings.rq` includes:

### Namespaces
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX IAO: <http://purl.obolibrary.org/obo/IAO_>
PREFIX obo: <http://purl.obolibrary.org/obo#>
PREFIX spin: <http://spinrdf.org/spin#>
```

### Label Properties
```sparql
rdfs:label          ← Universal
skos:prefLabel      ← GMO
dc:title            ← D3O (1 use)
dcterms:title       ← Rare
spin:labelTemplate  ← N4L
```

### Synonym Properties
```sparql
oboInOwl:hasExactSynonym    ← Standard OBO
oboInOwl:hasBroadSynonym    ← Standard OBO
oboInOwl:hasNarrowSynonym   ← Standard OBO
oboInOwl:hasRelatedSynonym  ← Standard OBO
skos:altLabel               ← GMO
owl:altLabel                ← FMPM
obo:Synonym                 ← BIPON (non-standard)
```

### Definition Properties
```sparql
IAO:0000115         ← Standard OBO definition
skos:definition     ← GMO
rdfs:comment        ← Universal fallback
dc:description      ← Rare
dcterms:description ← Rare
obo:Definition      ← BIPON (non-standard)
```

## Recommendations

1. **Query is comprehensive** - Covers all patterns found in 13 non-OLS ontologies
2. **Standards-compliant** - Prioritizes IAO, oboInOwl, SKOS
3. **Pragmatic** - Includes non-standard properties where actually used (BIPON, FMPM, N4L)
4. **Fallbacks included** - Uses rdfs:comment when standard definitions absent (D3O)

## Testing

To verify property coverage for a specific ontology:

```bash
# Check label properties
robot query --input non-ols/D3O.owl --query <(cat << EOF
SELECT DISTINCT ?property (COUNT(*) AS ?count) WHERE {
  ?s ?property ?o
  FILTER(CONTAINS(LCASE(STR(?property)), "label"))
} GROUP BY ?property ORDER BY DESC(?count)
EOF
) results.tsv

# Check synonym properties
# Check definition properties
# (Replace "label" with "synonym" or "definition")
```
