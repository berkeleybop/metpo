# BactoTraits Naming Reference

**Quick reference for BactoTraits file versions and naming conventions**

---

## Version Euphemisms

When referring to BactoTraits data in documentation, code, or conversation, use these standard terms:

### **"provider"** or **"provider version"**
- **Filename:** `BactoTraits_databaseV2_Jun2022.csv`
- **Euphemism:** "original provider file"
- **Source:** https://ordar.otelo.univ-lorraine.fr/files/ORDAR-53/
- **Field mapping key:** `provider.field_name`

### **"kg-microbe"** or **"processed version"**
- **Filename:** `BactoTraits.tsv`
- **Euphemism:** "processed TSV file"
- **Location:** `kg_microbe/transform_utils/bactotraits/tmp/`
- **Field mapping key:** `kg_microbe_field`

### **"mongodb"** or **"current MongoDB version"**
- **Collection:** `bactotraits.bactotraits`
- **Euphemism:** "current MongoDB collection"
- **Field mapping key:** `mongodb_field`

### **"sanitized"** or **"proposed sanitized"**
- **Status:** Not yet implemented
- **Euphemism:** "proposed sanitized fields"
- **Field mapping key:** `sanitized_field`

---

## File Locations

Multiple copies exist in different locations with the same sizes:

### Provider CSV
```
/Users/MAM/Documents/gitrepos/metpo/downloads/BactoTraits_databaseV2_Jun2022.csv
/Users/MAM/Documents/gitrepos/kg-microbe/data/raw/BactoTraits_databaseV2_Jun2022.csv
```

### kg-microbe TSV
```
/Users/MAM/culturebot/kg-microbe/kg_microbe/transform_utils/bactotraits/tmp/BactoTraits.tsv
/Users/MAM/Documents/gitrepos/kg-microbe/kg_microbe/transform_utils/bactotraits/tmp/BactoTraits.tsv
```

---

## MongoDB Collections Reference

### bactotraits.file_versions
**Purpose:** Documents file versions and naming conventions

**Query examples:**
```javascript
// Get all version euphemisms
db.file_versions.find(
  {version_key: {$ne: "_metadata"}},
  {version_key: 1, euphemism: 1, filename: 1}
)

// Get details for specific version
db.file_versions.findOne({version_key: "provider"})
```

### bactotraits.field_mappings
**Purpose:** Maps field names across all versions

**Query examples:**
```javascript
// Look up a specific field across versions
db.field_mappings.findOne({mongodb_field: "pHO_7_to_8"})

// Find all fields needing sanitization
db.field_mappings.find({
  $expr: {$ne: ["$mongodb_field", "$sanitized_field"]}
})
```

### bactotraits.bactotraits
**Purpose:** The actual BactoTraits data

**Query examples:**
```javascript
// Get a sample document
db.bactotraits.findOne({}, {_id: 0})

// Count organisms with aerobic oxygen preference
db.bactotraits.countDocuments({Ox_aerobic: "1"})
```

---

## Standardized Terminology for Documentation

When writing docs or discussing the data, use these phrases consistently:

| Context | Preferred Term | Example |
|---------|---------------|---------|
| Original CSV | "provider version" | "The provider version has a 3-row header structure" |
| Cleaned TSV | "kg-microbe version" or "processed version" | "The kg-microbe version removes the category row" |
| MongoDB data | "MongoDB version" or "current collection" | "The MongoDB version has periods converted to underscores" |
| Proposed clean | "sanitized version" | "The sanitized version removes all leading spaces" |
| Field name reference | Use version key from field_mappings | "See field_mappings.mongodb_field for current names" |

---

## Cross-Referencing Versions

Use the `field_mappings` collection to cross-reference field names:

```javascript
// Find what provider called a MongoDB field
db.field_mappings.findOne(
  {mongodb_field: "pHd_lte_1"},
  {"provider.field_name": 1}
)
// Returns: "pHd_<=1"

// Find sanitized name for a provider field
db.field_mappings.findOne(
  {"provider.field_name": " S_rod"},
  {sanitized_field: 1}
)
// Returns: "S_rod" (space removed)
```

---

## Examples in Context

### In Documentation
> "The **provider version** (`BactoTraits_databaseV2_Jun2022.csv`) contains 105 columns with a 3-row header structure. The **kg-microbe version** simplifies this to a single header row while preserving field names from the provider's row 3."

### In Code Comments
```python
# Read field name from provider version
provider_field = mapping['provider']['field_name']

# Map to current MongoDB field
mongodb_field = mapping['mongodb_field']

# Get proposed sanitized name
sanitized_field = mapping['sanitized_field']
```

### In Conversation
> "Are you referring to the **provider version** or the **kg-microbe version**? The provider still has periods in field names, but kg-microbe keeps those. Only when we import to MongoDB do the periods become underscores."

---

## Related Documentation

- **Field Mappings:** `docs/bactotraits_header_mapping.md`
- **Data Sources:** `docs/data_sources_formats_and_reconciliation.md`
- **Size Analysis:** `docs/bactotraits_size_reduction_analysis.md`
- **Scripts:**
  - `src/scripts/create_bactotraits_header_mapping.py`
  - `src/scripts/create_bactotraits_file_versions.py`
