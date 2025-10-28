#!/bin/bash
# Validate all ontologies in /ontologies directory with ROBOT
# Generates comprehensive quality reports for ICBO abstract evidence

set +e  # Don't exit on errors, handle individually

RESULTS_DIR="validation_results"
mkdir -p "$RESULTS_DIR"

# Summary file
SUMMARY="$RESULTS_DIR/validation_summary.txt"
echo "============================================" > "$SUMMARY"
echo "ONTOLOGY VALIDATION SUMMARY" >> "$SUMMARY"
echo "Date: $(date)" >> "$SUMMARY"
echo "Working Directory: $(pwd)" >> "$SUMMARY"
echo "============================================" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# Function to validate one ontology
validate_ontology() {
    local input_file="$1"
    local ont_name="$2"

    if [ ! -f "$input_file" ]; then
        echo "Skipping $ont_name - file not found: $input_file"
        echo "$ont_name: ✗ File not found" >> "$SUMMARY"
        echo "---" >> "$SUMMARY"
        return 1
    fi

    local filesize=$(ls -lh "$input_file" | awk '{print $5}')
    echo ""
    echo "=========================================="
    echo "Validating: $ont_name ($filesize)"
    echo "Input: $input_file"
    echo "=========================================="

    local prefix="$RESULTS_DIR/${ont_name}"

    # Test 1: Can ROBOT read it?
    echo "[1/5] Testing ROBOT can read and convert..."
    if robot convert --input "$input_file" \
        --output "$prefix.converted.owl" 2>&1 | tee "$prefix.convert.log" | head -20; then
        echo "  ✓ Conversion successful"
        echo "$ont_name: ✓ Readable" >> "$SUMMARY"
    else
        echo "  ✗ CONVERSION FAILED"
        echo "$ont_name: ✗ NOT READABLE - CRITICAL FAILURE" >> "$SUMMARY"
        echo "---" >> "$SUMMARY"
        return 1
    fi

    # Test 2: Logical consistency
    echo "[2/5] Checking logical consistency (reasoning)..."
    if robot reason --reasoner ELK \
        --input "$input_file" \
        --output "$prefix.reasoned.owl" 2>&1 | tee "$prefix.reason.log" | tail -20; then
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
            2>&1 | tee -a "$prefix.reason.log" | tail -10 || true
    fi

    # Test 3: OBO quality report
    echo "[3/5] Running OBO quality report..."
    if robot report --input "$input_file" \
        --output "$prefix.report.tsv" \
        --format HTML --output "$prefix.report.html" \
        --print 10 2>&1 | tee "$prefix.report.log" | tail -30; then

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
        --output "$prefix.profile-DL.txt" 2>&1 | tee "$prefix.profile.log" | head -20; then
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
        --output "$prefix.metrics.tsv" 2>&1 | tee "$prefix.metrics.log" | head -20; then

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

echo "============================================"
echo "ONTOLOGY VALIDATION FOR ICBO 2025"
echo "============================================"
echo ""
echo "Starting validation of all ontologies..."
echo "Results will be saved to $RESULTS_DIR/"
echo ""

# List of ontologies to validate
ONTOLOGIES=(
    # METPO baseline
    "../src/ontology/metpo.owl:METPO"

    # Microbial-specific ontologies (local)
    "D3O.owl:D3O"
    "fao.owl:FAO"
    "mco.owl:MCO"
    "MicrO.owl:MicrO"
    "mpo_v0.5.owl:MPO-v0.5"
    "omp.owl:OMP"

    # High-performing ontologies from search
    "flopo.owl:FLOPO"
    "pato.owl:PATO"
    "oba.owl:OBA"
    "upheno.owl:UPHENO"
)

# Validate each ontology
for ont_spec in "${ONTOLOGIES[@]}"; do
    IFS=':' read -r file name <<< "$ont_spec"
    validate_ontology "$file" "$name"
done

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
echo "QUICK REFERENCE TABLE FOR ICBO"
echo "=========================================="
echo ""
printf "%-15s %-10s %-12s %-10s %-8s %-10s\n" "Ontology" "Readable" "Consistent" "OWL DL" "Errors" "Classes"
echo "--------------------------------------------------------------------------------"

for ont_spec in "${ONTOLOGIES[@]}"; do
    IFS=':' read -r file ont <<< "$ont_spec"

    readable=$(grep "^$ont:.*Readable" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    consistent=$(grep "^$ont:.*Consistent" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    owl_dl=$(grep "^$ont:.*OWL DL" "$SUMMARY" | grep -q "✓" && echo "✓" || echo "✗")
    errors=$(grep "^$ont:.*ERROR" "$SUMMARY" | sed 's/.*: \([0-9]*\) ERROR.*/\1/' 2>/dev/null || echo "?")
    classes=$(grep "^$ont:.*Classes=" "$SUMMARY" | sed 's/.*Classes=\([0-9]*\).*/\1/' 2>/dev/null || echo "?")

    printf "%-15s %-10s %-12s %-10s %-8s %-10s\n" "$ont" "$readable" "$consistent" "$owl_dl" "$errors" "$classes"
done

echo ""
echo "=========================================="
echo "KEY FINDINGS FOR ICBO ABSTRACT"
echo "=========================================="
echo ""

# Count failures
total=$(echo "${ONTOLOGIES[@]}" | wc -w)
not_readable=$(grep "✗ NOT READABLE" "$SUMMARY" | wc -l | tr -d ' ')
inconsistent=$(grep "✗ INCONSISTENT" "$SUMMARY" | wc -l | tr -d ' ')
invalid_dl=$(grep "✗ OWL DL INVALID" "$SUMMARY" | wc -l | tr -d ' ')

echo "Total ontologies tested: $total"
echo "Not readable by ROBOT: $not_readable"
echo "Logically inconsistent: $inconsistent"
echo "Invalid OWL DL profile: $invalid_dl"
echo ""

# Find high error counts
echo "Ontologies with high error counts (>50 ERRORs):"
grep "ERROR" "$SUMMARY" | grep -v "0 ERROR" | while read line; do
    errors=$(echo "$line" | sed 's/.*: \([0-9]*\) ERROR.*/\1/')
    if [ "$errors" -gt 50 ] 2>/dev/null; then
        echo "  $line"
    fi
done

echo ""
echo "Detailed reports available in $RESULTS_DIR/"
echo "HTML reports: $RESULTS_DIR/*.report.html"
echo ""
echo "For ICBO abstract, use:"
echo "  - Validation summary: $SUMMARY"
echo "  - Individual HTML reports for evidence"
echo "  - Quick reference table above for comparison"
