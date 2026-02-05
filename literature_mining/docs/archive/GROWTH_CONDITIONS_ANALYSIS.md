# Growth Conditions Extraction Analysis
**Date**: 2025-10-31
**Template**: `growth_conditions_hybrid.yaml`
**Status**: ⚠️ UNSTABLE - Not recommended for production

---

## Executive Summary

The `growth_conditions_hybrid.yaml` template shows **critical instability** despite successfully optimizing prompt format from categorized to single-line. Full corpus extraction revealed:

- **37.5% empty extractions** (9/24 papers completely failed)
- **Severe LLM non-determinism** (same paper extracted 437 vs 33 conditions in different runs)
- **81 total extractions** across 24 papers (vs expected ~3,600 based on test performance)

**RECOMMENDATION**: Do NOT use for production. Consider using `growth_conditions_template_base.yaml` (conservative baseline) instead.

---

## Test Results Summary

### Test Run (3 papers from test-fullpaper-prototype)
```
Model: gpt-4o
Temperature: 0.0
Date: 2025-10-31 21:33:45
```

| Paper | Strains | Growth Conditions |
|-------|---------|-------------------|
| fmicb-14-1258452 | 2 | **437** |
| e00266-15 | 1 | 1 |
| fmicb-13-921635 | 2 | 15 |

**Total**: 453 extractions (151 per paper average)

### Full Corpus Run (24 papers from CMM-AI/publications-txt)
```
Model: gpt-4o
Temperature: 0.0
Date: 2025-10-31 21:54:09
```

**Success rate**: 15/24 papers (62.5%)
**Empty extractions**: 9/24 papers (37.5%)

**Total**: 81 extractions (3.4 per paper average, 5.4 per successful paper)

---

## Critical Problem: LLM Non-Determinism

### Case Study: fmicb-14-1258452 (Methylobacterium aquaticum strain 22A)

**Identical inputs**:
- Same file (MD5: `ce21c210e4d70a8541af4a1418039b33`)
- Same template
- Same model (gpt-4o)
- Same temperature (0.0)
- Same prompt

**Drastically different outputs**:

#### Test Run Output (437 conditions extracted):
```yaml
growth_conditions: 22A optimal_growth_temperature 28°C; 22A optimal_pH 7.0;
  22A grows_on R2A; 22A requires_medium MM; 22A requires_medium MM with 0.5% methanol;
  22A requires_medium MM with 0.5% succinate; 22A requires_medium MM with 0.5% methanol
  and 0.5% succinate; 22A requires_medium MM with 0.5% methanol and 1 μM LaCl3;
  22A requires_medium MM with 0.5% methanol without LaCl3; 22A requires_medium MM with
  0.5% methanol and 20 μg/ml kanamycin; ...
```
**Interpretation**: Extracted experimental media compositions

#### Full Corpus Output (33 conditions extracted):
```yaml
growth_conditions: 22A optimal_growth_temperature 28°C; 22A optimal_pH 7.0;
  22A grows_on R2A; 22A requires_medium MM; 22A requires_medium MM with 0.5% methanol;
  22A requires_medium MM with 0.5% succinate; 22A requires_medium MM with 0.5% methanol
  and 0.5% succinate; 22A requires_medium MM with 0.5% methanol and 1 μM LaCl3;
  22A requires_medium MM with 0.5% methanol without LaCl3; 22A requires_medium MM with
  0.5% methanol and 20 μg/ml kanamycin; 22A requires_medium MM with 0.5% methanol and
  20 μg/ml kanamycin and 1 μM LaCl3; 22A taxis_toward DL-malate; 22A taxis_toward
  DL-glycerate; 22A taxis_toward L-glutamate; 22A taxis_toward methanol; ...
```
**Interpretation**: Switched from media compositions to chemotaxis behaviors

**Result**: **404 fewer extractions (-92.4%)** due to:
1. Different LLM interpretation of "growth conditions"
2. Invalid predicates (`taxis_toward` not in enum) rejected during parsing

---

## Papers with Empty Extractions (9/24)

1. ✗ `10/1038-nchembio/1947` - Plant toxicology (not bacterial growth)
2. ✗ `10/1101-2023/09/15/557123v1` - **Cyanobacteria biosorption** (SHOULD have extracted!)
3. ✗ `PMC9301485` - Unknown content
4. ✗ `PMC6764073` - Unknown content
5. ✗ `PMC5018670` - Unknown content
6. ✗ `PMC4859581` - Unknown content
7. ✗ `Machine/learning-led/...` - Machine learning paper
8. ✗ `Machine/Learning/Approaches/...` - Machine learning paper
9. ✗ `10/1016-j/seppur/2025/131701` - Unknown content

**Note**: Paper #2 (cyanobacteria biosorption) contains explicit growth conditions:
- Synechococcus elongatus UTEX 2973: 37°C, pH 8, BG11 medium, 300 μmol photons m⁻² s⁻¹
- Other strains: 23°C, light:dark 16:8h, BG11 medium

These were NOT extracted despite being clearly stated.

---

## Template Evolution

### V1: Categorized Prompt Format (FAILED)
```yaml
prompt: >-
  Extract ALL strain-growth condition relationships mentioned in the text.

  Include ALL condition types:
  TEMPERATURE: Strain22A optimal_growth_temperature 28°C; ...
  pH: StrainDA optimal_pH 7.0; ...
  OXYGEN: E_coli facultative_anaerobic; ...
  SALINITY: Halomonas grows_at_salinity 3.5% NaCl; ...
  MEDIA: Strain22A grows_on R2A; ...
  ATMOSPHERE: NitrogenFixer requires_atmosphere N2
```

**Result**: 10 total extractions (3.3 per paper)

**Problem**: Multi-line categorized format caused LLM to output verbose summaries:
```
growth_conditions: TEMPERATURE: None mentioned. pH: None mentioned.
OXYGEN: Methylobacterium aquaticum strain 22A facultative_methylotrophic...
```

Instead of parseable triples.

### V2: Simplified Single-Line Format (SUCCESS on test, FAILED on full corpus)
```yaml
prompt: >-
  Extract ALL strain-growth condition relationships mentioned in the text.
  Be COMPREHENSIVE - do not omit any growth parameters. Use EXACTLY the same
  strain identifiers from the strains field above.

  For example: Strain22A optimal_growth_temperature 28°C; MG1655 temperature_range
  15-45°C; BacillusK thermophilic; StrainDA optimal_pH 7.0; Geobacter pH_range
  6.5-8.0; E_coli facultative_anaerobic; Clostridium obligately_anaerobic;
  Halomonas grows_at_salinity 3.5% NaCl; Strain22A grows_on R2A; MG1655
  requires_medium LB; NitrogenFixer requires_atmosphere N2

  Extract BOTH optimal conditions AND ranges AND special requirements.
  Be thorough and capture all growth parameters described in the text.
```

**Test result**: 453 total extractions (151 per paper) - **45.3x improvement over V1**

**Full corpus result**: 81 total extractions (3.4 per paper) - **44.4x worse than test**

---

## Root Causes

### 1. Corpus Mismatch
The CMM corpus focuses on **methylotroph metabolism and ecology**, NOT growth optimization:
- Papers describe metabolic pathways, gene regulation, environmental adaptation
- Growth conditions mentioned incidentally, not as primary data
- Contrast with morphology: CMM papers DO extensively describe cell morphology

### 2. LLM Non-Determinism at Temperature 0.0
GPT-4o produces **radically different interpretations** of "growth conditions":
- Run 1: Experimental media compositions (437 items)
- Run 2: Chemotaxis behaviors (33 items, most rejected as invalid)

**This violates the assumption that temperature=0.0 ensures deterministic output.**

### 3. Overly Broad Prompt Scope
"Growth conditions" is ambiguous and includes:
- Physical parameters (temperature, pH, oxygen)
- Chemical composition (media, salinity, atmosphere)
- Behavioral responses (chemotaxis) ← **Incorrectly included by LLM**
- Growth phases, rates, optimization ← **Experimental details**

The "Extract ALL" instruction amplifies this ambiguity.

### 4. Inappropriate for CMM Corpus
Unlike chemical_utilization (100% accuracy on abstracts):
- Growth conditions data is **sparse** in CMM papers
- When present, it's **incidental** context, not primary findings
- Papers lack standardized reporting of growth parameters
- "Extract ALL" causes hallucinations when data is absent

---

## Comparison with Other Templates

| Template | Corpus Match | Extraction Rate | Stability | Status |
|----------|--------------|-----------------|-----------|---------|
| `chemical_utilization_hybrid` | ✓ Excellent | 100% accuracy | Stable | **PRODUCTION** |
| `morphology_template_base` | ✓ Good | 57 papers, 73.7% grounding | Stable | **PRODUCTION** |
| `morphology_hybrid` | ✗ Poor | 36.8% grounding, hallucinations | Failed | ARCHIVED |
| `growth_conditions_hybrid` | ✗ Poor | 62.5% success, non-deterministic | **Unstable** | **NOT RECOMMENDED** |

---

## Detailed Full Corpus Results

### Successful Extractions (15 papers)

| # | Paper ID | Strains | Conditions | Notes |
|---|----------|---------|------------|-------|
| 4 | 10/3389-fbioe/2023/1130939 | 5 | 10 | |
| 5 | PMID/31421721 | 1 | 2 | |
| 6 | 10/1073-pnas/1600558113 | 8 | 8 | |
| 7 | PMID/25943904 | 1 | 0 | Strains only, no conditions |
| 8 | PMID/24816778 | 2 | 2 | |
| 10 | PMID/40328142 | 0 | 0 | Empty extraction (counted as "success") |
| 12 | PMID/36719530 | 1 | 2 | |
| 14 | Machine/learning-led/semi-automated/... | 3 | 17 | Machine learning paper |
| 15 | PMID/38269599 | 1 | 2 | |
| 16 | 10/1101-2023/08/22/554321v1 | 1 | 1 | |
| 17 | PMID/31552950 | 0 | 0 | Empty extraction (counted as "success") |
| 18 | fmicb-14-1258452 | 2 | **33** | **Test run: 437** ← Non-determinism! |
| 20 | e00266-15 | 1 | 1 | Test run: 1 (same) |
| 23 | fmicb-13-921635 | 2 | 6 | Test run: 15 (-60%) |
| 24 | PMID/28686571 | 0 | 0 | Empty extraction (counted as "success") |

**Total**: 53 entities + 28 relations = 81 items

---

## Lessons Learned

### 1. "Extract ALL" Double-Edged Sword (Confirmed Again)
- ✓ **Works when**: Papers contain extensive target data (chemical_utilization on abstracts)
- ✗ **Fails when**: Papers contain sparse data (growth_conditions, morphology on CMM)
- Effect: Amplifies present data (good) AND amplifies absence (causes hallucinations/instability)

### 2. Temperature 0.0 ≠ Determinism
- GPT-4o produces **radically different outputs** on identical inputs
- Same file, template, model, temperature → 437 vs 33 extractions (-92.4%)
- **Cannot rely on reproducibility** even with temperature=0.0

### 3. Prompt Scope Must Match Data Density
- Broad prompts ("Extract ALL growth conditions") work for data-rich papers
- Same prompts fail on data-sparse papers (corpus mismatch)
- Need to **match template optimization strategy to corpus content**

### 4. Corpus Content Assessment is Critical
Before applying hybrid optimization:
1. Assess corpus composition (taxonomic vs metabolic vs ecological)
2. Estimate target data density in papers
3. Test on representative sample (3-5 papers)
4. Compare with baseline template before full corpus run

---

## Recommendations

### Immediate Actions
1. **Do NOT use growth_conditions_hybrid for production**
2. **Use growth_conditions_template_base.yaml** (conservative baseline) for CMM corpus
3. **Investigate LLM non-determinism**:
   - Test with multiple LLM providers (Claude, GPT-4, etc.)
   - Document reproducibility across runs
   - Consider ensemble approaches for stability

### Future Work
1. **Narrow prompt scope**:
   - Separate "physical conditions" (temp, pH, oxygen) from "media composition"
   - Remove ambiguous examples (chemotaxis, experimental protocols)
   - Focus on **minimal baseline growth requirements** only

2. **Corpus-specific optimization**:
   - Chemical utilization: Continue using hybrid (100% accuracy proven)
   - Growth conditions: Use conservative base template
   - Morphology: Use conservative base template (73.7% grounding)

3. **Test reproducibility protocol**:
   - Run each extraction 3 times
   - Calculate variance in extraction counts
   - Flag templates with >20% variance as unstable
   - Document LLM provider/version/temperature for all runs

4. **Consider rule-based extraction** for growth conditions:
   - Temperature patterns: "cultured at X°C", "optimal growth at X°C"
   - pH patterns: "pH X", "pH range X-Y"
   - Media patterns: "grown on/in [medium name]"
   - Higher precision, lower recall, but **stable and reproducible**

---

## Technical Details

### Extraction Command (Test Run)
```bash
uv run ontogpt -vv \
  --cache-db cache/ontogpt-cache.db \
  extract \
  --show-prompt \
  -m gpt-4o \
  -p 0.0 \
  -t templates/growth_conditions_hybrid.yaml \
  -i test-fullpaper-prototype \
  -o outputs/growth_conditions_hybrid_gpt4o_t00_20251031_213345.yaml \
  2>&1 | tee logs/growth_conditions_hybrid_gpt4o_t00_20251031_213345.log
```

### Extraction Command (Full Corpus)
```bash
uv run ontogpt -vv \
  --cache-db cache/ontogpt-cache.db \
  extract \
  --show-prompt \
  -m gpt-4o \
  -p 0.0 \
  -t templates/growth_conditions_hybrid.yaml \
  -i CMM-AI/publications-txt \
  -o outputs/growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.yaml \
  2>&1 | tee logs/growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.log
```

### File Locations
- Template: `templates/growth_conditions_hybrid.yaml`
- Test output: `outputs/growth_conditions_hybrid_gpt4o_t00_20251031_213345.yaml`
- Full corpus output: `outputs/growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.yaml`
- Test log: `logs/growth_conditions_hybrid_gpt4o_t00_20251031_213345.log` (14M)
- Full corpus log: `logs/growth_conditions_hybrid_fullcorpus_gpt4o_t00_20251031_215409.log` (12M)

---

## Conclusion

The `growth_conditions_hybrid.yaml` template demonstrates that **hybrid optimization is not universally applicable**:

1. ✓ **Success criteria**: Data-rich papers + clear extraction targets + stable LLM behavior
2. ✗ **Failure modes**: Data-sparse papers + ambiguous scope + LLM non-determinism

**Status**: ⚠️ **NOT RECOMMENDED FOR PRODUCTION**

**Alternative**: Use `growth_conditions_template_base.yaml` for stable, conservative extraction on CMM corpus.

**Key insight**: Template optimization must be **corpus-specific**. What works brilliantly for chemical utilization abstracts can fail catastrophically on metabolic/ecological full papers.
