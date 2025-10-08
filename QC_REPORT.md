# METPO Sheets QC Report

**Date**: 2025-10-08
**Sheets analyzed**: metpo_sheet.tsv, metpo-properties.tsv

## Executive Summary

**Status**: ❌ FAILED - 2 errors

**Critical Issues**:
1. 2 self-referential parent properties (rows 145, 146 in metpo-properties.tsv)

## Detailed Findings

### 1. Stub Definitions - NOT AN ERROR ✅

The properties sheet contains 26 "stub" class definitions that appear to duplicate classes from the main sheet. **This is intentional and correct** for the build process.

| ID | Label | metpo_sheet.tsv row | metpo-properties.tsv row (stub) |
|----|-------|---------------------|---------------------------------|
| METPO:1000059 | phenotype | 3 | 5 |
| METPO:1000188 | quality | 7 | 6 |
| METPO:1000525 | microbe | 74 | 7 |
| METPO:1000526 | chemical entity | 75 | 8 |
| METPO:1000630 | biological process | 105 | 9 |
| METPO:1001000 | observation | 193 | 10 |
| ... and 20 more observation subclasses ... | | |

**Why this is OK**: The stubs in metpo-properties.tsv allow ROBOT template to use labels (like "microbe", "chemical entity") in DOMAIN and RANGE columns. These reference the full definitions in metpo_sheet.tsv.

### 2. Self-Referential Parents (2 errors) ❌

Two properties reference themselves as their parent:

| ID | Label | Row | Issue |
|----|-------|-----|-------|
| METPO:2000511 | has observation | 145 | Parent property column says "has observation" (its own label) |
| METPO:2000512 | has oxygen observation | 146 | Parent property column says "has oxygen observation" (its own label) |

**Root Cause**: Parent property column contains the property's own label instead of a different parent.

**Impact**:
- Creates circular hierarchy
- Will fail reasoning/validation
- **This is likely causing the ROBOT build errors**

## Recommendations

### Fix: Correct Self-Referential Parents ❌ REQUIRED

**Row 145** (METPO:2000511 "has observation"):
- **Current parent**: "has observation" (self-referential)
- **Suggested fix**: Remove parent value (leave blank) - make it a top-level property

**Row 146** (METPO:2000512 "has oxygen observation"):
- **Current parent**: "has oxygen observation" (self-referential)
- **Suggested fix**: Change to "has observation" (or leave blank if no parent intended)

### After Fixes: Verify Build

```bash
cd src/ontology
./run.sh make squeaky-clean
./run.sh make all
```

Should build without errors if self-referential parents are fixed.

## QC Script Usage

Run anytime to check for issues:

```bash
# Check downloaded sheets
python qc_metpo_sheets.py --download

# Check local files
python qc_metpo_sheets.py metpo_sheet.tsv metpo-properties.tsv
```

The QC script now correctly recognizes stub definitions and does NOT report them as errors.

## Technical Details

### Why Stub Definitions Are Needed

ROBOT template supports **label resolution** in DOMAIN, RANGE, and parent property columns. When you write:

```
RANGE: chemical entity
```

ROBOT looks up the label "chemical entity" and resolves it to the entity with that label. The stub definitions in metpo-properties.tsv ensure these labels are available during the properties sheet build, even though the full definitions exist in metpo_sheet.tsv.

**Build process**:
1. metpo_sheet.tsv → components/metpo_sheet.owl (full class definitions)
2. metpo-properties.tsv → components/metpo-properties.owl (properties + stub references)
3. Merge components → final ontology

The stubs act as forward declarations, allowing the properties component to be built independently.

## Conclusion

The build errors are **likely caused by the 2 self-referential parents** in rows 145-146 of metpo-properties.tsv.

**Action required**:
1. ❌ Fix row 145 (METPO:2000511): Remove parent value or set to different property
2. ❌ Fix row 146 (METPO:2000512): Change to "has observation" or remove parent

**NOT required**:
- ✅ Stub definitions are correct and needed - keep them

Run `python qc_metpo_sheets.py --download` after making changes to verify the fixes.
