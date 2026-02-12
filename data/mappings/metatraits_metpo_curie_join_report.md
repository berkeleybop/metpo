# MetaTraits-to-METPO CURIE Join Report
**Date:** 2026-02-12
**Method:** Deterministic CURIE set intersection + METPO property synonym resolution

## Input Summary

| Source | Count |
|--------|------:|
| MetaTraits cards total | 2860 |
| Base (uncomposed) traits | 81 |
| Composed traits | 2779 |
| METPO CURIE cross-references | 226 |
| Unique bridging CURIEs in METPO | 165 |
| METPO object properties with synonyms | 28 |
| Generic CURIEs excluded | 5 |

## SSSOM Mapping Results

| Metric | Count |
|--------|------:|
| Total mappings (deduplicated) | 250 |
| Base trait mappings | 35 |
| Composed trait mappings | 216 |
| Base traits unmatched | 55 / 81 |
| Composed traits unmatched | 2573 / 2779 |
| Unique MetaTraits terms mapped | 231 |
| Unique METPO terms matched | 28 |

### Predicate Distribution

| Predicate | Count | % |
|-----------|------:|--:|
| `skos:closeMatch` | 247 | 98.8% |
| `skos:relatedMatch` | 3 | 1.2% |

## KGX Edge Template Results

METPO object properties resolved from MetaTraits base categories via synonym matching.

| Metric | Count |
|--------|------:|
| KGX edge templates generated | 2557 |
| With CHEBI object | 2163 |
| Without CHEBI object | 394 |
| Categories resolved to METPO property | 25 |
| Categories unresolved | 6 |

### Category → METPO Property Resolution

| MetaTraits Category | METPO Predicate (+) | METPO Predicate (-) | Composed Traits |
|--------------------|--------------------|--------------------|---------:|
| produces | `METPO:2000202` produces | `METPO:2000222` does not produce | 499 |
| carbon source | `METPO:2000006` uses as carbon source | `METPO:2000031` does not use as carbon source | 319 |
| assimilation | `METPO:2000002` assimilates | `METPO:2000027` does not assimilate | 315 |
| growth | `METPO:2000012` uses for growth | `METPO:2000038` does not use for growth | 252 |
| builds acid from | `METPO:2000003` builds acid from | `METPO:2000028` does not build acid from | 176 |
| enzyme activity | *unresolved* | *unresolved* | 132 |
| energy source | `METPO:2000010` uses as energy source | `METPO:2000036` does not use as energy source | 124 |
| oxidation | `METPO:2000016` oxidizes | `METPO:2000042` does not oxidize | 124 |
| hydrolysis | `METPO:2000013` hydrolyzes | `METPO:2000039` does not hydrolyze | 110 |
| fermentation | `METPO:2000011` ferments | `METPO:2000037` does not ferment | 102 |
| degradation | `METPO:2000007` degrades | `METPO:2000033` does not degrade | 85 |
| respiration | `METPO:2000019` uses for respiration | `METPO:2000046` does not use for respiration | 84 |
| utilizes | *unresolved* | *unresolved* | 80 |
| nitrogen source | `METPO:2000014` uses as nitrogen source | `METPO:2000040` does not use as nitrogen source | 79 |
| electron donor | `METPO:2000009` uses as electron donor | `METPO:2000035` does not use as electron donor | 68 |
| electron acceptor | `METPO:2000008` uses as electron acceptor | `METPO:2000034` does not use as electron acceptor | 47 |
| reduction | `METPO:2000017` reduces | `METPO:2000044` does not reduce | 46 |
| anaerobic growth | `METPO:2000049` uses for anaerobic growth | `METPO:2000024` does not use for anaerobic growth | 27 |
| required for growth | `METPO:2000045` is not required for growth | - | 26 |
| aerobic growth | `METPO:2000043` uses for aerobic growth | `METPO:2000022` does not use for aerobic growth | 20 |
| builds gas from | `METPO:2000005` builds gas from | `METPO:2000030` does not build gas from | 17 |
| aerobic catabolization | `METPO:2000032` uses for aerobic catabolization | `METPO:2000021` does not use for aerobic catabolization | 10 |
| builds base from | `METPO:2000004` builds base from | `METPO:2000029` does not build base from | 10 |
| anaerobic growth with light | `METPO:2000051` uses for anaerobic growth with light | `METPO:2000026` does not use for anaerobic growth with light | 8 |
| oxidation in darkness | *unresolved* | *unresolved* | 4 |
| anaerobic catabolization | `METPO:2000048` uses for anaerobic catabolization | `METPO:2000023` does not use for anaerobic catabolization | 4 |
| denitrification | *unresolved* | *unresolved* | 3 |
| anaerobic growth in the dark | `METPO:2000050` uses for anaerobic growth in the dark | `METPO:2000025` does not use for anaerobic growth in the dark | 3 |
| sulfur source | `METPO:2000020` uses as sulfur source | `METPO:2000047` does not use as sulfur source | 2 |
| ammonification | *unresolved* | *unresolved* | 2 |
| cell color | *unresolved* | *unresolved* | 1 |

### Sample KGX Edge Templates

Pattern: `<subject> --[predicate_id]--> <object_id>`

| MetaTraits Trait | Predicate | Object (CHEBI) | Substrate |
|-----------------|-----------|---------------|----------|
| aerobic catabolization: (-)-quinic acid | `METPO:2000032` uses for aerobic catabolization | `CHEBI:17521` | (-)-quinic acid |
| aerobic catabolization: 2-oxoglutarate | `METPO:2000032` uses for aerobic catabolization | `CHEBI:30916` | 2-oxoglutarate |
| aerobic catabolization: 4-hydroxybutyrate | `METPO:2000032` uses for aerobic catabolization | `CHEBI:16724` | 4-hydroxybutyrate |
| aerobic catabolization: acetate | `METPO:2000032` uses for aerobic catabolization | `CHEBI:30089` | acetate |
| aerobic catabolization: alpha-D-glucose | `METPO:2000032` uses for aerobic catabolization | `CHEBI:17925` | alpha-D-glucose |
| aerobic catabolization: cellobiose | `METPO:2000032` uses for aerobic catabolization | `CHEBI:17057` | cellobiose |
| aerobic catabolization: cis-aconitate | `METPO:2000032` uses for aerobic catabolization | `CHEBI:16383` | cis-aconitate |
| aerobic catabolization: D-fructose | `METPO:2000032` uses for aerobic catabolization | `CHEBI:15824` | D-fructose |
| aerobic catabolization: D-galactose | `METPO:2000032` uses for aerobic catabolization | `CHEBI:12936` | D-galactose |
| aerobic catabolization: dihydrogen | `METPO:2000032` uses for aerobic catabolization | `CHEBI:18276` | dihydrogen |
| aerobic growth: chemoheterotrophy | `METPO:2000043` uses for aerobic growth | `` | chemoheterotrophy |
| aerobic growth: anoxygenic phototrophy | `METPO:2000043` uses for aerobic growth | `` | anoxygenic phototrophy |
| aerobic growth: (+)-L-ornithine | `METPO:2000043` uses for aerobic growth | `CHEBI:15729` | (+)-L-ornithine |
| aerobic growth: acetate | `METPO:2000043` uses for aerobic growth | `CHEBI:30089` | acetate |
| aerobic growth: acetic acid | `METPO:2000043` uses for aerobic growth | `CHEBI:16411` | acetic acid |
| aerobic growth: adipate | `METPO:2000043` uses for aerobic growth | `CHEBI:17128` | adipate |
| aerobic growth: alginate | `METPO:2000043` uses for aerobic growth | `CHEBI:58187` | alginate |
| aerobic growth: alpha-D-glucose | `METPO:2000043` uses for aerobic growth | `CHEBI:17925` | alpha-D-glucose |
| aerobic growth: arabinose | `METPO:2000043` uses for aerobic growth | `CHEBI:22599` | arabinose |
| aerobic growth: aspartate | `METPO:2000043` uses for aerobic growth | `CHEBI:35391` | aspartate |
| aerobic growth: butyrate | `METPO:2000043` uses for aerobic growth | `CHEBI:17968` | butyrate |
| aerobic growth: casamino acids | `METPO:2000043` uses for aerobic growth | `` | casamino acids |
| aerobic growth: casein hydrolysate | `METPO:2000043` uses for aerobic growth | `` | casein hydrolysate |
| aerobic growth: cellobiose | `METPO:2000043` uses for aerobic growth | `CHEBI:17057` | cellobiose |
| aerobic growth: citrate | `METPO:2000043` uses for aerobic growth | `CHEBI:16947` | citrate |

## Base Trait Matches

| MetaTraits | METPO | Bridging CURIE | Confidence |
|------------|-------|----------------|----------:|
| acidophilic | alkaphilic | `OMP:0005009` | 0.9 |
| acidophilic | acidophilic | `OMP:0005009` | 0.9 |
| acidophilic | facultatively alkaphilic | `OMP:0005009` | 0.9 |
| acidophilic | facultatively acidophilic | `OMP:0005009` | 0.9 |
| acidophilic | alkalotolerant | `OMP:0005009` | 0.9 |
| aerobic catabolization | respiration | `GO:0009060` | 0.9 |
| aerobic catabolization | Aerobic respiration | `GO:0009060` | 0.9 |
| aerotolerant | aerotolerant | `MICRO:0000502` | 0.9 |
| anaerobic catabolization | Anaerobic respiration | `GO:0009061` | 0.9 |
| builds base from | metabolism | `GO:0008152` | 0.5 |
| builds gas from | metabolism | `GO:0008152` | 0.5 |
| cell shape | cell shape | `OMP:0000073` | 0.9 |
| facultative anaerobe | facultatively anaerobic | `OMP:0000087` | 0.9 |
| facultative anaerobe | facultatively aerobic | `OMP:0000087` | 0.9 |
| facultative anaerobe | microaerotolerant | `OMP:0000087` | 0.9 |
| facultative anaerobe | facultative oxygen preference | `OMP:0000087` | 0.9 |
| fermentation | Fermentation | `GO:0006113` | 0.9 |
| fermentation | Fermentation | `GO:0006113` | 0.9 |
| gram positive | gram positive | `OMP:0000188` | 0.9 |
| obligate anaerobic | strictly anaerobic | `OMP:0000184` | 0.9 |
| pH growth | pH growth preference | `OMP:0005008` | 0.9 |
| pH maximum | pH growth preference | `OMP:0005008` | 0.9 |
| pH minimum | pH growth preference | `OMP:0005008` | 0.9 |
| pH preference | pH growth preference | `OMP:0005008` | 0.9 |
| presence of motility | motile | `OMP:0000005` | 0.9 |
| psychrophilic | psychrophilic | `MICRO:0001306` | 0.9 |
| psychrophilic | facultative psychrophilic | `MICRO:0001306` | 0.9 |
| respiration | respiration | `GO:0045333` | 0.9 |
| sporulation | sporulation | `GO:0043934` | 0.9 |
| temperature growth | temperature preference | `OMP:0005002` | 0.9 |
| temperature maximum | temperature preference | `OMP:0005002` | 0.9 |
| temperature minimum | temperature preference | `OMP:0005002` | 0.9 |
| temperature preference | temperature preference | `OMP:0005002` | 0.9 |
| thermophilic | thermophilic | `MICRO:0000118` | 0.9 |
| utilizes | metabolism | `GO:0008152` | 0.5 |

## Unmatched Base Traits

These base traits had no CURIE overlap with METPO definition sources:

- **GC percentage** — CURIEs: mesh:D001482
- **aerobic growth** — CURIEs: GO:0040007, PATO:0001455
- **anaerobic growth** — CURIEs: GO:0040007, PATO:0001456
- **anaerobic growth in the dark** — CURIEs: FBcv:0007038, GO:0040007, PATO:0001456
- **anaerobic growth with light** — CURIEs: FBcv:0007038, GO:0040007, PATO:0001456
- **assimilation** — CURIEs: GO:0009058
- **biosafety level** — CURIEs: NCIT:C164457
- **builds acid from** — CURIEs: GO:0016053
- **capnophilic** — CURIEs: SNOMED:413748004
- **carbon source** — CURIEs: GO:0015976
- **cell color** — CURIEs: OMP:0000116
- **cell length** — CURIEs: OMP:0000322
- **cell length maximum** — CURIEs: OMP:0000322
- **cell length minimum** — CURIEs: OMP:0000322
- **cell width** — CURIEs: OMP:0000317
- **cell width maximum** — CURIEs: OMP:0000317
- **cell width minimum** — CURIEs: OMP:0000317
- **coding density** — CURIEs: SIO:001276, SNOMED:258755000, mesh:D059646
- **degradation** — CURIEs: GO:0009056
- **denitrification pathway** — CURIEs: GO:0019333
- **electron acceptor** — CURIEs: CHEBI:17654
- **electron donor** — CURIEs: CHEBI:15022
- **energy source** — CURIEs: GO:0015980
- **enzyme activity** — CURIEs: SNOMED:424017009
- **estimated gene count** — CURIEs: NCIT:C25498, OBI:0002568, gene
- **estimated genome size** — CURIEs: GENEPIO:0001561
- **flagellum arrangement** — CURIEs: OMP:0000078
- **gene count** — CURIEs: OBI:0002568, gene
- **generalism_score** — CURIEs: inbio:000022
- **generalist** — CURIEs: inbio:000022
- **genome size** — CURIEs: GENEPIO:0001561
- **gram negative** — CURIEs: OMP:0000189
- **growth** — CURIEs: GO:0040007
- **habitat_count** — CURIEs: ENVO:01000739
- **hydrolysis** — CURIEs: GO:0016787
- **indole test** — CURIEs: MICRO:0000430
- **intra_species_nucleotide_diversity** — CURIEs: mesh:D014644
- **methyl red test** — CURIEs: SNOMED:5894006
- **nitrification** — CURIEs: OMIT:0027217
- **nitrogen fixation** — CURIEs: GO:0009399
- **nitrogen source** — CURIEs: GO:0019740
- **obligate aerobic** — CURIEs: OMP:0000185
- **oxidation** — CURIEs: GO:0055114
- **oxygen preference** — CURIEs: MICRO:0000491
- **pangenome_openness** — CURIEs: (none)
- **presence of hemolysis** — CURIEs: OMP:0005117
- **produces** — CURIEs: GO:0009058
- **reduction** — CURIEs: GO:0055114
- **required for growth** — CURIEs: CHEBI:33284, SNOMED:405662005
- **salinity growth** — CURIEs: OMP:0005013
- **salinity maximum** — CURIEs: OMP:0005013
- **salinity minimum** — CURIEs: OMP:0005013
- **salinity preference** — CURIEs: OMP:0005013
- **sulfur source** — CURIEs: GO:0006791
- **voges-proskauer test** — CURIEs: SNOMED:66592006

## Composed Trait Coverage by Base Category

| Base Category | Total | Unique Cards Mapped | % |
|---------------|------:|--------------------:|--:|
| produces | 499 | 0 | 0% |
| carbon source | 319 | 0 | 0% |
| assimilation | 315 | 0 | 0% |
| growth | 252 | 4 | 2% |
| builds acid from | 176 | 0 | 0% |
| enzyme activity | 132 | 0 | 0% |
| energy source | 124 | 0 | 0% |
| oxidation | 124 | 0 | 0% |
| hydrolysis | 110 | 0 | 0% |
| fermentation | 102 | 102 | 100% |
| degradation | 85 | 0 | 0% |
| respiration | 84 | 84 | 100% |
| utilizes | 80 | 0 | 0% |
| nitrogen source | 79 | 0 | 0% |
| electron donor | 68 | 0 | 0% |
| electron acceptor | 47 | 0 | 0% |
| reduction | 46 | 0 | 0% |
| anaerobic growth | 27 | 0 | 0% |
| required for growth | 26 | 0 | 0% |
| aerobic growth | 20 | 2 | 10% |
| builds gas from | 17 | 0 | 0% |
| aerobic catabolization | 10 | 10 | 100% |
| builds base from | 10 | 0 | 0% |
| anaerobic growth with light | 8 | 0 | 0% |
| anaerobic catabolization | 4 | 4 | 100% |
| oxidation in darkness | 4 | 0 | 0% |
| anaerobic growth in the dark | 3 | 0 | 0% |
| denitrification | 3 | 0 | 0% |
| ammonification | 2 | 0 | 0% |
| sulfur source | 2 | 0 | 0% |
| cell color | 1 | 0 | 0% |

## Fully Unmatched Base Categories (SSSOM)

No composed traits in these categories matched via CURIE join.
Many of these **do** resolve to METPO properties (see KGX section above).

- **ammonification** (2 traits)
- **anaerobic growth** (27 traits) → KGX: `METPO:2000049` uses for anaerobic growth
- **anaerobic growth in the dark** (3 traits) → KGX: `METPO:2000050` uses for anaerobic growth in the dark
- **anaerobic growth with light** (8 traits) → KGX: `METPO:2000051` uses for anaerobic growth with light
- **assimilation** (315 traits) → KGX: `METPO:2000002` assimilates
- **builds acid from** (176 traits) → KGX: `METPO:2000003` builds acid from
- **builds base from** (10 traits) → KGX: `METPO:2000004` builds base from
- **builds gas from** (17 traits) → KGX: `METPO:2000005` builds gas from
- **carbon source** (319 traits) → KGX: `METPO:2000006` uses as carbon source
- **cell color** (1 traits)
- **degradation** (85 traits) → KGX: `METPO:2000007` degrades
- **denitrification** (3 traits)
- **electron acceptor** (47 traits) → KGX: `METPO:2000008` uses as electron acceptor
- **electron donor** (68 traits) → KGX: `METPO:2000009` uses as electron donor
- **energy source** (124 traits) → KGX: `METPO:2000010` uses as energy source
- **enzyme activity** (132 traits)
- **hydrolysis** (110 traits) → KGX: `METPO:2000013` hydrolyzes
- **nitrogen source** (79 traits) → KGX: `METPO:2000014` uses as nitrogen source
- **oxidation** (124 traits) → KGX: `METPO:2000016` oxidizes
- **oxidation in darkness** (4 traits)
- **produces** (499 traits) → KGX: `METPO:2000202` produces
- **reduction** (46 traits) → KGX: `METPO:2000017` reduces
- **required for growth** (26 traits) → KGX: `METPO:2000045` is not required for growth
- **sulfur source** (2 traits) → KGX: `METPO:2000020` uses as sulfur source
- **utilizes** (80 traits)

## Comparison with Label-Matching Approach

| Metric | Label Matching (PR #332) | CURIE Join (this) |
|--------|------------------------:|------------------:|
| Total SSSOM mappings | 420 | 250 |
| Unique MetaTraits terms | 362 | 231 |
| Unique METPO terms | 90 | 28 |
| Semantic errors (antonym swaps) | 6 | 0 |
| Substrate preserved | No (308 lost) | Yes (CHEBI in comment + KGX edges) |
| KGX edge templates | 0 | 2557 |
| METPO predicates resolved | 0 | 25 categories |
| Fuzzy matching | Yes (threshold 85) | None |
| Embeddings required | No | No |

## Implications

- The CURIE join approach produces **zero semantic errors** by construction.
- Composed traits preserve substrate identity via CHEBI CURIEs.
- METPO property resolution covers **all 25 composed base categories**,
  enabling KGX-ready edge generation for the full MetaTraits catalog.
- Coverage gaps in SSSOM indicate where embeddings or manual curation would add value.
- The two approaches are complementary: CURIE join for grounded SSSOM mappings,
  property resolution for KGX edge templates.
