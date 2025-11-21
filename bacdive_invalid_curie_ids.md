# BacDive Invalid CURIE IDs

Analysis of nodes in `../kg-microbe/data/transformed/bacdive/nodes.tsv` where the `id` field does not match valid CURIE pattern `^[^\s:]+:[^\s:]+$`.

**Total invalid IDs found:** 100 out of 196,168 nodes (0.05%)

## Issues Found

1. **Assay identifiers with spaces** (59 rows): IDs contain spaces in the local identifier part
2. **Strain identifiers with extra colons** (40 rows): IDs contain additional colons beyond the prefix separator
3. **Literal "nan" value** (1 row): Missing identifier replaced with string "nan"

## Complete List

| Row | ID | Category | Name |
|-----|----|---------|----|
| 241 | assay:API_zym_Cystine arylamidase | biolink:PhenotypicQuality | API zym - Cystine arylamidase |
| 245 | assay:API_zym_Acid phosphatase | biolink:PhenotypicQuality | API zym - Acid phosphatase |
| 246 | assay:API_zym_Esterase Lipase | biolink:PhenotypicQuality | API zym - Esterase Lipase |
| 247 | assay:API_zym_Valine arylamidase | biolink:PhenotypicQuality | API zym - Valine arylamidase |
| 248 | assay:API_zym_beta- Glucosidase | biolink:PhenotypicQuality | API zym - beta- Glucosidase |
| 249 | assay:API_zym_Leucine arylamidase | biolink:PhenotypicQuality | API zym - Leucine arylamidase |
| 250 | assay:API_zym_alpha- Glucosidase | biolink:PhenotypicQuality | API zym - alpha- Glucosidase |
| 265 | assay:API_zym_N-acetyl-beta- glucosaminidase | biolink:PhenotypicQuality | API zym - N-acetyl-beta- glucosaminidase |
| 302 | assay:API_zym_Alkaline phosphatase | biolink:PhenotypicQuality | API zym - Alkaline phosphatase |
| 634 | assay:API_zym_alpha- Chymotrypsin | biolink:PhenotypicQuality | API zym - alpha- Chymotrypsin |
| 635 | assay:API_zym_beta- Glucuronidase | biolink:PhenotypicQuality | API zym - beta- Glucuronidase |
| 1317 | assay:API_rID32A_beta GAL | biolink:PhenotypicQuality | API rID32A - beta GAL |
| 1318 | assay:API_rID32A_beta GP | biolink:PhenotypicQuality | API rID32A - beta GP |
| 1321 | assay:API_rID32A_beta NAG | biolink:PhenotypicQuality | API rID32A - beta NAG |
| 1376 | assay:API_zym_beta- Galactosidase | biolink:PhenotypicQuality | API zym - beta- Galactosidase |
| 1383 | assay:API_rID32A_alpha GAL | biolink:PhenotypicQuality | API rID32A - alpha GAL |
| 1403 | assay:API_rID32A_alpha GLU | biolink:PhenotypicQuality | API rID32A - alpha GLU |
| 1414 | assay:API_rID32A_beta GLU | biolink:PhenotypicQuality | API rID32A - beta GLU |
| 1466 | assay:API_zym_alpha- Galactosidase | biolink:PhenotypicQuality | API zym - alpha- Galactosidase |
| 1488 | assay:API_zym_alpha- Mannosidase | biolink:PhenotypicQuality | API zym - alpha- Mannosidase |
| 1504 | assay:API_rID32STR_beta GLU | biolink:PhenotypicQuality | API rID32STR - beta GLU |
| 1505 | assay:API_rID32STR_alpha GAL | biolink:PhenotypicQuality | API rID32STR - alpha GAL |
| 1514 | assay:API_rID32A_ADH Arg | biolink:PhenotypicQuality | API rID32A - ADH Arg |
| 1526 | assay:API_coryne_beta GAL | biolink:PhenotypicQuality | API coryne - beta GAL |
| 1530 | assay:API_coryne_alpha GLU | biolink:PhenotypicQuality | API coryne - alpha GLU |
| 1531 | assay:API_coryne_beta NAG | biolink:PhenotypicQuality | API coryne - beta NAG |
| 1536 | assay:API_NH_beta GAL | biolink:PhenotypicQuality | API NH - beta GAL |
| 1574 | assay:API_zym_alpha- Fucosidase | biolink:PhenotypicQuality | API zym - alpha- Fucosidase |
| 1617 | assay:API_rID32STR_beta GAL | biolink:PhenotypicQuality | API rID32STR - beta GAL |
| 1620 | assay:API_rID32STR_beta GAR | biolink:PhenotypicQuality | API rID32STR - beta GAR |
| 1629 | assay:API_rID32A_alpha ARA | biolink:PhenotypicQuality | API rID32A - alpha ARA |
| 1658 | assay:API_ID32STA_beta GAL | biolink:PhenotypicQuality | API ID32STA - beta GAL |
| 1681 | assay:API_coryne_beta GUR | biolink:PhenotypicQuality | API coryne - beta GUR |
| 1682 | assay:API_rID32A_beta GUR | biolink:PhenotypicQuality | API rID32A - beta GUR |
| 1687 | assay:API_rID32STR_Mbeta DG | biolink:PhenotypicQuality | API rID32STR - Mbeta DG |
| 1690 | assay:API_rID32STR_ADH Arg | biolink:PhenotypicQuality | API rID32STR - ADH Arg |
| 1691 | assay:API_rID32STR_beta GUR | biolink:PhenotypicQuality | API rID32STR - beta GUR |
| 1725 | assay:API_rID32A_alpha FUC | biolink:PhenotypicQuality | API rID32A - alpha FUC |
| 2128 | assay:API_20NE_GLU_ Assim | biolink:PhenotypicQuality | API 20NE - GLU_ Assim |
| 2292 | assay:API_20E_ADH Arg | biolink:PhenotypicQuality | API 20E - ADH Arg |
| 2298 | assay:API_20E_LDC Lys | biolink:PhenotypicQuality | API 20E - LDC Lys |
| 2347 | assay:API_ID32E_beta GAL | biolink:PhenotypicQuality | API ID32E - beta GAL |
| 2351 | assay:API_ID32E_ADH Arg | biolink:PhenotypicQuality | API ID32E - ADH Arg |
| 2353 | assay:API_ID32E_alpha GLU | biolink:PhenotypicQuality | API ID32E - alpha GLU |
| 2400 | assay:API_20NE_ADH Arg | biolink:PhenotypicQuality | API 20NE - ADH Arg |
| 2404 | assay:API_20NE_GLU_ Ferm | biolink:PhenotypicQuality | API 20NE - GLU_ Ferm |
| 2613 | assay:API_20E_TDA Trp | biolink:PhenotypicQuality | API 20E - TDA Trp |
| 2656 | assay:API_ID32E_beta NAG | biolink:PhenotypicQuality | API ID32E - beta NAG |
| 2672 | assay:API_ID32E_alpha GAL | biolink:PhenotypicQuality | API ID32E - alpha GAL |
| 2748 | assay:API_ID32E_beta GLU | biolink:PhenotypicQuality | API ID32E - beta GLU |
| 3345 | nan | biolink:OrganismTaxon | (empty) |
| 4369 | strain:NRRL-:-NRS-341 | biolink:OrganismTaxon | NRRL : NRS-341 |
| 4401 | strain:NRRL-:-B-14393 | biolink:OrganismTaxon | NRRL : B-14393 |
| 5329 | strain:NRRL:-NRS-236 | biolink:OrganismTaxon | NRRL: NRS-236 |
| 7937 | strain:NRRL:-NRS-1321 | biolink:OrganismTaxon | NRRL: NRS-1321 |
| 8413 | assay:API_rID32STR_beta MAN | biolink:PhenotypicQuality | API rID32STR - beta MAN |
| 8415 | assay:API_rID32STR_beta NAG | biolink:PhenotypicQuality | API rID32STR - beta NAG |
| 12590 | assay:API_20STR_beta GAL | biolink:PhenotypicQuality | API 20STR - beta GAL |
| 12591 | assay:API_20STR_alpha GAL | biolink:PhenotypicQuality | API 20STR - alpha GAL |
| 15838 | strain:NRRL:-B-2065 | biolink:OrganismTaxon | NRRL: B-2065 |
| 16129 | strain:NRRL:-B2611 | biolink:OrganismTaxon | NRRL: B2611 |
| 21237 | assay:API_ID32E_LDC Lys | biolink:PhenotypicQuality | API ID32E - LDC Lys |
| 21799 | assay:API_ID32E_beta GUR | biolink:PhenotypicQuality | API ID32E - beta GUR |
| 25659 | assay:API_ID32STA_beta GUR | biolink:PhenotypicQuality | API ID32STA - beta GUR |
| 33427 | strain:NRRL:-B-3934 | biolink:OrganismTaxon | NRRL: B-3934 |
| 34756 | assay:API_LIST_alpha MAN | biolink:PhenotypicQuality | API LIST - alpha MAN |
| 34790 | assay:API_LIST_beta HEM | biolink:PhenotypicQuality | API LIST - beta HEM |
| 39732 | assay:API_ID32STA_ADH Arg | biolink:PhenotypicQuality | API ID32STA - ADH Arg |
| 39840 | strain:NRRL:-B-287 | biolink:OrganismTaxon | NRRL: B-287 |
| 47742 | strain:NRRL:-B-2066 | biolink:OrganismTaxon | NRRL: B-2066 |
| 47833 | strain:NRRL:-B-2045 | biolink:OrganismTaxon | NRRL: B-2045 |
| 52741 | strain:NRRL:-NRS-354 | biolink:OrganismTaxon | NRRL: NRS-354 |
| 52742 | strain:NRRL:-B-372 | biolink:OrganismTaxon | NRRL: B-372 |
| 52813 | strain:NRRL:-NRS-277 | biolink:OrganismTaxon | NRRL: NRS-277 |
| 52957 | strain:NRRL:-NRS-1351 | biolink:OrganismTaxon | NRRL: NRS-1351 |
| 53818 | strain:NRRL:-B-4156 | biolink:OrganismTaxon | NRRL: B-4156 |
| 55522 | strain:NRRL:-NRS-1530 | biolink:OrganismTaxon | NRRL: NRS-1530 |
| 58638 | strain:NRRL:-B-25 | biolink:OrganismTaxon | NRRL: B-25 |
| 59675 | strain:NRRL:-B-927 | biolink:OrganismTaxon | NRRL: B-927 |
| 60022 | strain:NRRL:-B-560 | biolink:OrganismTaxon | NRRL: B-560 |
| 65017 | strain:NRRL-:-B-2054 | biolink:OrganismTaxon | NRRL : B-2054 |
| 67738 | strain:NRRL-:-B-314 | biolink:OrganismTaxon | NRRL : B-314 |
| 67936 | strain:NRRL-:-B-313 | biolink:OrganismTaxon | NRRL : B-313 |
| 68899 | assay:API_20STR_beta GUR | biolink:PhenotypicQuality | API 20STR - beta GUR |
| 68912 | assay:API_20STR_beta HEM | biolink:PhenotypicQuality | API 20STR - beta HEM |
| 93179 | strain:CCM-A-29:1289 | biolink:OrganismTaxon | CCM A-29:1289 |
| 117015 | strain:NRRL:-NRS-1004 | biolink:OrganismTaxon | NRRL: NRS-1004 |
| 118145 | strain:NRRL:-NRS-611 | biolink:OrganismTaxon | NRRL: NRS-611 |
| 118157 | strain:NRRL:-NRS-683 | biolink:OrganismTaxon | NRRL: NRS-683 |
| 118557 | strain:NRRL-:-B-1142 | biolink:OrganismTaxon | NRRL : B-1142 |
| 120409 | strain:NRRL:-B-367 | biolink:OrganismTaxon | NRRL: B-367 |
| 120413 | strain:NRRL:-B-366 | biolink:OrganismTaxon | NRRL: B-366 |
| 120485 | strain:NRRL:-NRS-616 | biolink:OrganismTaxon | NRRL: NRS-616 |
| 121190 | strain:NRRL-:-NRS-232 | biolink:OrganismTaxon | NRRL : NRS-232 |
| 123089 | strain:NRRL-:-NRS-201 | biolink:OrganismTaxon | NRRL : NRS-201 |
| 123486 | strain:NRRL:-NRS-1238 | biolink:OrganismTaxon | NRRL: NRS-1238 |
| 123722 | strain:NRRL-:-B-652 | biolink:OrganismTaxon | NRRL : B-652 |
| 123998 | strain:NRRL-:-B-2618 | biolink:OrganismTaxon | NRRL : B-2618 |
| 124443 | strain:NRRL:-B-465 | biolink:OrganismTaxon | NRRL: B-465 |
| 124828 | strain:NRRL:-NRS-778 | biolink:OrganismTaxon | NRRL: NRS-778 |

## Recommendations

1. **Assay IDs**: Replace spaces with underscores or URL-encode them
   - Example: `assay:API_zym_Cystine_arylamidase` instead of `assay:API_zym_Cystine arylamidase`

2. **Strain IDs**: Remove or replace colons in the local identifier part
   - Example: `strain:NRRL_NRS_341` instead of `strain:NRRL-:-NRS-341`

3. **Missing IDs**: Handle null/missing values properly instead of converting to "nan" string

## Impact

These invalid CURIEs will cause issues with:
- RDF export/serialization
- CURIE expansion to IRIs
- Downstream tools expecting valid CURIE format
- Data validation pipelines
