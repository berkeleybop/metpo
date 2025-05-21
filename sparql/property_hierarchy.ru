# partial

INSERT DATA {
  GRAPH <http://example.com/n4l_metpo/property_hierarchy> {
    <http://example.com/n4l/name_id> a owl:DatatypeProperty ;
                                     rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
    <http://example.com/n4l/n4l_name_id> a owl:DatatypeProperty ;
                                         rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
    <http://example.com/n4l/n4l_id> a owl:DatatypeProperty ;
                                    rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
    <http://example.com/n4l/n4l_preferred_id> a owl:DatatypeProperty ;
                                              rdfs:subPropertyOf <http://example.com/n4l_metpo/nm_identifier> .
  }
}
