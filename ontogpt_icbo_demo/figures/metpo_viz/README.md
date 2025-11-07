# METPO Visualizations - Production Version

**METPO Version:** 2025-10-31 (current production release)  
**Source:** `/home/mark/gitrepos/metpo/metpo.owl`  
**Generated:** 2025-11-07

## Important Note on Version

These visualizations use the **current production METPO** (Oct 31, 2025 release) from the main branch. The OntoGPT extraction outputs in this demo were generated with an earlier version (June 2025) and reference deprecated METPO IDs that have since been restructured.

## Files Generated

### 1. Overall Structure

**metpo_top_level.png** - METPO's main top-level classes
- `material entity` (1000186) - Physical microbial entities
- `quality` (1000188) - Phenotypes and characteristics  
- `biological process` (1000630) - Biological processes
- Shows immediate children (1-hop down)
- Current production METPO has 216 quality descendants

### 2. Phenotype Hierarchies

**quality_hierarchy.png** - Complete quality (phenotype) class hierarchy
- Shows all direct children of the quality root class
- 216 total phenotype/characteristic descendants in current version

**aerobic_hierarchy.png** - Oxygen relationship phenotypes
- aerobic (1000602) - Requires oxygen
- Shows hierarchical context up to quality root
- Current production IDs (different from June version used in extractions)

**motile_hierarchy.png** - Motility phenotypes  
- motile (1000702) - Capable of self-propelled movement
- Hierarchical context showing morphological trait relationships

**cell_shape_hierarchy.png** - Cell morphology phenotypes
- cell shape (1000666) with descendants
- Includes coccus, rod, spiral, filamentous, etc.

**temperature_phenotype_hierarchy.png** - Temperature adaptation phenotypes
- temperature phenotype (1000800) hierarchy
- Includes psychrophile, mesophile, thermophile classifications

## Technical Details

All visualizations generated using OAK (Ontology Access Kit):

```bash
uv run runoak -i /home/mark/gitrepos/metpo/metpo.owl viz \
  -p i <TERM_IRI> [--max-hops N] [--down] \
  -o figures/metpo_viz/filename.png --no-view
```

Options used:
- `-p i` - Use only is-a (rdfs:subClassOf) predicates
- `--max-hops N` - Limit graph traversal distance  
- `--down` - Include descendants
- `--no-view` - Save only, don't open viewer

## METPO Structure

Current production METPO has:
- **4 root classes:** material entity, quality, biological process, observation
- **216 quality (phenotype) descendants**
- Restructured IDs from earlier versions

### Properties

METPO uses standard OWL/RDFS for its class hierarchy (rdfs:subClassOf). For relationships between instances (e.g., "strain X has_phenotype motile"), applications use:
- RO (Relation Ontology) properties in production data
- See KG-Microbe edges.tsv files for actual property usage

## Version Mismatch Note

The OntoGPT extractions in `outputs/` reference IDs from June 2025 METPO (e.g., 1000008, 1000379, 1000380) which have been restructured in the October 2025 release. Current equivalent terms:
- Old 1000008 (aerobe) → Current 1000602 (aerobic)  
- Old 1000379 (motile) → Current 1000702 (motile)
- Gram staining terms removed/restructured

This demonstrates METPO's active development and refinement.

## Use for ICBO Presentation

These visualizations show METPO's **current production structure**, not the deprecated June version. For the ICBO demo:
- Use these to show current METPO organization
- Note the version evolution as evidence of active curation
- The extraction outputs represent a snapshot using an earlier version
