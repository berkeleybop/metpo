# Backend: OntoText GraphDB repository (metpo_n4l_etc_automated)
# Purpose: Create owl:sameAs links between N4L organisms and NCBI Taxonomy IRIs
# Used by: N4L/KG-Microbe integration workflow (archived)
# Type: SPARQL UPDATE (inserts into named graph)

PREFIX owl: <http://www.w3.org/2002/07/owl#>
INSERT {
    GRAPH <http://example.com/n4l_metpo/direct_ncbitaxid_same_as> {
        ?s owl:sameAs ?ncbi_iri .
        ?ncbi_iri a <http://example.com/n4l_metpo/organism> .
    }
}
WHERE {
    ?s <http://example.com/n4l/ncbi_tax_id> ?raw_id .
    FILTER(isLiteral(?raw_id))
    BIND(STR(?raw_id) AS ?id_str)
    BIND(STRBEFORE(?id_str, ".") AS ?int_part)
    FILTER(STRLEN(?int_part) > 0 && REGEX(?int_part, "^[0-9]+$"))
    BIND(IRI(CONCAT("http://purl.obolibrary.org/obo/NCBITaxon_", ?int_part)) AS ?ncbi_iri)
}
