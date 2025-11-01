# Update on Non-OLS Ontology Processing

Here is a summary of the progress and issues encountered while processing the list of non-OLS ontologies.

### **Goal:**
Our objective was to download a list of 12 non-OLS ontologies from BioPortal, extract their terms using a SPARQL query, and then embed those terms into a ChromaDB database.

---

### **Step 1: Fetching Ontologies from BioPortal**

We attempted to download all 12 ontologies into the `non-ols/` directory.

*   **Successful Downloads (9/12):**
    *   `BIPON.owl`
    *   `D3O.owl`
    *   `FMPM.owl`
    *   `GMO.owl`
    *   `ID-AMR.owl`
    *   `MCCV.owl`
    *   `MPO.owl`
    *   `OMP.owl`
    *   `OFSMR.owl`
    *   `TYPON.owl`

*   **Download Failures (3/12):**
    *   **`HMADO`**: The download failed because BioPortal returned a `422` error: `"Upload File Path is not set"`. This ontology is not available for download via the API.
    *   **`MISO`**: The download failed because BioPortal returned a `404` error: `"There is no latest submission loaded for download"`. This ontology is also unavailable via the API.

---

### **Step 2: Extracting Terms with SPARQL**

The next step was to run `robot query` on each successfully downloaded file to generate a `.tsv` file in `notebooks/non-ols-terms/`.

*   **Successful Extractions (8/10):**
    *   `BIPON.tsv`
    *   `D3O.tsv`
    *   `FMPM.tsv`
    *   `GMO.tsv`
    *   `MCCV.tsv`
    *   `MPO.tsv`
    *   `OMP.tsv`
    *   `TYPON.tsv`

*   **SPARQL Query Failures (2/10):**
    *   **`MEO.owl`**: The query failed because this ontology contains imports to external ontologies that could not be resolved (e.g., `https://mdatahub.org/data/msv/`).
    *   **`ID-AMR.owl` & `OFSMR.owl`**: These produced **0-byte (empty) `.tsv` files**. The reason is that these ontologies define their terms using `skos:Concept`, but our SPARQL query was only looking for `owl:Class`.

---

### **Summary of Corrective Actions & Current Status**

1.  **Removed from Process:** Due to the persistent failures, `HMADO`, `MISO`, and `MEO` have been removed from the `Makefile` processing list.
2.  **SPARQL Query Fixed:** The SPARQL query (`sparql/extract_for_embeddings.rq`) has been **modified** to recognize both `owl:Class` and `skos:Concept` terms.

The next step is to re-run the `make` command, which will use the updated query to correctly process `ID-AMR.owl` and `OFSMR.owl`, and then proceed to embed all the successfully generated `.tsv` files.
