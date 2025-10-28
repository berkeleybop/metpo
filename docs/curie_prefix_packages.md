# Python packages for converting between CURIE and IRI representations

Below are the Python libraries people actually use in practice to go back and forth between CURIEs (`ENVO:00002006`) and full IRIs (`http://purl.obolibrary.org/obo/ENVO_00002006`). They’re grouped by how opinionated / batteries-included they are.

---

## 1. `curies`

**TL;DR:** lightweight, focused, modern.  
**Use it if:** you want a clean little utility whose only job is CURIE ↔ IRI expansion/compaction using a prefix map you control.

```python
from curies import Converter

prefix_map = {
    "ENVO": "http://purl.obolibrary.org/obo/ENVO_",
    "CHEBI": "http://purl.obolibrary.org/obo/CHEBI_",
}

conv = Converter.from_prefix_map(prefix_map)

conv.expand("ENVO:00002006")
# -> 'http://purl.obolibrary.org/obo/ENVO_00002006'

conv.contract("http://purl.obolibrary.org/obo/CHEBI_15377")
# -> 'CHEBI:15377'
```

Why it's nice:
- Doesn’t drag in RDF libraries.
- Round-tripping is deterministic if your map is deterministic.
- You can merge multiple prefix maps and choose priority order.

Why it might *not* be enough alone:
- It doesn’t fetch prefixes from registries for you; you decide the mapping.

This is usually the first recommendation for pipelines where you already know the prefix policy (e.g. OBO style vs BioPortal style).

---

## 2. `linkml-runtime` / `prefixmaps`

**TL;DR:** LinkML-native approach.  
**Use it if:** you're already in the LinkML ecosystem and you want to use the same prefix map as your schema.

LinkML models carry a `prefixes:` block, and `linkml-runtime` knows how to use that to expand/contract.

```python
from linkml_runtime.linkml_model.meta import Prefix
from prefixmaps import load_context
from prefixmaps.datamodel.prefixmaps import PrefixMap

prefixes = {
    "envo": Prefix(prefix_prefix="envo",
                   prefix_reference="http://purl.obolibrary.org/obo/ENVO_"),
    "nmdc": Prefix(prefix_prefix="nmdc",
                   prefix_reference="https://w3id.org/nmdc/")
}

pm = PrefixMap(prefixes=[*prefixes.values()])

pm.expand_curie("envo:00002006")
# -> 'http://purl.obolibrary.org/obo/ENVO_00002006'

pm.compress_iri("https://w3id.org/nmdc/Study")
# -> 'nmdc:Study'
```

Why it's nice:
- Your schema is the source of truth. No silent drift between what validation thinks and what your ETL thinks.
- Supports JSON-LD-style contexts and multiple contexts layered together.

Why it might annoy you:
- A little more ceremony to construct the maps.
- Some functions live in `prefixmaps`, some are surfaced via `linkml_runtime`; it's improving but occasionally fiddly.

In workflows where you're emitting JSON that has to validate against a LinkML schema (like NMDC), this is usually what you want so you don't get `CHEBI` vs `chebi` surprises.

---

## 3. `oaklib`

**TL;DR:** same job as `curies`, but in a larger ontology toolkit.  
**Use it if:** you're already using OAKlib for ontology I/O, reasoning, term lookup, etc.

OAKlib loads prefix maps from ontologies, the OBO library conventions, Bioregistry, etc., and gives you helpers to go back and forth:

```python
from oaklib.utilities.curie_util import expand_curie, contract_uri
from oaklib import get_adapter

# Most OAK adapters come preloaded with a prefix map
adapter = get_adapter("sqlite:obo:envo")

expand_curie("ENVO:00002006", adapter)
# -> 'http://purl.obolibrary.org/obo/ENVO_00002006'

contract_uri("http://purl.obolibrary.org/obo/ENVO_00002006", adapter)
# -> 'ENVO:00002006'
```

Why it's nice:
- You don't have to maintain the prefix map yourself if you trust the ontology source.
- Plays well with multiple ontologies and cross-prefix collisions.

Why it might be overkill:
- Pulls in more machinery than you may want in a tiny microservice whose only job is CURIE munging.

If you're doing term normalization anyway (ENVIRONMENT → ENVO:XXXXXX), OAKlib earns its keep.

---

## 4. `bioregistry`

**TL;DR:** global registry of biomedical prefixes.  
**Use it if:** you need registry-backed normalization across life science prefixes, including non-OBO stuff like UniProt or PubChem.

```python
from bioregistry import curie_to_uri, uri_to_curie

curie_to_uri("ENVO:00002006")
# -> 'http://purl.obolibrary.org/obo/ENVO_00002006'

uri_to_curie("http://purl.obolibrary.org/obo/ENVO_00002006")
# -> 'envo:00002006'  # note: lowercase prefix style
```

Why it's nice:
- It knows about tons of namespaces, not just OBO.
- It can canonicalize prefixes (e.g. `EnVo` → `envo`).

Why it can bite you:
- The returned prefix form might not match what *you* consider canonical (e.g. `CHEBI` vs `chebi`). If you're emitting IDs into an ecosystem with opinions (NCBI, OBO, MIxS submissions, etc.), that matters.

`bioregistry` is great when you're trying to ingest foreign IDs and guess what the submitter meant.

---

## 5. `rdflib`

**TL;DR:** old reliable RDF stack.  
**Use it if:** you're already in RDF graphs and namespaces, e.g. you're serializing Turtle/JSON-LD.

`rdflib` has a `NamespaceManager` that can bind a prefix to a base IRI and can `qname()` an IRI back to CURIE-ish form:

```python
from rdflib import Graph, Namespace, URIRef

g = Graph()
g.bind("envo", Namespace("http://purl.obolibrary.org/obo/ENVO_"))

iri = URIRef("http://purl.obolibrary.org/obo/ENVO_00002006")
g.namespace_manager.qname(iri)
# -> 'envo:00002006'
```

Going the other direction:

```python
from rdflib.namespace import split_uri

prefix, local = split_uri(iri)
# prefix = 'http://purl.obolibrary.org/obo/ENVO_'
# local = '00002006'
```

Why it's nice:
- You’re probably already using it if you're round-tripping RDF/XML, Turtle, etc.
- Namespace bindings survive serialization so you get stable CURIEs in output.

Why it's not ideal for standalone CURIE work:
- There's no single "expand this CURIE string" helper unless you reimplement a tiny wrapper.
- It will happily emit CURIEs that are syntactically fine for Turtle but not what you want in MIxS-style tabular IDs.

---

## 6. Honorable mentions

These aren't pure CURIE/IRI converters, but worth knowing:

- **`pronto`**: ontology library in Python. It parses OBO and often exposes terms as `id` (CURIE) and `iri` (full IRI). Great for inspection, less great as a general converter.
- **`robot`** (Java, not Python): If you shell out to ROBOT in Make/CLI land, `robot convert --prefixes`. You’ve probably already done this in ODK work.
- **`prefixcommons` / `prefixmap` older libs**: mostly superseded by `curies`, `prefixmaps`, and `bioregistry`.

---

## How to choose

Here’s how to pick in different situations:

- **You want a tiny, explicit utility in your own ETL code:**  
  → `curies` with your own prefix map checked into git.

- **You’re emitting/validating LinkML (NMDC schema, MIxS schema) and want zero drift between schema and runtime:**  
  → `linkml-runtime` / `prefixmaps`.

- **You’re already using OAKlib for ontology lookups, synonyms, ancestors, etc.:**  
  → use OAKlib’s CURIE helpers so your expansion rules match whatever ontology source you loaded.

- **You’re normalizing arbitrary life science prefixes from the wild (UniProt, NCBI Taxon, PubChem, etc.) and want best-effort guessing:**  
  → `bioregistry`.

- **You’re serializing RDF with rdflib and just want pretty CURIEs in Turtle / JSON-LD output:**  
  → bind prefixes in `rdflib`’s `NamespaceManager` and let it qname() / compact for you.

---

## Subtle but important gotcha for MIxS / NMDC work

There is no single “correct” expansion of a CURIE unless you freeze a prefix map.

Example:

- `ENVO:00002006`  
  - OBO-style → `http://purl.obolibrary.org/obo/ENVO_00002006`  
  - BioPortal-style → `http://purl.bioontology.org/ontology/ENVO/00002006`

Both are “IRIs,” but only one is the one you want to hand to OBO tooling, and only one will round-trip back to `ENVO:00002006` using OBO prefix rules.

So: whichever library you choose, treat the prefix map as part of your contract and version it like code, not like a runtime guess.

---

## Practical recommendation (for MIxS / NMDC-style work)

Given:
- you're already generating LinkML for MIxS/NMDC
- you care about reproducibility and audit trails
- you sometimes emit tables with CURIEs and sometimes JSON-LD-ish objects with IRIs

Recommended pattern:

1. Define the canonical prefix map once in your LinkML schema (or a small YAML you treat like that).
2. Use `curies.Converter` in lightweight code and `prefixmaps`/`linkml_runtime` where you’re already importing the schema.
3. Only fall back to `bioregistry` when you're trying to interpret somebody else's weird prefix and guess what IRI they meant.

That gives you predictable round-tripping and keeps reviewers from arguing about `CHEBI:` vs `chebi:` in PRs.
