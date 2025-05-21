assign temperature range assertions, like would be found in local/flattened_n4l_temperature_components.tsv, agaisnt the minimum and maximum boundaries in metpo.owl

```sparql
PREFIX metpo: <https://w3id.org/metpo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select
distinct ?s ?l ?min ?max
where {
    values ?o  {
        metpo:1000147 metpo:1000217
    }
    ?s rdfs:subClassOf+ ?o ;
    rdfs:label ?l ;
    metpo:Unit "C" . # THERE ARE A FEW UNITLESS ASSERTIONS TOO
    optional {
        ?s metpo:RangeMax ?max
    }
    optional {
        ?s metpo:RangeMin ?min
    }
}
order by ?l
```

> Showing results from 0 to 30 of 30. Query took 0.1s, moments ago.

s | l | min | max
-- | -- | -- | --
https://w3id.org/metpo/1000339 | extreme hyperthermophile | 90 | 125
https://w3id.org/metpo/1000338 | extreme thermophile | 60 | 80
https://w3id.org/metpo/1000161 | hyperthermophile | 80 | 115
https://w3id.org/metpo/1000181 | mesophile | 20 | 45
https://w3id.org/metpo/1000259 | psychrophile | 0 | 20
https://w3id.org/metpo/1000336 | psychrotolerant | 0 | 45
https://w3id.org/metpo/1000303 | temperature delta |   |  
https://w3id.org/metpo/1000487 | temperature delta high | 30 |  
https://w3id.org/metpo/1000484 | temperature delta low | 5 | 10
https://w3id.org/metpo/1000485 | temperature delta mid1 | 10 | 20
https://w3id.org/metpo/1000486 | temperature delta mid2 | 20 | 30
https://w3id.org/metpo/1000483 | temperature delta very low | 1 | 5
https://w3id.org/metpo/1000329 | temperature optimum |   |  
https://w3id.org/metpo/1000447 | temperature optimum high | 40 |  
https://w3id.org/metpo/1000442 | temperature optimum low | 10 | 22
https://w3id.org/metpo/1000443 | temperature optimum mid1 | 22 | 27
https://w3id.org/metpo/1000444 | temperature optimum mid2 | 27 | 30
https://w3id.org/metpo/1000445 | temperature optimum mid3 | 30 | 34
https://w3id.org/metpo/1000446 | temperature optimum mid4 | 34 | 40
https://w3id.org/metpo/1000441 | temperature optimum very low |   | 10
https://w3id.org/metpo/1000330 | temperature range |   |  
https://w3id.org/metpo/1000454 | temperature range high | 40 |  
https://w3id.org/metpo/1000449 | temperature range low | 10 | 22
https://w3id.org/metpo/1000450 | temperature range mid1 | 22 | 27
https://w3id.org/metpo/1000451 | temperature range mid2 | 27 | 30
https://w3id.org/metpo/1000452 | temperature range mid3 | 30 | 34
https://w3id.org/metpo/1000453 | temperature range mid4 | 34 | 40
https://w3id.org/metpo/1000448 | temperature range very low |   | 10
https://w3id.org/metpo/1000308 | thermophile | 45 | 80
https://w3id.org/metpo/1000337 | thermotolerant | 0 | 50

Doesn't include facultative psychrophile (0-30?) from KG microbe yet



N4L temperature predicates, after normalization by

- metpo/n4l_tables_to_quads.ipynb -> local/n4l-tables.nq -> multiple GrapDB named graphs
    - see also assets/n4l_predicate_mapping_normalization.csv
- sparql/temperature_query.rq -> local/n4l-temperature.csv
- metpo/classify_temperature_values.ipynb -> local/n4l-temperature.ttl and local/n4l-temperature-un-parsed.csv
- sparql/flatten_n4l_parsing_components.rq -> local/flattened_n4l_temperature_components.tsv


* <http://example.com/n4l/temperature>
    * handled by metpo/classify_temperature_values.ipynb, sparql/report_parsed_temperature_categories.rq
* <http://example.com/n4l/temperature_(grows)>
* <http://example.com/n4l/temperature_optimum>
* <http://example.com/n4l/temperature_range>
* <http://example.com/n4l/temperature_(does_not_grow)>

What can be inferred from another temperature assertion?

* Delta can always be calculated from the range.
* Range can be inferred from delta plus one limit (min or max).
* Optimum is generally measured, not inferred.
* Categorical labels are assigned based on optimum (and sometimes range).
* Psychrotolerant/thermotolerant specifically require both optimum and range for accurate assignment.