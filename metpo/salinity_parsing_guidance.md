# Salinity Parsing Guidance

This document summarizes the comprehensive rules and expectations for parsing `raw_text` fields describing microbial salinity growth conditions.

---

## 1. Value and Range Parsing

- Parse individual values: `2%`, `3.0 M`, `30 g/L`, `0.5 mM`, etc.
- Parse explicit ranges:
  - Hyphens: `3.0–3.5 M`, `20-80 gNaCl l-1`
  - Words: `5 to 700 mM`, `between 0.25 and 3.75%`
- Interpret relational expressions:
  - `up to 4%` → min: 0, max: 4
  - `more than 6%` or `>6%` → min: 6
  - `less than 2%` or `<2%` → max: 2

---

## 2. Value List Splitting

- Split multi-valued entries like:
  - `0, >6%` → two rows
  - `0.5, 1.5, 3.0, 4.5 or 6.0%` → five rows
  - `2, 4, 6, 8% (wt/vol), 10% (weak), 12% (weak)` → one per value
  - `5 to 700 mM (0.029–4.1%)` → one row per unit

---

## 3. Unit Normalization

- Normalize `%`, `g/L`, `mol/L`, `M`, `mM`, `mg/L`
- Accept malformed variants:
  - `"g 1^-l"` → `g/L`
  - `"mol/i"`, `"M/l"` → `mol/L`
- Accept both `2%` and `2 %`

---

## 4. Qualifier Extraction

- Extract `(w/v)`, `wt/vol` as `concentration_qualifier`
- Do not repeat these in `unparsed_text`

---

## 5. Growth Pattern & Category

- growth_pattern: `weak`, `poor`, `enhances growth`, `slight inhibition`
- categorical_description: `halophile`, `moderate halotolerance`, etc.

---

## 6. Chemical Entity Recognition

- Recognize `NaCl`, `ASW`, `artificial sea salt`, `marine salts`, etc.
- Use pipe-separated list if multiple

---

## 7. Taxon Constraints

- Extract phrases like `most strains`, `some isolates`
- Store in `taxon_constraints`

---

## 8. Growth Response

- Normalize predicate into `growth_response`:
  - `na_cl_(does_not_grow)` → `does not grow`
  - `na_cl_(grows)` → `grows`

---

## 9. Output Columns

- growth_response
- concentration_value, concentration_range_min, concentration_range_max
- concentration_unit, concentration_qualifier
- chemical_entities
- growth_pattern, categorical_description, taxon_constraints
- unparsed_text (optional, no duplication)