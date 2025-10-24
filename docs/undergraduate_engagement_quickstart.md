# METPO Undergraduate Engagement - Quick Start Guide

This is a condensed guide for students getting started. For comprehensive details, see [undergraduate_engagement_plan.md](undergraduate_engagement_plan.md).

## Overview

**Goal**: Create high-quality definitions and ontology mappings for METPO classes to support EBI OLS submission and ICBO 2025 presentation.

**Core Principle**: Change one thing at a time, document the result, iterate.

## Getting Started

### Prerequisites

1. **Install tools**:
   ```bash
   # ROBOT (ontology tool)
   brew install robot  # macOS
   # or download from https://robot.obolibrary.org/

   # Python dependencies
   pip install oaklib requests pandas sentence-transformers chromadb

   # BioPortal API key (free)
   # Sign up: https://bioportal.bioontology.org/accounts/new
   export BIOPORTAL_API_KEY="your-key-here"
   ```

2. **Clone repo and understand structure**:
   ```bash
   cd metpo/
   ls src/templates/  # ROBOT templates
   ls docs/           # Analysis documents
   ```

3. **Read background**:
   - [bacdive_keywords_key_findings.md](bacdive_keywords_key_findings.md) - What data we have
   - [kg_microbe_bacdive_implementation_analysis.md](kg_microbe_bacdive_implementation_analysis.md) - How it's used

## Two Main Tasks

### Task A: Create SKOS Mappings

**When**: METPO class has a good match in another ontology (OMP, PATO, MCO, ENVO)

**Steps**:
1. Search OLS4 and BioPortal for similar terms
2. Use OLS4 "Similar classes" feature (for PATO, ENVO)
3. Validate semantic type (quality vs entity)
4. Add mapping to ROBOT template
5. Document decision in metpo-kgm-studio/

**Example**:
```
METPO "thermophilic" → PATO:0002078 (exact match)
```

### Task B: Write Aristotelian Definitions

**When**: No suitable ontology match exists

**Steps**:
1. Research the concept (BacDive docs, literature)
2. Write definition: "An A is a B that C"
3. Cite source
4. Add to ROBOT template
5. Document decision in metpo-kgm-studio/

**Example**:
```
thermophilic: "A quality of an organism that exhibits optimal growth at
temperatures between 45°C and 80°C."
Source: "BacDive culture temperature analysis (2025-10-24)"
```

## Key Innovation: Semantic Similarity via Embeddings

### For OLS4 Ontologies (PATO, ENVO)

1. Search OLS4: https://www.ebi.ac.uk/ols4/
2. Click on term
3. Check "Similar classes" tab
4. Finds semantically similar terms even with different labels!

**Example**: Searching "thermophilic" might find "high-temperature growth" or "heat-loving"

### For BioPortal-Only Ontologies (OMP, MCO)

Use custom embeddings (see Task 2b in full plan):
```python
from sentence_transformers import SentenceTransformer

# Load biomedical embedding model
model = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')

# Search for similar terms
similar = find_similar_terms("thermophilic", omp_embeddings)
```

**Alternative**: Use OpenAI embeddings (~$0.01 for all ontologies):
```python
import openai
client = openai.OpenAI()
embedding = client.embeddings.create(
    input="thermophilic",
    model="text-embedding-3-small"
)
```

## Critical: Entity vs Quality Distinction

**Problem**: Embedding similarity can conflate different ontological types!

**Example**:
- "thermophilic" (quality) ✓
- "thermophile" (organism) ✗

**Solution**: Always check parent classes after finding similar terms:
```python
def is_quality_term(term_iri, ontology):
    # Get parent classes from OLS/BioPortal
    parents = get_parent_classes(term_iri, ontology)

    # Check if quality vs entity
    quality_indicators = ["PATO_0000001", "BFO_0000020"]
    entity_indicators = ["BFO_0000040", "NCBITaxon_1"]

    # Return: quality, entity, or unknown
```

Only map if semantic types align!

## Git Workflow

**Rule**: ONE CLASS PER COMMIT

```bash
# 1. Create branch
git checkout -b add-thermophilic-mapping

# 2. Edit ROBOT template (one row only)
nano src/templates/metpo.tsv

# 3. Validate
make build
robot reason --input metpo.owl --reasoner ELK

# 4. Commit
git add src/templates/metpo.tsv
git commit -m "Add PATO mapping for thermophilic (METPO:0000001)

- Maps to PATO:0002078
- Decision: metpo-kgm-studio/mapping-decisions/2025-10-24-thermophilic.md"

# 5. Push and create PR
git push -u origin add-thermophilic-mapping
gh pr create --title "Add PATO mapping for thermophilic"
```

## Documentation Format

Create file: `metpo-kgm-studio/mapping-decisions/YYYY-MM-DD-{label}-{mapping|definition}.md`

**Template**:
```markdown
# thermophilic - Mapping Decision

**Date**: 2025-10-24
**Author**: @username
**METPO ID**: METPO:0000001

## Search
- APIs: OLS4, BioPortal
- Ontologies: PATO, OMP, MCO

## Results
1. PATO:0002078 "thermophilic" (quality)
2. OMP:0005508 "thermophilic organism phenotype"

## Validation
- PATO:0002078 is quality ✓
- Definition matches BacDive validation ✓
- Semantic type: quality (not entity) ✓

## Decision
MAPPING: skos:exactMatch to PATO:0002078

**Rationale**: Exact semantic and ontological alignment

## Implementation
```tsv
ID	Label	skos:exactMatch	IAO:0000119
METPO:0000001	thermophilic	PATO:0002078	Mapped via OLS search 2025-10-24
```

## Student Roles

### Software Engineering
- Build API clients for OLS/BioPortal
- Create embedding indexing pipeline
- Maintain CI/CD for ROBOT
- Help others with git issues

### Machine Learning
- Build semantic similarity scoring
- Compare embedding models
- Train definition quality checker
- Cluster analysis for gaps

### Knowledge Management
- Lead SKOS mapping decisions
- Review definition quality
- Maintain metpo-kgm-studio docs
- Train others on ontology principles

### Microbiology
- Validate biological accuracy
- Research phenotypes in literature
- Prioritize by biological importance
- Review uncertain cases

## Resources

**Tools**:
- ROBOT: https://robot.obolibrary.org/
- OAK: https://incatools.github.io/ontology-access-kit/
- OLS4: https://www.ebi.ac.uk/ols4/
- BioPortal: https://bioportal.bioontology.org/

**Ontologies**:
- OMP (Ontology of Microbial Phenotypes): https://bioportal.bioontology.org/ontologies/OMP
- PATO (Phenotype and Trait Ontology): https://www.ebi.ac.uk/ols4/ontologies/pato
- MCO (Microbial Conditions Ontology): https://bioportal.bioontology.org/ontologies/MCO
- ENVO (Environment Ontology): https://www.ebi.ac.uk/ols4/ontologies/envo

**OBO Foundry Principles**:
- FP-006 Textual Definitions: http://obofoundry.org/principles/fp-006-textual-definitions.html
- FP-007 Relations Reuse: http://obofoundry.org/principles/fp-007-relations.html

**BacDive Analysis** (in docs/):
- bacdive_keywords_inventory.tsv
- bacdive_keywords_key_findings.md
- bacdive_culture_temp_analysis.md

## Weekly Schedule

**Monday (1 hr)** - Status meeting
- Review progress
- Discuss blockers
- Assign new classes

**Thursday (1 hr)** - Review session
- Peer review 3-5 PRs
- Discuss difficult cases
- Share lessons learned

**Friday (30 min)** - Office hours (optional)
- One-on-one help
- Debug issues

## Quality Checklist

### For Mappings
- [ ] SKOS predicate is appropriate
- [ ] Semantic alignment validated (quality vs entity)
- [ ] Target term has definition
- [ ] Source citation included
- [ ] Decision documented

### For Definitions
- [ ] Follows Aristotelian form "An A is a B that C"
- [ ] Not circular
- [ ] Cites authoritative source
- [ ] Uses appropriate OBO relations

### For All
- [ ] Single class changed (atomic commit)
- [ ] ROBOT build passes
- [ ] Reasoner check passes
- [ ] No merge conflicts

## Common Issues

### "Build failed with template error"
- Check TSV syntax (tabs not spaces)
- Verify IRI format
- Check for duplicate IDs

### "Reasoner reports unsatisfiable class"
- Check parent class exists
- Verify logical definition syntax
- Review object property usage

### "Git merge conflict"
```bash
git fetch origin
git merge origin/main
# Resolve conflicts in editor
git add .
git commit
```

## Getting Help

- **Slack**: #technical, #ontology-questions, #biology
- **GitHub Issues**: Tag appropriate person
- **Office Hours**: Friday afternoons
- **Full Documentation**: [undergraduate_engagement_plan.md](undergraduate_engagement_plan.md)

## Next Steps

1. Read full plan: [undergraduate_engagement_plan.md](undergraduate_engagement_plan.md)
2. Review example PRs in repo
3. Pick first class to work on
4. Ask questions in Slack!

**Remember**: Change one thing, document it, iterate. Quality over quantity!
