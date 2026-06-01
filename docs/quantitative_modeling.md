# Modeling quantitative growth traits in METPO

Status: draft for discussion (2026-05-29). Covers how METPO represents
quantitative, gradient-response traits, why the `optimum` / `minimum` /
`maximum` / `range` / `delta` variants exist, and the policy for choosing
between a quantitative data property, a phenotype class, or both.

## The quantitative axes

METPO represents three kinds of quantitative information, and only the first
kind carries the full variant set:

1. **Growth-response gradients.** Continuous environmental variables that an
   organism responds to with a growth-rate curve over a permissive interval:
   - temperature (Celsius)
   - pH
   - salinity / NaCl concentration (% w/v)

2. **Genome / sequence metrics.** Fixed scalar properties of the genome, each a
   single value with no internal optimum: GC percentage, genome size, gene
   count, coding density.

3. **Cell morphometry.** Cell length and cell width, which have a measured
   spread (min, max) but no biological "optimum".

A consequence: the variant vocabulary tracks the *shape* of the underlying
quantity. Growth-response gradients get `optimum`, `range`, and `delta` bin
families; GC gets only coarse `low` / `mid` / `high` bins; cell dimensions get
only `minimum` / `maximum` value properties.

## Why the min / max / optimum / range / delta variants

An organism's relationship to a continuous gradient is not a single number. It
is a growth-response curve: a permissive window with an internal peak. Several
descriptors are needed to characterize that curve, and each answers a different
biological question.

| Variant | Meaning | Question it answers |
|---|---|---|
| minimum | lower bound of the permissive window | what is the coldest / most acidic / least saline condition that still permits growth |
| maximum | upper bound of the permissive window | what is the hottest / most alkaline / most saline condition that still permits growth |
| optimum | value at which growth rate is maximal | where does the organism grow best (this is **not** the midpoint of min and max; it usually sits closer to the maximum) |
| range | the interval [min, max] | what is the full permissive window |
| delta | the width of the window, `max - min` | how broad is the organism's tolerance (stenotolerant vs eurytolerant) |

`minimum`, `optimum`, and `maximum` are the three cardinal points that define
the curve. `range` and `delta` are derived summaries of its breadth. They are
not redundant: two organisms can share an optimum of 37 C while one grows
30 to 40 C (narrow) and another 4 to 50 C (wide); `delta` is what distinguishes
them. Because `delta` is a computed difference, its equivalent-class formula is
error-prone (see issue #357, an inverted NaCl-delta formula).

Each cardinal or derived variable is then discretized into a named bin family
(`very low` / `low` / `mid1..4` / `high`). The classic qualitative phenotypes
(psychrophile / mesophile / thermophile; acidophile / neutrophile / alkaliphile;
halophile) are bins of the **optimum** variable.

## Property, class, or both

The same quantitative fact can be modeled two ways:

- **Quantitative data property** (number on an edge): e.g.
  `<organism> 'has minimum temperature value' "4.0"^^xsd:decimal`. Lossless,
  supports numeric query and aggregation, faithful to numeric source data, no
  threshold commitments.
- **Phenotype class** (a quality term): e.g. `'temperature minimum tolerance'`,
  or a bin such as `'temperature optimum high'`. Mappable to other ontologies,
  reasonable, browsable, and the only sensible home for traits that have no
  number (catalase positive, rod-shaped, motile).

### The hazard: silent shadows

Issue #228 records the rule: METPO should not carry the same fact as both an
independently-asserted class and an independently-asserted property. When a
single source gives a number and a curator *also* hand-asserts a bin, the two
can drift, and a query against one representation silently misses facts recorded
only in the other.

### Why "both" is still sometimes correct

Sources are heterogeneous, and this is the decisive point:

- A numeric source (BacDive, metatraits) reports values ("grows 4 to 42 C,
  optimum 37"). Here the data property is the lossless primary, and the bin
  class can be **derived** from the value.
- A label-only source (BactoTraits) reports just the bin ("mesophilic") with no
  underlying number. Here only the class can be populated; there is no value to
  store, and the number cannot be recovered from the bin.

So the class and the property are not always shadows: they can carry
information from sources that cannot be derived from one another. Both
representations legitimately exist as ingest targets for the two kinds of
evidence.

### Policy

1. **Categorical traits** (biochemical tests, colony morphology, flagellation,
   capsule, biofilm, lifestyle tolerances): **class only**. There is no value to
   lose.
2. **Quantitative growth parameters** (temperature / pH / salinity, each of
   optimum / min / max): keep the quantitative **data property as the source of
   truth for the value**.
   - When a class (bin or tolerance term) is also wanted, it must be **derived**
     from the value, not independently asserted. Encode the derivation in the
     schema as an equivalent-class axiom over the property
     (the `'temperature optimum' and ('has value' some xsd:decimal[>= 40])`
     pattern already in the sheet), so there is one source of truth.
   - When evidence is label-only, assert the class directly and leave the value
     empty.
3. **Documentation requirement.** Wherever both representations coexist, the
   relationship must be explicit in two places: this document (textual), and the
   schema (the equivalent-class axiom, plus a machine-actionable companion
   annotation linking a class to its datatype property rather than only a
   free-text "Companion to ..." note in the definition).
4. **QC requirement.** For any organism that has both a value and an asserted
   bin, a check must confirm the asserted bin matches the bin the value would
   derive. A mismatch is a data error.

### Tooling caveat

The build reasoner is ELK (`reason_test`). ELK does **not** reason over datatype
facet restrictions (`xsd:decimal[>= 40]`). A derivation that is meant to be
*inferred* therefore needs either a non-ELK reasoner (HermiT / Pellet) in CI, or
a materialization step (SPARQL / Python) that computes bin membership from the
value. If the derivation lives only in prose, it is the silent shadow that
policy item 2 forbids.

## References

- #228: we do not need both properties and classes for optimal pH observation
- #357: NaCl delta high equivalent-class formula is inverted
- #371: removal of the observation reification layer (the reason values sit
  directly on the organism edge rather than on a reified measurement node)
- #424: Marcin's proposed cohort that completes both sides of the dual for the
  temperature / pH / salinity optimum, min, and max parameters
