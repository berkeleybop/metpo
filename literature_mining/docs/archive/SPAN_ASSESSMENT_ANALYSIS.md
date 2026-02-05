# Named Entity Span Assessment: Problems and Opportunities

## Status: DEPRIORITIZED (Focus on strain consistency and template guidance first)

## Problem Summary

The span coordinate system in OntoGPT extractions shows a systematic off-by-one truncation pattern:

### Key Findings from CBORG GPT-5 Analysis (Latest Data)
- **100% entities have spans** - good coverage of span information
- **0% perfect matches** - systematic coordinate issue, not missing spans
- **100% prefix matches** - spans point to correct locations but are truncated
- **Consistent off-by-one pattern**: All spans truncated by exactly 1 character
  - Examples: "DA-C8" → "DA-C", "JCM 34211" → "JCM 3421", "Insulambacter thermoxylanivorax" → "Insulambacter thermoxylanivora"
- **Span proximity working**: Compound expressions show meaningful distances (14-104 characters)

### Specific Patterns Observed
```
Entity: "NCBITaxon:2749268" Label: "Insulambacter thermoxylanivorax"
Span: "1731:1761" Expected: "Insulambacter thermoxylanivorax" 
Actual: "Insulambacter thermoxylanivora" ❌

Entity: "AUTO:DA-C8" Label: "DA-C8"
Spans: ["243:247", "581:585", "727:731", ...]
Expected: "DA-C8" Actual: "DA-C" (all spans) ❌

Entity: "CHEBI:17234" Label: "glucose"  
Span: "1136:1142" Expected: "glucose" Actual: "glucos" ❌
```

## Root Cause Analysis

### Likely Technical Issues
1. **Text preprocessing differences**: Extraction and span calculation may use different text processing
2. **Unicode/encoding issues**: Character counting affected by encoding differences  
3. **Tokenization boundaries**: Word/character boundaries not aligning with span coordinates
4. **Template processing**: OntoGPT may be modifying source text during processing
5. **URL encoding artifacts**: Some spans contain encoded characters (`%20`, `%3C`, etc.)

### OntoGPT Pipeline Issues
- Span calculation happens at a different stage than entity extraction
- Named entity recognition and coordinate assignment may be decoupled
- Post-processing steps may modify text after span assignment

## Current Capabilities in Unified Assessor

The span assessment functionality is implemented in `metpo_assessor.py`:

### Span Distance Analysis
- Analyzes proximity between subject-object pairs in compound expressions
- Categories: close (<100 chars), medium (100-500), far (>500), cross-section (title-body)
- **Latest Results**: 65.2% close relationships, 24.3% medium, 10.4% far

### Verbatim Traceability
- Verifies entities appear at specified span coordinates  
- Tracks content extraction success through pipeline
- **Current Status**: 100% content extraction success, 0% span verification

### Implementation Details
```python
def _assess_span_distances(self, extractions: List[Dict]) -> Dict[str, Any]
def _assess_verbatim_traceability(self, extractions: List[Dict]) -> Dict[str, Any]  
def _verify_spans(self, content: str, entity_label: str, spans: List) -> Dict[str, Any]
```

## What We Should Actually Track

### Span Coverage Metrics
- **Entities with spans vs without spans**: Track which entity types get span information
- **Span completeness**: Percentage of named entities that have `original_spans` fields
- **Multi-span entities**: Entities with multiple occurrences across the document

### Span Accuracy Patterns  
- **Perfect matches**: Exact text matches (currently 0% due to off-by-one bug)
- **Prefix matches**: Spans that capture beginning of entity correctly  
- **Truncation patterns**: Off-by-one, off-by-two, other systematic errors
- **Entity type accuracy**: Which types (CHEBI, NCBITaxon, AUTO) have better spans

### Compound Expression Proximity
- **Subject-object distances**: How close are related entities in text
- **Cross-document references**: Subject in title, object in body (good extraction)
- **Same-sentence extractions**: Very close proximities indicating tight relationships
- **Distance distribution**: Close (<100 chars), medium (100-500), far (>500), cross-section

### Diagnostic Value from Spans

#### Quality Indicators
- **Proximity suggests quality**: Closer entities likely indicate stronger relationships
- **Multi-mention consistency**: Same entity appearing multiple times with consistent spans
- **Cross-reference detection**: Title entities connected to body details

#### Problem Detection
- **Missing spans**: Entities that OntoGPT couldn't locate in source text (possible hallucinations)
- **Impossible distances**: Relationships extracted between very distant text (possible errors)
- **Inconsistent mentions**: Same entity with very different span patterns

### Research Applications
- **Model behavior analysis**: Study how different models handle entity boundary detection
- **Template optimization**: Identify which prompts lead to better span accuracy
- **Pipeline debugging**: Isolate where in OntoGPT processing spans become misaligned

## Decision: Why Deprioritized

### Higher Priority Issues Identified
1. **Strain naming consistency**: Direct impact on relationship accuracy
2. **Template guidance**: Immediate improvement to extraction quality
3. **Predicate compliance**: Core METPO ontology alignment

### Technical Investment Required  
- **Deep OntoGPT debugging**: Would require understanding internal text processing
- **Coordinate system overhaul**: Potentially complex changes to span calculation
- **Limited immediate impact**: Doesn't affect grounding or relationship extraction quality

### Resource Allocation Strategy
- Focus effort on issues that directly improve extraction accuracy
- Span precision is valuable but secondary to content accuracy
- Can revisit once core extraction quality is optimized

## Future Work (When Prioritized)

### Investigation Steps
1. **OntoGPT source analysis**: Understand span calculation implementation
2. **Text processing audit**: Compare input text at different pipeline stages  
3. **Encoding analysis**: Test with different character encodings and text formats
4. **Model comparison**: Test span accuracy across different LLM providers

### Potential Solutions
1. **Post-processing correction**: Implement span coordinate adjustment based on fuzzy matching
2. **Alternative coordinate system**: Use sentence/paragraph boundaries instead of character positions
3. **OntoGPT enhancement**: Contribute fixes upstream to improve span accuracy
4. **Fallback mechanisms**: Graceful degradation when spans are imprecise

## Monitoring

The span assessment remains active in the unified assessor to track:
- Whether span accuracy improves with different models/templates
- If specific entity types have better span precision
- Impact of template changes on coordinate accuracy

This provides ongoing visibility without active development effort.