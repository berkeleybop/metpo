# Environmental Condition Parse Model  
*Version 0.3 – 2025-05-07*

This document defines a reusable ontology **pattern** and data‑model for normalising free‑text statements about a microbe’s relationship to an environmental condition (temperature, pH, oxygen requirement, salinity, …).

The pattern centres on a *ParseGroup* wrapper and multiple *ParseComponent* children.  
It generalises the earlier temperature‑only draft by adding a **qualifier** field (e.g. “optimum”, “upper limit”) and by noting how the same structure can be adopted for other factors.

---

## 1 Scope

* **ParseGroup / ParseComponent** is *factor‑agnostic*.  
  *The same classes and properties apply to temperature, pH, oxygen, salinity, pressure, etc.*  
* Factor‑specific details—allowed units, recognised categorical tokens—can be documented in companion cheat‑sheets.

---

## 2 Goal

Restate each free‑text RDF triple as:

```
subject  predicate  [ a :ParseGroup ;
                      :raw_text "...free text..." ;
                      :parse_component 1 ;
                      :parse_component 2 ; … ] .
```

---

## 3 Ontology (Turtle)

```turtle
@prefix :        <http://example.org/env‑parse#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

################################################################################
#   Core classes
################################################################################

:ParseGroup      a owl:Class ;
  rdfs:label   "Parse group" ;
  rdfs:comment "Wrapper for one raw value string and its structured parsing." .

:ParseComponent  a owl:Class ;
  rdfs:label   "Parse component" ;
  rdfs:comment "Structured fragment extracted from the raw value." .

################################################################################
#   Object property
################################################################################

:parse_component a owl:ObjectProperty ;
  rdfs:label   "has parse component" ;
  rdfs:domain  :ParseGroup ;
  rdfs:range   :ParseComponent ;
  rdfs:comment "Links a ParseGroup to one or more ParseComponent instances." .

################################################################################
#   Datatype properties
################################################################################

:raw_text          a owl:DatatypeProperty ; rdfs:domain :ParseGroup    ; rdfs:range xsd:string  .

:component_text    a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:string  .

:minimum_value     a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:decimal .
:maximum_value     a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:decimal .
:spot_value        a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:decimal .

:unit              a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:string  ;
  rdfs:comment "UCUM code (e.g. 'Cel', 'pH', 'atm')." .

:categorical_label a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:string  ;
  rdfs:comment "Category term such as 'mesophilic', 'alkaliphilic', 'anaerobic'." .

:qualifier_label   a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:string  ;
  rdfs:comment "Qualifier such as 'optimum', 'upper limit', 'minimum', 'mean'." .

:unparsed_text     a owl:DatatypeProperty ; rdfs:domain :ParseComponent; rdfs:range xsd:string  .

################################################################################
#   Ontology header
################################################################################

<http://example.org/env‑parse>
  a owl:Ontology ;
  rdfs:label      "Environmental Condition Parse Ontology Pattern" ;
  owl:versionInfo "0.3 – 2025-05-07" .
```

---

## 4 Cardinality & Validation

* **ParseGroup**: exactly **1** `:raw_text`; at least **1** `:parse_component`.  
* **ParseComponent**: must contain at least one of  
  `minimum_value`, `maximum_value`, `spot_value`, `categorical_label`, `qualifier_label`, `unparsed_text`.

---

## 5 Datatype & Unit Guidance

* Numeric literals output as **xsd:decimal**.  
* `unit` uses **UCUM codes** (`Cel`, `pH`, `%`, `atm`, …).  
* Factor‑specific cheat‑sheets enumerate valid units.

---

## 6 Categorical vs Qualifier Labels

| Example free text                     | categorical_label     | qualifier_label |
|---------------------------------------|-----------------------|-----------------|
| “mesophilic”                          | mesophilic            | —               |
| “optimum 30 °C”                       | —                     | optimum         |
| “upper limit 50 °C”                   | —                     | upper limit     |
| “strict anaerobe”                     | anaerobic             | strict          |
| “moderately halophilic (3 – 15 %)”    | halophilic            | moderately      |

Parsers SHOULD normalise tokens to lower case and strip punctuation before matching.

---

## 7 Worked Example (temperature)

```turtle
:strain123 :hasTemperatureGrowth "15–37 °C (optimum 30 °C)" .
```

Restated:

```turtle
:strain123 :hasTemperatureGrowth [
    a                :ParseGroup ;
    :raw_text        "15–37 °C (optimum 30 °C)" ;
    :parse_component [
        a               :ParseComponent ;
        :component_text "15–37 °C" ;
        :minimum_value  15 ;
        :maximum_value  37 ;
        :unit           "Cel"
    ] ;
    :parse_component [
        a               :ParseComponent ;
        :component_text "optimum 30 °C" ;
        :spot_value     30 ;
        :unit           "Cel" ;
        :qualifier_label "optimum"
    ]
] .
```

---

## 8 Worked Example (oxygen)

```turtle
:strainABC :hasOxygenRelationship "strict anaerobe, grows best at 35 °C" .
```

Restated (showing multi‑factor potential):

```turtle
:strainABC :hasOxygenRelationship [
    a                :ParseGroup ;
    :raw_text        "strict anaerobe, grows best at 35 °C" ;
    :parse_component [
        a                :ParseComponent ;
        :component_text  "strict anaerobe" ;
        :categorical_label "anaerobic" ;
        :qualifier_label  "strict"
    ] ;
    :parse_component [
        a                :ParseComponent ;
        :component_text  "grows best at 35 °C" ;
        :spot_value      35 ;
        :unit            "Cel" ;
        :qualifier_label "optimum"
    ]
] .
```

---

## 9 CSV → RDF Mapping Recipe

*(unchanged from v0.2; see previous version for details)*

---

## 10 Future Work

* Publish cheat‑sheets for each environmental factor (valid units, categorical tokens, qualifiers).  
* SHACL shape library to enforce both the generic pattern and factor‑specific rules.  
* Optional `:confidence` and `:parse_error` telemetry fields for quality assessment.

---

*End of document*  
