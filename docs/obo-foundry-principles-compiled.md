# OBO Foundry Principles (Compiled)

> Source root: <https://obofoundry.org/principles/>
> License: CC-BY — attribute OBO Foundry and original authors.
> Compiled on: 2025-11-03 17:58:48


---

**Source:** <https://obofoundry.org/principles/fp-000-summary.html>

Principles: Overview
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
These principles are intended as normative for OBO Foundry ontologies, and ontologies submitted for review will be evaluated according to them. We consider these to be generally good practice, and recommend they be considered even if there are no plans to submit an ontology for review by the Foundry. Where we use capitalized words such as “MUST”, and “SHOULD”, they will be interpreted according to [RFC 2119: Key words for use in RFCs to Indicate Requirement Levels](https://www.ietf.org/rfc/rfc2119.html) when the principles are applied during reviews of ontologies for inclusion in the Foundry.
There is currently an ongoing process to clarify the wording of the principles and expand on their purpose, implementation, and criteria to be used to evaluate ontologies for compliance with each principle. Please use the [issue tracker](https://github.com/OBOFoundry/OBOFoundry.github.io/issues) to let us know if there are further clarifications that you would like to see addressed for any of the principles.
Quick Summary
The following summarizes each principle. See individual pages for details.
P1) Open - The ontology MUST be openly available to be used by all without any constraint other than (a) its origin must be acknowledged and (b) it is not to be altered and subsequently redistributed in altered form under the original name or with the same identifiers.
P2) Common Format - The ontology is made available in a common formal language in an accepted concrete syntax.
P3) URI/Identifier Space - Each ontology MUST have a unique IRI in the form of an OBO Foundry permanent URL (PURL).
P4) Versioning - The ontology provider has documented procedures for versioning the ontology, and different versions of ontology are marked, stored, and officially released.
P5) Scope - The scope of an ontology is the extent of the domain or subject matter it intends to cover. The ontology must have a clearly specified scope and content that adheres to that scope.
P6) Textual Definitions - The ontology has textual definitions for the majority of its classes and for top level terms in particular.
P7) Relations - Relations should be reused from the Relations Ontology (RO).
P8) Documentation - The owners of the ontology should strive to provide as much documentation as possible.
P9) Documented Plurality of Users - The ontology developers should document that the ontology is used by multiple independent people or organizations.
P10) Commitment To Collaboration - OBO Foundry ontology development, in common with many other standards-oriented scientific activities, should be carried out in a collaborative fashion.
P11) Locus of Authority - There should be a person who is responsible for communications between the community and the ontology developers, for communicating with the Foundry on all Foundry-related matters, for mediating discussions involving maintenance in the light of scientific advance, and for ensuring that all user feedback is addressed.
P12) Naming Conventions - The names (primary labels) for elements (classes, properties, etc.) in an ontology must be intelligible to scientists and amenable to natural language processing. Primary labels should be unique among OBO Library ontologies.
P13) Notification of Changes - Ontologies SHOULD announce major changes to relevant stakeholders and collaborators ahead of release.
P16) Maintenance - The ontology needs to reflect changes in scientific consensus to remain accurate over time.
P19) Term Stability - The definition of a term MUST always denote the same thing(s)–known as “referent(s)”–in reality. If a proposed change to the definition would substantially change its referents, then a new term with new IRI and definition MUST instead be created.
P20) Responsiveness - Ontology developers MUST offer channels for community participation and SHOULD be responsive to requests.

---

**Source:** <https://obofoundry.org/principles/fp-001-open.html>

Principle: Open (principle 1)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The ontology MUST be openly available to be used by all without any constraint other than (a) its origin must be acknowledged and (b) it is not to be altered and subsequently redistributed in altered form under the original name or with the same identifiers.
Purpose
OBO Foundry ontologies are resources for the entire biological and biomedical community. Furthermore, in order to realize the OBO Foundry vision of a suite of interoperable ontologies, ontology developers must be free to re-use terms from any OBO Foundry ontology. For these reasons, the ontologies must be available to all without any constraint on their use or redistribution. Nonetheless, it is proper that their original source is always credited and that after any external alterations, ontologies must never be redistributed under the same name or with the same identifiers.
Recommendations and Requirements
For ontology providers
OBO Foundry Ontologies MUST EITHER be released under a [Creative Commons Attribution 3.0 Unported (CC BY 3.0)](https://creativecommons.org/licenses/by/3.0/) license or later (e.g. [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), OR released into the public domain under [Creative Commons CC0 1.0 Public Domain Dedication (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/). The license MUST be clearly stated using the [http://purl.org/dc/terms/license](http://purl.org/dc/terms/license) property followed by the URL representing the license (e.g. [https://creativecommons.org/licenses/by/3.0/](https://creativecommons.org/licenses/by/3.0/)) in the ontology file ([OWL example](https://oboacademy.github.io/obook/reference/formatting-license/)).
Note: CC-BY licenses allow others to distribute, remix, tweak, and build upon the work, even commercially, as long as they credit the creators for the original creation. CC0 specifies that the creators of an ontology waive, to the extent that they legally can be, all rights and place the ontology in the public domain. It does not prevent them from requesting that the ontology be properly credited and cited, but prevents any legal recourse if it is not credited. Many pros and cons of CC-BY versus CC0 are laid out in [this discussion](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/285). It is important to note that one can move from CC-BY to CC0 but not the other way around.
For ontology re-use
-
The original source of an ontology must be credited according to the terms specified in the comment annotation of the ontology.
-
Altered versions of an ontology that are not part of an official release (that is, by the ontology developers) must not be redistributed under the same name or with the same ontology IRI.
-
If an individual term is reused without change to the definition, the original term IRI should be used. If the definition of a term (either text or logical) is changed, the original term IRI should not be reused. Suggestions for changes or improvements to term definitions should be submitted to the appropriate ontology issue tracker.
-
Regardless of which license an ontology uses, we strongly request and recommend that any reuse of an ontology attributes the source in accordance with scientific norms and the
[OBO Citation and Attribution Policy](/citation/Citation.html).
Implementation
For ontology providers
.owl
files
-
OBO Foundry Ontologies MUST specify the reuse constraints using the following annotations in any publically released OWL version of the ontology:
- dcterms:license - specifies the license - see Example 1 (below)
- rdfs:comment - specifies terms of reuse - see Example 1 (below)
-
OBO Foundry Ontologies that host terms developed by an external group (but which are not part of an existing ontology) must credit the external group - see Examples (below)
-
See below under ontology re-use for guidelines on importing individual terms from external ontologies.
.obo
files
- OBO Foundry Ontologies must specify the reuse constraints using the following annotations in any publically released OBO version of the ontology:
- the license in a separate property annotation, which can be converted to a dc:license statement if the ontology is converted to OWL - see Example 2 (below)
- the reuse constraints using a comment in the official OBO version of the ontology - see Example 2 (below)
For ontology re-use
Individual terms
The attribution method for individual terms reused in another ontology (e.g., by MIREOT) is via use of their original IRI or ID - see Examples (below).
-
In OWL - Any ontology re-using individual terms from another ontology should:
- re-use the original term IRI (which for OBO Foundry ontologies is generally in the form of an OBO Foundry PURL)
- use an IAO:imported from annotation
[http://purl.obolibrary.org/obo/IAO_0000412](http://purl.obolibrary.org/obo/IAO_0000412)on each imported term to link back to the group (i.e. ontology) maintaining it, where more information would be available about the license - include any annotations for term or definition editors from the original ontology
-
In OBO - Any ontology re-using individual terms from another ontology should:
- re-use the original term ID (of the form <GO:0000001>)
- include any XREFs to the original term editor(s) from the original ontology
Full ontologies
The attribution method for importing an entire ontology in OWL is simply to import the ontology without modification.
- The attribution method for using an ontology for an analysis is to cite the ontology as requested by the ontology developers. If the developers have not specified how to cite their ontology, use the ontology IRI, a publication if available, and the ontology website if available.
Examples
NOTE: All examples are for illustration purposes and should not be considered valid ontology axioms.
Example 1: RDF-XML code for the license annotations:
<dcterms:license rdf:resource="http://creativecommons.org/licenses/by/4.0/"/>
<rdfs:comment xml:lang="en">"Ontology name" by "developer groups" is licensed
under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).</rdfs:comment>
<rdfs:comment xml:lang="en">"Ontology name" by developer groups is
licensed under CC BY 4.0. You are free to share (copy and redistribute
the material in any medium or format) and adapt (remix, transform, and
build upon the material) for any purpose, even commercially. for any
purpose, even commercially. The licensor cannot revoke these freedoms as
long as you follow the license terms. You must give appropriate credit
(by using the original ontology IRI for the whole ontology and original
term IRIs for individual terms), provide a link to the license, and
indicate if any changes were made. You may do so in any reasonable
manner, but not in any way that suggests the licensor endorses you or
your use.</rdfs:comment>
The above comment for reuse conditions is for example only. Ontologies may use different wording appropriate to their own needs, as long as it is consistent with the license.
Example 2: Example of OBO code for the license annotation:
property_value: http://purl.org/dc/terms/license http://creativecommons.org/licenses/by/4.0/
remark: *Ontology name* by *developer group(s)* is licensed under CC BY 4.0. You
are free to share (copy and redistribute the material in any medium
or format) and adapt (remix, transform, and build upon the material)
for any purpose, even commercially. You must give appropriate credit
(by using the original ontology IRI for the whole ontology or
original term IRIs for individual terms), provide a link to the
license, and indicate if any changes were made. You may do so in any
reasonable manner, but not in any way that suggests the licensor
endorses you or your use.
Example 3: How to credit an external group for developing a term in your ontology.
The first course of action should be to reuse the external term as is, by importing it with the original IRI (e.g. by MIREOT). At a minimum, the term definition should be imported, but there is still an open discussion about which other annotation need to be imported.
Please see the discussion tab for additional discussion of how to use different annotation properties to credit external ontologies or definition sources.
Example 3A: IAO:imported from
The Ontology for Biomedical Investigation (OBI) imports the class “environmental material” from the Environment Ontology (ENVO), using OntoFox. The imported from axiom is automatically generated by Ontofox and added to “environmental material” in OBI:
<!-- <http://purl.obolibrary.org/obo/ENVO_00010483> -->
<owl:Class rdf:about="&obo;ENVO_00010483">
<rdfs:label rdf:datatype="&xsd;string">environmental
material</rdfs:label>
<rdfs:subClassOf rdf:resource="&obo;BFO_0000040"/>
<obo:IAO_0000115 rdf:datatype="&xsd;string">Material in or on which
organisms may live.</obo:IAO_0000115>
<obo:IAO_0000111 rdf:datatype="&xsd;string">environmental
material</obo:IAO_0000111>
<obo:IAO_0000412 rdf:resource="&obo;envo.owl"/>
</owl:Class>
Counter-Examples
- An ontology with no license statement is by default subject to the most restrictive copyright laws for those parts of the ontology that are copyrightable, and therefore is not useful within the OBO Foundry.
- CC BY-ND allows for redistribution, commercial and non-commercial, as long as it is passed along unchanged and in whole, with credit to the creators. This license is too restrictive for the OBO Foundry, because it requires that the ontology be re-used in its entirety, which prevents the re-use of individual terms.
Criteria for Review
The ontology must have a license that is equivalent to or less restrictive than CC-BY, specified as described in the text and examples above.
[This check is automatically validated.](checks/fp_001) The automatic check fully covers the requirements for this principle.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%231+%22Open%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%231+%22Open%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).
See also [this discussion of licensing](https://github.com/OBOFoundry/Operations-Committee/issues/103) by the OBO Foundry Operations Committee focusing on Creative Commons licenses.

---

**Source:** <https://obofoundry.org/principles/fp-002-format.html>

Principle: Common Format (principle 2)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The ontology is made available in a common formal language in an accepted concrete syntax.
Purpose
A common format allows the maximum number of people to access and reuse an ontology.
Recommendations and Requirements
All ontologies MUST have at least one OWL product whose name corresponds to the registered prefix (e.g., ‘GO’ –> go.owl, ‘OBI’ –> obi.owl). Thus the ontology whose IRI is http://purl.obolibrary.org/obo/ro.owl (known to the OBO Foundry as ‘RO’), must have at least the product ro.owl. Developers are free to use whatever combination of technologies and formats is appropriate for development. However, the official OWL PURL (see [Principle 3](https://obofoundry.org/principles/fp-003-uris.html)) for the ontology MUST resolve to a syntactically valid OWL file using the [RDF-XML](https://www.w3.org/TR/rdf-syntax-grammar/) syntax.
Developers can OPTIONALLY produce ontologies in other formats. These are conventionally the same IRI as the owl, but with .owl changed to the relevant extension (e.g., ‘.obo’, ‘.json’). Note that such products are not listed by default. If you produce an additional format product, you should register it under the ‘products’ field in the appropriate metadata file found in this [folder](https://github.com/OBOFoundry/OBOFoundry.github.io/tree/master/ontology).
Implementation
ROBOT offers functionality to convert a variety of formats, including OBO, to RDF/XML. Protégé allows you to save ontologies in RDF/XML, as well. The [Ontology 101 Tutorial](https://ontology101tutorial.readthedocs.io/en/latest/StartingProtege.html) has directions on starting and saving in Protégé.
Examples
-
The
[Gene Ontology](http://geneontology.org)is maintained as OBO-Format. It is automatically converted to OWL and is available in both OBO and OWL via the OBO Foundry. -
The
[ChEBI ontology](https://www.ebi.ac.uk/chebi/)is maintained in a relational database using a custom schema, but makes an OBO-Format file available that is automatically converted to OWL. It is available in both OBO and OWL via the OBO Foundry. -
[OBI](http://obi-ontology.org)is maintained as an OWL ontology.
Counter-Examples
An ontology that is in Frames format, OWL/XML, or OWL Manchester Syntax.
Criteria for Review
The ontology MUST be available in RDF/XML format.
[This check is automatically validated.](checks/fp_002) The automatic check fully covers the requirements for this principle.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%232+%22Format%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%232+%22Format%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-003-uris.html>

Principle: URI/Identifier Space (principle 3)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
Each ontology MUST have a unique IRI in the form of an OBO Foundry persistent URL (PURL) that includes the ontology’s short namespace.
Purpose
A unique namespace within the OBO Foundry Library allows the source of an element or term (e.g., class, property) from any ontology to be identified immediately by the prefix of the identifier. It also allows ontology element IRIs to be shortened to a compact URI or CURIE, which allows developers to use CURIES for working with ontologies. OWL syntax allows for ontologies and their elements to have identifiers in the form of an IRI. The OBO Foundry uses IRIs in the form of PURLs to allow an ontology and its elements to be resolvable (findable on the web). PURLs are URLs (and thus locate the resource) that are permanent or redirectable, allowing the URL to point to a new location when the resource moves. OBO Foundry PURLs use a standard format that includes the ontology namespace so that they can be easily maintained by a group of volunteers, and so ontology maintainers can update the location their PURL points to using a GitHub pull request.
Recommendations and Requirements
Each ontology MUST have a unique IRI in the form of an OBO Foundry permanent URL (PURL). The PURL must include the ontology namespace, which is a short string of letters (usually 2-5) that represents the ontology. Namespaces MUST be approved by the OBO Foundry Operations Committee. Every element (class, property, etc.) created by the ontology MUST use the namespace in the identifier of each element, as specified in the OBO Foundry [ID policy](http://www.obofoundry.org/id-policy).
Implementation
Ontology Namespace:
The ontology namespace MUST be unique; that is, it MUST NOT be in current use or have been used in the past. When used as part of the ontology IRI, the namespace is in lower case. When used as part of a CURIE, on its own, or as part of a term ID, the namespace MUST be capitalized (Note: this applies to ontologies submitted after 1st June 2024; mixed-case prefixes for ontologies submitted before this date may be retained).
To request a new namespace, ontology developers MUST follow the guidelines outlined here. Note that very short namespaces (2-3 characters) are reserved for ontologies that cover a general domain and are likely to be frequently used.
Ontology IRI:
The primary IRI for an OBO ontology IRI MUST have the following format: https://purl.obolibrary.org/obo/$namespace.owl
Note: To conform with OBO Foundry [Principle 2](https://obofoundry.org/principles/fp-002-format.html), the ontology IRI MUST resolve to the ontology file, not a landing page.
For guidelines on how to create IRIs for ontology elements/terms, see the OBO Foundry [ID policy](http://www.obofoundry.org/id-policy).
Examples
| Namespace | Ontology IRI | Term IRI | Term CURIE |
|---|---|---|---|
| GO | http://purl.obolibrary.org/obo/go.owl | http://purl.obolibrary.org/obo/GO_0008150 | GO:0008150 |
| PCO | http://purl.obolibrary.org/obo/pco.owl | http://purl.obolibrary.org/obo/PCO_0000000 | PCO:0000000 |
Counter Examples
The following counter examples are valid ontology IRIs, but do not conform with OBO Foundry principles.
- http://iridl.ldeo.columbia.edu/ontologies/SWEET.owl
Furthermore, these IRIs do not resolve to the ontology file.
-
http://purl.org/dc/terms/
-
http://dbpedia.org/ontology/
Criteria for Review
The ontology namespace MUST be registered following the procedures outlined within the [OBO Foundry membership requirements and technical details](http://www.obofoundry.org/docs/Policy_for_OBO_namespace_and_associated_PURL_requests.html) document. In addition, the ontology IRI MUST follow the format given above.
[This check is automatically validated.](checks/fp_003) The automatic check fully covers the requirements for this principle.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%233+%22URIs%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%233+%22URIs%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).
See also [this discussion](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/2596) of URI capitalization by the OBO Foundry Operations Committee.

---

**Source:** <https://obofoundry.org/principles/fp-004-versioning.html>

Principle: Versioning (principle 4)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The ontology provider has documented procedures for versioning the ontology, and different versions of ontology are marked, stored, and officially released.
Purpose
OBO projects share their ontologies using files in OWL or OBO format (see [Principle 2](https://obofoundry.org/principles/fp-002-format.html)). Ontologies are expected to change over time as they are developed and refined (see [Principle 16](https://obofoundry.org/principles/fp-016-maintenance.html)). This will lead to a series of different files. Consumers of ontologies must be able to specify exactly which ontology files they used to encode their data or build their applications, and be able to retrieve unaltered copies of those files in perpetuity. Note that this applies only to those versions which have been officially released.
Recommendations and Requirements
In addition to an IRI specifying the current release (see [Principle 3](https://obofoundry.org/principles/fp-003-uris.html)), each official release MUST have a unique version IRI that resolves to the specific ontology artifact indicated. Consumers can then use the version IRI to uniquely identify which official release of the ontology they used, and to retrieve unaltered copies of the file(s). A version IRI is a full path that MUST resolve to the particular version of the ontology artifact. Both the version IRI and the corresponding artifact MUST contain an identical version identifier string.
Version identifiers MUST either be of the form “YYYY-MM-DD” (that is, a date) OR use a numbering system (such as semantic versioning, i.e, of the form “NN.n”). Each version MUST associate with a distinct official release. The date versioning system is preferred, as it meshes with the requirement that version IRIs be specified using dated PURLs (see below).
If a date-based version identifier is used, it MUST conform to [ISO-8601](https://www.iso.org/iso-8601-date-and-time-format.html), ie. “YYYY-MM-DD”. Variants of this–such as (a) using two digits for year instead of four (b) using one digit for month or year (c) using a delimiter other than a hyphen (d) any other ordering such as day/month/year or month/day/year (c) any other variant–MUST NOT be used.
All OBO projects MUST also have versioned PURLs that resolve to the corresponding artifacts specified by the version IRIs, in perpetuity. If the files are moved, the PURL MUST be updated to resolve to the new location.
Note that the content of official release files MUST NOT be changed. For example, if a bug is found in some official released file for some ontology, the bug MUST NOT be fixed by changing the file(s) for that official release. Instead the bug fixes should be included in a new official release, with new files, and consumers can switch to the new release.
Additionally, each ontology SHOULD have an owl:versionInfo statement. When this is stated, it MUST correspond to the version Info.
Implementation
See examples (below) for guidelines on how to specify the version within the ontology itself. If terms are imported from an external ontology, the “IAO:imported from” annotation (see [Principle 1](http://obofoundry.org/principles/fp-001-open.html)) may specify a dated version of the ontology from which they are imported.
Regardless of the versioning system used for the ontology artifact, the version IRI SHOULD use an ISO-8601 dated PURL. In cases where there are multiple releases on the same day, the PURL points to the newest, and the previous release stays in the same folder or a subfolder, named in such a way as to distinguish the releases. Specifications for version IRIs are fully described in the OBO Foundry [ID policy](http://obofoundry.org/id-policy) document. In short:
For a given version of an ontology, the ontology should be accessible at the following URL, where ‘idspace’ is replaced by the IDSPACE in lower case:
OWL: http://purl.obolibrary.org/obo/idspace/YYYY-MM-DD/idspace.owl
OBO: http://purl.obolibrary.org/obo/idspace/YYYY-MM-DD/idspace.obo
For example, for the version of OBI released 2009-11-06, the OWL document is accessible at http://purl.obolibrary.org/obo/obi/2009-11-06/obi.owl.
An accepted alternative to the above scheme is to include /releases/ in the PURL, as follows:
OWL: http://purl.obolibrary.org/obo/idspace/releases/YYYY-MM-DD/idspace.owl
OBO: http://purl.obolibrary.org/obo/idspace/releases/YYYY-MM-DD/idspace.obo
Examples
For an OBO format ontology use the metadata tag:
data-version: 2015-03-31
data-version: 44.0
For an OWL format ontology, owl:versionInfo identifies the version and versionIRI identifies the resource:
<owl:versionInfo rdf:datatype="http://www.w3.org/2001/XMLSchema#string">2014-12-03</owl:versionInfo>
<owl:versionIRI rdf:resource="http://purl.obolibrary.org/obo/obi/2014-12-03/obi.owl"/>
CHEBI is an example of an OBO ontology that uses a non-date based system system for version identifier. An example versionIRI for CHEBI is http://purl.obolibrary.org/obo/chebi/187/chebi.owl. This corresponds to a value of 187
for data-version
in OBO format.
Criteria for Review
The released ontology MUST have a version IRI. The version IRI MUST use a date format (NS/YYYY-MM-DD/ontology.owl) OR use a semantic versioning format (e.g., NS/NN.n/ontology.owl). The version IRI MUST resolve to an ontology artifact that is associated with the same version identifier as used in the version IRI.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%234+%22Versioning%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%234+%22Versioning%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-005-delineated-content.html>

Principle: Scope (principle 5)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
NOTE
The wording of this principle is still in progress, with some issues still to be addressed (see Issues To Be Addressed below).
Summary
The scope of an ontology is the extent of the domain or subject matter it intends to cover. The ontology must have a clearly specified scope and content that adheres to that scope.
Purpose
An in-scope ontology prevents overlaps between ontologies (duplication of terms), facilitates user searches for specific content, and enables quick selection of ontologies of interest, yet still allows for new terms to be created via combination of existing terms (cross-products).
Recommendations and Requirements
Ideally the scope should be fairly narrow. Required terms that are out of scope should be imported from the appropriate ontology unless no such ontology exists and there is an immediate need for an out-of-scope term (or set thereof). We encourage the ontology maintainers to create a shareable file with such terms so that the community can access, reuse, edit, and add these new terms as new ontologies with the intended scope are developed.
Implementation
The domain (scope) covered by the ontology should be clearly stated. The statement should be brief and free of jargon; a few sentences should suffice. The content of the ontology should stay within the confines of the stated scope. Out-of-scope terms should be placed within a separate module that can be imported/exported as a single unit.
Generic terms must be maintained with community needs in mind. Mid/upper level terms should be considered for the [Core Ontology for Biology and Biomedicine (COB)](https://obofoundry.org/ontology/cob.html).
Examples
Counter-Examples
Issues To Be Addressed (partial list):
1.Would like a metadata tag in the ontology itself for this. TBD.
2.Possible need for controlled vocabulary for scope/domain (for example: Anatomy, Upper Level Ontology, Disease, Phenotype, Applicable taxonomy)
Criteria for Review
A scope (‘domain’) MUST be declared in the registry data, and terms from the ontology have to fall within that scope.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%235+%22Scope%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%235+%22Scope%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-006-textual-definitions.html>

Principle: Textual Definitions (principle 6)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The ontology has textual definitions for the majority of its classes and for top level terms in particular.
Purpose
A textual definition provides a human-readable understanding about what is a member of the associated class. Textual definitions are, optimally, in concordance with associated machine-readable logical definitions (the latter of which are OPTIONAL).
Recommendations and Requirements
Textual definitions MUST be unique within an ontology (i.e. no two terms should share a definition) and be written in English. Textual definitions SHOULD follow Aristotelian form (e.g. “a B that Cs” where B is the parent and C is the differentia), where this is practical.
For terms lacking textual definitions, there should be evidence of implementation of a strategy to provide definitions for all remaining undefined terms. In lieu of textual definitions, there can be elucidations when the term can not be rigorously defined. Note that textual definitions can be programmatically generated from logical definitions, if available (see [http://oro.open.ac.uk/21501/1/](http://oro.open.ac.uk/21501/1/)). In addition, [Dead Simple Ontology Design Patterns](https://github.com/INCATools/dead_simple_owl_design_patterns) (DOSDPs) can be used to generate both textual and logical definitions. DOSDPs are design specifications, written in YAML format, that specify structured text definitions and logical definitions for groups of ontology terms. These are widely used in many OBO Foundry ontologies, such as Mondo and uPheno. For some example patterns, see [Mondo patterns](https://mondo.readthedocs.io/en/latest/editors-guide/patterns/) and [uPheno patterns](https://github.com/obophenotype/upheno/tree/master/src/patterns/dosdp-patterns).
Logical definitions, when present, should agree with textual definitions and vice versa. This is important for two reasons: (1) Reasoners classify terms solely based on logical definitions, while humans predominantly classify terms based on textual definitions, and mismatches between the two can cause unexpected misclassification; and (2) Curators could create incorrect annotations. An example of mismatched definitions:
http://purl.obolibrary.org/obo/OBI_0003243 blood assay datum
Text definition: "A data item that is the specified output of a blood assay."
Logical definition (that does not match the textual def):
= 'information content entity' and (is_specified_output_of some 'blood assay')
Logical definition (that matches the textual def):
= 'data item' and (is_specified_output_of some 'blood assay')
While both logical definitions can be used to define the class, one better fits with the textual definition than the other.
Note that it’s permissible to not to have a logical definition if the class is fuzzy or the axioms/relations can’t be composed equivalence axioms.
Terms often benefit from examples of usage, as well as editor notes about edge cases and the history of the term, but these should be included as separate annotations and not in the definition.
Instances, such as organizations or geographical locations, can benefit from definitions although it is understood that definitions for instances are not required. It is recognized that OBO format (e.g., versions 1.2 and 1.4) does not allow this as an option.
Implementation
Textual definitions should be identified using the annotation property: ‘definition’ [http://purl.obolibrary.org/obo/IAO_0000115](http://purl.obolibrary.org/obo/IAO_0000115). The source of the definition should be provided using the annotation property ‘definition source’ [http://purl.obolibrary.org/obo/IAO_0000119](http://purl.obolibrary.org/obo/IAO_0000119), or as an axiom annotation on the definition assertion.
An example of providing source in an axiom annotation:
<http://purl.obolibrary.org/obo/GO_0000109> rdf:type owl:Class ;
<http://purl.obolibrary.org/obo/IAO_0000115> "Any complex formed of proteins that act in nucleotide-excision repair."@en ;
rdfs:label "nucleotide-excision repair complex"^^xsd:string .
[ rdf:type owl:Axiom ;
owl:annotatedSource <http://purl.obolibrary.org/obo/GO_0000109> ;
owl:annotatedProperty <http://purl.obolibrary.org/obo/IAO_0000115> ;
owl:annotatedTarget "Any complex formed of proteins that act in nucleotide-excision repair."@en ;
<http://www.geneontology.org/formats/oboInOwl#hasDbXref> "PMID:10915862"^^xsd:string
] .
this corresponds to the obo format:
id: GO:0000109
name: nucleotide-excision repair complex
def: "Any complex formed of proteins that act in nucleotide-excision repair." [PMID:10915862]
Examples
Class: primary phloem sieve element
Term IRI: [http://purl.obolibrary.org/obo/PO_0025452](http://purl.obolibrary.org/obo/PO_0025452)
Definition: A sieve element (PO:0025406) that is part of a portion of primary phloem (PO:0006075).
Logical definition:
'sieve element'
and ('part of' some 'primary phloem')
Class: ecto-epithelial cell
Term IRI: [http://purl.obolibrary.org/obo/CL_0002077](http://purl.obolibrary.org/obo/CL_0002077)
Definition: An epithelial cell derived from ectoderm.
Logical definition:
'epithelial cell'
and ('develops from' some 'ectodermal cell')
Counter-Examples
- No definition
- Circular/Self-referential definition “A chromatography device is a device that uses chromatography” when chromatography is not defined elsewhere
Criteria for Review
Each definition MUST be unique. Each entity MUST NOT have more than one textual definition (tagged using [IAO:0000115](http://purl.obolibrary.org/obo/IAO_0000115)). Textual definitions SHOULD be provided for most terms, and for top level terms especially.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%236+%22Definitions%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%236+%22Definitions%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-007-relations.html>

Principle: Relations (principle 7)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
Existing relations MUST be reused. New relations SHOULD be submitted to the Relations Ontology (RO).
Purpose
To facilitate interoperability between multiple ontologies, especially with respect to logical inference, because a reasoner can only detect logical inconsistencies between ontologies and infer new axioms if the ontologies use the same relations (aka object properties).
Recommendations and Requirements
For any given relation need, each OBO ontology MUST reuse a relation from the Relations Ontology (RO) or other ontology if the appropriate relation already exists,
rather than declaring new a relation that holds the same meaning. Where it makes sense for an ontology to declare a new relation in
its own ID space and there is a RO relation that is logically a super-property of the new relation, the new relation MUST be asserted to be
a sub-property of the RO relation. In such cases, it is requested that there still be coordination with RO, for example in the form of an issue
submitted to the [RO tracker](https://github.com/oborel/obo-relations/issues).
Implementation
Reusing relations
‘Reuse’ means that the actual existing-relation PURL is used. Ontology developers should be aware that (in rare instances) relations can evolve over time and previous relations might become obsolete. This means developers should monitor the state of the relations they use. The Relations Ontology MUST be the first source for appropriate relations, and ontology developers SHOULD, with due diligence, search RO for needed relations. If a necessary relation cannot be found within RO, then the developers MUST search other OBO ontologies for reasonable candidates using, for example, an ontology search engine such as [Ontobee](https://ontobee.org/) or [OLS](https://www.ebi.ac.uk/ols4/).
Creating New Relations
The appropriate home for a new relation (‘R’) will depend on multiple factors, including the general applicability of ‘R’ beyond its use by developers of the ‘R’-proposing ontology (‘O’), and with consideration of the domain and range for ‘R’:
- If both the domain and range of ‘R’ are classes in the same ontology ‘O’ as ‘R’, ‘R’ MAY be kept in ‘O’;
- If either the domain or range of ‘R’ are classes not in ‘O’, and ‘R’ does not seem to be general enough for use by other ontologies, ‘R’ MAY be kept in ‘O’;
- If ‘R’ seems generally usable (that is, could potentially be used by ontologies other than ‘O’), the relation SHOULD be submitted to RO;
- For any ‘R’ not submitted to RO, if a suitable RO parent (‘P’) exists, then ‘R’ MUST be declared a sub-property of ‘P’;
- An effort to specify a domain and range for ‘R’ SHOULD be made, though caution is advised to ensure that each is neither too broad nor too specific.
While it is never a bad idea to submit a new relation to RO, if there are any doubts about how to proceed based on the above, a discussion with RO developers SHOULD be made via the [RO issue tracker](https://github.com/oborel/obo-relations/issues) or the [OBO Community Slack](https://obo-communitygroup.slack.com) using the #relation-ontology channel.
Note regarding property chains: If a proposed property chain makes use of relations that are themselves in RO, the property chain SHOULD be submitted to RO.
Examples
Counter-Examples
Criteria for Review
Each relation in the ontology that does not use an RO IRI will be checked to see if there is an exact label match in RO. If so, this will be flagged as an ERROR. Any other non-RO properties will be flagged with an INFO message.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%237+%22Relations%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%237+%22Relations%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-008-documented.html>

Principle: Documentation (principle 8)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
NOTE
The wording of this principle is still in progress, with some issues still to be addressed (see Issues To Be Addressed below).
Summary
The owners of the ontology should strive to provide as much documentation as possible. The documentation should detail the different processes specific to an ontology life cycle and target various audiences (users or developers).
Purpose
Central to the issue of ontology documentation is ensuring transparency and traceability of artefact development. For each of the development steps, clear procedures should be made available. Documentation availability will be used to assess the quality of the resource. The following itemized list provides a core checklist, distinguishing general ontology documentation (general information about the resource) and local ontology documentation (documentation at artefact level itself and representational unit level (class and relations)). Documentation assessment with the purpose of assessing Ontology soundness, will cover updates and revision to the documentation. As ontology evolve, so should the documentation, for example by including a release documentation file.
Recommendations and Requirements
Implementation
Term adoption
If a term that was previously defined in an identifier space belonging to ontology A (e.g. http://purl.obolibrary.org/obo/A_123) is adopted by ontology B (with a different identifier scheme, e.g. http://purl.obolibrary.org/obo/B_123) the following annotation assertion MUST be added to that term:
OWL format (Turtle serialisation):
<http://purl.obolibrary.org/obo/A_123> rdfs:isDefinedBy <http://purl.obolibrary.org/obo/b.owl>
OBO format:
property_value: isDefinedBy http://purl.obolibrary.org/obo/b.owl
Examples
Embedded or ‘in-situ’ documentation: Namely any specific metadata available from the ontology artefact itself providing information about the resource in its entirety or parts of it. global ontology description (about the ontology as a whole):
- creator(s)
- maintainer(s)
- license
- version
local ontology documentation (about each term): documentation for individual representational unit annotation
- justify the different elements of class metadata
- justify class axiomatization documentation about the textual definition: is it manually created or generated with software assistance by relying on patterns and class axioms.
User documentation: A documentation detailing the ontology’s raison d’etre, its coverage, the use cases and query cases (including translation into SPARQL queries) it is intended to support documentation about how to access the resource documentation about how to produce semantic web document compatible with the representation intended by the developers (OWL examples, OWL coding patterns)
- availability of peer-reviewed publication about the resource
- availability of training material and tutorial
- availability of presentations (e.g. on slideshare)
- availability of web seminars (e.g. on a youtube channel)
Developer documentation:
- documentation about collaborating and submitting issues by creating a
[CONTRIBUTING.md file](http://mozillascience.github.io/working-open-workshop/contributing/)as described[here](http://obofoundry.org/principles/fp-020-responsiveness.html#implementation). - documentation about authors contributions
- documentation about licensing terms, rights of use.
- documentation about version control
- documentation about release process
- documentation about changes in ontology between release version
- continuous integration
- documentation about the methodology used for developing the resource
- documentation about interaction with orthogonal resources
- documentation about resource acknowledgement
- documentation about term submission/term requests
- documentation about batch submission
- documentation about term deprecation and deprecation policy (aka retirement policy)
- documentation about conflict resolution
- a documentation detailing the use of software agent devised or exploited to develop, maintain, enhance, perform quality control and ensure high availability of the resource
- documentation about how the ontology is being used
Issues To Be Addressed (partial list):
-
What minimal metadata is needed?
-
What minimal documentation is needed?
-
Clarification of the role of publications
the ontology is well-documented (e.g. in a published paper describing the ontology or in manuals for developers and users)

---

**Source:** <https://obofoundry.org/principles/fp-009-users.html>

Principle: Documented Plurality of Users (principle 9)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The ontology developers should document that the ontology is used by multiple independent people or organizations.
Purpose
This principle aims to ensure that the ontology tackles a relevant scientific area and does so in a usable and sustainable fashion.
Recommendations and Requirements
It is important to be able to illustrate usage outside of the immediate circle of ontology developers and stakeholders. Demonstrations of usage MUST be publicly available. Preferred indicators of usage are those that directly demonstrate such, including:
-
Use of the target ontology’s term IRIs in an external ontology. Indicators of this type MUST include one or more IRIs for a term within the external ontology that uses a term from the target ontology.
-
Documentation of requests from multiple users. Indicators of this type MUST link to specific requests in the issue tracker, OR link to an issue tracker search (for example, showing new term requests), OR link to an email thread or other mechanism if publicly viewable.
-
Publications showing the ontology being used in research by external users. Indicators of this type MUST provide citation details for the publications (link to PubMed or full text) and MUST include a sentence demonstrating the use (preferably taken from the title, abstract, or full text of the cited reference). Note that if citing full text that is behind a paywall, it may be necessary to provide a PDF for the paper.
-
Use of terms from the ontology to provide structure to or annotation of experimental or derived data. Indicators of this type MUST provide a link to a URL that shows the annotation or demonstrates the structure.
-
Terms imported into external ontologies. Indicators of this type MUST link to direct evidence of import, such as the OntoBee page for the term (which includes a section indicating which ontologies have imported it), OR to the OBO Dashboard page for the target ontology (which includes a section “Which ontologies use it?”), OR to any other source of direct evidence. A link to the importing ontology as a whole does not constitute appropriate evidence, as this is too indirect (that is, it requires extra steps to verify).
-
Inclusion of the target ontology on a documentation page that lists which resources are used for the project. Indicators of this type MUST include a link to the appropriate documentation page.
Other indicators are currently possible as well:
-
Use in semantic web projects (e.g., Open PHACTS usage).
-
Use in software applications, including text mining or analysis pipelines.
-
Citations to the ontology publication(s); Note that such citations are only relevant if the authors indicate actual use of the cited ontology within some community (mere mention of the existence is not enough to warrant inclusion).
Note that the ontology can still be listed on the OBO Foundry website while publicising your resource in appropriate channels and searching for users with needs you can meet.
Implementation
The ontology developers MUST provide links/citations to publicly available evidence of
use within your ontology [metadata file](https://github.com/OBOFoundry/OBOFoundry.github.io/tree/master/ontology) as given below (replacing with the correct group name, link, and description):
usages:
- user: http://www.informatics.jax.org/disease (link to group)
description: MGI disease model annotations use DO (description of group)
examples:
- url: http://www.informatics.jax.org/disease/DOID:4123 (link to specific example)
description: Human genes and mouse homology associated with nail diseases (description of specific example)
You may have multiple examples for each user, and mulitple users under the usages
tag.
Examples
Use of PSI-MOD term IRI (in the form of a CURIE) in the PR ontology:
- user: http://purl.obolibrary.org/obo/pr
description: Protein Ontology
examples:
- url: https://proconsortium.org/app/export/obo/PR:000027653/
description: OBO Format stanza showing use of PSI-MOD term in logical definition
Term requests to PR from multiple users:
- user: (multiple)
description: Term requests made via the Protein Ontology GitHub tracker
examples:
- url: https://github.com/PROconsortium/PRoteinOntology/issues?q=is%3Aissue+label%3A%22Term+Request%22
description: List of issues tagged with 'Term Request' to PRO
Publication showing the Disease Ontology being used in research by external users
- user: https://pubmed.ncbi.nlm.nih.gov/36860337/
description: Machine learning-based prediction of candidate gene biomarkers correlated with immune infiltration in patients with idiopathic pulmonary fibrosis
examples:
- url: https://pubmed.ncbi.nlm.nih.gov/36860337/
description: In abstract, "Functional annotation, pathway enrichment, Disease Ontology and gene set enrichment analyses revealed..."
Use of terms from GO for annotation:
- user: https://www.uniprot.org
description: UniProt
examples:
- url: https://www.uniprot.org/uniprotkb/Q15796/entry#function
description: Functional annotation using GO (see subsection entitled "GO annotations")
OBI terms imported into external ontologies
- user: (multiple)
description: Ontologies using OBI terms
examples:
- url: http://dashboard.obofoundry.org/dashboard/obi/dashboard.html
description: List of ontologies using at least one OBI term (See section entitled "Info: Which ontologies use it?")
- url: https://ontobee.org/ontology/OBI?iri=http://purl.obolibrary.org/obo/OBI_0000691
description: List of ontologies using the term 'ABI 377 automated sequencer' (See section entitled "Ontologies that use the Class")
Counter-Examples
-
Mere mention of the existence of an ontology in a publication is not enough to count as evidence of usage
-
Reference to any evidence that cannot be viewed publicly
Criteria for Review
Ontology developers must demonstrate at least three external users specified within the metadata file. External users are defined either as researchers not significantly overlapping in personnel with the developers or three independent groups with three independent artefacts (db, etc) that use the ontology. Note that new ontologies are not expected to have a plurality of users, and thus the automatic evaluation of this criterion can be ignored.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%239+%22Users%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%239+%22Users%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-010-collaboration.html>

Principle: Commitment To Collaboration (principle 10)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
Summary
OBO Foundry ontology development, in common with many other standards-oriented scientific activities, should be carried out in a collaborative fashion.
Purpose
The benefits of collaboration are threefold: (1) Avoid duplication of work; (2) Increase interoperability; and (3) Ensure that ontology content is both scientifically sound and meets community needs.
Implementation
Recommendation:
It is expected that Foundry ontologies will collaborate with other Foundry ontologies, particularly in ensuring orthogonality of distinct ontologies, in re-using content from other ontologies in cross-product definitions where appropriate, and in establishing and evolving Foundry principles to advance the Foundry suite of ontologies to better serve the joint users. Where there are multiple ontology providers in a particular domain, they are particularly encouraged to get together and determine how the domain should be divided between the ontologies, or whether the ontologies should be merged into a single artifact. Should it be determined that there is a competing ontology in the same domain, the Foundry ontology should invite the developers of the external ontology to collaborate and should strive to negotiate an arrangement that is beneficial to both projects. If necessary, conflicts can be mediated in dedicated workshops or using the [obo-discuss mailing list](https://groups.google.com/forum/#!forum/obo-discuss) where Foundry advisors and members of the editorial board can help the parties negotiate to a mutually agreeable solution.
Examples:
- Collaborative workshop: http://ncorwiki.buffalo.edu/index.php/Protein_Ontology_Workshop
- Conflict resolution: The Statistical Methods Ontology (STATO) and Ontology of Biological and Clinical Statistics (OBCS) both cover statistics. The developers of each have posted to the OBO Foundry discussion list to work out how to collaborate.
- Contribution to external ontology: Plant Ontology (PO) curators contribute definitions to Gene Ontology (GO) for biological processes and cell components in plants. PO then uses the GO terms in their definition of corresponding structures and stages.
- Documentation of collaboration: Cell Line Ontology (CLO), Cell Ontology (CL), and Ontology of Biomedical Investigations (OBI) published a paper sorting out their overlap and documented working together. Sarntivjiai et al., “CLO: The cell line ontology”, J. Biomed. Sem., 2014, 5, 37. http://www.ncbi.nlm.nih.gov/pubmed/25852852
- Providing terms upon request: The Disease Ontology (DO) responded to a request from the PRotein Ontology for curation of certain disease terms.
- Providing guidance on how to contribute: The Relations Ontology (RO) GitHub includes a
[CONTRIBUTING.md](https://github.com/oborel/obo-relations/blob/master/CONTRIBUTING.md)file.
Counter-examples:
Interactions between ontologies developed by the same entity (person, consortium) are not evidence of collaboration.
Criteria for Review
Ontology developers must document their attempts at an open dialog with OBO Foundry members, for example by attempting to ascertain if there are other possible ontologies in (or overlapping) the domain of interest. Such documentation can be a simple pointer to an e-mail thread on the OBO discuss list. If there are other ontologies that might need to be aligned or have boundaries determined, evidence of coordination or cooperation should be provided. Further evidence of collaboration may include examples of terms that have been provided to other ontologies in the OBO Foundry community, while evidence for a willingness to collaborate includes the creation of a CONTRIBUTING.md file to provide guidance for contributions ([learn more](http://mozillascience.github.io/working-open-workshop/contributing/)). Finally, hosting or participating in collaborative workshops or meetings attended by OBO Foundry community members is considered evidence of collaboration.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%2310+%22Collaboration%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%2310+%22Collaboration%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-011-locus-of-authority.html>

Principle: Locus of Authority (principle 11)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
There should be a person who is responsible for communications between the community and the ontology developers, for communicating with the Foundry on all Foundry-related matters, for mediating discussions involving maintenance in the light of scientific advance, and for ensuring that all user feedback is addressed.
Purpose
It is important that there is a person responsible for communication rather than a group of people or a list. Often in communications to a list, the responsibility for responding can be diffused and it is likely that in some scenarios no response will be given. It may also, from time to time, be necessary to engage in strategic communications (e.g. relating to funding or collaboration possibilities) that are not able to be made public, and these should not be conducted on public mailing lists. The designation of a contact person is not to be interpreted as a designation for credit. Note that alternative contacts can be designated in case the primary contact is unavailable. However, as for the primary contact, each alternative contact must be an individual.
Recommendations and Requirements
A primary contact person MUST be assigned.
The name, email address and GitHub username of the contact person MUST be provided when requesting to register with [OBO](http://obofoundry.org). The contact person MUST be subscribed to obo-discuss in order to be kept abreast of community developments of relevance to
participating ontology projects, but the primary contact person can, of course, delegate
these responsibilities for the project as necessary. The email address of the person who is the locus of the
authority MUST be kept up-to-date, and before that person ceases to have responsibility
for the project, they should identify a replacement and update the metadata accordingly
(via the [OBO Foundry issue tracker](https://github.com/OBOFoundry/OBOFoundry.github.io/issues)) before they move on.
Implementation
First, read the [FAQ](http://obofoundry.github.io/faq/how-do-i-edit-metadata.html) on how to edit the metadata for your ontology.
The contact email MUST NOT be a mailing list. The GitHub account MUST be for the individual designated as the locus of authority. If this person does not already have a GitHub account, we request that they [create one](https://github.com/join). Then, add the following to your [metadata file](https://github.com/OBOFoundry/OBOFoundry.github.io/tree/master/ontology) (replacing with the correct email, name, and GitHub username):
contact: email: foo@bar.com label: John Smith github: jsmith123
Examples:
For Mondo, the primary contact person is Nicole Vasilevsky (nicole {at} tislab.org) and her GitHub handle is: nicolevasilevsky.
Counter-Examples:
- Mailing list; such as go-discuss {at} geneontology.org
- Help desk; such as chebi-help {at} ebi.ac.uk
- Group email; such as ontologygroup {at} resource.org (where it is unclear precisely who receives the email and who is responsible for responding)
- Issue tracker;
- Email address of responsible person’s assistant or admin; the responsible person must be directly reachable
Criteria for Review
Email address will be checked to ensure it is for an individual and that it is written in a standard format.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%2311+%22Contact%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%2311+%22Contact%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-012-naming-conventions.html>

Principle: Naming Conventions (principle 12)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
NOTE
The content of this page is scheduled to be reviewed. Improved wording will be posted as it becomes available.
Details
For full details, see this paper: [http://www.biomedcentral.com/1471-2105/10/125](http://www.biomedcentral.com/1471-2105/10/125)
Briefly, some important things to remember:
- use rdfs:label for the primary label
- include exactly one rdfs:label for every declared entity (e.g. class, property)
- write labels, synonyms, etc as if writing in plain English text. ie use spaces to separate words, only capitalize proper names (e.g. Parkinson disease). Do not use CamelCase, do_not_use_underscores
- avoid extra spaces between words, or at the beginning or end of the term label
- spell out abbreviations. Abbreviations can be included as a separate property.
- make the primary labels to be as unambiguous as possible. Remember, your ontology may be used in a different context than that for which it was originally intended. Remember also of course that the label should be unambiguous without looking at parent terms
- labels should be unique within an ontology
- use the IAO property ‘obo foundry unique label’
[http://purl.obolibrary.org/obo/IAO_0000589](http://purl.obolibrary.org/obo/IAO_0000589)to declare a pan-OBO unique label if required

---

**Source:** <https://obofoundry.org/principles/fp-013-notification.html>

Principle: Notification of Changes (principle 13)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
Ontologies SHOULD announce major changes to relevant stakeholders and collaborators ahead of release.
Purpose
To maintain the reliability of an ontology for stakeholders, advance announcement of upcoming changes–as opposed to giving after-the-fact notice (or none at all)–is crucial. Such announcement will provide stakeholders an opportunity for input on upcoming changes, and will allow updates to any dependencies (e.g., terms, annotations, ontologies) affected by those changes.
Recommendations and Requirements
Ontology owners SHOULD, in accordance with this principle, pre-announce changes to a primary group of users who actively monitor the ontology and its changes, for example, via a mailing list (ontology-specific or more general, as deemed suitable), a social media group (relevant to the ontology), or via announcements on a home page or elsewhere. The lead time for announcements can be determined according to release lifecycles of major ontology applications and is expected to vary by domain.
The kinds of changes that might warrant a pre-announcement include (but are not limited to):
- Planned obsoletions. Terms that will be made obsolete. Such announcements can provide users the opportunity to intervene if necessary.
- Major hierarchy rearrangements. Moving branches from one point in the hierarchy to another, especially large branches affecting many terms or those close to the top of the hierarchy.
Term additions and small hierarchy changes are not expected to need pre-announcement but doing so is not prohibited.
Implementation
The need for notification of changes–and the time frame in which notifications are made–should be based on the granularity of the changes and their potential impact (for example, changes to low-level terms are likely not as impactful as those to high-level terms). Types of changes that might benefit from notification include term obsoletions, term modifications, new terms, and any others that are determined with stakeholder benefit in mind. Announcments can be concise or verbose, and SHOULD be made a minimum of 7 days in advance of the release in which the changes take effect.
The following are possible avenues for notification:
- Submission of a GitHub ticket announcing the change
- Announcement made via social media (Twitter, Facebook, Slack, etc)
- Announcement made via general or ontology-specific mailing list
- Announcement of pending changes made as a GitHub pre-release
- Change log or release note, if published in advance
It is expected that announcements include links to where discussions or questions can be directed.
Examples
- GitHub issue: https://github.com/geneontology/go-announcements/issues/275
- Social media (Twitter): https://twitter.com/diseaseontology/status/1301907848625033216
- Mailing list announcement (general): https://groups.google.com/g/obo-discuss/c/RrCF5f9FRC4/m/nEVwLqN5CQAJ
- Mailing list announcement (ontology-specific): https://groups.google.com/g/obi-users/c/wweskCfHbSc
- GitHub pre-release: https://github.com/obi-ontology/obi/pull/1558
- Advance release note: https://proconsortium.org/download/release_55.0/pro_release_note.txt
Counter-Examples
The following mechanisms, while useful, do not fulfill the recommendations herein since they occur concurrently with the changes of interest:
- Announcement of changes in a release note when that note is for the same release as that in which the change first appears
- A change log that is not published in advance
Criteria for Review
Notification of changes SHOULD be published prior to a new release version of the Ontology. The period between publishing the changes and the release date must be no less than 7 days but can be longer (based upon agreement between ontology developers and users).
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%2313+%22Notification%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%2313+%22Notification%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).

---

**Source:** <https://obofoundry.org/principles/fp-016-maintenance.html>

Principle: Maintenance (principle 16)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
NOTE
The wording of this principle is still in progress.
Summary and Purpose
The ontology needs to reflect changes in scientific consensus to remain accurate over time.
Implementation
Ideally, the maintainer of an ontology SHOULD actively monitor for any changes in scientific consensus, but–at a minimum–the maintainer MUST respond to requests from the community pointing out such changes in accordance with the [Responsiveness principle](http://obofoundry.org/principles/fp-020-responsiveness.html). Tentatively, we consider scientific consensus to be reached if multiple publications by independent labs over a year come to the same conclusion, and there is no or limited (<10%) dissenting opinions published in the same time frame. In cases when an area remains controversial, and no consensus is reached, then it is up to the ontology maintainer to either leave out the controversial term, or pick a viewpoint for practical considerations, and note the presence of controversy in an editor note.
Examples
Counter-Examples
Criteria for Review
The developers of the ontology need to include a statement specifying how they are planning to maintain the ontology. We expect that an ontology will be maintained for at least 3 years from the time of acceptance.

---

**Source:** <https://obofoundry.org/principles/fp-019-term-stability.html>

Principle: Stability of Term Meaning (principle 19)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
The definition of a term MUST always denote the same thing(s)–known as “referent(s)”–in reality. If a proposed change to the definition would substantially change its referents, then a new term with new IRI and definition MUST instead be created.
Purpose
Users of an ontology depend on the stability of its terms and their meanings. Therefore, changes to the definition of a term should never substantially shift its meaning. Put another way, its set of referents MUST remain stable, within reason. That is, changes to a term definition–or any mechanism to denote meaning, including elucidations and logical axioms–should not cause that term to point to different entities than it denotes already.
Recommendations and Requirements
Below, we use ‘definition’ to encompass all possible mechanisms to denote term meaning, as described above.
If changing a term definition would change its referents, then instead a new term MUST be created with a new IRI and the new definition. Minor changes to the definition for clarity, grammar, and/or proper punctuation that do not change the referents are permitted. What is considered a ‘minor change’ will likely need to be evaluated on a case-by-case basis; it is left to the ontology developers to decide. However, any feedback from users MUST be taken into account.
The creation of a new term/definition implies that the old term should possibly be deprecated/obsoleted. Conditions under which a term MUST be deprecated according to this principle, or for which term deprecation SHOULD be considered, include:
1) The old textual definition misses the target(s) intended by the ontology developers. This includes cases where the term refers to non-existent referents (as might happen, for example, when new research reveals that the referent does not exist in reality). 1) The original term definition is considered sufficiently “damaged” (too vague, too restrictive, too misused or too misunderstood).
In all cases the developers SHOULD provide guidance on how to handle deprecated terms (either by exact replacement or by considering other terms), and be mindful of the potential costs to users of the ontology who might use the existing term. As well, developers SHOULD pre-announce term obsoletions. See [Principle 13](http://obofoundry.org/principles/fp-013-notification.html) for guidance on such announcements.
Implementation
Detailed procedures for obsoleting a term are described on the OBO Academy page [Obsoleting an Existing Ontology Term](https://oboacademy.github.io/obook/howto/obsolete-term/).
To obsolete a term, the ontology developer MUST:
- Mark the term as obsolete:
- OWL format: Add an “owl:deprecated” annotation property with value of “true^xsd:boolean”
- OBO format: Add an “is_obsolete: true” tag
- Prepend the string “obsolete “ (including the space) to the term label and the
editor preferred term
(IAO:0000111), if present- NOTE: To be consistent with
[Principle 12](https://obofoundry.org/principles/fp-012-naming-conventions.html)“Naming Conventions”, the syntax/format MUST be precisely as given above (that is, the exact string as shown, lowercase and space included, with no other punctuation before or after). Thus, the following are disallowed: “Obsolete {label}”, “obsolete_{label}”, “OBSOLETE {label}” (and variations thereof).
- NOTE: To be consistent with
- Remove all existing logical axioms from the term
- Remove or replace all usages of the term elsewhere in the ontology. For example, if an ontology has A part-of B, and B has been deprecated with replacement by C, then the corrected axiom would be A part-of C. Likewise, if A part-of B, and B part-of C, if B is deprecated, then any part-of axiom involving B MUST be removed; that is, by stating instead A part-of C.
It is not necessary (and not advisable) to delete the textual definition.
To obsolete a term, the ontology developer SHOULD:
- Indicate any exact term replacement:
- OWL: Use the
term replaced by
annotation property from OMO ([IAO:0100001](http://purl.obolibrary.org/obo/IAO_0100001)) with the value set to the IRI of the relevant term - OBO: Use the
replaced_by:
tag with the value set to the CURIE of the relevant term
- OWL: Use the
- Indicate any inexact term replacements:
-
OWL: Use the
oboInOwl:consider
annotation property with the value set to the full IRI(s) of the relevant term(s):<oboInOwl:consider rdf:resource="http://purl.obolibrary.org/obo/OBI_0001544">
-
OBO: Use the
consider:
tag with the value set to the CURIE(s) of the relevant term(s):consider: OBI:0001544
Note that some older implementations in OWL used the CURIE method as shown below, but this is not preferred.
-
<oboInOwl:consider rdf:datatype="http://www.w3.org/2001/XMLSchema#string">OBI:0001544</oboInOwl:consider>
To obsolete a term, the ontology developer MAY:
- Prepend the string “OBSOLETE. “ (this precise string, including the space) to the term definition. NOTE: This MUST be implemented consistently. That is, if applied at all, it has to be applied to every obsoleted term definition.
- Indicate the reason(s) for obsoleting:
- OWL: Use the
has obsolescence reason
annotation property from OMO ([IAO:0000231](http://purl.obolibrary.org/obo/IAO_0000231)) with the value set to the IRI of one of the individuals of the “obsolescence reason specification” term[IAO:0000225](http://purl.obolibrary.org/obo/IAO_0000225). See below for example. - OBO: Use
relationship:
with the CURIE for the annotation property (IAO:0000231) and a CURIE for the specific reason (an individual from the “obsolescence reason specification” term[IAO:0000225](http://purl.obolibrary.org/obo/IAO_0000225)). See below for example. Note that older implementations often used alternative methods (described after the examples). These methods are still valid, but are not preferred.
- OWL: Use the
Examples
The Ontology for Biomedical Investigations obsolete term “cell lysate MHC competitive binding assay using radioactivity detection” (OBI:0001574) can be deprecated as follows:
OWL:
<owl:Class rdf:about="http://purl.obolibrary.org/obo/OBI_0001574">
<obo:IAO_0000111>obsolete cell lysate MHC competitive binding assay using radioactivity detection</obo:IAO_0000111>
<obo:IAO_0000115>Competitive inhibition of binding assay measuring MHC ligand binding by radioactivity detection using MHC derived from a cell lysate</obo:IAO_0000115>
<obo:IAO_0000231 rdf:resource="http://purl.obolibrary.org/obo/IAO_0000227"/>
<obo:IAO_0100001 rdf:resource="http://purl.obolibrary.org/obo/OBI_0001544"/>
<rdfs:label>obsolete cell lysate MHC competitive binding assay using radioactivity detection</rdfs:label>
<owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</owl:deprecated>
</owl:Class>
OBO:
[Term]
id: OBI:0001574
name: obsolete cell lysate MHC competitive binding assay using radioactivity detection
def: "OBSOLETE. Competitive inhibition of binding assay measuring MHC ligand binding by radioactivity detection using MHC derived from a cell lysate." []
relationship: IAO:0000231 IAO:0000227
is_obsolete: true
replaced_by: OBI:0001544
Obsolescence reasons have, historically, been indicated multiple ways. In addition to the preferred methods shown above, the following alternatives are in current use:
1) As a free text comment (rdfs:comment
in OWL or comment:
in OBO).
1) In OBO format, using a property_value:
tag instead of a relationship:
tag.
1) In OBO format, using an annotation property label-as-identifier (with underscores) instead of the CURIE IAO:0000231
, and the obsolescence reason label instead of the relevant CURIE. Note that the underscore version of the property label will need to be created in the ontology:
[Typedef]
id: has_obsolescence_reason
name: has obsolescence reason
xref: IAO:0000231
is_metadata_tag: true
Then:
relationship: has_obsolescence_reason IAO:0000227 ! terms merged
Or:
property_value: has_obsolescence_reason IAO:0000227
Counter-example
The PRO term “phosphoprotein” (PR:000037070) is defined as “A protein that includes at least one phosphorylated residue.” A study finds 2000 more examples than was previously known. In this case, no new term needs to be made (nor the original deleted) because (1) the term definition did not change; and (2) the referent–proteins with a phophoresidue–did not change (that is, the newly-discovered phosphoproteins are just additional examples of that referent).
Criteria for review
The OBO Dashboard will show:
- An ERROR if any obsolete term (that is, a term with an
owl:deprecated
property oris_obsolete: true
tag) does not also have ‘obsolete ‘ (that exact string, lowercase and space included, with no other punctuation) prepended to the label - An ERROR if any obsolete term (as indicated by term label or definition) lacks an
owl:deprecated
property oris_obsolete: true
tag - An ERROR if an obsolete term has, itself, any logical axioms (including any subClassOf/is_a declarations) or if it is referenced by logical axioms from other terms
- A WARN if there is at least one term with ‘OBSOLETE. ‘ prepended to the definition but not all obsolete terms are likewise prepended
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%2319+%22Stability%22of%22Term%22Meaning%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub].
See also [this discussion](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/597) by the OBO Foundry Operations Committee focusing on term deprecation and [this discussion](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/964) regarding the proposal of this principle.

---

**Source:** <https://obofoundry.org/principles/fp-020-responsiveness.html>

Principle: Responsiveness (principle 20)
-
[Overview](fp-000-summary.html) -
[Open (principle 1)](fp-001-open.html) -
[Common Format (principle 2)](fp-002-format.html) -
[URI/Identifier Space (principle 3)](fp-003-uris.html) -
[Versioning (principle 4)](fp-004-versioning.html) -
[Scope (principle 5)](fp-005-delineated-content.html) -
[Textual Definitions (principle 6)](fp-006-textual-definitions.html) -
[Relations (principle 7)](fp-007-relations.html) -
[Documentation (principle 8)](fp-008-documented.html) -
[Documented Plurality of Users (principle 9)](fp-009-users.html) -
[Commitment To Collaboration (principle 10)](fp-010-collaboration.html) -
[Locus of Authority (principle 11)](fp-011-locus-of-authority.html) -
[Naming Conventions (principle 12)](fp-012-naming-conventions.html) -
[Notification of Changes (principle 13)](fp-013-notification.html) -
[Maintenance (principle 16)](fp-016-maintenance.html) -
[Stability of Term Meaning (principle 19)](fp-019-term-stability.html) -
[Responsiveness (principle 20)](fp-020-responsiveness.html)
GO TO: [Recommendations/Requirements](#recommendations-and-requirements) | [Implementation](#implementation) | [Examples/Counter‑Examples](#examples) | [Criteria for Review](#criteria-for-review) | [Feedback/Discussion](#feedback-and-discussion)
Summary
Ontology developers MUST offer channels for community participation and SHOULD be responsive to requests.
Purpose
Ontology development benefits from community input, which is strongly encouraged by the OBO Foundry. Accordingly, “responsiveness” is a key quality of our general collaborative spirit. This principle is intended to ensure that channels for community input are available and that responses to input are given swiftly.
Recommendations and Requirements
Ontology developers MUST set up a public mechanism to track community requests and suggestions (collectively, “issues”), and SHOULD aim to respond within 2-5 working days. To facilitate submission of well-crafted issues, ontology developers SHOULD create a set of guidelines/instructions for contributions. Optional: Establish a discussion forum for more general communication with and between users.
Expectations of responsiveness:
- Issues are contributions - and should be met by a thankful attitude. When receiving an item on your issue tracker, the first thing to do is thank the contributor, even if it cannot be addressed right away.
- If an issue cannot be addressed right away, explain when you plan to address the issue.
- Do not close issues without responding. If an issue is out of scope for a repository, recommend moving it to a different repository.
- It is recommended that one or more developers be designated to triage issues.
Implementation
Issue tracker:
Specify the URL for an issue tracker (GitHub is recommended) in the ontology configuration file (YAML) that is used to display ontology details on the OBO Foundry web site. Specification of the tracker is done using the following text (customized for your ontology) within its [metadata file](https://github.com/OBOFoundry/OBOFoundry.github.io/tree/master/ontology):
tracker: <URL pointing to issue tracker>
Guideline for contributions (recommended):
Create a file called ‘CONTRIBUTING.md’ ([example](https://github.com/mapping-commons/sssom/blob/master/CONTRIBUTING.md)) in an easy-to-find main folder for the appropriate ontology (for example, in the root directory of the ontology GitHub repository, where one would expect to find LICENSE or README files). Learn more about contribution guidelines [here](http://mozillascience.github.io/working-open-workshop/contributing/)).
Discussion forum (optional): Establish a discussion forum (For example, Google groups mailing list, Slack, Twitter). Each of these is specified in the configuration file as given below:
mailing_list: <email address>
twitter: <twitter handle>
slack: <URL pointing to slack channel>
Examples
Issue tracker: https://github.com/monarch-initiative/mondo/issues
Mailing list: mondo-users@googlegroups.com
Twitter: diseaseontology
Slack: https://geneontologyworkspace.slack.com
Counter-Examples
Specifying a private issue tracker. Waiting until an issue is resolved before responding, if such resolution comes well after submission of a ticket.
Criteria for Review
There is a functioning public issue tracker for ontology requests specified on the OBO Foundry web site.
Feedback and Discussion
To suggest revisions or begin a discussion pertaining to this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Editorial+WG,principles&title=Principle+%2320+%22Responsiveness%22+%3CENTER+ISSUE+TITLE%3E).
To suggest revisions or begin a discussion pertaining to the automated validation of this principle, please [create an issue on GitHub](https://github.com/OBOFoundry/OBOFoundry.github.io/issues/new?labels=attn%3A+Technical+WG,automated+validation+of+principles&title=Principle+%2320+%22Responsiveness%22+-+automated+validation+%3CENTER+ISSUE+TITLE%3E).
