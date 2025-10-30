Here is a breakdown of how the abstract fetching process works and a plan to get the abstracts you want.

### How the Abstract Fetching Target Works

Based on my analysis of the `literature_mining/Makefile`:

*   **Makefile Target:** The target to run is `abstracts-$(SOURCE)`, where `SOURCE` is a name you provide. For example, `make -C literature_mining abstracts-cmm`.
*   **Input List:** The Makefile is currently configured to look for a specific input file format: `inputs/random-$(SOURCE)-pmids.txt`. This means the input filename is not flexible without modifying the Makefile.
*   **Output Directory:** The output directory is hardcoded to `literature_mining/abstracts/`. This means that, by default, all new abstracts will be saved there.

### Strategy for Your Request

Since the output directory is hardcoded, the cleanest way to handle this without modifying your Makefile is to run the `artl-cli` command directly for each PMID and save the files to a new directory.

Here is the plan I propose:

1.  **Create a new directory:** I will create a new directory named `literature_mining/cmm_pfas_abstracts/` to store the new abstracts.
2.  **Create a PMID list:** I will gather all the PMIDs I found for the CMM and PFAS papers and save them to a new file: `literature_mining/inputs/cmm_pfas_pmids.txt`.
3.  **Fetch the abstracts:** I will then run the `artl-cli` command for each PMID in that list, saving each abstract to the new `literature_mining/cmm_pfas_abstracts/` directory.