# ICBO 2025 - Open Questions & Unresolved Issues

**Date:** 2025-11-06
**Status:** Questions to resolve before ICBO presentation
**Purpose:** Track unresolved questions for Marcin, Mark, and further investigation

---

## Table of Contents

1. [Questions for Mark](#questions-for-mark)
2. [Questions for Marcin](#questions-for-marcin)
3. [Unresolved Questions from GPT-5 Research](#unresolved-questions-from-gpt-5-research)
4. [Gemini's Technical Questions](#geminis-technical-questions)

---

## Questions for Mark

### 1. The "Why" - Real-World Impact
**Question:** The abstract mentions predicting optimal growth media. Could you elaborate a little on the real-world impact of this? Is it for bioremediation, industrial biotechnology, understanding gut microbiomes, etc.? A concrete example would be very powerful for the introduction.

**Context:** This would make the talk introduction more compelling by grounding the technical work in practical applications.

### 2. Visuals for the Talk
**Question:** The narrative implies a certain flow of slides. Do you have any existing diagrams or figures that would be good to include? I can also try to generate some based on the content. For example:
- A diagram showing data sources (BacDive, etc.) flowing into KG-Microbe, with METPO as the semantic layer
- A screenshot of the Google Sheet template to illustrate the workflow
- A simple visualization of the `E. coli` triple

**Context:** Visual aids would significantly enhance the presentation's clarity and impact.

### 3. Priority Terms for Manual Definition Creation
**Question:** Out of the 41 terms with no good semantic matches (distance >0.60 or no matches), which are most critical for CMM/ICBO presentation?

**Context:** We have limited time before the presentation. Focusing on critical terms will maximize impact.

---

## Questions for Marcin

### 1. The "How" - KG Structure and Prediction
**Question:** Could you provide a simple, 2-3 sentence explanation of *how* the knowledge graph structure helps in predicting growth media?

**Suggested format:** "By representing traits and their relationships as a graph, we can use link prediction algorithms to infer missing information, such as a microbe's ability to metabolize a certain compound, which is a key component of a growth medium."

**Context:** Mark mentioned being out of his comfort zone with the KG-M prediction part. A "canned" explanation from you would be invaluable for the talk.

### 2. KG-Microbe Query Examples
**Question:** The background summary mentions specific applications like "Multi-hop queries and vector algebra." Could you provide a snippet of a SPARQL or Cypher query that demonstrates one of these applications? A concrete example would be very powerful for a slide.

**Context:** I couldn't find code examples in the `kg-microbe` repository. A working example would make the talk much more concrete.

### 3. Data Mapping Examples
**Question:** Do you have a small, illustrative sample (even a few lines in a CSV or JSON format) showing how a raw trait (e.g., from a BacDive entry) is mapped to a METPO term? This would be excellent for visualizing the data pipeline.

**Context:** This would help explain the practical application of METPO in the KG-Microbe workflow.

### 4. Status of Lanthanide Work
**Question:** The talk narrative mentions ongoing work on lanthanide interactions, but I found no trace of it in the repository. Could you point me to the specific file, branch, or even a Google Doc where this work is being drafted? Knowing the status of this work would make the "Future Work" section of the talk more concrete.

**Context:** We want to accurately represent current and future work without overstating progress.

### 5. Expired Repository Invitation
**Question:** A check for repository invitations revealed an expired invitation from you for **`realmarcin/fitness-mcp`** described as "mcp for mutant pool fitness data". Is this a relevant project to discuss? Should I request a new invitation?

**Context:** Found during GitHub repository analysis. May or may not be relevant to CMM/ICBO work.

---

## Unresolved Questions from GPT-5 Research

### 1. For Deepening the CMM–KG-Microbe Link
**Question:** Is there a README, proposal, or internal summary document in the local CMM or CultureBot directories that explicitly links KG-Microbe to CMM goals (e.g., lanthanide modeling or bioprospecting)?

**Finding:** No separate local documents found. The `ICBO_PREP_SUMMARY_UPDATED.md` provides this context, but not as a standalone document in the requested format.

**Status:** Resolved - information is in this consolidated documentation.

### 2. For Slide Content & Examples - Presentation Files
**Question:** Do you have internal or draft slides/presentations about METPO or KG-Microbe that Marcin or Cecilia used in CMM contexts?

**Finding:** No local presentation files found.

**Status:** Unresolved - may need to create slides from scratch or ask Marcin.

### 3. For Slide Content & Examples - Code Examples
**Question:** Is there a notebook or script in the `metpo-kgm-studio` or `kg-microbe` repo that shows a working example of querying or reasoning over a KG triple involving METPO terms?

**Finding:** No explicit code examples found in the `kg-microbe` repository.

**Status:** Unresolved - see "Questions for Marcin #2" above.

### 4. For Domain Connection - Data Mapping
**Question:** Are there JSON/CSV data extracts or processed versions of BacDive/BactoTraits/Madin in the local filesystem that show how raw trait data was mapped into METPO terms or KG-Microbe structure?

**Finding:** No JSON/CSV data extracts found in the `metpo` repository showing mapping to METPO terms.

**Status:** Unresolved - see "Questions for Marcin #3" above.

### 5. For Domain Connection - Lanthanide Work
**Question:** Any signs of ongoing work related to lanthanide traits or methylotrophy? Look for commits, new METPO terms, or notes in spreadsheets/templates that mention: lanthanide, Ln, rare earth, MeDH, XoxF, Methylobacterium, etc.

**Finding:** No explicit mentions found in the `metpo` repository files.

**Status:** Unresolved - see "Questions for Marcin #4" above.

---

## Gemini's Technical Questions

### 1. Regarding Sibling Coherence Results
**Question:** The analysis we ran showed very low coherence scores (mean 8.2%), indicating a significant structural divergence between METPO and other ontologies, even when term-level mappings exist. This is a very interesting, data-driven finding. For the talk, how would you like to frame this?

**Options:**
- As a key justification for METPO's creation, highlighting the "gaps" in the existing ontology landscape?
- As a general challenge in ontology alignment that METPO's development process helps to navigate?

**Context:** This could be a powerful argument for METPO's necessity, but needs careful framing.

**Status:** Open for discussion.

### 2. Unresolved N4L Hierarchy
**Question:** We were unable to determine the parent of N4L's 'Mid range temperature condition' (and other N4L terms) because the `n4l_merged.db` file does not contain the expected N4L ontology terms. While `n4l_merged.owl` exists, we haven't confirmed if `oaklib` is successfully parsing its hierarchy. This impacts our understanding of the coherence scores for N4L terms. Could you investigate the `n4l_merged.db` and `n4l_merged.owl` files to ensure `oaklib` can correctly access the N4L hierarchy?

**Context:** This is a technical issue that may affect the accuracy of our coherence analysis.

**Impact:** N4L had the highest ROI (167.40 good matches per 1000 embeddings), so accurate analysis is important.

**Status:** Technical investigation needed.

---

## Next Steps

### High Priority
- [ ] Get Marcin's explanation of KG prediction methods (Question for Marcin #1)
- [ ] Obtain query examples from Marcin (Question for Marcin #2)
- [ ] Decide how to frame sibling coherence results (Gemini's Question #1)
- [ ] Determine priority terms for manual definition (Question for Mark #3)

### Medium Priority
- [ ] Get data mapping examples (Question for Marcin #3)
- [ ] Confirm status of lanthanide work (Question for Marcin #4)
- [ ] Create visual diagrams for talk (Question for Mark #2)
- [ ] Articulate real-world impact examples (Question for Mark #1)

### Low Priority
- [ ] Investigate N4L hierarchy parsing issue (Gemini's Question #2)
- [ ] Follow up on fitness-mcp repository (Question for Marcin #5)
- [ ] Check for existing presentation files (GPT-5 Question #2)
