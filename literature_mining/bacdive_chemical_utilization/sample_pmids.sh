#!/bin/bash
#
# Sample random PMIDs from N4L reference mapping CSV
#
# Usage: ./sample_pmids.sh [N] [seed]
#   N:    Number of PMIDs to sample (default: 10)
#   seed: Random seed for reproducibility (optional)
#

N=${1:-10}
SEED=${2:-}
CSV_PATH="../assets/N4L_phenotypic_ontology_2016/reference_id_mapping.csv"
OUTPUT_FILE="sampled_pmids.txt"

# Check if CSV exists
if [[ ! -f "$CSV_PATH" ]]; then
    echo "Error: CSV file not found at $CSV_PATH"
    exit 1
fi

# Extract valid PMIDs (numeric only)
echo "Extracting PMIDs from $CSV_PATH..."
PMIDS=$(cut -d, -f3 "$CSV_PATH" | grep -v "^$" | grep -v "pubmedid" | grep "^[0-9]\+$")
TOTAL_PMIDS=$(echo "$PMIDS" | wc -l)

echo "Found $TOTAL_PMIDS valid PMIDs"

if [[ $N -gt $TOTAL_PMIDS ]]; then
    echo "Warning: Requested $N samples but only $TOTAL_PMIDS available"
    N=$TOTAL_PMIDS
fi

# Sample N random PMIDs
echo "Sampling $N PMIDs..."
if [[ -n "$SEED" ]]; then
    echo "Using random seed: $SEED"
    SAMPLED=$(echo "$PMIDS" | shuf --random-source=<(seq $SEED) -n $N)
else
    SAMPLED=$(echo "$PMIDS" | shuf -n $N)
fi

# Save to file
echo "$SAMPLED" > "$OUTPUT_FILE"
echo "Sampled PMIDs saved to $OUTPUT_FILE:"
echo "$SAMPLED"