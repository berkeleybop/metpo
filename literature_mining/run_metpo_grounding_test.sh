#!/bin/bash
#
# Quick-start script for METPO grounding tests
# Run Test 1: Controlled validation that OntoGPT+METPO works
#

set -e  # Exit on error

echo "================================================================================"
echo "METPO Grounding Test - Controlled Validation"
echo "Test 1 from METPO_GROUNDING_TEST_PLAN.md"
echo "================================================================================"
echo ""

# Create test directories
mkdir -p test_inputs
mkdir -p test_results

# Create test document with known METPO terms
cat > test_inputs/metpo_grounding_test.txt << 'EOF'
Title: Growth characteristics of diverse bacterial phenotypes

Study 1: Mesophilic facultative anaerobes
The bacterium Strain A grows optimally at 37°C (mesophilic). It is a
facultative anaerobe, capable of both aerobic and anaerobic growth. The
organism is Gram-negative and shows optimal growth at pH 7.0 (neutrophilic).
It tolerates up to 3% NaCl (halotolerant).

Study 2: Thermophilic alkaliphiles
Strain B is thermophilic with a temperature range of 45-80°C. It is an
obligate aerobe and alkaliphilic, growing best at pH 9.5. The organism
is Gram-positive with endospore formation capability.

Study 3: Psychrophilic acidophiles
Strain C is psychrophilic, growing at temperatures below 15°C. It is
an anaerobe and acidophilic, preferring pH 4.0. The organism shows
psychrotolerant behavior and is microaerophilic under certain conditions.

Study 4: Halophilic methylotrophs
Strain D is a halophilic methylotroph, requiring at least 3% NaCl for
growth. It is an obligate aerobe and mesophilic. The organism utilizes
methanol as a carbon source (methylotrophic) and is Gram-negative.
EOF

echo "✓ Created test input with known METPO phenotypes"
echo "  File: test_inputs/metpo_grounding_test.txt"
echo ""

# Expected METPO terms (for validation)
cat > test_results/expected_metpo_terms.txt << 'EOF'
Expected METPO Groundings:
==========================

Temperature phenotypes:
  - mesophilic (37°C)
  - thermophilic (45-80°C)
  - psychrophilic (<15°C)
  - psychrotolerant

Oxygen requirements:
  - facultative anaerobe
  - obligate aerobe
  - anaerobe
  - aerobic
  - anaerobic
  - microaerophilic

Gram stain:
  - Gram-negative
  - Gram-positive

pH preferences:
  - neutrophilic (pH 7.0)
  - alkaliphilic (pH 9.5)
  - acidophilic (pH 4.0)

Salinity:
  - halotolerant (3% NaCl)
  - halophilic (requires NaCl)

Metabolic:
  - methylotroph
  - methylotrophic

Morphology:
  - endospore formation

TARGET SUCCESS: >80% of these terms should ground to METPO
EOF

echo "✓ Created expected terms list for validation"
echo "  File: test_results/expected_metpo_terms.txt"
echo ""

# Check if ontogpt is available
if ! command -v ontogpt &> /dev/null; then
    echo "⚠ ontogpt not found. Checking uv..."
    if ! command -v uv &> /dev/null; then
        echo "✗ ERROR: Neither ontogpt nor uv found"
        echo "  Install with: pip install ontogpt"
        echo "  Or use: uv"
        exit 1
    fi
    ONTOGPT="uv run ontogpt"
else
    ONTOGPT="ontogpt"
fi

echo "✓ OntoGPT command: $ONTOGPT"
echo ""

# Run extraction with growth_conditions template (has METPO annotators)
echo "Running extraction with growth_conditions_hybrid template..."
echo "(This template has METPO annotators configured)"
echo ""

$ONTOGPT extract \
  -t templates/growth_conditions_hybrid.yaml \
  -i test_inputs/metpo_grounding_test.txt \
  -o test_results/metpo_grounding_test.yaml \
  --model gpt-4o \
  --temperature 0.0

echo ""
echo "✓ Extraction complete"
echo "  Output: test_results/metpo_grounding_test.yaml"
echo ""

# Analyze results
echo "Analyzing results..."
echo ""

METPO_COUNT=$(grep -c "METPO:" test_results/metpo_grounding_test.yaml || echo "0")
AUTO_COUNT=$(grep -c "AUTO:" test_results/metpo_grounding_test.yaml || echo "0")

TOTAL=$((METPO_COUNT + AUTO_COUNT))
if [ $TOTAL -gt 0 ]; then
    GROUNDING_RATE=$(awk "BEGIN {printf \"%.1f\", ($METPO_COUNT / $TOTAL) * 100}")
else
    GROUNDING_RATE="0.0"
fi

echo "================================================================================"
echo "RESULTS"
echo "================================================================================"
echo ""
echo "METPO terms found:  $METPO_COUNT"
echo "AUTO terms found:   $AUTO_COUNT"
echo "Grounding rate:     ${GROUNDING_RATE}%"
echo ""

if [ $METPO_COUNT -gt 0 ]; then
    echo "✓ SUCCESS! OntoGPT successfully grounded to METPO"
    echo ""
    echo "METPO terms extracted:"
    grep "METPO:" test_results/metpo_grounding_test.yaml | head -20
else
    echo "✗ FAILURE: No METPO terms found"
    echo ""
    echo "This indicates a configuration problem:"
    echo "  1. Check template has METPO annotators configured"
    echo "  2. Verify ../src/ontology/metpo.owl path is correct"
    echo "  3. Check METPO classes have proper labels/synonyms"
fi

echo ""
echo "================================================================================"
echo "NEXT STEPS"
echo "================================================================================"
echo ""
if [ $METPO_COUNT -gt 0 ]; then
    echo "1. Review test_results/metpo_grounding_test.yaml to see what grounded"
    echo "2. Compare to test_results/expected_metpo_terms.txt"
    echo "3. For any missing, check if METPO has matching label/synonym"
    echo "4. If successful (>80%), proceed to Test 2: Template optimization"
else
    echo "1. Check template configuration in templates/growth_conditions_hybrid.yaml"
    echo "2. Verify annotators are set to: sqlite:../src/ontology/metpo.owl"
    echo "3. Test with: uv run ontogpt --help to ensure working"
    echo "4. Check ../src/ontology/metpo.owl exists and is readable"
fi

echo ""
echo "View full results: cat test_results/metpo_grounding_test.yaml"
echo "View expected terms: cat test_results/expected_metpo_terms.txt"
echo ""
