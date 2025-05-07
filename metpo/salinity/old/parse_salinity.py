#%%
import pandas as pd
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from quantulum3 import parser
from rdflib import Dataset, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, XSD
#%%
# Correct endpoint for your 'n4l_tables' repository
endpoint_url = "http://localhost:7200/repositories/n4l_tables"
#%%
# Namespaces
EX = Namespace("http://example.com/n4l_metpo_quantulum3/")
N4L = Namespace("http://example.com/n4l_metpo/")
#%%
# Named graph URI
graph_uri = URIRef("http://example.com/n4l_metpo/parsed_salinity")
#%%
parsed_salinity_nquads = "parsed_salinity.nq"
#%%

query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT distinct ?provenance ?subject ?organism ?p ?value
WHERE {
    graph ?provenance {
        ?subject ?p ?value .
    }
    ?subject owl:sameAs ?organism
    graph <http://example.com/n4l_metpo/property_hierarchy> {
        ?p rdfs:subPropertyOf <http://example.com/n4l_metpo/salinity_text> .
    }
    GRAPH <http://example.com/n4l_metpo/direct_ncbitaxid_same_as> {
        ?organism a <http://example.com/n4l_metpo/organism> .
    }
}
"""
#%%
# Set up SPARQL connection
sparql = SPARQLWrapper(endpoint_url)
#%%
sparql.setQuery(query)
#%%
sparql.setReturnFormat(JSON)
#%%
# Run the query
results = sparql.query().convert()
#%%
# Convert to DataFrame
bindings = results["results"]["bindings"]
#%%
records = [
    {
        "provenance": b["provenance"]["value"],
        "subject": b["subject"]["value"],
        "organism": b["organism"]["value"],
        "predicate": b["p"]["value"],
        "value": b["value"]["value"]
    }
    for b in bindings
]
#%%
df = pd.DataFrame(records)
#%%
df
#%%
# Create an RDF Dataset
ds = Dataset()
g = ds.graph(graph_uri)

g.bind("ex", EX)
g.bind("xsd", XSD)
g.bind("n4l", N4L)
#%%
# Iterate through the DataFrame
for idx, row in df.iterrows():
    provenance_graph = URIRef(row["provenance"])
    subject = URIRef(row["subject"])
    organism = URIRef(row["organism"])
    predicate = URIRef(row["predicate"])
    input_text = row["value"]

    # Create a node for the parsing source
    source_node = BNode()
    g.add((source_node, RDF.type, EX.ParsingSource))
    g.add((source_node, EX.hasRawText, Literal(input_text)))

    # Attach provenance information
    g.add((source_node, EX.provenanceGraph, provenance_graph))
    g.add((source_node, EX.originalSubject, subject))
    g.add((source_node, EX.organism, organism))
    g.add((source_node, EX.predicate, predicate))

    # Parse quantities
    quantities = parser.parse(input_text)

    for q in quantities:
        quantity_node = BNode()
        g.add((quantity_node, RDF.type, EX.ParsedQuantity))
        g.add((quantity_node, EX.surfaceText, Literal(q.surface)))

        # Handle min/max
        if q.uncertainty is None:
            min_value = max_value = q.value
        else:
            min_value = q.value - q.uncertainty
            max_value = q.value + q.uncertainty

        g.add((quantity_node, EX.hasMinimumValue, Literal(min_value, datatype=XSD.double)))
        g.add((quantity_node, EX.hasMaximumValue, Literal(max_value, datatype=XSD.double)))

        if q.unit and q.unit.name != "dimensionless":
            g.add((quantity_node, EX.hasUnit, Literal(q.unit.name)))

        # Handle prefix/suffix
        span_start, span_end = q.span
        prefix = input_text[:span_start].strip()
        suffix = input_text[span_end:].strip()

        if prefix:
            g.add((quantity_node, EX.prefixText, Literal(prefix)))
        if suffix:
            g.add((quantity_node, EX.suffixText, Literal(suffix)))

        # Link quantity to its parsing source
        g.add((quantity_node, EX.fromSource, source_node))
#%%
# Serialize into N-Quads string (not saving to file)
nquads_output = ds.serialize(format="nquads")
#%%
upload_url = f"{endpoint_url}/statements"
#%%
# POST directly from memory
response = requests.post(
    upload_url,
    headers={"Content-Type": "application/n-quads"},
    data=nquads_output.encode("utf-8")  # requests expects bytes
)

# Check result
print(f"Status code: {response.status_code}")
if response.ok:
    print("✅ Upload successful!")
else:
    print(f"❌ Upload failed: {response.text}")
#%%
