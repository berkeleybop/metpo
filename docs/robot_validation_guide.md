# ROBOT Validation Commands for Ontology Quality Checking

## Quick Reference: Essential ROBOT Quality Checks

For your ICBO abstract argument about unmaintained ontologies failing basic checks, use these commands:

### 1. **reason** - Check Logical Consistency (MOST CRITICAL)
Detects inconsistencies and unsatisfiable classes that make an ontology unusable.

```bash
robot reason --reasoner ELK \
  --input ontology.owl \
  --output reasoned.owl
```

**Exit code non-zero = FAILURE** (inconsistent or unsatisfiable classes)

**For debugging failures:**
```bash
robot reason --reasoner ELK \
  --input ontology.owl \
  --dump-unsatisfiable unsatisfiable.owl \
  --output reasoned.owl
```

**Reasoner options:**
- `ELK` - fastest, good for large ontologies (default)
- `HermiT` - most comprehensive, slower
- `JFact` - alternative full reasoner
- `Whelk` - lightweight
- `structural` - minimal checking

### 2. **report** - Comprehensive Quality Control
Runs ~20+ SPARQL queries checking OBO best practices.

```bash
robot report --input ontology.owl \
  --output report.tsv \
  --print 10
```

**Output formats:**
- TSV (default) - tab-separated violations
- HTML - visual report
- YAML, JSON, XLSX - for processing

**Severity levels:**
- **ERROR** - must fix before release (e.g., multiple labels on one class)
- **WARN** - should fix soon (e.g., deprecated references)
- **INFO** - good practice (e.g., definition formatting)

**Common checks include:**
- Missing labels
- Multiple labels
- Deprecated class usage
- Annotation formatting
- Definition cardinality
- Circular dependencies
- Label/ID mismatches

### 3. **validate-profile** - OWL Profile Compliance
Check if ontology conforms to OWL 2 profiles (for reasoner compatibility).

```bash
robot validate-profile --profile DL \
  --input ontology.owl \
  --output validation.txt
```

**Profiles:**
- `DL` - Description Logic (most common for bio-ontologies)
- `EL` - Polynomial-time reasoning
- `QL` - Query-optimized
- `RL` - Rule-based systems
- `Full` - Complete OWL 2 (often unreasonable)

**Why this matters:** Most bio-ontologies should be OWL DL compatible. Violations suggest poor ontology engineering.

### 4. **verify** - Custom SPARQL Rule Checking
Run your own SPARQL queries to find specific violations.

```bash
robot verify --input ontology.owl \
  --queries custom-rules.sparql \
  --output-dir violations/
```

**Example custom check (no-orphans.sparql):**
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class WHERE {
  ?class a owl:Class .
  FILTER NOT EXISTS { ?class rdfs:subClassOf ?parent }
  FILTER (!isBlank(?class))
}
```

**Use --fail-on-violation false** to warn but continue:
```bash
robot verify --input ontology.owl \
  --queries warnings.sparql \
  --output-dir results/ \
  --fail-on-violation false
```

## Recommended Workflow for Comparing Ontologies

### Step 1: Check if they're even loadable
```bash
robot reason --reasoner ELK \
  --input MPO.owl \
  --output MPO-reasoned.owl \
  2>&1 | tee MPO-reason.log
echo "Exit code: $?"
```

### Step 2: Generate quality report
```bash
robot report --input MPO.owl \
  --output MPO-report.tsv \
  --format HTML \
  --output MPO-report.html
```

### Step 3: Profile validation
```bash
robot validate-profile --profile DL \
  --input MPO.owl \
  --output MPO-profile.txt \
  2>&1 | tee MPO-profile.log
echo "Exit code: $?"
```

### Step 4: Summary stats
```bash
robot measure --input MPO.owl \
  --metrics all \
  --output MPO-metrics.tsv
```

## Batch Script for Multiple Ontologies

```bash
#!/bin/bash
# check_ontologies.sh

for ont in MPO MicrO MCO OMP D3O FAO; do
  echo "=== Checking $ont ==="

  # Reasoning check
  echo "  [1/3] Reasoning..."
  if robot reason --reasoner ELK \
    --input ${ont}.owl \
    --output ${ont}-reasoned.owl 2>&1 | tee ${ont}-reason.log; then
    echo "    ✓ Reasoning passed"
  else
    echo "    ✗ Reasoning FAILED (exit code: $?)"
  fi

  # Quality report
  echo "  [2/3] Quality report..."
  robot report --input ${ont}.owl \
    --output ${ont}-report.tsv \
    --print 5 2>&1 | tee -a ${ont}-reason.log

  # Profile validation
  echo "  [3/3] Profile validation..."
  if robot validate-profile --profile DL \
    --input ${ont}.owl \
    --output ${ont}-profile.txt 2>&1 | tee -a ${ont}-reason.log; then
    echo "    ✓ OWL DL profile valid"
  else
    echo "    ✗ OWL DL profile INVALID"
  fi

  echo ""
done

# Summarize results
echo "=== SUMMARY ==="
for ont in MPO MicrO MCO OMP D3O FAO; do
  errors=$(grep -c "ERROR" ${ont}-report.tsv 2>/dev/null || echo "N/A")
  warns=$(grep -c "WARN" ${ont}-report.tsv 2>/dev/null || echo "N/A")
  echo "$ont: $errors errors, $warns warnings"
done
```

## What to Look For in Results

### Red flags for "unmaintained":
1. **Reasoning fails** - unsatisfiable classes, inconsistencies
2. **High ERROR count** in report (>10 for small ontologies, >100 for large)
3. **Profile violations** - doesn't conform to OWL DL
4. **Missing imports** - broken external references
5. **Deprecated class usage** - references to obsolete terms

### METPO comparison points:
```bash
# Show METPO passes all checks
robot reason --reasoner ELK --input metpo.owl --output metpo-reasoned.owl
robot report --input metpo.owl --output metpo-report.tsv
robot validate-profile --profile DL --input metpo.owl --output metpo-profile.txt

# Compare with unmaintained ontologies
robot report --input MPO.owl --output MPO-report.tsv --print 20
```

## Expected Issues in Unmaintained Ontologies

### MPO (2014) likely issues:
- Broken imports (URLs changed in 11 years)
- Deprecated property usage
- OWL 1 vs OWL 2 syntax issues
- Missing annotations (pre-OBO conventions)

### MicrO (2018) likely issues:
- Large size = more reasoning problems
- Import closure failures
- Annotation inconsistencies

### MCO (2019) likely issues:
- Unmaintained imports
- Profile violations
- Circular dependencies

## For Your ICBO Abstract

Run this minimal check and report results:

```bash
# Quick validation of each ontology
for ont in MPO.owl MicrO.owl MCO.owl OMP.owl; do
  echo "Checking $ont..."
  robot reason --reasoner ELK --input $ont --output /dev/null 2>&1 && \
    echo "  ✓ Consistent" || echo "  ✗ INCONSISTENT/UNSATISFIABLE"

  errors=$(robot report --input $ont --output ${ont%.owl}-report.tsv 2>&1 | grep -c "ERROR" || echo 0)
  echo "  Report: $errors ERRORs"
done
```

Then in your abstract: "Validation with ROBOT revealed that X of 6 existing microbial ontologies fail consistency checks, and Y contain critical errors according to OBO quality standards."

## Additional Commands

### measure - Get ontology statistics
```bash
robot measure --input ontology.owl \
  --metrics extended \
  --output metrics.tsv
```

Provides counts of:
- Classes, properties, individuals
- Axioms by type
- Annotation usage
- Import statistics

### diff - Compare ontologies
```bash
robot diff --left old-version.owl \
  --right new-version.owl \
  --output changes.txt
```

Useful for showing maintenance activity (or lack thereof).

### explain - Debug reasoning
```bash
robot explain --reasoner ELK \
  --input ontology.owl \
  --axiom "'Problem Class' SubClassOf owl:Nothing" \
  --explanation explanation.md
```

## Documentation
- Main: https://robot.obolibrary.org/
- Report: https://robot.obolibrary.org/report
- Verify: https://robot.obolibrary.org/verify
- Reason: https://robot.obolibrary.org/reason
- Validate-profile: https://robot.obolibrary.org/validate-profile
