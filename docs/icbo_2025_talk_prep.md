# ICBO 2025 Talk Preparation: METPO

This document summarizes the draft narrative and key resources for the ICBO 2025 short talk on METPO.

---

## Draft Talk Narrative

### Slide 1: Title Slide
*   **Title:** METPO: A Pragmatic Ontology for Microbial Ecophysiological Traits
*   **Presenter:** Mark [Your Last Name]
*   **Affiliation:** Lawrence Berkeley National Laboratory
*   **Conference:** ICBO 2025

### Slide 2: The Data Integration Challenge
"Good morning. Microbes are the engines of our planet. They hold the keys to new medicines, sustainable biofuels, and a deeper understanding of our own health. The amount of data we have about them is exploding, with fantastic resources like BacDive, BactoTraits, and the Madin et al. trait dataset providing detailed information on tens of thousands of microbial strains.

But this data is messy. It's stored in different formats, uses different vocabularies, and lacks a common semantic framework. This makes it incredibly difficult to perform integrative analyses. We can't easily ask a simple but powerful question like, 'Show me all microbes that are both halophilic and psychrophilic' and get a comprehensive answer across all these datasets. To unlock the full potential of this data, we need to make it speak the same language. We need semantic normalization, and the best tool for that job is an ontology."

### Slide 3: The Gap in the Ontology Landscape (Revised)
"Naturally, our first step was to look for an existing ontology... We found several, but none were suitable. The reasons were practical and technical:
1.  **Incompleteness:** No single ontology covered the breadth of traits in our key data sources—BacDive, BactoTraits, and Madin's dataset.
2.  **Lack of Maintenance:** Many promising ontologies hadn't been updated in years.
3.  **Technical Issues:** Crucially, many failed to validate with standard OBO tools like ROBOT, or were difficult to work with using modern libraries like the Ontology Access Kit.

The best candidate, MicrO, while a great effort, exemplified these issues: it was unmaintained since 2018, had over 100 ROBOT validation errors, and still lacked the coverage we required. This motivated us to build a new resource, engineered for modern tooling and our specific use case."

### Slide 4: Introducing METPO: A Pragmatic Approach
"And that resource is METPO: the Microbial Ecophysiological Trait and Phenotype Ontology. Our goal with METPO was not to create another monolithic, all-encompassing ontology. Our goal was to be pragmatic. We needed a tool that was focused, lightweight, and purpose-built for a specific, demanding application: a knowledge graph called KG-Microbe.

METPO is intentionally simple. It's a trait hierarchy of about 250 classes, designed specifically to provide coverage for the physiological and metabolic traits found in BacDive, BactoTraits, and the Madin dataset."

### Slide 5: METPO's Modern & Pragmatic Design (Second Revision)
"To build METPO, we used the standard OBO Foundry **Ontology Development Kit (ODK)**. Our source of truth isn't a complex OWL file, but a set of simple **ROBOT-compatible spreadsheets**. This makes it easy for domain experts to contribute and review terms.

But a key part of our pragmatic approach is ensuring METPO is a good citizen in the ontology ecosystem. To do this, we built a custom semantic search pipeline to guide our development and find potential mappings.

We started by loading the entire OLS text embeddings corpus into a local SQLite database. We then augmented this with embeddings from other ontologies in BioPortal, and from valuable, domain-specific resources like the **Names for Life** project.

This powerful setup allowed us to query our candidate METPO term labels against a massive corpus of existing ontology terms. It helped us rapidly identify ontologies with similar concepts, which we could then investigate for potential reuse or mapping. These mappings are captured in **SSSOM (Simple Standard for Sharing Ontology Mappings)** format, utilizing predicates like `skos:exactMatch`, `skos:closeMatch`, and `skos:relatedMatch`. The mappings are generated using `openai_text-embedding-3-small`, demonstrating a sophisticated, data-driven approach to ensuring interoperability.

This hybrid approach—collaborative spreadsheets plus a powerful, custom semantic search pipeline—is central to our agile development philosophy."

### Slide 6: METPO in Action: Powering KG-Microbe
"So, how is METPO used? Its primary role is to provide the semantic backbone for KG-Microbe. KG-Microbe is a large-scale knowledge graph that integrates strain-level trait data with the goal of predicting optimal growth media and conditions for the vast number of microbes that we have yet to culture in the lab. METPO provides the vocabulary for the 'predicates' and 'objects' in our knowledge graph triples."

### Slide 7: KG-Microbe Examples
"For example, a simple statement like 'E. coli K-12 has the mesophilic phenotype' is represented as a clean, semantic triple: The subject is the taxon, the predicate is a property from METPO, and the object is the 'mesophilic' class from METPO. Because these are all URIs, we can reason over them. We can query for all 'mesophiles', or go up the hierarchy and query for all organisms with a defined 'temperature preference'.

METPO also provides properties for more complex statements, like optimal growth temperatures, and for representing chemical interactions. To keep the ontology lightweight, we don't import the entirety of ChEBI. Instead, METPO defines properties like 'reduces', and in the knowledge graph, we can link a microbe to a chemical using its ChEBI identifier. For non-binary relationships, like the reduction of one chemical *to* another, we create simple reification classes. This pragmatic approach gives us maximum expressive power with minimum ontological overhead."

### Slide 8: The Big Picture & Future Work
"By structuring the data this way, KG-Microbe enables the application of powerful graph-based machine learning techniques to predict the ideal growth conditions for uncultured organisms—a central goal of our PI, Marcin Joachimiak's, research group.

And METPO is a living project. It grows as our needs evolve. We are currently developing extensions to represent microbial interactions with lanthanides. We also use a form of literature-based discovery; when we text-mine an abstract that describes a phenotype not yet in METPO, it triggers a manual curation workflow to add it. The data itself drives the ontology's development."

### Slide 9: Conclusion & Our Philosophy
"In conclusion, METPO is a pragmatic, application-driven ontology that effectively normalizes microbial trait data. It demonstrates a modern, agile approach to ontology development, leveraging both automated methods and careful curation.

We acknowledge that METPO does not strictly adhere to all OBO Foundry principles. This is a conscious design choice. By focusing on a clear and present use case—powering KG-Microbe—we've created a resource that is stable, useful, and sustainable. We believe this pragmatic approach is a valuable model for building domain-specific ontologies in a rapidly evolving scientific landscape.

Thank you."

---

## Key Resources

### Links

*   **METPO:**
    *   GitHub: https://github.com/berkeleybop/metpo
    *   BioPortal: https://bioportal.bioontology.org/ontologies/METPO
*   **KG-Microbe:**
    *   GitHub: https://github.com/Knowledge-Graph-Hub/kg-microbe
*   **Data Sources:**
    *   BacDive: https://bacdive.dsmz.de/
    *   BactoTraits Article: https://www.sciencedirect.com/science/article/pii/S1470160X21007123
    *   BactoTraits Portal: https://ordar.otelo.univ-lorraine.fr/record?id=10.24396/ORDAR-53
    *   Madin et al. Paper: https://www.nature.com/articles/s41597-020-0497-4
    *   Madin et al. Data: https://jmadinlab.github.io/datasets/madin-2020
*   **Tools, Methods & Related Projects:**
    *   Ontology Development Kit (ODK): https://github.com/INCATools/ontology-development-kit
    *   ROBOT: https://robot.obolibrary.org/
    *   Semantic SQL: https://github.com/INCATools/semantic-sql
    *   Ontology Access Kit (OAK): https://github.com/INCATools/ontology-access-kit
    *   METPO Google Sheet Template: https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit?gid=355012485#gid=355012485
    *   Charles Hoyt's Embeddings Blog: https://cthoyt.com/2025/08/04/ontology-text-embeddings.html
    *   NamesforLife (N4L) Paper: https://www.researchgate.net/publication/47552964_NamesforLife_Semantic_Resolution_Services_for_the_Life_Sciences/fulltext/00b391240cf2d1b855041f3c/NamesforLife-Semantic-Resolution-Services-for-the-Life-Sciences.pdf
    *   N4L in CLOCKSS (Main): https://clockss.org/preserving-the-namesforlife-taxonomic-abstracts/
    *   N4L CLOCKSS Mirror (Edinburgh): triggered.edinburgh.clockss.org
    *   N4L CLOCKSS Mirror (Stanford): triggered.stanford.clockss.org
    *   N4L DOI Resolution (Crossref): https://www.crossref.org/documentation/retrieve-metadata/multiple-resolution/
    *   N4L in CLOCKSS Triggered Content: https://www.clockss.org/triggered-content/

### Local Filesystem Paths (on Ubuntu NUC)

*   **METPO Git Repo:** `/home/mark/gitrepos/metpo/`
*   **OBO Foundry Principles:** `/home/mark/work/obof_princips/obo-foundry-principles-compiled.md`
*   **METPO ROBOT Templates:** `/home/mark/gitrepos/metpo/src/templates/`
*   **METPO SSSOM Mappings (Relaxed):** `/home/mark/gitrepos/metpo/notebooks/metpo_mappings_combined_relaxed.sssom.tsv`
*   **METPO SSSOM Mappings (Optimized):** `/home/mark/gitrepos/metpo/notebooks/metpo_mappings_optimized.sssom.tsv`
*   **METPO SSSOM Integration Guide:** `/home/mark/gitrepos/metpo/docs/metpo_sssom_integration_guide.md`
*   **GitHub Activity Log:** `/home/mark/work/crosscutting-docs/turbomam-comprehensive-github-activity-CORRECTED.md`
*   **ICBO 2025 Background Summary:** `/home/mark/gitrepos/metpo/icbo_2025_background_summary.md`

---

## Project Context & Analysis

### Official Meaning of CMM

The acronym **CMM** stands for **Critical Minerals and Materials**. This term is used officially by the U.S. Department of Energy (DOE), especially in the context of initiatives focused on securing domestic supply chains for critical materials required in energy and environmental technologies.

Multiple sources, including DOE budget documents and Lawrence Berkeley National Laboratory (LBNL) publications, confirm this interpretation.

**Key Sources:**
- [DOE CMM Program Portal](https://www.energy.gov/science/critical-minerals-and-materials-program)
- DOE BER Budget References mentioning *critical minerals and materials (CMM)*
- LBNL Earth & Environmental Sciences documentation on CMM research

### Key People & Collaborators

*   **Marcin Joachimiak (LBNL):**
    - Computational biologist and PI for the **KG-Microbe** project
    - Leads ontology, knowledge graph, and AI/ML work under CMM
    - Developer of METPO and key contributor to microbial data integration and prediction efforts
*   **N. Cecilia Martinez-Gomez (UC Berkeley):**
    - Microbiologist specializing in **lanthanide-dependent methylotrophy**
    - Leads experimental research on microbial metabolism and elemental cycling
    - Collaborates on the integration of metabolic traits into KG-Microbe
*   **Ning Sun (CMM Team):** [https://biosciences.lbl.gov/profiles/ning-sun-2/](https://biosciences.lbl.gov/profiles/ning-sun-2/)

### GitHub Repository Analysis (from activity log)

#### Directly Related Repositories
*   `berkeleybop/metpo`
*   `Knowledge-Graph-Hub/kg-microbe`
*   `berkeleybop/metpo-kgm-studio`
*   `monarch-initiative/metpo`

#### Thematically Related Repositories
*   `microbiomedata/nmdc-schema`
*   `microbiomedata/nmdc-ontology`
*   `GenomicsStandardsConsortium/mixs`
*   `linkml/*` (various repositories)
*   `PennTURBO/turbo-ontology`
*   `CultureBotAI` (organization, no contributions yet)

### Repository Invitations (Expired)

A check for repository invitations revealed no active invitations. However, it did show a relevant **expired** invitation:

*   **`realmarcin/fitness-mcp`**: An invitation from Marcin Joachimiak for a repository described as "mcp for mutant pool fitness data". This could be a relevant project to discuss with Marcin.

### KG-Microbe Applications

**KG-Microbe** is a large-scale knowledge graph developed under the CMM project. It integrates data on microbial traits, functions, environments, and taxonomic information. Its primary applications include:

### 1. Predicting Optimal Growth Media
- ML models trained on KG-Microbe data accurately predict which media a given microbe will grow on
- Explainable rule-based models and black-box ML approaches both showed over 70% precision in benchmark datasets

### 2. Microbial Trait Prediction
- Graph embeddings were used to infer traits such as cell shape or metabolic strategy for uncultivated microbes

### 3. Hypothesis Generation
- Multi-hop queries and vector algebra enabled discovery of previously unknown trait associations and potential microbial interactions

### Related Publications and Talks
- Joachimiak et al., *KG-Microbe: A Reference Knowledge-Graph and Platform for Harmonized Microbial Information*, CEUR-WS, 2021
- ISMB/ECCB 2025: “Knowledge-Graph-driven and LLM-enhanced Microbial Growth Predictions” (Talk)
- CSBJ 2025: *Explainable Rule-Based Prediction of Microbial Growth Media* (Máša, Kliegr, Joachimiak)

---

## Unresolved Questions & Suggestions from GPT-5 Research

1.  **For Deepening the CMM–KG-Microbe Link:**
    *   **Question:** Is there a README, proposal, or internal summary document in the local CMM or CultureBot directories that explicitly links KG-Microbe to CMM goals (e.g., lanthanide modeling or bioprospecting)?
    *   **Finding:** No separate local documents found. The `icbo_2025_background_summary.md` (now integrated) provides this context, but not as a standalone document in the requested format.

2.  **For Slide Content & Examples:**
    *   **Question:** Do you have internal or draft slides/presentations about METPO or KG-Microbe that Marcin or Cecilia used in CMM contexts?
    *   **Finding:** No local presentation files found.

3.  **For Slide Content & Examples:**
    *   **Question:** Is there a notebook or script in the `metpo-kgm-studio` or `kg-microbe` repo that shows a working example of querying or reasoning over a KG triple involving METPO terms?
    *   **Finding:** No explicit code examples found in the `kg-microbe` repository.

4.  **For Domain Connection:**
    *   **Question:** Are there JSON/CSV data extracts or processed versions of BacDive/BactoTraits/Madin in the local filesystem that show how raw trait data was mapped into METPO terms or KG-Microbe structure?
    *   **Finding:** No JSON/CSV data extracts found in the `metpo` repository showing mapping to METPO terms.

5.  **For Domain Connection:**
    *   **Question:** Any signs of ongoing work related to lanthanide traits or methylotrophy? Look for commits, new METPO terms, or notes in spreadsheets/templates that mention: lanthanide, Ln, rare earth, MeDH, XoxF, Methylobacterium, etc.
    *   **Finding:** No explicit mentions found in the `metpo` repository files.

---

## Open Questions for Mark

1.  **The "Why":** The abstract mentions predicting optimal growth media. Could you elaborate a little on the real-world impact of this? Is it for bioremediation, industrial biotechnology, understanding gut microbiomes, etc.? A concrete example would be very powerful for the introduction.
2.  **The "How" (for Marcin):** You mentioned being out of your comfort zone with the KG-M prediction part. This is a perfect opportunity to get a "canned" explanation from Marcin. Could you ask him for a simple, 2-3 sentence explanation of *how* the knowledge graph structure helps in predicting growth media? (e.g., "By representing traits and their relationships as a graph, we can use link prediction algorithms to infer missing information, such as a microbe's ability to metabolize a certain compound, which is a key component of a growth medium.")
3.  **Visuals:** The narrative implies a certain flow of slides. Do you have any existing diagrams or figures that would be good to include? I can also try to generate some based on the content. For example:
    *   A diagram showing data sources (BacDive, etc.) flowing into KG-Microbe, with METPO as the semantic layer.
    *   A screenshot of the Google Sheet template to illustrate the workflow.
    *   A simple visualization of the `E. coli` triple.

---

## Gemini's Questions for Mark/GPT-5

1.  **For KG-Microbe Query Examples:** The `icbo_2025_background_summary.md` mentions specific applications like "Multi-hop queries and vector algebra." Since I couldn't find code examples in the `kg-microbe` repository, could you provide a snippet of a SPARQL or Cypher query that demonstrates one of these applications? A concrete example would be very powerful for a slide.

2.  **For Data Mapping Examples:** Similarly, the summary mentions integrating data from BacDive, BactoTraits, and Madin. While I couldn't find the processed data files, do you have a small, illustrative sample (even a few lines in a CSV or JSON format) showing how a raw trait (e.g., from a BacDive entry) is mapped to a METPO term? This would be excellent for visualizing the data pipeline.

3.  **For Lanthanide Work:** The talk narrative mentions ongoing work on lanthanide interactions, but I found no trace of it in the repository. Could you point me to the specific file, branch, or even a Google Doc where this work is being drafted? Knowing the status of this work would make the "Future Work" section of the talk more concrete.

4.  **Regarding the Sibling Coherence Results:** The analysis we ran showed very low coherence scores, indicating a significant structural divergence between METPO and other ontologies, even when term-level mappings exist. This is a very interesting, data-driven finding. For the talk, how would you like to frame this?
    *   As a key justification for METPO's creation, highlighting the "gaps" in the existing ontology landscape?
    *   As a general challenge in ontology alignment that METPO's development process helps to navigate?

5.  **Unresolved N4L Hierarchy:** We were unable to determine the parent of N4L's 'Mid range temperature condition' (and other N4L terms) because the `n4l_merged.db` file does not contain the expected N4L ontology terms. While `n4l_merged.owl` exists, we haven't confirmed if `oaklib` is successfully parsing its hierarchy. This impacts our understanding of the coherence scores for N4L terms. Could you investigate the `n4l_merged.db` and `n4l_merged.owl` files to ensure `oaklib` can correctly access the N4L hierarchy?

---

## Sibling Coherence Analysis Results

**What's working well?**

*   **The Connection Strategy:** Our 5-step connection strategy is working beautifully. The script is now successfully connecting to your local databases for `n4l_merged`, `mco`, and `micro`, and to the local OWL file for `meo`. This is confirmed by the disappearance of the `No graph named...` warnings for these ontologies.
*   **More Complete Analysis:** Because we can now connect to these local ontologies, the analysis is far more complete. The number of terms for which we could retrieve external siblings more than doubled (from 56 to 112).
*   **Meaningful Coherence Scores:** We are now getting meaningful, non-zero coherence scores for terms mapped to these local ontologies, which was impossible before. This gives us a much truer picture of the structural alignment.

**What should I be skeptical of?**

*   **The `ECOCORE` Warning:** The log still shows a warning: `Could not fetch class for ECOCORE:00000008`. This means that even with our robust 5-step strategy, we couldn't find the ECOCORE ontology. This is a minor issue, but it means any coherence scores related to ECOCORE mappings will be `0.0`.
*   **The `UnicodeWarning`s:** The script mentions `unsound encoding` for some local OWL files. While it seems to have handled them, this suggests the source files themselves might have minor encoding issues. It doesn't appear to have broken the analysis, but it's a sign that the source files might not be perfectly clean.
*   **The Definition of "Best Match":** The script currently only considers the single best match (`idxmin()`) for each METPO term when calculating coherence. This is a reasonable simplification, but in reality, a METPO term might have several equally good matches to different ontologies. The coherence score is therefore dependent on which single match was chosen as the "best".

**Is it doing what I asked for?**

*   **Yes, absolutely.** The user asked for a way to "identify gaps in METPO and in the comparison ontologies" by analyzing sibling similarity. This script does exactly that. The low coherence scores are the "gaps" the user was looking for. It provides a quantitative measure of structural alignment, which is a powerful tool for ontology analysis and curation.

### METPO Terms with HIGH Coherence:

The analysis shows that the most structurally aligned parts of METPO are the fine-grained temperature and pH ranges.

*   **`temperature range mid1 (METPO:1000450)`** and **`temperature range mid2 (METPO:1000451)`** both have the highest coherence score of **0.500** with `n4l_merged`. This means that 50% of their siblings in METPO have a corresponding match to a sibling of `MidRangeTemperatureCondition` in N4L. This is a strong sign of structural alignment in this specific area.
*   **`pH range mid3 (METPO:1000463)`** has a coherence of **0.400** with `mco`, again showing good structural agreement.

### METPO Terms with LOW Coherence:

This is perhaps the most interesting finding for your talk. Many of METPO's core, high-level concepts have very poor structural alignment with their best semantic matches in other ontologies.

*   **`metabolism (METPO:1000060)`**
*   **`GC content (METPO:1000127)`**
*   **`temperature optimum (METPO:1000304)`**
*   **`pH optimum (METPO:1000331)`**
*   **`NaCl optimum (METPO:1000333)`**

All of these (and others listed in the output) have a coherence score of **0.000**. This indicates that while the terms themselves are good semantic matches, their children and neighbors in METPO are organized very differently from their counterparts in ontologies like `n4l_merged`, `micro`, and `meo`. This is a powerful, data-driven justification for METPO's existence, as it demonstrates that a simple one-to-one mapping of high-level terms is not enough to capture the specific structural details needed for your use case.

---

## Other Analysis Scripts

Here's a summary of what the other `analyze_*.py` scripts in the `notebooks` directory do and how they differ:

*   **`analyze_branch_coverage.py`:**
    *   **Purpose:** To determine which external ontologies provide the best *coverage* for different branches (sub-hierarchies) within METPO.
    *   **Key Question:** "If I care about the 'temperature' part of METPO, which external ontology is most likely to have all the terms I need?"

*   **`analyze_coherence_results.py`:**
    *   **Purpose:** This script is a *meta-analysis* script. It takes the output of `analyze_sibling_coherence.py` (`sibling_coherence_analysis_output.csv`) and performs a deeper analysis on it.
    *   **Key Question:** "Given the coherence results, which METPO terms are the best candidates for alignment, and which external ontologies are the most structurally compatible with METPO overall?"

*   **`analyze_match_quality.py`:**
    *   **Purpose:** To provide a simple, high-level assessment of the *semantic similarity* (match quality) for a given list of non-OLS ontologies.
    *   **Key Question:** "For these specific local ontologies, how good are the semantic matches overall?"

*   **`analyze_matches.py`:**
    *   **Purpose:** To provide a general, high-level overview of the match results from an SSSOM file.
    *   **Key Question:** "What is the 30,000-foot view of the mapping results?"

**How they differ:**

*   `sibling_coherence` is about **structural alignment** (do the graph neighborhoods look the same?).
*   `branch_coverage` is about **topical coverage** (does an ontology have all the terms for a specific topic?).
*   `match_quality` and `matches` are about **semantic similarity** (how good are the individual term-to-term matches based on distance?).
*   `coherence_results` is a **deeper dive** into the output of `sibling_coherence`.