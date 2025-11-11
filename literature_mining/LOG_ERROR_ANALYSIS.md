# Literature Mining Log Error Analysis

**Analysis Date:** 2025-11-11
**Analyzed By:** Claude Code
**Total Logs Analyzed:** 33 files (~421 MB before cleanup)

---

## Overview

This document summarizes all error types found in OntoGPT literature extraction logs from October-November 2025. The logs were analyzed to identify problems and determine which logs could be safely deleted.

## Log Cleanup Summary

- **Initial logs:** 33 files, ~421 MB
- **Deleted:** 7 files (API key errors), ~160 KB
- **Remaining before final cleanup:** 26 files, ~347 MB
- **Final action:** All logs deleted (extraction results preserved in YAML outputs)

---

## Error Types Found

### 1. Missing API Key Errors ❌ FATAL

**Status:** Deleted
**Files Affected:** 7 logs (73-91 KB each)
**Date Range:** November 1, 2025

**Files:**
- `growth_conditions_20251101_131400.log` through `132427.log` (6 files)
- `cmm_fullcorpus_gpt4o_t00_20251031_193816.log`

**Error Message:**
```
ERROR:ontogpt.clients.llm_client:Encountered error due to bad request:
litellm.BadRequestError: OpenAIException - You didn't provide an API key.
You need to provide your API key in an Authorization header using Bearer auth
(i.e. Authorization: Bearer YOUR_KEY)...
```

**Root Cause:**
Missing or empty `OPENAI_API_KEY` environment variable

**Impact:**
Immediate fatal failure at first API call. No data processed.

**Resolution:**
Ensure `OPENAI_API_KEY` is set in environment before running extraction scripts.

---

### 2. LLM Response Format/Parsing Errors ⚠️ NON-FATAL

**Status:** Present in successful runs
**Frequency:** ~94+ occurrences across all logs
**Impact:** Warning only - system skips malformed responses and continues

#### 2a. "Line does not contain a colon; ignoring"

**Description:**
LLM returns explanatory prose instead of structured `field: value` format.

**Common Examples:**
- "The provided text does not contain any specific information about bacterial or archaeal taxa..."
- "It seems that the text provided does not contain any relevant information..."
- "This response reflects the nature of the article as a geological study rather than a study on microbial metabolism..."
- "If you have another text or document that is relevant to microbiology, please provide it..."

**Why It Happens:**
- Input text is journal metadata, not scientific content
- PDF extraction captured paywall/subscription pages
- Wrong document type (computer science, geology, etc.)
- LLM can't find requested entities so explains why

**System Behavior:**
Logs warning, skips the line, continues processing next document.

#### 2b. "Cannot find slot for X"

**Description:**
LLM generates field names that don't exist in the extraction template schema.

**Common Examples:**
```
Cannot find slot for -_strain in - strains: No specific strain designations are mentioned...
Cannot find slot for -_chemicals_mentioned in - chemicals_mentioned: Methanol, pyrroloquinoline quinone...
Cannot find slot for based_on_the_provided_text,_here_are_the_extracted_entitie...
```

**Why It Happens:**
- LLM improvises field names not in template
- LLM uses explanatory text as field name
- Template schema mismatch

**System Behavior:**
Logs warning, skips invalid field, continues with valid fields.

---

### 3. Wrong Output Format Errors ⚠️ NON-FATAL

**Status:** Present in successful runs
**Frequency:** ~30+ occurrences
**Impact:** Warning only

**Description:**
LLM returns bullet lists instead of colon-separated `key: value` format.

**Examples:**
```
'- 22A strain_of Methylobacterium aquaticum' does not contain a colon
'- UTEX 2973 strain_of Synechococcus elongatus' does not contain a colon
'- Ler strain_of Arabidopsis thaliana' does not contain a colon
'- 22A exhibits_chemotaxis_toward methanol' does not contain a colon
```

**Why It Happens:**
LLM prefers markdown bullet lists over plain key-value pairs for readability.

**System Behavior:**
Logs warning, skips malformed lines, continues processing.

---

### 4. Model Cost Calculation Errors ⚠️ NON-FATAL

**Status:** Present in Claude Sonnet runs
**Frequency:** 21 occurrences
**Impact:** Can't calculate API costs, but extraction continues

**Error Message:**
```
This model isn't mapped yet. model=anthropic/claude-sonnet, custom_llm_provider=anthropic.
Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.
```

**Root Cause:**
LiteLLM library missing pricing data for `anthropic/claude-sonnet` model.

**Impact:**
- Can't track API costs in logs
- Extraction completes successfully
- No data loss

**Resolution:**
Update LiteLLM library or add custom pricing configuration.

---

### 5. Content Quality Errors ⚠️ NON-FATAL

**Status:** Expected in corpus processing
**Frequency:** Variable
**Impact:** Warning only - document skipped

**Description:**
Input text is not relevant scientific content for the extraction template.

**Common Scenarios:**
1. **Journal website pages:** Subscription info, editorial boards, navigation menus
2. **Wrong discipline:** Computer science, geology papers fed to microbiology templates
3. **Empty/truncated PDFs:** Incomplete downloads or paywalled content
4. **Metadata only:** Title pages, abstracts without methods/results

**Example Error Messages:**
- "The article appears to be focused on geochemistry and geology, specifically related to carbon subduction and mantle processes"
- "The paper related to computer science, specifically focusing on human-computer interaction and machine learning"
- "The provided text does not contain information related to bacterial or archaeal taxa, strain designations, or chemical compounds"

**System Behavior:**
Logs error explaining why extraction failed for that document, moves to next document.

---

## Log File Size Analysis

### Small Logs (Failed Runs)
- **Size:** 73-91 KB
- **Count:** 7 files
- **Status:** Deleted
- **Reason:** API key errors, no useful data

### Medium Logs (Partial/Short Runs)
- **Size:** 400 KB - 10 MB
- **Count:** 12 files
- **Status:** Deleted (after verification of outputs)
- **Contains:** Mix of successful and skipped extractions

### Large Logs (Full Corpus Runs)
- **Size:** 10-73 MB
- **Count:** 14 files
- **Status:** Deleted (after verification of outputs)
- **Contains:** Successful full-corpus extractions with many warnings

**Largest logs:**
1. `fullpaper_prototype_v3_20251031_163102.log` - 73 MB
2. `cmm_fullcorpus_gpt4o_t00_20251031_193935.log` - 58 MB
3. `fullpaper_hybrid_gpt4o_t03.log` - 52 MB

---

## Key Findings

### What Worked
✅ All large logs (>1 MB) completed successfully despite warnings
✅ Extraction results preserved in YAML files in `outputs/` directories
✅ System error handling is robust - gracefully skips problematic documents
✅ Multiple LLM backends working (GPT-4o, Claude Sonnet)

### What Failed
❌ Only 7 runs failed completely (missing API key)
❌ No network/timeout failures
❌ No database/storage failures

### False Alarms
- "ERROR" log lines are mostly warnings, not failures
- Parsing errors are expected when processing diverse document types
- System designed to handle malformed LLM responses

---

## Recommendations

### For Future Runs

1. **API Key Management**
   - Verify `OPENAI_API_KEY` set before starting extractions
   - Consider using `.env` file with validation script

2. **Input Filtering**
   - Pre-filter PDFs to remove journal metadata pages
   - Validate document content type before extraction
   - Skip known paywalled/subscription pages

3. **Log Management**
   - Set log level to WARNING or ERROR only (reduce INFO/DEBUG verbosity)
   - Implement log rotation (daily or by size)
   - Auto-archive logs older than 7 days
   - Keep only error summary, not full debug logs

4. **Monitoring**
   - Track only fatal errors (API failures, crashes)
   - Count successful vs skipped extractions
   - Monitor API cost separately from debug logs

5. **Template Improvements**
   - Add examples of correct format in LLM prompts
   - Penalize bullet-list responses
   - Request explicit "key: value" format

---

## Gitignore Rules Added

Added to `.gitignore` to prevent logs from being committed:

```gitignore
# Large log files from literature mining
literature_mining/logs/*.log
literature_mining/outputs/**/*.log
```

Small output logs (358-2032 bytes) in `outputs/` directories were also gitignored as they contain similar warning messages without useful debugging information.

---

## Files Preserved

**Extraction results** (not deleted):
- `literature_mining/outputs/annotator_comparison/*.yaml`
- `literature_mining/outputs/annotator_comparison_fair/*.yaml`
- `literature_mining/outputs/icbo_examples/*.yaml`

These contain the actual extracted data and are the permanent output of the literature mining pipeline.

---

## Conclusion

The literature mining pipeline is working correctly. All "ERROR" messages in logs were either:
1. Expected warnings for malformed LLM responses (handled gracefully)
2. Content quality issues (documents not matching extraction template)
3. One-time API key configuration issue (resolved)

No bugs or system failures were found. All logs can be safely deleted as extraction results are preserved in YAML output files.
