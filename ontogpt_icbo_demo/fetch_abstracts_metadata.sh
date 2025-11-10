#!/bin/bash
# Fetch metadata for all input abstracts using artl-cli

OUTPUT_FILE="abstracts_metadata.json"
ARTL_CLI="/home/mark/gitrepos/metpo/.venv/bin/artl-cli"

echo "[" > "$OUTPUT_FILE"

# Extract PMIDs from filenames
first=true
for file in inputs/*-abstract.txt; do
    pmid=$(basename "$file" -abstract.txt)
    
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "$OUTPUT_FILE"
    fi
    
    echo "Fetching metadata for PMID: $pmid"
    
    # Get comprehensive metadata from EuropePMC
    $ARTL_CLI get-all-identifiers-from-europepmc --identifier "$pmid" >> "$OUTPUT_FILE" 2>&1
done

echo "" >> "$OUTPUT_FILE"
echo "]" >> "$OUTPUT_FILE"

echo "Metadata saved to $OUTPUT_FILE"
