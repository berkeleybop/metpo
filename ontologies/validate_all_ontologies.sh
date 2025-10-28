#!/bin/bash
# Validate all ontologies in large/owl directory with ROBOT
# Generates comprehensive quality reports for ICBO abstract evidence

set -e  # Exit on error for critical failures, but we'll handle individually

RESULTS_DIR="validation_results"
mkdir -p "$RESULTS_DIR"

# Summary file
SUMMARY="$RESULTS_DIR/validation_summary.txt"
echo "============================================" > "$SUMMARY"
echo "ONTOLOGY VALIDATION SUMMARY" >> "$SUMMARY"
echo "Date: $(date)" >> "$SUMMARY"
echo "============================================" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Function to validate one ontology
validate_ontology() {
    local input_file="$1"
    local ont_name="$2"

    echo ""
    echo "=========================================="
    echo "Validating: $ont_name"
    echo "Input: $input_file"
    echo "=========================================="

    local prefix="$RESULTS_DIR/${ont_name}"

    # Test 1: Can ROBOT read it?
    echo "[1/5] Testing ROBOT can read and convert..."
    if robot convert --input "$input_file" \
        --output "$prefix.converted.owl" 2>&1 | tee "$prefix.convert.log"; then
        echo "  ✓ Conversion successful"
        echo "$ont_name: ✓ Readable" >> "$SUMMARY"
    else
        echo "  ✗ CONVERSION FAILED"
        echo "$ont_name: ✗ NOT READABLE - CRITICAL FAILURE" >> "$SUMMARY"
        return 1
    fi

    # Test 2: Logical consistency
    echo "[2/5] Checking logical consistency (reasoning)..."
    if robot reason --reasoner ELK \
        --input "$input_file" \
        --output "$prefix.reasoned.owl" 2>&1 | tee "$prefix.reason.log"; then
        echo "  ✓ Reasoning passed (logically consistent)"
        echo "$ont_name: ✓ Consistent" >> "$SUMMARY"
    else
        local exit_code=$?
        echo "  ✗ REASONING FAILED (exit code: $exit_code)"
        echo "$ont_name: ✗ INCONSISTENT/UNSATISFIABLE" >> "$SUMMARY"

        # Try to dump unsatisfiable classes for debugging
        echo "  Attempting to dump unsatisfiable classes..."
        robot reason --reasoner ELK \
            --input "$input_file" \
            --dump-unsatisfiable "$prefix.unsatisfiable.owl" \
            2>&1 | tee -a "$prefix.reason.log" || true
    fi

    # Test 3: OBO quality report
    echo "[3/5] Running OBO quality report..."
    if robot report --input "$input_file" \
        --output "$prefix.report.tsv" \
        --format HTML --output "$prefix.report.html" \
        --print 10 2>&1 | tee "$prefix.report.log"; then

        # Count violations
        local errors=$(grep -c "^ERROR" "$prefix.report.tsv" 2>/dev/null || echo "0")
        local warns=$(grep -c "^WARN" "$prefix.report.tsv" 2>/dev/null || echo "0")
        local infos=$(grep -c "^INFO" "$prefix.report.tsv" 2>/dev/null || echo "0")

        echo "  Violations: $errors ERRORs, $warns WARNs, $infos INFOs"
        echo "$ont_name: $errors ERRORs, $warns WARNs, $infos INFOs" >> "$SUMMARY"
    else
        echo "  ✗ Report generation failed"
        echo "$ont_name: ✗ Report failed" >> "$SUMMARY"
    fi

    # Test 4: OWL DL profile validation
    echo "[4/5] Validating OWL DL profile..."
    if robot validate-profile --profile DL \
        --input "$input_file" \
        --output "$prefix.profile-DL.txt" 2>&1 | tee "$prefix.profile.log"; then
        echo "  ✓ OWL DL profile valid"
        echo "$ont_name: ✓ OWL DL valid" >> "$SUMMARY"
    else
        echo "  ✗ OWL DL profile violations detected"
        echo "$ont_name: ✗ OWL DL INVALID" >> "$SUMMARY"
    fi

    # Test 5: Metrics
    echo "[5/5] Collecting metrics..."
    if robot measure --input "$input_file" \
        --metrics extended \
        --output "$prefix.metrics.tsv" 2>&1 | tee "$prefix.metrics.log"; then

        # Try to extract key metrics
        if [ -f "$prefix.metrics.tsv" ]; then
            local classes=$(awk -F'\t' '/^Classes/ {print $2}' "$prefix.metrics.tsv" || echo "?")
            local axioms=$(awk -F'\t' '/^Axioms/ {print $2}' "$prefix.metrics.tsv" || echo "?")
            echo "  Classes: $classes, Axioms: $axioms"
            echo "$ont_name: Classes=$classes, Axioms=$axioms" >> "$SUMMARY"
        fi
    else
        echo "  ⚠ Metrics collection failed (non-critical)"
    fi

    echo ""
    echo "$ont_name validation complete. Results in $RESULTS_DIR/"
    echo "---" >> "$SUMMARY"
}

# Main execution

echo "Starting validation of all ontologies..."
echo "Results will be saved to $RESULTS_DIR/"
echo ""

# Handle gzipped files first
echo "Decompressing gzipped ontologies..."
for gz_file in *.owl.gz; do
    if [ -f "$gz_file" ]; then
        base="${gz_file%.gz}"
        if [ ! -f "$RESULTS_DIR/$base" ]; then
            echo "  Decompressing $gz_file..."
            gunzip -c "$gz_file" > "$RESULTS_DIR/$base"
        fi
    fi
done

# Validate METPO (our baseline)
echo ""
echo "=========================================="
echo "VALIDATING METPO (BASELINE)"
echo "=========================================="
validate_ontology "../../src/ontology/metpo.owl" "METPO"

# Validate each ontology
validate_ontology "D3O.owl" "D3O"
validate_ontology "fao.owl" "FAO"
validate_ontology "mco.owl" "MCO"
validate_ontology "$RESULTS_DIR/MicrO-2025-03-20-merged.owl" "MicrO-2025"
validate_ontology "$RESULTS_DIR/MicrO-for-metpo.owl" "MicrO-for-metpo"
validate_ontology "mpo_v0.74.en_only.owl" "MPO"
validate_ontology "n4l_merged.owl" "N4L"
validate_ontology "omp.owl" "OMP"

# Generate final summary
echo ""
echo "=========================================="
echo "VALIDATION COMPLETE"
echo "=========================================="
echo ""
echo "Summary written to: $SUMMARY"
echo ""
cat "$SUMMARY"

# Create a quick reference table
echo ""
echo "=========================================="
echo "QUICK REFERENCE TABLE"
echo "=========================================="
echo ""
printf "%-20s %-12s %-12s %-12s %-8s\n" "Ontology" "Readable" "Consistent" "OWL DL" "Errors"
echo "--------------------------------------------------------------------------------"

for ont in METPO D3O FAO MCO MicrO-2025 MicrO-for-metpo MPO N4L OMP; do
    readable=$(grep "^$ont:.*Readable" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    consistent=$(grep "^$ont:.*Consistent" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    owl_dl=$(grep "^$ont:.*OWL DL" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    errors=$(grep "^$ont:.*ERROR" "$SUMMARY" | sed 's/.*: \([0-9]*\) ERROR.*/\1/' || echo "?")

    printf "%-20s %-12s %-12s %-12s %-8s\n" "$ont" "$readable" "$consistent" "$owl_dl" "$errors"
done

echo ""
echo "Detailed reports available in $RESULTS_DIR/"
echo "HTML reports: $RESULTS_DIR/*.report.html"
