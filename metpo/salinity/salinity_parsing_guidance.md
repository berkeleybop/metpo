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

# Salinity Prompt Refinement Notes  
*Compiled 2025‑05‑02*

The list below captures **all feedback items not yet baked into the LLM
extraction prompt**.  Use it as a checklist for the next prompt iteration.

---

## 1  Qualifier Handling
* Normalize `wt/vol`, `vol/vol`, `v/w` → **`w/v`** in `concentration_qualifier`.
* Tokens like `most`, `all`, `near`, `range` are **not** qualifiers of any kind.

## 2  Chemical Entity Rules
* Add **`broth`** to the allowed chemical list.
* Output **`NaCl`** only if it appears in `raw_text`.
* Never merge multiple salts in one row.  
  *Example*: “1 % NaCl **or** 0.5–1 % artificial sea salts” → two rows.
* Canonicalise `ASW` and `artificial sea water` to the same string.

## 3  Field Classification Fixes
| Phrase | Correct column |
|--------|----------------|
| `halophilic`, `slightly halophilic` | `categorical_description` |
| `optimum` | _none_ (ignore) |
| `most strains`, `some isolates`, etc. | `taxon_constraints` |

## 4  Row‑Splitting Rules
* Comma lists like `6 %, 0 %, 22 % (w/v)` → **one row per value**.
* Phrases like “weakly at 1 %” → separate row for the “weakly” limit.
* Mixed‑chemical statements → one row **per chemical**.

## 5  Relational & Range Parsing
* Parse relational lists:  
  * `below 3 %, above 18 %`  
  * `10 %<x<3 %`  
  * `below 0.5 %`
* Convert malformed unit strings, e.g. `19 g 1^-1` → `19 g/L`.

## 6  Whitespace Pre‑clean
* Replace thin spaces (U+2009, U+202F) with normal space **before** tokenising.

## 7  Unit Policy
* When no unit present, keep `concentration_unit = "unknown"`  
  (do **not** assume `%`).

## 8  Growth Response
* `growth_response` may remain blank when directionality is ambiguous.

---

*End of notes.*
