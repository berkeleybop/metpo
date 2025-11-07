# METPO Visualizations for ICBO 2025

**METPO Version:** 2025-11-07 (current production release)
**Source:** `/home/mark/gitrepos/metpo/metpo.owl`
**Generated:** 2025-11-07

## Overview

This directory contains slide-appropriate visualizations of key METPO structures for the ICBO 2025 presentation. All visualizations use the current production METPO (Nov 7, 2025 release) and were designed to be legible and informative on slides.

## Phenotype Visualizations

### aerobic_hierarchy.png (341 × 437 pixels)
Shows the oxygen preference phenotype hierarchy with context:
- **aerobic** (METPO:1000602) - Requires oxygen for growth
- Shows parent/child relationships up the hierarchy
- Includes related terms like "obligately aerobic", "facultatively aerobic"
- Good example of branching phenotype structure

### motile_hierarchy.png (341 × 417 pixels)
Shows the motility phenotype hierarchy:
- **motile** (METPO:1000702) - Capable of self-propelled movement
- Shows hierarchical context within morphological traits
- Includes specific motility types (flagellar, gliding, twitching)

### cell_shape_examples.png (1051 × 339 pixels)
Shows cell morphology phenotype examples:
- **cell shape** (METPO:1000666) parent term
- **coccus shaped** (METPO:1000668)
- **rod shaped** (METPO:1000681)
- **spiral shaped** (METPO:1000684)
- Demonstrates diversity of cell shape terms

### temperature_preference_examples.png (1405 × 319 pixels)
Shows temperature preference phenotype hierarchy:
- **temperature preference phenotype** (METPO:1000613) parent
- **psychrophilic** (METPO:1000614) - grows at low temperatures (~15°C or below)
- **mesophilic** (METPO:1000615) - grows at intermediate temperatures (~20-45°C)
- **thermophilic** (METPO:1000616) - grows at elevated temperatures (≥45°C)
- **hyperthermophilic** (METPO:1000617) - grows at very high temperatures (≥80°C)
- Shows environmental adaptation classification

## Biological Process Visualizations

### respiration_examples.png (696 × 319 pixels)
Shows respiration biological processes:
- **respiration** (METPO:1000800) parent process
- **Aerobic respiration** (METPO:1000801)
- **Anaerobic respiration** (METPO:1000802)
- Demonstrates METPO's biological process hierarchy

## Property Documentation

### key_properties.ttl
Turtle file documenting METPO's key object properties with their domains and ranges:

**Main properties:**
- `has_phenotype` (2000102): microbe → phenotype
  - Example: *E. coli* has_phenotype aerobic

- `capable_of` (2000103): microbe → biological process
  - Example: *B. subtilis* capable_of sporulation

- `organism interacts with chemical` (2000001): microbe → chemical entity
  - Root property for ~20 chemical utilization subproperties
  - Subproperties include: ferments, degrades, oxidizes, uses_as_carbon_source, etc.
  - Example: *E. coli* ferments glucose
  - Example: *P. aeruginosa* degrades toluene

**Domain classes:**
- microbe (1000525) - The organism
- chemical entity (1000526) - Chemical compounds
- phenotype (1000059) - Observable characteristics
- biological process (1000630) - Biological activities

## Technical Details

### Visualization Commands

All PNG visualizations generated using OAK (Ontology Access Kit):

```bash
# Phenotype/process hierarchies (show context up and down)
uv run runoak -i metpo.owl viz -p i <TERM_IRI> --max-hops 3 \
  -o filename.png --no-view

# Examples with multiple specific terms
uv run runoak -i metpo.owl viz -p i <IRI1> <IRI2> <IRI3> --max-hops 1 \
  -o filename.png --no-view
```

Options used:
- `-p i` - Use only is-a (rdfs:subClassOf) predicates for class hierarchies
- `--max-hops N` - Limit graph traversal distance for manageable output
- `--no-view` - Save only, don't open viewer
- Multiple IRIs can be specified to show multiple branches together

### Design Considerations

These visualizations were specifically designed for slide presentation:
- **Width < 1500 pixels** for standard slide dimensions
- **Show branching** to demonstrate ontology structure
- **Legible labels** at slide resolution
- **Representative examples** of METPO's key content areas

### Verification

All terms were verified before visualization generation:
```bash
# Always verify term labels before creating visualizations
uv run runoak -i metpo.owl info <IRI>
```

## Use for ICBO Presentation

**Key talking points:**

1. **Phenotype diversity** - aerobic, motile, cell shape, temperature visualizations show METPO's coverage of diverse microbial characteristics

2. **Semantic precision** - Hierarchical organization enables precise phenotype assertions and computational reasoning

3. **Chemical interaction modeling** - 20+ specialized properties descended from root "organism interacts with chemical" property enable fine-grained chemical utilization assertions

4. **Biological processes** - METPO models microbial processes like respiration, fermentation, sporulation

5. **Real-world utility** - These exact terms and properties are used in OntoGPT literature mining and KG-Microbe knowledge graph integration

## METPO Structure Summary

Current production METPO (Nov 7, 2025) has:
- **255 classes** (phenotypes, processes, entities)
  - 216+ quality/phenotype descendants
  - Including temperature preference, oxygen preference, morphology, motility phenotypes
- **121 properties** (20+ chemical interaction properties)
- **Standard OBO format** with definitions, synonyms, cross-references

### Root Classes
- `material entity` (1000186) - Physical microbial entities
- `quality` (1000188) - Phenotypes and characteristics
- `biological process` (1000630) - Biological processes
- `observation` - Experimental observations

For property relationships in actual data (edges between organism instances), see:
- KG-Microbe edges.tsv files
- OntoGPT extraction outputs in `ontogpt_icbo_demo/outputs/`
