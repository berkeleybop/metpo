This is a great set of questions that gets to the heart of the literature mining workflow. Let's break it down.

### 1. How to Fetch Abstracts from a List of PMIDs

You are correct, there is a `Makefile` target for this. The `abstracts` target in `literature_mining/Makefile` is designed to fetch abstracts for a list of PMIDs.

Here is how you would use it:

1.  **Create a list of PMIDs:** Create a text file with one PMID per line. For example, you could create `inputs/my_cmm_pmids.txt`.
2.  **Run the `make` target:** You would then run the `make` command, pointing to your file. The Makefile is set up to look for a file named `inputs/random-[SOURCE]-pmids.txt`, so you would either use that naming convention or adapt the Makefile.

Looking at the `Makefile`, the `abstracts-$(SOURCE)` target is what does the work. For example, to fetch abstracts for a source named `cmm`:

```makefile
# You would need to add a rule like this to your Makefile
abstracts-cmm: inputs/my_cmm_pmids.txt | abstracts
    @echo "📄 Fetching abstracts from CMM PMIDs..."
    cat $< | while read pmid; do \
        if [ ! -f "abstracts/$$pmid-abstract.txt" ]; then \
            echo "Fetching PMID $$pmid"; \
            uv run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt" 2>/dev/null || rm -f "abstracts/$$pmid-abstract.txt"; \
        fi; \
    done
```

The command uses `artl-cli` to fetch the abstract for each PMID in the input file and saves it to a file in the `abstracts/` directory with the format `[PMID]-abstract.txt`.

### 2. Strategy for Papers Without PMIDs

For the papers where we only have a DOI or a title, here are a few strategies we can use to get the abstracts:

**Reproducible (API-based) Approaches:**

*   **`artl-cli` with DOIs:** The `artl-cli` tool might be able to fetch abstracts using DOIs as well as PMIDs. We would need to check its documentation or help text to confirm this. If it does, this would be the most consistent approach.
*   **CrossRef API:** We can use the CrossRef API to get metadata for a given DOI. This metadata often includes the abstract. The endpoint is `https://api.crossref.org/works/[DOI]`.
*   **Unpaywall API:** This is a great resource for finding open-access versions of papers. For a given DOI, it can often provide a link to a full-text version of the paper, from which we can extract the abstract.

**LLM-based Approach:**

If the above methods fail, I can use an LLM-based approach. You would provide me with the DOI or the title of the paper, and I would:

1.  Perform a web search to find the paper's page on the publisher's website or on a pre-print server like arXiv or bioRxiv.
2.  Use my `web_fetch` tool to read the content of that page.
3.  Parse the HTML to extract the abstract text.

This is a powerful fallback, but the reproducible, API-based approaches are generally preferable for a systematic workflow.

### 3. Which Papers to Exclude?

You are right to question whether all of these papers are relevant. Based on the filenames and the content I've seen, here is my assessment of the two "machine learning" papers:

*   **`Machine_learning-led_semi-automated_medium_optimiz.md`**: **Keep this one.** The abstract is about "semi-automated medium optimization" for *Pseudomonas putida* to produce flaviolin. This is highly relevant as it will almost certainly contain detailed information about growth conditions and chemical utilization.

*   **`Machine_Learning_Approaches_to_Predicting_Lanthani.md`**: **Probably exclude this one.** The abstract for this paper is about "Antagonising explanation and revealing bias directly through sequencing and multimodal inference" and seems to be a computer science paper about the theory of generative models. It is unlikely to contain specific, extractable information about microbial phenotypes.

**General Strategy for Exclusion:**

A good strategy would be to do a quick review of the title and abstract of each paper. You should probably **exclude** a paper if:

*   It does not mention a specific microorganism (or a group of microorganisms).
*   It does not describe any specific phenotypes, growth conditions, or metabolic activities.
*   It is a purely theoretical or methodological paper from a different field (like computer science or social science).

I can help with this review process if you'd like.
