DELETE {
  ?s ?p "0" .
}
WHERE {
  ?s ?p "0" .
  FILTER(?p = <http://example.com/n4l/subfamily_taxon> ||
         ?p = <http://example.com/n4l/subgenus_taxon> ||
         ?p = <http://example.com/n4l/subclass_taxon> ||
         ?p = <http://example.com/n4l/subspecies_taxon> ||
         ?p = <http://example.com/n4l/suborder_taxon> ||
         ?p = <http://example.com/n4l/species_taxon> ||
         ?p = <http://example.com/n4l/genus_taxon> ||
         ?p = <http://example.com/n4l/family_taxon> ||
         ?p = <http://example.com/n4l/order_taxon> ||
         ?p = <http://example.com/n4l/class_taxon> ||
         ?p = <http://example.com/n4l/product_id> ||
         ?p = <http://example.com/n4l/vendor_id> ||
         ?p = <http://example.com/n4l/url> ||
         ?p = <http://example.com/n4l/vendor> ||
         ?p = <http://example.com/n4l/phylum_taxon> ||
         ?p = <http://example.com/n4l/domain_taxon>)
}
