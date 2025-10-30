#!/bin/bash
# Benchmark OntoGPT extraction with comprehensive metrics collection

set -e

# Parse arguments
TEMPLATE=${1:-taxa}
MODEL=${2:-lbl/cborg-chat}
INPUT_DIR=${3:-abstracts/test-taxa-minimal}
LOG_FILE=${4:-extraction_benchmarks.tsv}

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMPLATE_FILE="templates/${TEMPLATE}_template_base.yaml"
OUTPUT_FILE="outputs/${TEMPLATE}_${MODEL//\//_}_${TIMESTAMP}.yaml"
EXTRACTION_LOG="logs/${TEMPLATE}_${MODEL//\//_}_${TIMESTAMP}.log"

echo "=========================================="
echo "OntoGPT Extraction Benchmark"
echo "=========================================="
echo "Template: $TEMPLATE"
echo "Model: $MODEL"
echo "Input: $INPUT_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY not set. Please source ~/claude-with-cborg.sh first."
    exit 1
fi

# 1. Collect input statistics
echo "Collecting input statistics..."
NUM_ABSTRACTS=$(ls -1 "$INPUT_DIR"/*.txt 2>/dev/null | wc -l | tr -d ' ')
TOTAL_CHARS=$(cat "$INPUT_DIR"/*.txt | wc -c | tr -d ' ')
TOTAL_WORDS=$(cat "$INPUT_DIR"/*.txt | wc -w | tr -d ' ')
AVG_CHARS=$((TOTAL_CHARS / NUM_ABSTRACTS))
AVG_WORDS=$((TOTAL_WORDS / NUM_ABSTRACTS))

echo "  Abstracts: $NUM_ABSTRACTS"
echo "  Total chars: $TOTAL_CHARS"
echo "  Avg chars/abstract: $AVG_CHARS"
echo "  Total words: $TOTAL_WORDS"
echo "  Avg words/abstract: $AVG_WORDS"
echo ""

# 2. Get account info and spend BEFORE extraction
echo "Querying CBORG account info (before)..."
USER_INFO=$(curl -s -X GET https://api.cborg.lbl.gov/user/info \
    -H "Authorization: Bearer $OPENAI_API_KEY")
KEY_OWNER=$(echo "$USER_INFO" | jq -r '.user_info.user_id // "unknown"')
MAX_BUDGET=$(echo "$USER_INFO" | jq -r '.user_info.max_budget // 0')
SPEND_BEFORE=$(echo "$USER_INFO" | jq -r '.user_info.spend // 0')
BUDGET_REMAINING=$(python3 -c "print(f'{$MAX_BUDGET - $SPEND_BEFORE:.2f}')")

echo "  Key owner: $KEY_OWNER"
echo "  Max budget: \$$MAX_BUDGET"
echo "  Spend before: \$$SPEND_BEFORE"
echo "  Budget remaining: \$$BUDGET_REMAINING"
echo ""

# 3. Run extraction with timing
echo "Running extraction..."
START_TIME=$(date +%s)

# Suppress LiteLLM cost estimation errors (we use CBORG API for actual costs)
export LITELLM_LOG=ERROR

uv run ontogpt -vv \
    --cache-db cache/ontogpt-cache.db \
    extract \
    --show-prompt \
    -m "$MODEL" \
    --model-provider openai \
    --api-base "https://api.cborg.lbl.gov" \
    --system-message "You are a precise data extraction system. Output ONLY the requested fields in the exact format specified. Do not add explanations, preambles, notes, or any other text. If a field has no value, write 'none' after the colon. Never leave a field completely empty." \
    -t "$TEMPLATE_FILE" \
    -i "$INPUT_DIR" \
    -o "$OUTPUT_FILE" \
    2>&1 | tee "$EXTRACTION_LOG"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo ""
echo "Extraction completed in ${DURATION}s"
echo ""

# 4. Get spend AFTER extraction
echo "Querying CBORG spend (after)..."
SPEND_AFTER=$(curl -s -X GET https://api.cborg.lbl.gov/user/info \
    -H "Authorization: Bearer $OPENAI_API_KEY" | \
    jq -r '.user_info.spend // 0')
echo "  Spend after: \$$SPEND_AFTER"

# Calculate actual input size from log file (template + abstracts across all API calls)
if [ -f "$EXTRACTION_LOG" ]; then
    TOTAL_INPUT_CHARS=$(grep "prompt\[" "$EXTRACTION_LOG" | grep -o 'prompt\[[0-9]*\]' | sed 's/prompt\[\([0-9]*\)\]/\1/' | awk '{sum+=$1} END {print sum}')
    NUM_API_CALLS=$(grep -c "prompt\[" "$EXTRACTION_LOG" || echo "0")
else
    TOTAL_INPUT_CHARS=$TOTAL_CHARS
    NUM_API_CALLS=$NUM_ABSTRACTS
fi

# Calculate cost metrics
COST=$(python3 -c "print(f'{$SPEND_AFTER - $SPEND_BEFORE:.6f}')")
COST_PER_ABSTRACT=$(python3 -c "print(f'{($SPEND_AFTER - $SPEND_BEFORE) / $NUM_ABSTRACTS:.6f}')")
COST_PER_1K_ABSTRACT_CHARS=$(python3 -c "print(f'{(($SPEND_AFTER - $SPEND_BEFORE) / $TOTAL_CHARS) * 1000:.6f}')")
COST_PER_1K_INPUT_CHARS=$(python3 -c "print(f'{(($SPEND_AFTER - $SPEND_BEFORE) / $TOTAL_INPUT_CHARS) * 1000:.6f}')")
TIME_PER_ABSTRACT=$(python3 -c "print(f'{$DURATION / $NUM_ABSTRACTS:.1f}')")
TIME_PER_1K_INPUT_CHARS=$(python3 -c "print(f'{($DURATION / $TOTAL_INPUT_CHARS) * 1000:.1f}')")

echo "  Cost: \$$COST"
echo "  Cost/abstract: \$$COST_PER_ABSTRACT"
echo "  Cost/1K abstract chars: \$$COST_PER_1K_ABSTRACT_CHARS"
echo "  Cost/1K input chars: \$$COST_PER_1K_INPUT_CHARS"
echo "  Time/abstract: ${TIME_PER_ABSTRACT}s"
echo "  Time/1K input chars: ${TIME_PER_1K_INPUT_CHARS}s"
echo "  Total input chars: $TOTAL_INPUT_CHARS (across $NUM_API_CALLS API calls)"
echo ""

# 5. Count extracted entities and relationships
echo "Analyzing extraction results..."
if [ -f "$OUTPUT_FILE" ]; then
    # Count named entities (approximate - counts all NamedEntity instances)
    TOTAL_ENTITIES=$(grep -c "NamedEntity" "$OUTPUT_FILE" || echo "0")

    # Count relationships (approximate - counts CompoundExpression instances)
    TOTAL_RELATIONSHIPS=$(grep -c "CompoundExpression" "$OUTPUT_FILE" || echo "0")

    # Try to get more accurate counts from YAML structure
    # This is template-specific - adjust as needed
    if command -v yq &> /dev/null; then
        # For taxa template specifically
        PRIMARY_TAXA=$(yq '.extracted_object.primary_taxa | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        RELATED_TAXA=$(yq '.extracted_object.related_taxa | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        STRAINS=$(yq '.extracted_object.strains | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        STRAIN_RELS=$(yq '.extracted_object.strain_relationships | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        ENV_RELS=$(yq '.extracted_object.environment_relationships | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")

        echo "  Primary taxa: $PRIMARY_TAXA"
        echo "  Related taxa: $RELATED_TAXA"
        echo "  Strains: $STRAINS"
        echo "  Strain relationships: $STRAIN_RELS"
        echo "  Environment relationships: $ENV_RELS"
    fi

    echo "  Total entities (approx): $TOTAL_ENTITIES"
    echo "  Total relationships (approx): $TOTAL_RELATIONSHIPS"
else
    TOTAL_ENTITIES=0
    TOTAL_RELATIONSHIPS=0
    echo "  WARNING: Output file not found!"
fi
echo ""

# 6. Log to TSV
echo "Logging results to $LOG_FILE..."

# Create header if file doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    echo -e "timestamp\ttemplate\tmodel\tkey_owner\tmax_budget\tbudget_remaining\tnum_abstracts\ttotal_abstract_chars\tavg_abstract_chars\ttotal_words\tavg_words\ttotal_input_chars\tnum_api_calls\ttotal_cost\tcost_per_abstract\tcost_per_1k_abstract_chars\tcost_per_1k_input_chars\ttotal_time_sec\ttime_per_abstract\ttime_per_1k_input_chars\tentities\trelationships\toutput_file\tlog_file" > "$LOG_FILE"
fi

# Append results
echo -e "${TIMESTAMP}\t${TEMPLATE}\t${MODEL}\t${KEY_OWNER}\t${MAX_BUDGET}\t${BUDGET_REMAINING}\t${NUM_ABSTRACTS}\t${TOTAL_CHARS}\t${AVG_CHARS}\t${TOTAL_WORDS}\t${AVG_WORDS}\t${TOTAL_INPUT_CHARS}\t${NUM_API_CALLS}\t${COST}\t${COST_PER_ABSTRACT}\t${COST_PER_1K_ABSTRACT_CHARS}\t${COST_PER_1K_INPUT_CHARS}\t${DURATION}\t${TIME_PER_ABSTRACT}\t${TIME_PER_1K_INPUT_CHARS}\t${TOTAL_ENTITIES}\t${TOTAL_RELATIONSHIPS}\t${OUTPUT_FILE}\t${EXTRACTION_LOG}" >> "$LOG_FILE"

echo "✅ Benchmark complete!"
echo ""
echo "Summary:"
echo "  Abstracts: $NUM_ABSTRACTS (${TOTAL_CHARS} chars, ${TOTAL_INPUT_CHARS} input chars across ${NUM_API_CALLS} API calls)"
echo "  Cost: \$$COST"
echo "    - \$${COST_PER_ABSTRACT}/abstract"
echo "    - \$${COST_PER_1K_ABSTRACT_CHARS}/1K abstract chars"
echo "    - \$${COST_PER_1K_INPUT_CHARS}/1K input chars (template + abstract)"
echo "  Time: ${DURATION}s"
echo "    - ${TIME_PER_ABSTRACT}s/abstract"
echo "    - ${TIME_PER_1K_INPUT_CHARS}s/1K input chars"
echo "  Entities: $TOTAL_ENTITIES"
echo "  Relationships: $TOTAL_RELATIONSHIPS"
echo ""
echo "Results logged to: $LOG_FILE"
echo "Output: $OUTPUT_FILE"
echo "Log: $EXTRACTION_LOG"
