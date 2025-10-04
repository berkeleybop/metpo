# METPO Coverage Analysis: Madin et al. Pathways

## Summary Statistics

- **Total unique pathway values in Madin**: 103
- **Total METPO classes with Madin synonyms**: 70
- **Pathway values in Madin but NOT in METPO**: 88
- **METPO classes claiming Madin synonyms**: 15 pathway-related classes

## Coverage Rate

- **Coverage**: 15/103 = **14.6%** of Madin pathway values are covered by METPO
- **Gap**: 88 pathway values from Madin are not represented in METPO

## Pathway Values in Madin NOT Covered by METPO (88 total)

These are legitimate pathway values from the Madin dataset that METPO should consider adding:

### Major Missing Categories

#### Degradation Pathways (27)
- aliphatic_non_methane_hydrocarbon_degradation
- aminoacid_degradation
- aromatic_compound_degradation
- aromatic_hydrocarbon_degradation
- cellobiose_degradation
- cellulose_degradation
- chitin_degradation
- chlorocarbon_degradation
- DMSP_degradation
- EDTA_degradation
- gelatin_degradation
- hydrocarbon_degradation
- lignin_degradation
- ligninolysis
- MTBE_degradation
- pah_degradation
- PAH_degradation (duplicate, different case)
- PCB_degradation
- plastic_degradation
- polyisoprene_degradation
- polymer_degradation
- RDX_degradation
- urea_degradation
- xylan_degradation

#### Reduction Pathways (16)
- arsenate_reduction
- carbonmonoxide_reduction
- carbonylsulfide_reduction
- chlorate_reduction
- cobalt_reduction
- denitrification / Denitrification
- fumarate_reduction
- iron_reduction
- manganese_reduction
- nitrate_reduction
- nitrate_reduction_to_ammonia
- nitric_oxide_reduction
- nitrite_reduction
- nitrite_reduction_to_ammonia
- nitrous_oxide_reduction
- selenate_reduction / Selenate_reduction
- sulfate_reduction
- sulfite_reduction
- sulfur_reduction
- thiocyanate_reduction
- thiosulfate_reduction
- uranyl_reduction

#### Oxidation Pathways (24)
- arsenite_oxidation
- carbon_monoxide_oxidation
- carbonmonoxide_oxidation
- carbonylsulfide_oxidation
- chalcopyrite_oxidation
- covellite_oxidation
- galena_oxidation
- hydrogen_oxidation
- hydrogen_oxidation_dark
- iron_oxidation
- iron_oxidation_dark
- manganese_oxidation
- methane_oxidation
- methanol_oxidation
- nitrification
- nitrite_oxidation
- propionate_oxidation
- pyrite_oxidation
- pyrrhotite_oxidation
- sphalerite_oxidation
- sulfide_oxidation
- sulfide_oxidation_dark
- sulfite_oxidation
- sulfite_oxidation_dark
- sulfur_compound_oxidation_dark
- sulfur_oxidation
- sulfur_oxidation_dark
- tetrathionate_oxidation
- thiocyanate_oxidation
- thiosulfate_oxidation
- thiosulfate_oxidation_dark
- trithionate_oxidation
- uraninite_oxidation
- uranium_oxidation

#### Disproportionation (2)
- dithionite_disproportionation
- thiosulfate_disproportionation

#### Nitrogen Cycle (1)
- annamox
- nitrogen_fixation

#### Methanogenesis Subtypes (2)
- methanogenesis_acetoclastic
- methanogenesis_H2CO2

## METPO Classes with Madin Pathway Synonyms (15)

These are currently covered:
1. acetogenesis
2. aerobic_anoxygenic_phototrophy
3. aerobic_chemo_heterotrophy
4. aerobic_heterotrophy
5. anoxygenic_photoautotrophy
6. anoxygenic_photoautotrophy_hydrogen_oxidation
7. anoxygenic_photoautotrophy_iron_oxidation
8. anoxygenic_photoautotrophy_sulfur_oxidation
9. autotrophy
10. fermentation
11. heterotrophic
12. methanogenesis
13. methylotrophy
14. photoautotrophy
15. photoheterotrophy

## Recommendations

1. **High Priority**: Add degradation pathway classes (27 missing)
   - These represent major microbial functions in carbon cycling

2. **High Priority**: Add reduction pathway classes (16 missing)
   - Critical for anaerobic metabolism and biogeochemical cycles

3. **High Priority**: Add oxidation pathway classes (24 missing)
   - Essential for aerobic/microaerobic metabolism

4. **Medium Priority**: Add specific methanogenesis subtypes
   - methanogenesis_acetoclastic
   - methanogenesis_H2CO2

5. **Note**: Some values appear to be duplicates with different casing
   - Denitrification vs denitrification
   - Selenate_reduction vs selenate_reduction
   - PAH_degradation vs pah_degradation

## Next Steps

1. Review which missing pathways should become METPO classes vs synonyms of existing classes
2. Map degradation pathways to appropriate parent classes (e.g., catabolism, biodegradation)
3. Map oxidation/reduction pathways to electron transport/respiration classes
4. Consider creating a hierarchy for:
   - Degradation processes
   - Oxidation processes
   - Reduction processes
   - Disproportionation processes
