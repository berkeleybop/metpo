# OLS Submission Fields: Complete Guide

This guide explains each field in the OLS ontology submission spreadsheet and how to fill it out correctly.

## Essential Fields (Start Here)

### preferredPrefix
**Type:** Single value (string)  
**Required:** Yes  
**Description:** A short identifier for your ontology in the OLS frontend  
**Requirements:**
- Must be lowercase
- At least 5 characters long
- Must be unique across all of OLS
- Examples: `cellont`, `phenoont`, `diseaseont`

**Purpose:** This is how users will refer to your ontology throughout OLS. Choose carefully as it's hard to change later.

---

### ontology_purl
**Type:** Single value (URL)  
**Required:** Yes  
**Description:** The stable, permanent URL where OLS will download your ontology  
**Requirements:**
- Must be publicly accessible
- Should be a PURL (Persistent URL) or stable location
- Can use protocols: `http://`, `https://`, `ftp://`, or `file://` (for local testing)
- Examples: 
  - `http://purl.obolibrary.org/obo/myont.owl`
  - `https://github.com/myorg/myont/releases/latest/download/myont.owl`

**Purpose:** OLS checks this URL regularly (nightly) to detect new releases and automatically update your ontology. This is your ontology's "home address" in OLS.

---

## Basic Metadata Fields

### title
**Type:** Single value  
**Required:** Yes  
**Description:** The full name of your ontology

**Note:** This will be overridden if your ontology file contains a `dc:title` annotation in the ontology header. If your OWL file has this annotation, OLS will use that instead.

**Example:** "Human Phenotype Ontology"

---

### description
**Type:** Single value (text)  
**Required:** Recommended  
**Description:** A clear description explaining what your ontology covers

**Note:** Like title, this will be overridden if your ontology contains a `dc:description` annotation.

**Purpose:** Displayed in OLS as part of the summary overview. Helps users understand if your ontology is relevant to their needs.

**Example:** "A structured controlled vocabulary for the phenotypic features encountered in human disease."

---

### uri
**Type:** Single value (URI)  
**Required:** Yes  
**Description:** The canonical ontology URI used to identify your ontology (the ontology IRI)

**Important:** This is different from `ontology_purl`!
- `uri` is the **logical identifier** of your ontology (what it "is")
- `ontology_purl` is where OLS **downloads** it from (where it "lives")

**Example:** 
- `uri`: `http://purl.obolibrary.org/obo/hp.owl`
- `ontology_purl`: `http://purl.obolibrary.org/obo/hp.owl` (often the same, but conceptually different)

---

### creator
**Type:** List (can have multiple entries)  
**Required:** Recommended  
**Description:** The creators/developers of the ontology

**Purpose:** Displayed in OLS as part of the summary overview for proper attribution.

**Format:** Provide as a comma-separated list or on separate rows in the spreadsheet  
**Example:** "Jane Doe, John Smith, Mary Johnson"

---

### homepage
**Type:** Single value (URL)  
**Required:** Recommended  
**Description:** Your ontology's project website or documentation page

**Purpose:** OLS provides a link to this page so users can learn more about your ontology project.

**Example:** `https://github.com/myorg/my-ontology`

---

### mailing_list
**Type:** Single value (email address)  
**Required:** Optional  
**Description:** Email address where users can contact you with questions

**Purpose:** Helps users reach you for support or collaboration.

**Example:** `my-ontology-users@googlegroups.com`

---

## Technical Configuration Fields

### is_foundry
**Type:** Boolean value  
**Options:** `true` or `false`  
**Required:** Yes  
**Description:** Set to `true` if this is an OBO Foundry ontology, otherwise `false`

**Purpose:** When set to `true`, OLS automatically configures default settings for:
- Synonym properties
- Definition properties  
- Other OBO-standard annotations

**When to use `true`:** Only if your ontology is registered with OBO Foundry or follows OBO conventions  
**When to use `false`:** For custom ontologies, domain-specific vocabularies, or non-OBO ontologies

---

### reasoner
**Type:** Single value  
**Options:** `OWL2`, `EL`, or `NONE`  
**Required:** Yes (but can ask for help)  
**Description:** Which reasoner OLS should use to classify your ontology

**Options explained:**
- **OWL2**: Uses HermiT reasoner - for ontologies with complex OWL 2 features
- **EL**: Uses ELK reasoner - for large ontologies using the EL profile (faster, more scalable)
- **NONE**: No reasoning - for simple ontologies or vocabularies

**How to choose:**
- If you use Protégé, check what reasoner you use there
- If you're not sure, start with `EL` or contact OLS team for help
- Large ontologies (>10,000 terms) often benefit from `EL`

**Purpose:** OLS uses this to compute inferred class hierarchies and validate your ontology.

---

### base_uri
**Type:** List or single value  
**Required:** Yes  
**Description:** The base URI(s) that distinguish your ontology's terms from imported terms

**Purpose:** OLS uses this to identify which terms "belong" to your ontology vs. which are imported from other ontologies. Critical for proper display and indexing.

**Example:** 
- If your term IRIs look like `http://purl.obolibrary.org/obo/MYONT_0000001`
- Your base_uri should be `http://purl.obolibrary.org/obo/MYONT_`

**Multiple base URIs:** If your ontology uses multiple prefixes (e.g., `MYONT_` and `MYONTO_`), list both:
```
http://purl.obolibrary.org/obo/MYONT_
http://purl.obolibrary.org/obo/MYONTO_
```

---

## Property Configuration Fields

These fields tell OLS which annotation properties in your ontology serve specific purposes. They're essential for proper indexing and display.

### label_property
**Type:** List (URIs)  
**Required:** Recommended  
**Description:** URI(s) of properties used to provide labels/names for terms

**Default:** If not specified, OLS uses `rdfs:label` and `skos:prefLabel`

**Purpose:** OLS indexes these to make terms searchable by their names. If your ontology uses multiple languages, OLS defaults to English labels.

**Common values:**
```
http://www.w3.org/2000/01/rdf-schema#label
http://www.w3.org/2004/02/skos/core#prefLabel
http://www.geneontology.org/formats/oboInOwl#hasExactSynonym
```

**When to customize:** If your ontology uses non-standard annotation properties for labels.

---

### definition_property
**Type:** List (URIs)  
**Required:** Recommended  
**Description:** URI(s) of properties used to provide term definitions

**Default:** If not specified, OLS looks for common definition properties

**Purpose:** OLS indexes definitions to make terms searchable by their meaning/description.

**Common values:**
```
http://purl.obolibrary.org/obo/IAO_0000115
http://www.w3.org/2004/02/skos/core#definition
```

**OBO ontologies typically use:** `http://purl.obolibrary.org/obo/IAO_0000115`

---

### synonym_property
**Type:** List (URIs)  
**Required:** Recommended  
**Description:** URI(s) of properties that indicate a term is a synonym for another term

**Purpose:** OLS indexes synonyms to improve search - users can find terms using alternative names.

**Common values for OBO ontologies:**
```
http://www.geneontology.org/formats/oboInOwl#hasExactSynonym
http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym
http://www.geneontology.org/formats/oboInOwl#hasNarrowSynonym
http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym
```

**For SKOS vocabularies:**
```
http://www.w3.org/2004/02/skos/core#altLabel
```

---

### hierarchical_property
**Type:** List (URIs)  
**Required:** Optional  
**Description:** URI(s) of properties used to construct hierarchical tree views

**Default:** By default, OLS renders trees using `rdfs:subClassOf` (is-a) relationships

**Purpose:** If your ontology uses other relationships that should appear in the tree view (like part-of, has-part, develops-from), specify them here.

**Common values:**
```
http://purl.obolibrary.org/obo/BFO_0000050  (part of)
http://purl.obolibrary.org/obo/RO_0002202  (develops from)
```

**Example use case:** In anatomy ontologies, you might want both "is-a" and "part-of" relationships visible in the tree.

---

### hidden_property
**Type:** List (URIs)  
**Required:** Optional  
**Description:** Properties to ignore when rendering the ontology in OLS

**Purpose:** Some ontologies have internal/administrative properties that shouldn't be displayed to end users. List them here.

**Example use cases:**
- Workflow metadata (creation dates, internal IDs)
- Properties used only during ontology development
- Deprecated annotation properties

---

### oboSlims
**Type:** Boolean value  
**Options:** `true` or `false`  
**Required:** Only for OBO ontologies  
**Description:** Whether your ontology uses OBO slims/subsets annotations

**Purpose:** OBO slims are curated subsets of terms (like "GO slim"). If `true`, OLS will index and display subset information.

**When to use `true`:** If your ontology has terms annotated with `oboInOwl:inSubset`  
**When to use `false`:** For non-OBO ontologies or OBO ontologies without slims

---

## Field Summary by Priority

### Must Have (Required)
1. **preferredPrefix** - Your ontology's short name in OLS
2. **ontology_purl** - Where OLS downloads your ontology from
3. **uri** - Your ontology's canonical identifier
4. **is_foundry** - Whether you follow OBO conventions
5. **reasoner** - Which reasoner to use (or NONE)
6. **base_uri** - Your ontology's namespace(s)

### Should Have (Strongly Recommended)
7. **title** - Full name (unless in your OWL file)
8. **description** - What your ontology covers (unless in your OWL file)
9. **creator** - Attribution for developers
10. **homepage** - Project website
11. **label_property** - How terms are labeled
12. **definition_property** - How terms are defined
13. **synonym_property** - How synonyms are indicated

### Nice to Have (Optional)
14. **mailing_list** - User contact email
15. **hierarchical_property** - Additional tree relationships
16. **hidden_property** - Properties to hide
17. **oboSlims** - If using OBO subsets

---

## Common Pitfalls and Tips

### Pitfall 1: Confusing `uri` and `ontology_purl`
- **uri**: What your ontology IS (its identity)
- **ontology_purl**: Where your ontology LIVES (download location)
- They can be the same URL, but serve different conceptual purposes

### Pitfall 2: Wrong base_uri
If OLS shows imported terms as if they're yours (or vice versa), your `base_uri` is wrong. It should match only YOUR term prefixes.

### Pitfall 3: Forgetting to set is_foundry
If you're an OBO ontology, set `is_foundry: true` to get automatic defaults. If not, set it to `false` and configure property URIs manually.

### Pitfall 4: Unstable ontology_purl
OLS checks this URL regularly. If it changes or becomes unavailable, your ontology will fail to update. Use PURLs or stable release URLs.

### Tip 1: Check existing OLS ontologies
Browse https://www.ebi.ac.uk/ols4/ontologies to see how similar ontologies are configured.

### Tip 2: Test locally first
If using `file://` paths, test your configuration before using a public URL.

### Tip 3: Use standard OBO properties
If you're creating a new ontology and want good OLS integration, use standard OBO annotation properties (IAO_0000115 for definitions, etc.). This makes configuration easier.

### Tip 4: Ask for help with the reasoner
If you don't know which reasoner to use, just say so in your submission. The OLS team can analyze your ontology and recommend the right one.

---

## Example: Complete Submission

Here's what a filled-out submission might look like:

```
preferredPrefix: phenoont
title: Phenotype Ontology
uri: http://purl.obolibrary.org/obo/pheno.owl
description: An ontology for describing phenotypes across multiple species
ontology_purl: http://purl.obolibrary.org/obo/pheno.owl
creator: Jane Doe, Phenotype Consortium
homepage: https://github.com/phenotype-ontology/pheno
mailing_list: pheno-discuss@googlegroups.com
is_foundry: true
reasoner: EL
base_uri: http://purl.obolibrary.org/obo/PHENO_
label_property: http://www.w3.org/2000/01/rdf-schema#label
definition_property: http://purl.obolibrary.org/obo/IAO_0000115
synonym_property: http://www.geneontology.org/formats/oboInOwl#hasExactSynonym, http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym
hierarchical_property: http://purl.obolibrary.org/obo/BFO_0000050
oboSlims: false
```

---

## After Submission

Once you submit your completed spreadsheet:

1. **Via GitHub:** Create an issue at https://github.com/EBISPOT/ols4/issues using the "Add a new ontology" template
2. **Via Email:** Send to ols-submission@ebi.ac.uk

The OLS team will review your submission, may ask clarifying questions, and configure your ontology. Expect response time of several weeks depending on their workload.