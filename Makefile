WGET=wget
UNZIP=unzip

-include .env
export

.PHONY: install clean-env clean-data

# Environment setup target
install:
	uv sync --all-extras

# Aggressively remove all UV and Poetry environment files
clean-env:
	rm -rf .venv/
	rm -f uv.lock poetry.lock
	rm -rf venv/ .python-version .uv/ 
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "All python environment files cleaned"

# Remove all generated data files
clean-data:
	rm -f downloads/taxdmp.zip
	rm -rf local/taxdmp/
	rm -f local/noderanks.ttl
	rm -f data/generated/bacdive_oxygen_phenotype_mappings.tsv
	rm -rf data/bioportal_owl/
	rm -rf data/entity_extracts/
	rm -rf data/reports/
	rm -rf downloads/sheets/
	@echo "All generated data files cleaned"

# see https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt regarding nodes.dmp

downloads/taxdmp.zip:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"

local/taxdmp: downloads/taxdmp.zip
	$(UNZIP) $< -d $@

local/taxdmp/nodes.dmp: local/taxdmp

# Extract taxonomy rank triples from NCBI nodes.dmp file to a TTL file
local/noderanks.ttl: local/taxdmp/nodes.dmp
	uv run extract-rank-triples --input-file $< --output-file $@

data/generated/bacdive_oxygen_phenotype_mappings.tsv: sparql/bacdive_oxygen_phenotype_mappings.rq src/ontology/metpo.owl
	mkdir -p $(dir $@)
	robot query \
		--query $(word 1,$^) $@ \
		--input $(word 2,$^)

# Extract terms from non-OLS ontologies for embedding generation
# Pattern: notebooks/non-ols-terms/<ontology-id>_terms.tsv
# Usage: make notebooks/non-ols-terms/D3O.tsv
# Make calls robot directly with catalog to handle broken imports
# Python validates output
notebooks/non-ols-terms/%.tsv: non-ols/%.owl sparql/extract_for_embeddings.rq
	@mkdir -p $(dir $@)
	@echo "Querying $* with ROBOT..."
	-@robot query --input $< --catalog catalog-v001.xml --query $(word 2,$^) $@ 2>&1 | tee -a .robot_query.log
	-@uv run validate-tsv $* --tsv $@

notebooks/non-ols-terms/%.tsv: non-ols/%.ttl sparql/extract_for_embeddings.rq
	@mkdir -p $(dir $@)
	@echo "Querying $* with ROBOT..."
	-@robot query --input $< --catalog catalog-v001.xml --query $(word 2,$^) $@ 2>&1 | tee -a .robot_query.log
	-@uv run validate-tsv $* --tsv $@

reports/leaf_classes_without_attributed_synonyms.tsv: src/ontology/metpo.owl sparql/find_leaf_classes_without_attributed_synonyms.sparql
	mkdir -p $(dir $@)
	robot query --input $(word 1,$^) --query $(word 2,$^) $@

reports/synonym-sources.tsv: src/ontology/metpo.owl src/sparql/synonym-sources.sparql
	mkdir -p $(dir $@)
	robot query \
		--input $< \
		--query $(word 2,$^) $@


reports/madin-metpo-reconciliation.yaml: reports/synonym-sources.tsv
	uv run reconcile-madin-coverage \
		--mode integrated \
		--format yaml \
		--tsv $< \
		--output $@

.PHONY: import-madin
import-madin: local/madin/madin_etal.csv
	mongoimport --db madin --collection madin --type csv --file $< --headerline --drop

.PHONY: clean-madin-db
clean-madin-db:
	mongosh madin --eval 'db.madin.drop()'

.PHONY: clean-bactotraits-db
clean-bactotraits-db:
	mongosh bactotraits --eval 'db.bactotraits.drop(); db.field_mappings.drop(); db.files.drop()'

.PHONY: clean-reports
clean-reports:
	rm -f reports/synonym-sources.tsv
	rm -f reports/bactotraits-metpo-set-diff.yaml
	rm -f reports/bactotraits-metpo-reconciliation.yaml
	rm -f reports/madin-metpo-reconciliation.yaml
	rm -f reports/leaf_classes_without_attributed_synonyms.tsv
	@echo "All analysis reports cleaned"

.PHONY: clean-all
clean-all: clean-env clean-data clean-bactotraits-db clean-madin-db clean-reports
	@echo "Complete cleanup finished"

.PHONY: import-all
import-all: import-bactotraits import-madin import-bactotraits-metadata import-madin-metadata
	@echo "All datasets and metadata imported successfully"

.PHONY: all-reports
all-reports: reports/synonym-sources.tsv reports/bactotraits-metpo-set-diff.yaml reports/bactotraits-metpo-reconciliation.yaml reports/madin-metpo-reconciliation.yaml
	@echo "All analysis reports generated successfully"

.PHONY: test-workflow
test-workflow: clean-all import-all all-reports
	@echo ""
	@echo "=========================================="
	@echo "Workflow Reproducibility Test Complete"
	@echo "=========================================="
	@echo ""
	@echo "MongoDB Collections:"
	@mongosh bactotraits --quiet --eval 'print("  bactotraits.bactotraits:", db.bactotraits.countDocuments({}), "documents")'
	@mongosh bactotraits --quiet --eval 'print("  bactotraits.field_mappings:", db.field_mappings.countDocuments({}), "documents")'
	@mongosh bactotraits --quiet --eval 'print("  bactotraits.files:", db.files.countDocuments({}), "documents")'
	@mongosh madin --quiet --eval 'print("  madin.madin:", db.madin.countDocuments({}), "documents")'
	@mongosh madin --quiet --eval 'print("  madin.files:", db.files.countDocuments({}), "documents")'
	@echo ""
	@echo "Generated Reports:"
	@ls -lh reports/*.yaml reports/*.tsv 2>/dev/null || echo "  No reports found"
	@echo ""

.PHONY: import-bactotraits
import-bactotraits:
	uv run import-bactotraits

.PHONY: import-bactotraits-metadata
import-bactotraits-metadata: metadata/bactotraits_field_mappings.json metadata/bactotraits_files.json
	jq '.mappings' metadata/bactotraits_field_mappings.json | \
		mongoimport --db bactotraits --collection field_mappings \
		--jsonArray --drop
	mongoimport --db bactotraits --collection files \
		--file metadata/bactotraits_files.json \
		--jsonArray --drop
	@echo "BactoTraits metadata collections imported"

.PHONY: import-madin-metadata
import-madin-metadata: metadata/madin_files.json
	mongoimport --db madin --collection files \
		--file metadata/madin_files.json \
		--jsonArray --drop
	@echo "Madin metadata collections imported"

reports/bactotraits-metpo-set-diff.yaml: metpo/scripts/bactotraits_metpo_set_difference.py reports/synonym-sources.tsv local/bactotraits/BactoTraits.tsv
	uv run bactotraits-metpo-set-difference \
		--bactotraits-file $(word 3, $^) \
		--synonyms-file $(word 2, $^) \
		--format yaml \
		--output $@

reports/bactotraits-metpo-reconciliation.yaml: metpo/scripts/reconcile_bactotraits_coverage.py reports/synonym-sources.tsv
	uv run reconcile-bactotraits-coverage \
		--mode field_names \
		--tsv $(word 2, $^) \
		--format yaml \
		--output $@

# BactoTraits field mappings - generates JSON and loads to MongoDB
metadata/bactotraits_field_mappings.json: local/bactotraits/BactoTraits_databaseV2_Jun2022.csv local/bactotraits/BactoTraits.tsv
	uv run create-bactotraits-field-mappings \
		--provider-file local/bactotraits/BactoTraits_databaseV2_Jun2022.csv \
		--kg-microbe-file local/bactotraits/BactoTraits.tsv \
		--output-json $@ \
		--db-name bactotraits \
		--collection-name field_mappings

.PHONY: create-bactotraits-file-versions
create-bactotraits-file-versions:
	uv run create-bactotraits-file-versions

.PHONY: create-bactotraits-files
create-bactotraits-files:
	uv run create-bactotraits-files

# =====================================================
# Google Sheets Download Targets
# =====================================================

# Default spreadsheet ID (from metpo.Makefile)
SPREADSHEET_ID = 1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU
BASE_URL = https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export

# All sheet gids discovered via Google Apps Script (10 total sheets)
GID_MINIMAL_CLASSES = 355012485
GID_PROPERTIES = 2094089867
GID_BACTOTRAITS = 1192666692
GID_MORE_SYNONYMS = 907926993
GID_MORE_CLASSES___INCONSISTENT = 1427185859
GID_METABOLIC_AND_RESPIRATORY_ROBOT = 2135183176
GID_METABOLIC_AND_RESPIRATORY_LLM = 499077032
GID_TROPHIC_MAPPING_BACDIVE__TBDELETED = 44169923
GID_ATTIC_CLASSES = 1347388120
GID_ATTIC_PROPERTIES = 565614186

.PHONY: download-all-sheets clean-sheets

# Download all discovered sheets to downloads/sheets/
download-all-sheets: downloads/sheets/minimal_classes.tsv downloads/sheets/properties.tsv downloads/sheets/bactotraits.tsv downloads/sheets/more_synonyms.tsv downloads/sheets/more_classes___inconsistent.tsv downloads/sheets/metabolic_and_respiratory_robot.tsv downloads/sheets/metabolic_and_respiratory_llm.tsv downloads/sheets/trophic_mapping_bacdive__tbdeleted.tsv downloads/sheets/attic_classes.tsv downloads/sheets/attic_properties.tsv
	@echo "All 10 sheets downloaded to downloads/sheets/"

# Individual sheet download targets
downloads/sheets/minimal_classes.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MINIMAL_CLASSES)' > $@

downloads/sheets/properties.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_PROPERTIES)' > $@

downloads/sheets/bactotraits.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_BACTOTRAITS)' > $@

downloads/sheets/more_synonyms.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MORE_SYNONYMS)' > $@

downloads/sheets/more_classes___inconsistent.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MORE_CLASSES___INCONSISTENT)' > $@

downloads/sheets/metabolic_and_respiratory_robot.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_METABOLIC_AND_RESPIRATORY_ROBOT)' > $@

downloads/sheets/metabolic_and_respiratory_llm.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_METABOLIC_AND_RESPIRATORY_LLM)' > $@

downloads/sheets/trophic_mapping_bacdive__tbdeleted.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_TROPHIC_MAPPING_BACDIVE__TBDELETED)' > $@

downloads/sheets/attic_classes.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_ATTIC_CLASSES)' > $@

downloads/sheets/attic_properties.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_ATTIC_PROPERTIES)' > $@

# Ensure downloads/sheets directory exists
downloads/sheets:
	mkdir -p $@

# Clean downloaded sheets
clean-sheets:
	rm -rf downloads/sheets/
	@echo "Downloaded sheets cleaned"

# =====================================================
# BiPortal METPO Releases Download Targets
# =====================================================

# BiPortal API URLs for METPO submissions
BIOPORTAL_SUBMISSION_BASE = https://data.bioontology.org/ontologies/METPO/submissions

# METPO submissions on BiPortal (submissions 2-10 have OWL files, submission 1 doesn't)
# Format: submission_id:version_date
METPO_SUBMISSIONS = \
	2:2025-03-13 \
	3:2025-03-19 \
	4:2025-03-22 \
	5:2025-03-24 \
	6:2025-04-25 \
	7:2025-06-25 \
	8:2025-08-18 \
	9:2025-09-22 \
	10:2025-09-23

.PHONY: download-all-bioportal-submissions clean-bioportal-submissions list-bioportal-submissions

# Download all METPO submissions from BiPortal
download-all-bioportal-submissions: $(foreach sub,$(METPO_SUBMISSIONS),data/bioportal_owl/metpo_submission_$(word 1,$(subst :, ,$(sub))).owl)
	@echo "All BiPortal METPO submissions downloaded to data/bioportal_owl/"

# Individual submission download targets
data/bioportal_owl/metpo_submission_%.owl: | data/bioportal_owl
	@echo "Downloading METPO submission $*..."
	@curl -L -s "$(BIOPORTAL_SUBMISSION_BASE)/$*/download?apikey=$$BIOPORTAL_API_KEY" -o $@
	@if [ -s $@ ]; then \
		echo "✓ Successfully downloaded submission $*"; \
		grep -m1 "versionInfo" $@ || echo "No version info found"; \
	else \
		echo "✗ Failed to download submission $*"; \
		rm -f $@; \
	fi

# Ensure data/bioportal_owl directory exists
data/bioportal_owl:
	mkdir -p $@

# Clean downloaded BiPortal submissions

# =====================================================
# Non-OLS BioPortal Ontology Download Targets
# =====================================================



# List of non-OLS ontologies to process from BioPortal
# MPO: MPO/RIKEN Microbial Phenotype Ontology
# OMP: Ontology of Microbial Phenotypes
# BIPON: Bacterial interlocked Process Ontology
# D3O: D3O/DSMZ Digital Diversity Ontology
# FMPM: Food Matrix for Predictive Microbiology
# GMO: Growth Medium Ontology
# HMADO: Human Microbiome and Disease Ontology
# ID-AMR: Infectious Diseases and Antimicrobial Resistance
# MCCV: Microbial Culture Collection Vocabulary
# MEO: Metagenome and Environment Ontology
# miso: Microbial Conditions Ontology
# OFSMR: Open Predictive Microbiology Ontology
# TYPON: Microbial Typing Ontology
NON_OLS_BIOPORTAL_ONTOLOGIES = MPO OMP BIPON D3O FMPM GMO HMADO ID-AMR MCCV MEO miso OFSMR TYPON

.PHONY: download-non-ols-bioportal-ontologies clean-non-ols-bioportal-ontologies

download-non-ols-bioportal-ontologies: $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),non-ols/$(ont).owl)
	@echo ""
	@echo "=========================================="
	@echo "Download phase complete"
	@echo "=========================================="
	@echo "Run 'make scan-manifest' to update tracking"
	@echo "Run 'make view-logs' to see any failures"


# Download ontology from BioPortal
# Python script handles all error checking, logging, and validation
# Exit code 0 = success, 1 = failure
non-ols/%.owl: | non-ols
	-@uv run download-ontology $* --output $@

non-ols/%.ttl: | non-ols
	-@uv run download-ontology $* --output $@

non-ols:
	mkdir -p $@

clean-non-ols-bioportal-ontologies:
	@echo "Cleaning downloaded non-OLS BioPortal ontologies..."
	@echo "Keeping manually added files: n4l_merged.owl, MISO.owl (if present)"
	rm -f $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),non-ols/$(ont).owl)
	@echo "Cleaned non-OLS BioPortal ontologies"

clean-non-ols-pipeline:
	@echo "Cleaning pipeline-generated files (keeping manual downloads)..."
	@echo "Removing BioPortal downloads..."
	rm -f $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),non-ols/$(ont).owl)
	@echo "Removing ROBOT query outputs..."
	rm -f notebooks/non-ols-terms/*.tsv
	@echo "Removing logs and manifest..."
	rm -f .ontology_manifest.json .ontology_fetch.log .robot_query.log
	@echo ""
	@echo "✓ Cleaned pipeline files"
	@echo "✓ Kept manual files: non-ols/n4l_merged.owl"
	@if [ -f non-ols/MISO.owl ]; then echo "✓ Kept manual files: non-ols/MISO.owl"; fi

clean-bioportal-submissions:
	rm -rf data/bioportal_owl/
	@echo "Downloaded BiPortal submissions cleaned"

# List available submissions
list-bioportal-submissions:
	@echo "Available METPO submissions on BiPortal:"
	@for sub in $(METPO_SUBMISSIONS); do \
		id=$$(echo $$sub | cut -d: -f1); \
		version=$$(echo $$sub | cut -d: -f2); \
		echo "  - Submission $$id: $$version"; \
	done
	@echo ""
	@echo "To download all: make download-all-bioportal-submissions"
	@echo "To download specific submission: make data/bioportal_owl/metpo_submission_5.owl"

# =====================================================
# METPO Entity Extraction Targets
# =====================================================

.PHONY: extract-all-metpo-entities clean-entity-extracts

# Extract METPO entities from all submissions
extract-all-metpo-entities: $(foreach sub,$(METPO_SUBMISSIONS),data/entity_extracts/metpo_submission_$(word 1,$(subst :, ,$(sub)))_all_entities.tsv)
	@echo "All METPO entities extracted to data/entity_extracts/"

# Individual entity extraction targets
data/entity_extracts/metpo_submission_%_all_entities.tsv: data/bioportal_owl/metpo_submission_%.owl | data/entity_extracts
	@echo "Extracting entities from METPO submission $*..."
	robot query -i $< -s analysis/sparql_queries/query_metpo_entities.sparql $@

# Ensure data/entity_extracts directory exists
data/entity_extracts:
	mkdir -p $@

# Clean extracted entity files
clean-entity-extracts:
	rm -rf data/entity_extracts/
	@echo "Extracted entity files cleaned"

# Ensure downloads/bioportal directory exists
downloads/bioportal:
	mkdir -p $@

# Clean downloaded BiPortal files
clean-bioportal:
	rm -rf downloads/bioportal/
	@echo "Downloaded BiPortal releases cleaned"

# List known releases (for manual verification)
list-bioportal-releases:
	@echo "Known METPO releases on BiPortal:"
	@for release in $(METPO_RELEASES); do \
		echo "  - metpo-$$release.owl"; \
	done
	@echo ""
	@echo "To download all: make download-all-bioportal"
	@echo "To download specific release: make downloads/bioportal/metpo-2025-09-23.owl"
	@echo ""
	@echo "Note: Set BIOPORTAL_API_KEY environment variable for authenticated downloads"

# ==============================================================================
# Ontology Alignment Pipeline - Granular Targets
# ==============================================================================

.PHONY: alignment-fetch-ontology-names alignment-categorize-ontologies \
        alignment-query-metpo-terms alignment-analyze-matches \
        alignment-analyze-coherence alignment-identify-candidates \
        alignment-run-all clean-alignment-results clean-alignment-all help-alignment

# Individual pipeline steps
alignment-fetch-ontology-names: notebooks/ontology_catalog.csv

notebooks/ontology_catalog.csv: notebooks/ontology_sizes.csv
	@echo "Fetching ontology metadata from OLS4 API..."
	cd notebooks && python fetch_ontology_names.py \
		--sizes-csv ontology_sizes.csv \
		--output-csv ontology_catalog.csv

alignment-categorize-ontologies: notebooks/ontologies_very_appealing.csv

notebooks/ontologies_very_appealing.csv: notebooks/ontology_catalog.csv
	@echo "Categorizing ontologies by relevance..."
	cd notebooks && python categorize_ontologies.py \
		--input-csv ontology_catalog.csv \
		--output-prefix ontologies

alignment-query-metpo-terms: notebooks/metpo_relevant_mappings.sssom.tsv

notebooks/metpo_relevant_mappings.sssom.tsv: notebooks/metpo_relevant_chroma
	@echo "Generating SSSOM mappings from METPO terms via ChromaDB..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "ERROR: OPENAI_API_KEY environment variable not set"; \
		exit 1; \
	fi
	cd notebooks && python chromadb_semantic_mapper.py \
		--metpo-tsv ../src/templates/metpo_sheet.tsv \
		--chroma-path ./metpo_relevant_chroma \
		--collection-name metpo_relevant_embeddings \
		--output metpo_relevant_mappings.sssom.tsv \
		--top-n 10 \
		--label-only \
		--distance-cutoff 0.35

alignment-analyze-matches: notebooks/metpo_relevant_mappings.sssom.tsv
	@echo "Analyzing match quality..."
	cd notebooks && python analyze_matches.py \
		--input-csv metpo_relevant_mappings.sssom.tsv \
		--good-match-threshold 0.9

alignment-analyze-coherence: notebooks/full_coherence_results.csv

notebooks/full_coherence_results.csv: notebooks/metpo_relevant_mappings.sssom.tsv
	@echo "Computing structural coherence (this may take a while)..."
	cd notebooks && python analyze_sibling_coherence.py \
		--input-csv metpo_relevant_mappings.sssom.tsv \
		--metpo-owl ../src/ontology/metpo.owl \
		--output-csv full_coherence_results.csv

alignment-identify-candidates: notebooks/alignment_candidates.csv

notebooks/alignment_candidates.csv: notebooks/full_coherence_results.csv
	@echo "Identifying alignment candidates..."
	cd notebooks && python analyze_coherence_results.py \
		--results-csv full_coherence_results.csv \
		--matches-csv metpo_relevant_mappings.sssom.tsv

# Run complete pipeline
alignment-run-all: alignment-identify-candidates
	@echo ""
	@echo "========================================="
	@echo "Alignment pipeline complete!"
	@echo "========================================="
	@echo "Output files:"
	@echo "  - notebooks/metpo_relevant_mappings.sssom.tsv"
	@echo "  - notebooks/full_coherence_results.csv"
	@echo "  - notebooks/alignment_candidates.csv"

# Clean alignment results
clean-alignment-results:
	@echo "Cleaning alignment pipeline results..."
	rm -f notebooks/metpo_*_matches.csv
	rm -f notebooks/*_coherence_results.csv
	rm -f notebooks/alignment_candidates.csv
	@echo "Alignment results cleaned (ontology catalog preserved)"

# Clean everything including ontology catalog

# =====================================================
# Non-OLS Embedding Targets
# =====================================================

NON_OLS_TSV_FILES = $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),notebooks/non-ols-terms/$(ont).tsv)

.PHONY: embed-non-ols-terms clean-non-ols-terms scan-manifest view-manifest view-logs

.PHONY: generate-non-ols-tsvs
generate-non-ols-tsvs: $(NON_OLS_TSV_FILES)
	@echo ""
	@echo "=========================================="
	@echo "Query phase complete"
	@echo "=========================================="
	@echo "Run 'make scan-manifest' to update tracking"
	@echo "Run 'make view-logs' to see any failures"

# Manifest and logging targets
scan-manifest:
	@echo "Scanning directories and updating manifest..."
	uv run scan-manifest --verbose

view-manifest:
	@if [ -f .ontology_manifest.json ]; then \
		cat .ontology_manifest.json | python -m json.tool; \
	else \
		echo "No manifest found. Run 'make scan-manifest' first."; \
	fi

view-logs:
	@echo "=== Recent Fetch Failures ==="
	@if [ -f .ontology_fetch.log ]; then tail -20 .ontology_fetch.log; else echo "No fetch failures logged"; fi
	@echo ""
	@echo "=== Recent Query Failures ==="
	@if [ -f .robot_query.log ]; then grep -E "QUERY_FAILED|QUERY_EMPTY" .robot_query.log | tail -20 || echo "No query failures logged"; else echo "No query log found"; fi

embed-non-ols-terms:
	@echo "Embedding non-OLS terms into ChromaDB..."
	uv run python notebooks/embed_ontology_to_chromadb.py \
		$(foreach tsv,$(wildcard notebooks/non-ols-terms/*.tsv),--tsv-file $(tsv)) \
		--chroma-path ./embeddings_chroma \
		--collection-name non_ols_embeddings
	@echo "Non-OLS terms embedded successfully."

clean-non-ols-terms:
	@echo "Cleaning generated non-OLS TSV files..."
	rm -f $(NON_OLS_TSV_FILES)
	@echo "Cleaned non-OLS TSV files"

clean-alignment-all: clean-alignment-results
	@echo "Cleaning all alignment files including ontology catalog..."
	rm -f notebooks/ontology_catalog.csv
	rm -f notebooks/ontologies_*.csv
	@echo "All alignment files cleaned"

# Help target
help-alignment:
	@echo "METPO Ontology Alignment Pipeline Targets:"
	@echo ""
	@echo "  Preparation:"
	@echo "    make alignment-fetch-ontology-names  - Fetch ontology metadata from OLS4"
	@echo "    make alignment-categorize-ontologies - Categorize by relevance"
	@echo ""
	@echo "  Analysis:"
	@echo "    make alignment-query-metpo-terms     - Query METPO against ChromaDB"
	@echo "    make alignment-analyze-matches       - Analyze match quality"
	@echo "    make alignment-analyze-coherence     - Compute structural coherence"
	@echo "    make alignment-identify-candidates   - Find high-quality candidates"
	@echo ""
	@echo "  Complete workflow:"
	@echo "    make alignment-run-all               - Run entire pipeline"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean-alignment-results         - Clean results only"
	@echo "    make clean-alignment-all             - Clean all including catalog"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    - Set OPENAI_API_KEY environment variable"
	@echo "    - Ensure ChromaDB collection exists at notebooks/metpo_relevant_chroma"
