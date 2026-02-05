# Range Metadata Column Design for minimal_classes.tsv

## Approach: Separate Data Columns + Formula Column

### New Columns to Add

| Column Name | ROBOT Directive | Description | Example Values |
|-------------|-----------------|-------------|----------------|
| `measurement_unit_ucum` | *(blank)* | UCUM unit code or UOM URL | `Cel`, `%`, *(empty for pH/GC)* |
| `range_min` | *(blank)* | Minimum value (float) | `5`, `22`, `1` |
| `range_max` | *(blank)* | Maximum value (float) | `9`, `27`, `3` |
| `equivalent_class_formula` | `EC %` | Google Sheets formula combining the above | *(see formulas below)* |

### ROBOT Template Row (Row 2)

```tsv
ID	label	...	measurement_unit_ucum		range_min		range_max		equivalent_class_formula
ID	LABEL	...			(blank)					(blank)			(blank)			EC %
```

## Google Sheets Formula Logic

The `equivalent_class_formula` column will contain a formula like:

```excel
=IF(AND(ISBLANK(range_min), ISBLANK(range_max)),
    "",
    IF(AND(NOT(ISBLANK(range_min)), NOT(ISBLANK(range_max))),
        "'has measurement value' some float[>= " & range_min & " , <= " & range_max & "]",
        IF(NOT(ISBLANK(range_max)),
            "'has measurement value' some float[<= " & range_max & "]",
            "'has measurement value' some float[>= " & range_min & "]"
        )
    )
)
```

### Simplified Formula (assuming both min and max are always present)

```excel
=IF(AND(NOT(ISBLANK(range_min)), NOT(ISBLANK(range_max))),
    "'has measurement value' some float[>= " & range_min & " , <= " & range_max & "]",
    ""
)
```

## Example Rows

### Example 1: pH delta high
```
ID: METPO:1000478
label: pH delta high
measurement_unit_ucum: [empty - pH is unitless]
range_min: 5
range_max: 9
equivalent_class_formula: 'has measurement value' some float[>= 5 , <= 9]
```

### Example 2: temperature optimum low
```
ID: METPO:1000442
label: temperature optimum low
measurement_unit_ucum: Cel
range_min: 10
range_max: 22
equivalent_class_formula: 'has measurement value' some float[>= 10 , <= 22]
```

### Example 3: NaCl optimum mid1
```
ID: METPO:1000466
label: NaCl optimum mid1
measurement_unit_ucum: %
range_min: 1
range_max: 3
equivalent_class_formula: 'has measurement value' some float[>= 1 , <= 3]
```

### Example 4: GC mid1
```
ID: METPO:1000430
label: GC mid1
measurement_unit_ucum: [empty - GC% is unitless or redundant]
range_min: 42.65
range_max: 57
equivalent_class_formula: 'has measurement value' some float[>= 42.65 , <= 57]
```

### Example 5: Parent class (no range)
```
ID: METPO:1000331
label: pH optimum
measurement_unit_ucum: [empty]
range_min: [empty]
range_max: [empty]
equivalent_class_formula: [empty - no formula result]
```

## UCUM Unit Mapping

### Units from BactoTraits.tsv → UCUM/UOM

| BactoTraits Unit | UCUM Code | UOM URL | Usage |
|------------------|-----------|---------|-------|
| `C` | `Cel` | https://units-of-measurement.org/Cel | Temperature classes |
| `% NaCl` | `%` | https://units-of-measurement.org/% | NaCl concentration |
| `pH` | *(none)* | *(none)* | pH is unitless (H+ activity) |
| `% GC` | *(none)* | *(none)* | GC% is a ratio (unitless) |

**Note:** We can add the `measurement_unit_ucum` as an annotation property later if needed, but it's not required for the EquivalentClass axiom to work.

## Unit Annotations (Optional Future Enhancement)

If you want to add unit annotations using IAO:0000039 (measurement unit label):

```tsv
measurement_unit_label | A IAO:0000039
```

With values like:
- `degree Celsius` (for temperature)
- `percent` (for NaCl)
- *(leave empty for pH and GC)*

Or using IAO:0000040 (has measurement unit label) with UOM URLs:
```tsv
measurement_unit_uom | A IAO:0000040
```

With values like:
- `https://units-of-measurement.org/Cel`
- `https://units-of-measurement.org/%`

## Implementation Steps

1. **Add new columns** to minimal_classes Google Sheet:
   - `measurement_unit_ucum` (column header)
   - `range_min` (column header)
   - `range_max` (column header)
   - `equivalent_class_formula` (column header)

2. **Update ROBOT template row** (row 2):
   - Leave the first three blank: `(blank)`
   - Add `EC %` for the formula column

3. **Populate data** for 60 classes:
   - Extract from bactotraits.tsv using migration script
   - Map units: `C` → `Cel`, `% NaCl` → `%`, `pH` → *(empty)*, `% GC` → *(empty)*

4. **Add Google Sheets formula** to `equivalent_class_formula` column:
   - Use the formula shown above
   - Apply to all 60 classes with range data

5. **Test download and build**:
   ```bash
   make download-all-sheets
   cd src/ontology && make metpo.owl
   ```

6. **Validate** with SPARQL:
   ```sparql
   SELECT ?class ?equiv WHERE {
     ?class owl:equivalentClass ?equiv .
     ?equiv a owl:Restriction .
     ?equiv owl:onProperty <http://purl.obolibrary.org/obo/IAO_0000004> .
   }
   ```

## Benefits of This Approach

✅ **Human-readable**: Min, max, and units are in separate columns
✅ **Maintainable**: Easy to update values without touching formula
✅ **Auditable**: Can see source data clearly
✅ **ROBOT-compatible**: Formula column produces valid Manchester syntax
✅ **Flexible**: Can add unit annotations later without restructuring
✅ **Google Sheets native**: Uses built-in formula functionality

## Questions to Resolve

1. Do we need unit annotations (IAO:0000039) or just the EquivalentClass axiom?
2. Should `measurement_unit_ucum` be included in the TSV or just documentation?
3. Should parent classes have any special annotations (e.g., "this is a grouping class")?
