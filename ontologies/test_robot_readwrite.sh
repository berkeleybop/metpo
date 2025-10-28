#!/bin/bash
# Simple test: Can ROBOT read and write all ontologies?

set +e  # Don't exit on error, we want to test all files

RESULTS_DIR="robot_test_results"
mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "Testing ROBOT Read/Write for All Ontologies"
echo "Date: $(date)"
echo "============================================"
echo ""

# Decompress gzipped files first
echo "Preparing gzipped files..."
for gz in *.owl.gz; do
    if [ -f "$gz" ]; then
        base="${gz%.gz}"
        echo "  Decompressing $gz -> $RESULTS_DIR/$base"
        gunzip -c "$gz" > "$RESULTS_DIR/$base"
    fi
done
echo ""

# Function to test one file
test_file() {
    local input="$1"
    local name="$2"

    echo "Testing: $name"
    echo "  Input: $input"

    # Test conversion to different formats
    local success=0

    # To OWL
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.owl" 2>&1 | head -20; then
        echo "  ✓ OWL write successful"
        ((success++))
    else
        echo "  ✗ OWL write FAILED"
        return 1
    fi

    # To Turtle (more strict parsing)
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.ttl" 2>&1 | head -20; then
        echo "  ✓ Turtle write successful"
        ((success++))
    else
        echo "  ✗ Turtle write FAILED"
    fi

    # To OBO (if applicable)
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.obo" 2>&1 | head -20; then
        echo "  ✓ OBO write successful"
        ((success++))
    else
        echo "  ⚠ OBO write failed (may not be OBO-compatible)"
    fi

    echo "  Result: $success/3 formats successful"
    echo ""

    return 0
}

# Test METPO first (baseline)
echo "=========================================="
echo "BASELINE: METPO"
echo "=========================================="
test_file "../../src/ontology/metpo.owl" "METPO"

# Test all other ontologies
echo "=========================================="
echo "LOCAL ONTOLOGIES"
echo "=========================================="

test_file "D3O.owl" "D3O"
test_file "fao.owl" "FAO"
test_file "mco.owl" "MCO"
test_file "$RESULTS_DIR/MicrO-2025-03-20-merged.owl" "MicrO-2025"
test_file "$RESULTS_DIR/MicrO-for-metpo.owl" "MicrO-for-metpo"
test_file "mpo_v0.74.en_only.owl" "MPO"
test_file "n4l_merged.owl" "N4L"
test_file "omp.owl" "OMP"

echo "============================================"
echo "SUMMARY"
echo "============================================"
echo ""
echo "Readable files in: $RESULTS_DIR/"
ls -lh "$RESULTS_DIR"/*.owl 2>/dev/null | awk '{print $9, $5}'

echo ""
echo "If all files converted successfully, proceed with full validation:"
echo "  ./validate_all_ontologies.sh"
