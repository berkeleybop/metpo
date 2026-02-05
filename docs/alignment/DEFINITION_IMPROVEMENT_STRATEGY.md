# METPO Definition Improvement Strategy

**Last Updated:** 2025-11-15

---

## OBO Foundry Definition Writing Guidelines

We follow the **Seppälä-Ruttenberg-Smith** definition writing guidelines (OBO Foundry Principle 6).

### Core Principles

1. **Genus-differentia form**: "A [genus] that [differentia]"
2. **Genus proximus**: Use the parent class as genus (or closely related)
3. **Necessary conditions**: Each part must be necessary
4. **No circularity**: Don't use the term being defined
5. **No examples**: Avoid "such as", "e.g." - examples belong in subclass labels, not definitions
6. **No generalizing**: Avoid "usually", "generally", "typically"
7. **Length**: 50-200 characters (concise but complete)
8. **No redundancy**: Don't create long-winded reiterations of parent class + self label
9. **Use rdfs:comment for elaboration**: Additional context, examples, and explanations go in comments, not definitions

### METPO-Specific Requirement

**Always base definitions on METPO parent classes**, not foreign ontology parent classes. When adapting definitions from other ontologies, we must:
- Replace foreign genus with METPO parent class
- Preserve the differentia (distinguishing characteristics)
- Maintain fidelity to source while conforming to METPO hierarchy

**Example:**
```
Foreign ontology: "A process that generates energy through oxidation"
METPO parent: "metabolic process"
METPO definition: "A metabolic process that generates energy through oxidation"
```

### When NOT to Write Definitions

**Skip definitions for these cases:**

1. **Fully defined by logical axioms**
   - Example: "minimum temperature 20°C, maximum temperature 30°C"
   - The OWL restrictions already provide complete semantics
   - A textual definition would just be redundant prose

2. **Observation classes (defer for now)**
   - Focus on phenotype/quality classes first
   - Observation classes can be added later once patterns are clear
   - Example: "temperature optimum observation" - skip initially

3. **Classes where definition = parent label + self label**
   - If all you can say is "A [parent] that is [self label]", skip it
   - Example: "oval shaped" child of "cell shape" - if definition is just "A cell shape that is oval", skip
   - Exception: If there's meaningful differentia to add (size ranges, specific characteristics)

4. **Highly specific leaf nodes with no sibling classes**
   - If it's the only child and adds no new information, consider if class is even needed
   - May be candidate for removal rather than definition

**Use rdfs:comment instead of definition when:**
- You want to provide examples → examples belong in comments
- You want to add historical context → comments
- You want to explain usage notes → comments
- You want to clarify scope → comments
- You want to elaborate beyond the essential definition → comments

---

## Iterative Definition Strategy

**This is inherently an iterative process.** Don't try to define all 255 terms at once.

### Phase 1: Find Near-Terminal Parents with Well-Defined Children

**Strategy:**
1. Identify near-terminal classes (1-2 levels above leaves) where most children have definitions
2. Analyze the pattern in child definitions
3. Use the pattern to construct definitions for remaining children (stragglers)
4. Use the pattern to improve/validate the parent definition

**Example workflow:**
```bash
# Find classes with children that mostly have definitions
# (Script to be developed: analyze-definition-coverage-by-subtree)

# Expected output:
# Parent: "trophic type" (80% of children defined)
# Children with definitions: 16/20
# Stragglers: "mixotrophic", "lithoheterotrophic", "photolithoautotrophic", "organoheterotrophic"
# Common pattern: "A trophic type characterized by [energy source] and [carbon source]"
```

**Benefits of this approach:**
- **Consistency**: Sibling classes have similar definition structure
- **Efficiency**: Pattern-based definition writing is faster
- **Quality**: Easier to validate when definitions follow same template
- **Stragglers become obvious**: Missing definitions stand out against siblings

### Phase 2: Iterative Refinement

**Round 1: Top-down (root → leaves)**
1. Define root classes (material entity, quality, process, etc.)
2. Define major branches (trophic type, cell shape, temperature phenotype)
3. Identify patterns in each branch

**Round 2: Bottom-up (leaves → root)**
1. Define leaf nodes using external sources (OMP, PATO, GO)
2. Observe patterns emerging in sibling groups
3. Refine parent definitions based on child patterns
4. Fill in stragglers using sibling patterns

**Round 3: Pattern validation**
1. Group classes by parent
2. Check definition consistency within groups
3. Identify outliers (definitions that don't follow group pattern)
4. Either fix outlier or document why it's different (rdfs:comment)

**Round 4: Decide on skips**
1. Identify classes that are fully defined by axioms
2. Identify observation classes to defer
3. Identify redundant leaf nodes
4. Mark these as "definition intentionally omitted" with reason in comment

### Phase 3: Pattern Templates by Parent Class

As patterns emerge, document them as templates:

**Example pattern library:**

```markdown
## Trophic Type Pattern
Template: "A trophic type characterized by the use of [energy source] as energy source and [carbon source] as carbon source."

Examples:
- chemolithotrophic: "...inorganic compounds...CO2..."
- photoautotrophic: "...light...CO2..."
- organoheterotrophic: "...organic compounds...organic compounds..."

## Cell Shape Pattern
Template: "A cell shape characterized by [geometric description] appearance."

Examples:
- bacillus shaped: "...rod-like..."
- coccus shaped: "...spherical..."
- helical shaped: "...spiral or helical..."

## Temperature Phenotype Pattern
Template: "A temperature phenotype characterized by optimal growth at [temperature description]."

Examples:
- thermophilic: "...high temperatures (45-80°C)..."
- psychrophilic: "...low temperatures (0-20°C)..."
```

---

## Definition Sources (High to Low Value)

### Tier 1: METPO Sheet and Undergraduate Contributions

**Already in METPO:**
- `src/templates/metpo_sheet_improved.tsv` - Current definitions and attributions
- 87 undergraduate-contributed definitions (Anthea Guo, Jed Kim-Ozaeta, Luke Wang)
- See: `docs/UNDERGRADUATE_DEFINITION_ATTRIBUTIONS.md`

### Tier 2: ChromaDB Embeddings (OLS + Custom Ontologies)

**ChromaDB collection:** `data/chromadb/chroma_ols20_nonols4/`
- 452,942 embeddings from OLS ontologies + custom sources
- Retrieved via `chromadb-semantic-mapper` tool
- Latest mappings: `data/mappings/metpo_mappings.sssom.tsv`

**Sweet spot ontologies** (best domain alignment):
1. **OMP** (Ontology of Microbial Phenotypes) - 1,131 mappings, mean similarity 0.834
2. **micro** (Micromorphological Traits) - 966 mappings, mean 0.820
3. **PATO** (Phenotype and Trait Ontology) - 187 mappings, mean 0.817
4. **ECOCORE** (Evidence & Conclusion Ontology) - 328 mappings, mean 0.843
5. **GO** (Gene Ontology) - 297 mappings, mean 0.804
6. **FLOPO** (Flower Phenotype Ontology) - 237 mappings, mean 0.817

See: `docs/chromadb_semantic_mapper.md` for full ontology performance analysis

### Tier 3: OLS and BioPortal Search Results

**Previous searches:**
- `data/ontology_assessments/phase1_high_quality_matches.tsv` (620KB)
- Label-based exact/fuzzy matching
- Good complement to embedding-based approach

**How to get definitions from matched terms:**
- Use OLS API: `https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/{encoded_iri}`
- Use BioPortal API: `https://data.biomedical.ontology.org/ontologies/{ontology}/classes/{encoded_iri}`
- Or extract from ChromaDB metadata (already embedded)

### Tier 4: KG-Microbe Sources (Limited Success)

**BacDive, BactoTraits, Madin:**
- BactoTraits Table 1: ✅ 80 trait descriptions extracted (`data/bactotraits/table1_extracted.tsv`)
- Madin et al.: ⚠️ Need to extract Table 1 + Supplementary Table S1
- BacDive: ❌ Paper focuses on data model, not definitions

**Status:** These provide trait descriptions but NOT formal OBO definitions. Good for understanding domain, not for direct definition import.

See: `docs/PDF_DEFINITION_LEADS.md`

### Tier 5: Web-Resolvable Sources (To Be Developed)

**Online textbooks (OpenStax, etc.):**
- ⚠️ Tend to be introductory or healthcare-oriented
- May lack precision needed for ontology definitions
- Could be used for general terms, must cite properly

**Programmatic search strategies (see below):**
- Wikidata SPARQL
- DBpedia
- Semantic Scholar API
- PubMed/Europe PMC

---

## Programmatic Web Search Strategies

### Wikidata SPARQL Queries

**Wikidata Query Service:** https://query.wikidata.org/

**Example: Find definitions for microbiology terms**

```sparql
# Find microbiology-related items with definitions
SELECT ?item ?itemLabel ?definition WHERE {
  ?item wdt:P31 wd:Q4936952 .  # instance of: metabolic pathway
  ?item schema:description ?definition .
  FILTER(LANG(?definition) = "en")
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Key Wikidata properties:**
- `schema:description` - Short description
- `wdt:P2888` - Exact match (to other identifiers/IRIs)
- `wdt:P1687` - Wikidata property for ontology mapping
- `wdt:P279` - Subclass of (genus)

**Useful Wikidata classes for METPO:**
- `wd:Q4936952` - Metabolic pathway
- `wd:Q7432` - Species
- `wd:Q5891` - Microorganism
- `wd:Q7187` - Gene
- `wd:Q898432` - Biological process
- `wd:Q104053751` - Phenotype

**CLI tool for Wikidata queries:**
```bash
# Install wikidata CLI
pip install wikidata

# Or use SPARQL endpoint directly
curl -H "Accept: application/json" \
  --data-urlencode "query=SELECT ?item WHERE { ?item wdt:P31 wd:Q4936952 } LIMIT 10" \
  https://query.wikidata.org/sparql
```

**Pro tip:** Wikidata descriptions are VERY short (1 sentence). Use them as inspiration, not direct import.

### DBpedia SPARQL

**DBpedia SPARQL Endpoint:** https://dbpedia.org/sparql

```sparql
# Find microbiology concepts with abstracts
SELECT ?resource ?abstract WHERE {
  ?resource dct:subject dbc:Microbiology .
  ?resource dbo:abstract ?abstract .
  FILTER(LANG(?abstract) = "en")
}
LIMIT 100
```

**DBpedia properties:**
- `dbo:abstract` - Wikipedia first paragraph (good for understanding, not formal definitions)
- `dbo:wikiPageWikiLink` - Links to related concepts
- `dct:subject` - Category

**Limitation:** DBpedia definitions are encyclopedic, not formal ontology definitions. Use for understanding domain concepts.

### Semantic Scholar API

**API Endpoint:** https://api.semanticscholar.org/

**Find papers about a term:**
```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=thermophile+definition&fields=title,abstract,url,citationCount"
```

**Use case:** Find authoritative papers that define terms, extract PMIDs for attribution.

**Limitation:** Rate limited (100 requests/5 min), need to parse abstracts manually.

### Europe PMC API

**API Endpoint:** https://www.ebi.ac.uk/europepmc/webservices/rest/

**Search for definitions in abstracts:**
```bash
# Search for papers defining "thermophile"
curl "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=thermophile%20AND%20definition&format=json"
```

**Use case:**
- Find papers with explicit definitions in abstracts
- Extract PMIDs for IAO:0000119 attribution
- More reliable than textbooks (peer-reviewed, citable)

**Advanced search:**
```bash
# Search for review articles defining key terms
curl "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=mesophile%20AND%20TITLE:review&format=json"
```

### Wikipedia API (For General Concepts Only)

**API Endpoint:** https://en.wikipedia.org/w/api.php

**Get article intro:**
```bash
curl "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&titles=Thermophile&format=json"
```

**Use case:**
- Understanding general concepts
- Finding related terms
- **DO NOT cite Wikipedia directly** - trace to original sources in references

---

## Workflow for Adding/Improving Definitions

### Step 1: Identify Terms Needing Definitions

```bash
# List terms without definitions
cut -f1,2,5 src/templates/metpo_sheet_improved.tsv | grep -P '\t$'
```

### Step 2: Search ChromaDB Embeddings (PREFERRED)

```bash
# Run semantic mapper (if not already done)
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2-)

uv run chromadb-semantic-mapper \
  --metpo-tsv src/templates/metpo_sheet_improved.tsv \
  --chroma-path data/chromadb/chroma_ols20_nonols4 \
  --collection-name combined_embeddings \
  --output data/mappings/metpo_mappings.sssom.tsv \
  --min-similarity 0.85
```

### Step 3: Retrieve Definitions from Matched Terms

**Option A: Extract from ChromaDB metadata**
```python
import chromadb
client = chromadb.PersistentClient(path="data/chromadb/chroma_ols20_nonols4")
collection = client.get_collection("combined_embeddings")

# Get by IRI
result = collection.get(
    ids=["http://purl.obolibrary.org/obo/OMP_0007851"],
    include=["metadatas"]
)
definition = result['metadatas'][0].get('definition', '')
```

**Option B: Use OLS4 API**
```bash
# URL encode the IRI
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('http://purl.obolibrary.org/obo/OMP_0007851'))")

# Fetch term details
curl "https://www.ebi.ac.uk/ols4/api/ontologies/omp/terms/${ENCODED}" | jq '.definition'
```

**Option C: Use BioPortal API**
```bash
API_KEY="your_bioportal_api_key"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('http://purl.obolibrary.org/obo/OMP_0007851'))")

curl -H "Authorization: apikey token=${API_KEY}" \
  "https://data.biomedical.ontology.org/ontologies/OMP/classes/${ENCODED}" | jq '.definition'
```

### Step 4: Adapt Definition to METPO Hierarchy

**Key question:** Does the foreign definition's genus match our parent class?

**Example:**
```
METPO term: chemolithotrophic
METPO parent: trophic type
Foreign (OMP): "An organism that uses inorganic compounds..."
                 ^^^^^^^^ genus mismatch!
METPO adapted: "A trophic type characterized by the use of inorganic compounds..."
                 ^^^^^^^^^^^ correct genus
```

### Step 5: Add Attribution

**Format for definition source (column 6):**

```
# Single source
OGMS:0000023

# Multiple sources (pipe-separated)
OMP:0007851|GO:0015980

# With PMID
PMID:23645609

# With human editor
[leave blank in column 6, add name to column 7]
```

**Format for term editor (column 7):**
```
Anthea Guo
Jed Kim-Ozaeta
Luke Wang
```

### Step 6: Validate Definition Quality

**Checklist:**
- [ ] Uses parent class as genus
- [ ] Follows "A [genus] that/where/which..." structure
- [ ] States essential differentiating characteristics
- [ ] No circularity
- [ ] No generalizing terms
- [ ] No examples
- [ ] Length 50-200 characters
- [ ] Appropriate specificity

---

## Balancing Fidelity vs. OBO Guidelines vs. METPO Hierarchy

### The Three-Way Tension

1. **Fidelity to source** - Preserve scientific accuracy from original definition
2. **OBO Foundry guidelines** - Follow genus-differentia form strictly
3. **METPO hierarchy** - Use METPO parent class as genus

**Solution:** Prioritize in this order:
1. **Scientific accuracy** (fidelity) - Never change the scientific meaning
2. **METPO hierarchy** (genus) - Always use METPO parent as genus
3. **OBO form** (structure) - Apply genus-differentia structure within constraints above

### Example Transformations

**Foreign definition (OMP):**
```
"Thermophilic organisms are those that thrive at relatively high temperatures,
typically between 45°C and 80°C."
```

**Issues:**
- Genus: "organisms" (foreign hierarchy)
- Generalizing: "typically"
- Not genus-differentia form

**METPO transformation:**
```
METPO parent: "trophic type"
Definition: "A trophic type characterized by optimal growth at temperatures
             between 45°C and 80°C."
Attribution: OMP:0007851|PMID:12345678
```

**What changed:**
- ✅ Genus: "organisms" → "trophic type" (METPO parent)
- ✅ Removed: "typically" (generalizing)
- ✅ Structure: Now genus-differentia form
- ✅ Preserved: Temperature range (scientific accuracy)

**Foreign definition (PATO):**
```
"A quality inhering in a bearer by virtue of the bearer's high degree of heat."
```

**Issues:**
- Too abstract for METPO (we're more specific)
- Genus "quality" is correct but definition is circular
- Lacks METPO context (organism temperature preference vs. environmental temperature)

**METPO transformation:**
```
METPO parent: "temperature phenotype"
Definition: "A temperature phenotype characterized by optimal growth occurring
             at high temperatures relative to mesophilic organisms."
Attribution: PATO:0000146 (adapted)
```

**What changed:**
- ✅ Genus: "quality" → "temperature phenotype" (METPO parent, more specific)
- ✅ Added: "optimal growth" context (METPO is about organism phenotypes)
- ✅ Added: "relative to mesophilic" (provides objective comparison)
- ✅ Preserved: "high temperature" concept (scientific accuracy)
- ⚠️ Attribution: Added "(adapted)" to note transformation

---

## Attribution Best Practices

### When to Use Each Annotation Property

**IAO:0000119 (definition source)** - Use for:
- Ontology term IRIs when definition adapted from that term
- PMIDs for literature sources
- URLs for authoritative web resources
- Format: `ONTOLOGY:ID` or `PMID:12345` or `https://...`

**IAO:0000117 (term editor)** - Use for:
- Humans who wrote/significantly edited the definition
- Format: `First Last` or `First Last (Institution)`

**dc:contributor / dcterms:contributor** - Use for:
- Ontology-level acknowledgments (not per-term)
- Project-level attribution

### When to Mark Definitions as "Adapted"

**Use "(adapted)" suffix when:**
- You changed the genus to match METPO parent
- You modified structure to follow genus-differentia form
- You added/removed qualifiers ("typically", "usually")
- Scientific meaning preserved but wording changed significantly

**Format:**
```
# Single adapted source
OMP:0007851 (adapted)

# Multiple sources, one adapted
OMP:0007851 (adapted)|GO:0015980

# All sources adapted
OMP:0007851 (adapted)|PATO:0000146 (adapted)
```

**Do NOT use "(adapted)" when:**
- You copied definition verbatim
- You only fixed typos or formatting
- You combined multiple exact quotes

---

## Outstanding Tasks

### High Priority

1. **Add definition sources for Jed's 28 terms**
   - These have definitions but no attribution
   - See: `docs/UNDERGRADUATE_DEFINITION_ATTRIBUTIONS.md`

2. **Review and improve all 87 undergraduate definitions**
   - Check genus matches parent class
   - Verify follows genus-differentia form
   - Add definition sources where missing

3. **Use new SSSOM mappings for high-quality sources**
   - Focus on OMP, micro, PATO, ECOCORE (sweet spot ontologies)
   - Extract definitions via OLS API or ChromaDB
   - Adapt to METPO hierarchy

### Medium Priority

4. **Develop Wikidata/DBpedia search scripts**
   - SPARQL queries for microbiology terms
   - Automated definition extraction
   - PMID discovery for citations

5. **Extract Madin et al. Table 1**
   - 23 trait definitions
   - Maps to ~60 METPO terms
   - See: `docs/PDF_DEFINITION_LEADS.md`

6. **Find web-resolvable definition sources**
   - OpenStax textbooks (if appropriate)
   - Authoritative websites (NCBI, MicrobeWiki)
   - Must be citable and stable URLs

### Low Priority

7. **Validate all definitions with ROBOT**
   - Automated genus checking
   - Circular definition detection
   - Structure validation

8. **Document definition writing process**
   - Create templates for common patterns
   - Example transformations by parent class type
   - Common pitfalls and solutions

---

## Tools and Scripts

### Existing Scripts (from Definition Enrichment Workflow)

All in `metpo/scripts/`, callable via `uv run <command>`:

- `chromadb-semantic-mapper` - Query ChromaDB for semantic matches
- `analyze-definition-opportunities` - Identify terms needing definitions
- `bootstrap-definition-enrichment` - Fetch definitions from OLS4 API
- `find-best-definitions` - Find best definition per term from SSSOM
- `find-best-definitions-comprehensive` - Combined SSSOM + API search
- `compare-definitions-with-hierarchy` - Check genus compatibility

### New Scripts Needed (Prioritized)

**High Priority (Iterative Strategy Support):**

**1. `analyze-definition-coverage-by-subtree`**
- Find near-terminal parents where most children have definitions
- Calculate coverage percentage by parent
- Identify stragglers (children missing definitions)
- Detect common patterns in sibling definitions
- Output: Parent class, coverage %, pattern template, straggler list

**2. `extract-sibling-definition-patterns`**
- Given a parent class, extract all child definitions
- Analyze structure to find common patterns
- Suggest template for remaining children
- Output: Pattern template, examples, suggested definitions for stragglers

**3. `identify-axiom-defined-classes`**
- Find classes fully defined by OWL restrictions
- Check for min/max value restrictions, exact cardinality, etc.
- Suggest which classes don't need textual definitions
- Output: Classes to skip with justification

**Medium Priority (External Source Discovery):**

**4. `wikidata-definition-search`**
- SPARQL queries for microbiology terms
- Extract short descriptions
- Map to METPO terms

**5. `europepmc-definition-search`**
- Search abstracts for explicit definitions
- Extract PMIDs for attribution
- Format for IAO:0000119

**6. `extract-definitions-from-chromadb`**
- Given SSSOM mapping file, extract definitions from ChromaDB
- Output: METPO_ID, definition, source_IRI, source_ontology
- Ready for import into METPO sheet

**Low Priority (Quality Assurance):**

**7. `validate-definition-attributions`**
- Check all definition sources are resolvable
- Verify ontology IRIs exist in OLS/BioPortal
- Check PMIDs are valid

**8. `detect-redundant-definitions`**
- Find definitions that are just "[parent] that is [label]"
- Suggest converting to rdfs:comment or omitting
- Identify candidates for axiom-only definitions

---

## Related Documentation

- `docs/DEFINITION_ENRICHMENT_WORKFLOW.md` - Comprehensive workflow from 2025-11-10
- `docs/UNDERGRADUATE_DEFINITION_ATTRIBUTIONS.md` - Student contributions
- `docs/PDF_DEFINITION_LEADS.md` - BacDive, BactoTraits, Madin extractions
- `docs/chromadb_semantic_mapper.md` - Semantic mapping tool documentation
- `docs/icbo_2025_prep/sepgfw_definition_guide.pdf` - Seppälä-Ruttenberg-Smith guidelines

---

## References

### OBO Foundry
- **Principles:** https://obofoundry.org/principles/
- **Principle 6 (Textual Definitions):** https://obofoundry.org/principles/fp-006-textual-definitions.html

### Ontology APIs
- **OLS4:** https://www.ebi.ac.uk/ols4/api/
- **BioPortal:** https://data.biomedical.ontology.org/documentation

### Semantic Web Resources
- **Wikidata Query Service:** https://query.wikidata.org/
- **DBpedia SPARQL:** https://dbpedia.org/sparql
- **Semantic Scholar API:** https://api.semanticscholar.org/
- **Europe PMC API:** https://europepmc.org/RestfulWebService

### Microbiology References
- **Bergey's Manual:** https://bergeys.org/
- **MicrobeWiki:** https://microbewiki.kenyon.edu/
- **NCBI Taxonomy:** https://www.ncbi.nlm.nih.gov/taxonomy

---

## Contact

For questions about definition improvement strategy:
- Check this document
- Review `docs/DEFINITION_ENRICHMENT_WORKFLOW.md`
- See `metpo/scripts/` for existing tools
- Contact: Mark A. Miller (MAM@lbl.gov)
