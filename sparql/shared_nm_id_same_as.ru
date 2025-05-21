PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

INSERT {
    GRAPH <http://example.com/n4l_metpo/shared_nm_id_same_as> {
        ?s1 owl:sameAs ?s2 .
    }
}
WHERE {
    ?s1 ?p1 ?o .
    ?s2 ?p2 ?o .
    FILTER(?s1 != ?s2)

    GRAPH <http://example.com/n4l_metpo/property_hierarchy> {
        ?p1 rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
        ?p2 rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
    }

    OPTIONAL { ?s1 <http://example.com/n4l/ncbi_tax_id> ?nt1 }
    OPTIONAL { ?s2 <http://example.com/n4l/ncbi_tax_id> ?nt2 }
    FILTER(BOUND(?nt1) || BOUND(?nt2))
}
