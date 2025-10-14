# Workflow Gaps and Inconsistencies Analysis

**Date**: 2025-10-14
**Purpose**: Complete audit of BactoTraits and Madin workflows for reproducibility refactoring

---

## Critical Issues Found

### 1. **Madin Workflow - Wrong Input File** ⚠️ CRITICAL
**Location**: `Makefile:65-66`
```makefile
import-madin: local/madin.madin_decomposed_2025-09-29-19-18-EDT.csv
	mongoimport --db madin --collection madin --type csv --file $< --headerline --drop
```

**Problem**: Using decomposed file (234 rows) instead of full dataset
**Reality**: Should use `local/madin/madin_etal.csv` (172,324 rows)
**Impact**: MongoDB would have wrong/incomplete data if re-imported

### 2. **Madin Workflow - Wrong Script Path** ⚠️ CRITICAL
**Location**: `Makefile:58-62`
```makefile
reports/madin-metpo-reconciliation.yaml: reports/synonym-sources.tsv
	uv run python src/scripts/reconcile_madin_coverage.py \
		--mode integrated \
		--format yaml \
		--output $@
```

**Problems**:
- Path `src/scripts/reconcile_madin_coverage.py` doesn't exist
- Actual location: `metpo/scripts/reconcile_madin_coverage.py`
- Not using CLI alias (calling Python directly)
**Impact**: Make target will fail

### 3. **Madin Script - Missing CLI Alias** ⚠️ HIGH PRIORITY
**Location**: `pyproject.toml` (missing entry)

**Problem**: No CLI alias for `reconcile-madin-coverage`
**Reality**: Script has click CLI fully implemented (lines 680-729)
**Impact**: Can't use `uv run reconcile-madin-coverage`

### 4. **BactoTraits - Inconsistent File Paths** ⚠️ MEDIUM
**Locations**: Multiple

**Current state**:
- Actual file: `local/bactotraits/BactoTraits.tsv`
- Makefile line 78 expects: `local/BactoTraits.tsv` (doesn't exist!)
- import_bactotraits.py default: `Path("local/BactoTraits.tsv")` (doesn't exist!)

**Impact**: Workflows reference non-existent files (but might work via CLI overrides)

---

## Missing Cleanup Targets

### 5. **No `clean-bactotraits-db` Target** ⚠️ HIGH PRIORITY
**Needed**: Drop bactotraits.bactotraits collection from MongoDB
**Current state**: `clean-madin-db` exists, but no equivalent for BactoTraits
**Pattern**:
```makefile
clean-bactotraits-db:
	mongosh bactotraits --eval 'db.bactotraits.drop()'
```

### 6. **No `clean-reports` Target** ⚠️ HIGH PRIORITY
**Needed**: Remove all generated YAML reports
**Files to clean**:
- `reports/synonym-sources.tsv`
- `reports/bactotraits-metpo-set-diff.yaml`
- `reports/bactotraits-metpo-reconciliation.yaml`
- `reports/madin-metpo-reconciliation.yaml`

### 7. **No Convenience Targets** ⚠️ MEDIUM
**Missing targets**:
- `clean-all` - Run all clean targets
- `import-all` - Import both datasets
- `all-reports` - Generate all reports
- `test-workflow` - Full reproducibility test

---

## File Organization Issues

### 8. **Data Files in Wrong Locations** ⚠️ LOW
**Current**: Data files in subdirectories (`local/bactotraits/`, `local/madin/`)
**References**: Scripts/Makefile expect files at `local/` root
**Inconsistency**: Not clear if subdirectories or root is the standard

---

## Workflow Summary

### BactoTraits Workflow Status: ⚠️ PARTIALLY BROKEN

**Working**:
- ✅ Script moved to `metpo/scripts/`
- ✅ Click CLI implemented
- ✅ CLI aliases in `pyproject.toml`
- ✅ Makefile uses aliases

**Broken/Missing**:
- ❌ File path inconsistency (`local/` vs `local/bactotraits/`)
- ❌ No `clean-bactotraits-db` target
- ❌ No `clean-reports` target
- ❌ Makefile dependency on `local/BactoTraits.tsv` that doesn't exist (line 76)

**Currently works because**: CLI tools have defaults that might be overridden at runtime

### Madin Workflow Status: ⚠️ COMPLETELY BROKEN

**Working**:
- ✅ Script has Click CLI fully implemented
- ✅ Script moved to `metpo/scripts/`
- ✅ `import-madin` target exists
- ✅ `clean-madin-db` target exists

**Broken/Missing**:
- ❌ **CRITICAL**: `import-madin` uses wrong file (decomposed CSV instead of madin_etal.csv)
- ❌ **CRITICAL**: Makefile calls script from wrong path (`src/scripts/` not `metpo/scripts/`)
- ❌ Missing CLI alias in `pyproject.toml`
- ❌ Makefile calls script directly instead of using alias
- ❌ No `clean-reports` target

**Cannot work**: Make target will fail due to wrong script path

---

## Recommendations - Priority Order

### Phase 1: Fix Critical Blockers
1. ✅ Fix `import-madin` to use correct file: `local/madin/madin_etal.csv`
2. ✅ Add `reconcile-madin-coverage` CLI alias to `pyproject.toml`
3. ✅ Fix Makefile to use CLI alias instead of direct Python call

### Phase 2: Complete Cleanup Infrastructure
4. ✅ Add `clean-bactotraits-db` target
5. ✅ Add `clean-reports` target
6. ✅ Add `clean-all` convenience target

### Phase 3: Fix File Path Consistency
7. ✅ Standardize on data file locations (choose: `local/<dataset>/` or `local/` root)
8. ✅ Update all references consistently (Makefile, script defaults, documentation)

### Phase 4: Add Convenience & Testing
9. ✅ Add `import-all` target
10. ✅ Add `all-reports` target
11. ✅ Add `test-workflow` target for full reproducibility check
12. ✅ Document the complete workflow in README

---

## Test Plan

After fixes, verify complete reproducibility:

```bash
# Clean everything
make clean-all

# Import both datasets
make import-all

# Generate all reports
make all-reports

# Verify MongoDB contents
mongosh bactotraits --eval 'db.bactotraits.countDocuments({})'
mongosh madin --eval 'db.madin.countDocuments({})'

# Verify report files exist
ls -lh reports/*.yaml reports/*.tsv
```

Expected results:
- BactoTraits: ~13,000 documents
- Madin: 172,324 documents
- All 4 reports generated successfully
