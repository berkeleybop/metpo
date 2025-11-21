# Additional BacDive Data Paths Found in Schema

## Paths Already Covered in Issues
✅ enzymes
✅ metabolite utilization
✅ metabolite production
✅ metabolite tests
✅ API 20A, API 20E, API 20NE, API coryne, API STA (API STAPH), API zym
✅ antibiotic resistance
✅ antibiogram

## Additional Paths Found in Schema (Not Yet Covered)

### Biochemical Test Results (High Priority)
1. **citrate test** - Citrate utilization (classic IMViC test)
2. **indole test** - Indole production (classic IMViC test)
3. **methylred-test** - Methyl red test (classic IMViC test)
4. **voges-proskauer-test** - VP test (classic IMViC test)
5. **compound production** - General compound production
6. **H2S** - Hydrogen sulfide production
7. **N2** - Nitrogen metabolism
8. **NO2** / **NO3** - Nitrate/nitrite tests

### Additional API Test Types (Medium Priority)
9. **API 50CHac** - Carbohydrate acidification
10. **API 50CHas** - Carbohydrate assimilation
11. **API biotype100**
12. **API CAM**
13. **API ID32E** - Enterobacteriaceae identification
14. **API ID32STA** - Staphylococcus identification
15. **API LIST**
16. **API NH**
17. **API rID32A**
18. **API rID32STR**
19. **API 20STR** - Streptococcus identification

### Classical Bacteriology Tests (High Priority)
20. **GRAM** - Gram stain
21. **CAT** / **Cat1** / **Cat2** / **Cat3** - Catalase variants
22. **OX** - Oxidase
23. **URE** - Urease
24. **GEL** - Gelatinase
25. **SPOR** - Sporulation
26. **MOB** - Motility
27. **IND** - Indole
28. **VP** - Voges-Proskauer
29. **CIT** - Citrate
30. **H2S** - Hydrogen sulfide

### Enzyme Tests (Medium Priority)
Many specific enzyme tests listed as individual properties:
- Acid phosphatase
- Alkaline phosphatase
- alpha-Chymotrypsin
- alpha-Fucosidase
- alpha-Galactosidase
- alpha-Glucosidase
- alpha-Mannosidase
- beta-Galactosidase
- beta-Glucosidase
- beta-Glucuronidase
- Cystine arylamidase
- Esterase
- Esterase Lipase
- Leucine arylamidase
- Lipase
- N-acetyl-beta-glucosaminidase
- Naphthol-AS-BI-phosphohydrolase
- Trypsin
- Valine arylamidase

### Substrate Utilization (Individual) (Lower Priority)
Hundreds of individual substrate codes (e.g., FRU, GLU, LAC, MAL, etc.)
These appear to be from API strips and are likely covered by the API issues.

### Phenotypic Properties (Already in METPO)
- oxygen tolerance ✅ (already using METPO)
- halophily ✅ (already using METPO)
- biosafety level ✅ (already using METPO)
- nutrition type ✅ (already using METPO)
- cell shape ✅ (already using METPO)
- gram stain ✅ (already using METPO)
- motility ✅ (already using METPO)
- spore formation ✅ (already using METPO)

### Molecular/Genomic Data (Out of Scope)
- fatty acid profile
- murein composition
- GC content
- 16S sequences
- Genome sequences

## Priority Assessment

### Critical Gaps (Should Create Issues)

1. **IMViC Tests** - These are classic, fundamental tests that should be separate from "metabolite tests":
   - Indole test
   - Methyl red test
   - Voges-Proskauer test
   - Citrate test

2. **Gas Production Tests**:
   - H2S production
   - N2 production
   - NO2/NO3 (nitrate reduction)

3. **API 50CH Tests** - Major test strips not covered:
   - API 50CHac (carbohydrate acidification)
   - API 50CHas (carbohydrate assimilation)

### Why IMViC Tests Deserve Separate Issue

IMViC is a standardized battery of 4 tests used universally for Enterobacteriaceae identification:
- **I**ndole
- **M**ethyl red
- **V**oges-**P**roskauer (actually "VP")
- **C**itrate

These have structured data with specific properties:
- `indole test`
- `methylred-test`
- `voges-proskauer-test`
- `citrate test`

They're separate from the general "metabolite tests" array and deserve dedicated modeling.

## Recommendation

Create 2-3 additional issues:

1. **Issue: IMViC Battery Tests** (indole, methyl red, VP, citrate)
2. **Issue: Gas Production Tests** (H2S, N2, NO2/NO3)
3. **Issue: API 50CH Tests** (API 50CHac, API 50CHas)

The individual enzyme properties (alpha-Galactosidase, etc.) are likely from API strips and covered by Issue #35.
