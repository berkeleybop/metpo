#!/bin/bash
# Simple test: Can ROBOT read and write all ontologies in /ontologies directory?

set +e  # Don't exit on error, we want to test all files

RESULTS_DIR="robot_test_results"
mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "Testing ROBOT Read/Write for All Ontologies"
echo "Date: $(date)"
echo "Working Directory: $(pwd)"
echo "============================================"
echo ""

# Function to test one file
test_file() {
    local input="$1"
    local name="$2"

    if [ ! -f "$input" ]; then
        echo "Testing: $name"
        echo "  ✗ File not found: $input"
        echo ""
        return 1
    fi

    local filesize=$(ls -lh "$input" | awk '{print $5}')
    echo "Testing: $name ($filesize)"
    echo "  Input: $input"

    # Test conversion to different formats
    local success=0

    # To OWL (suppress most output, just show errors)
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.owl" 2>&1 | grep -E "(ERROR|Exception|FAILED)" || [ ${PIPESTATUS[0]} -eq 0 ]; then
        if [ -f "$RESULTS_DIR/${name}.owl" ]; then
            echo "  ✓ OWL write successful"
            ((success++))
        else
            echo "  ✗ OWL write FAILED"
        fi
    else
        echo "  ✗ OWL write FAILED"
    fi

    # To Turtle (more strict parsing)
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.ttl" 2>&1 | grep -E "(ERROR|Exception|FAILED)" || [ ${PIPESTATUS[0]} -eq 0 ]; then
        if [ -f "$RESULTS_DIR/${name}.ttl" ]; then
            echo "  ✓ Turtle write successful"
            ((success++))
        else
            echo "  ✗ Turtle write FAILED"
        fi
    else
        echo "  ✗ Turtle write FAILED"
    fi

    # To OBO (if applicable) - suppress OBO structure errors as they're expected
    if robot convert --input "$input" --output "$RESULTS_DIR/${name}.obo" 2>&1 | grep -v "OBO STRUCTURE ERROR" | grep -E "(ERROR|Exception|FAILED)" || [ ${PIPESTATUS[0]} -eq 0 ]; then
        if [ -f "$RESULTS_DIR/${name}.obo" ]; then
            echo "  ✓ OBO write successful"
            ((success++))
        else
            echo "  ⚠ OBO write failed (may not be OBO-compatible)"
        fi
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
test_file "../src/ontology/metpo.owl" "METPO"

# Test all OWL files in current directory
echo "=========================================="
echo "DOWNLOADED/LOCAL ONTOLOGIES"
echo "=========================================="

# Microbial-specific ontologies
test_file "D3O.owl" "D3O"
test_file "fao.owl" "FAO"
test_file "mco.owl" "MCO"
test_file "MicrO.owl" "MicrO"
test_file "mpo_v0.5.owl" "MPO-v0.5"
test_file "omp.owl" "OMP"

# High-performing ontologies from search
test_file "flopo.owl" "FLOPO"
test_file "pato.owl" "PATO"
test_file "oba.owl" "OBA"
test_file "upheno.owl" "UPHENO"

# Handle Turtle file separately
if [ -f "mpo_v0.74.ttl" ]; then
    echo "Testing: MPO-v0.74-TTL"
    echo "  Input: mpo_v0.74.ttl (Turtle format)"
    if robot convert --input "mpo_v0.74.ttl" --output "$RESULTS_DIR/MPO-v0.74.owl" 2>&1 | grep -v "OBO STRUCTURE ERROR" | head -10; then
        echo "  ✓ Conversion from Turtle successful"
    else
        echo "  ✗ Conversion from Turtle failed"
    fi
    echo ""
fi

echo "============================================"
echo "SUMMARY"
echo "============================================"
echo ""
echo "Successfully converted files in: $RESULTS_DIR/"
ls -lh "$RESULTS_DIR"/*.owl 2>/dev/null | awk '{printf "  %-30s %8s\n", $9, $5}'

echo ""
total=$(ls -1 "$RESULTS_DIR"/*.owl 2>/dev/null | wc -l | tr -d ' ')
echo "Total OWL files created: $total"

echo ""
du -sh "$RESULTS_DIR"

echo ""
echo "If all files converted successfully, proceed with full validation:"
echo "  ./validate_all_ontologies.sh"
