WGET=wget
UNZIP=unzip

-include .env
export

# ==============================================================================
# Default Target
# ==============================================================================

.DEFAULT_GOAL := help

# MetaTraits Mongo demo defaults (override at invocation time if needed)
METATRAITS_MONGO_URI ?= mongodb://localhost:27017
METATRAITS_DB ?= metatraits
METATRAITS_COLLECTION ?= genome_traits
METATRAITS_LIMIT ?= 50
METATRAITS_CARDS ?= data/mappings/metatraits_cards.tsv
METATRAITS_RESOLUTION_TABLE ?= data/mappings/metatraits_in_sheet_resolution.tsv
METATRAITS_RESOLUTION_REPORT ?= data/mappings/metatraits_in_sheet_resolution_report.md
METATRAITS_DEMO_OUTPUT_PREFIX ?= data/mappings/demo_metatraits_mongo_kgx
METATRAITS_DEMO_FORMAT ?= tsv

# ==============================================================================
# Environment Setup Targets
# ==============================================================================

.PHONY: help install install-dev install-literature install-databases install-notebooks install-all check-env clean-env clean-data metpo-report metatraits-helper-files clean-metatraits-helper-files demo-metatraits-mongo clean-metatraits-demo

# Show available targets and usage information
help:
	@echo "METPO Project - Main Makefile"
	@echo ""
	@echo "Environment Setup:"
	@echo "  make install              - Install core dependencies"
	@echo "  make install-dev          - Install development environment"
	@echo "  make install-literature   - Install literature mining environment"
	@echo "  make install-databases    - Install database workflows environment"
	@echo "  make install-notebooks    - Install notebooks environment"
	@echo "  make install-all          - Install all optional dependencies"
	@echo "  make check-env            - Check environment status"
	@echo ""
	@echo "Quality Control:"
	@echo "  make metpo-report.tsv     - Generate ROBOT quality control report"
	@echo ""
	@echo "Data Import:"
	@echo "  make import-all           - Import all datasets (BactoTraits + Madin)"
	@echo "  make import-bactotraits   - Import BactoTraits data to MongoDB"
	@echo "  make import-madin         - Import Madin et al. data to MongoDB"
	@echo "  make metatraits-helper-files - Generate deterministic MetaTraits helper files"
	@echo "  make demo-metatraits-mongo - Build KGX demo edges from MongoDB MetaTraits records"
	@echo ""
	@echo "Analysis Reports:"
	@echo "  make all-reports          - Generate all analysis reports"
	@echo ""
	@echo "Ontology Alignment Pipeline:"
	@echo "  make help-alignment       - Show detailed alignment pipeline help"
	@echo "  make alignment-run-all    - Run complete alignment pipeline"
	@echo ""
	@echo "External Ontology Downloads:"
	@echo "  make download-external-bioportal-ontologies  - Download non-OLS ontologies"
	@echo "  make generate-non-ols-tsvs                   - Extract terms for embeddings"
	@echo "  make scan-manifest                           - Update ontology manifest"
	@echo ""
	@echo "Literature Mining:"
	@echo "  make -C literature_mining help               - Show literature mining help"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean-all            - Complete cleanup (env + data + databases)"
	@echo "  make clean-env            - Remove virtual environments"
	@echo "  make clean-data           - Remove generated data files"
	@echo "  make clean-metatraits-helper-files - Remove generated MetaTraits helper files"
	@echo "  make clean-metatraits-demo - Remove generated MetaTraits demo KGX outputs"
	@echo "  make clean-reports        - Remove analysis reports"
	@echo ""
	@echo "Testing:"
	@echo "  make test-workflow        - Test complete workflow reproducibility"

# Base installation (core dependencies only: click, python-dotenv, pyyaml, requests)
install:
	uv sync

# Development environment (adds: oaklib, pandas, pymongo, rdflib, semsql, tqdm, litellm, openai)
install-dev:
	uv sync --extra dev

# Literature mining environment (adds: artl-mcp, oaklib, ontogpt, pandas, litellm, openai, semsql)
install-literature:
	uv sync --extra literature

# Database workflows (adds: pandas, pymongo for BactoTraits/Madin imports)
install-databases:
	uv sync --extra databases

# Notebooks environment (adds: jupyter, notebook, matplotlib, numpy, chromadb, etc.)
install-notebooks:
	uv sync --extra notebooks

# Install all optional dependencies
install-all:
	uv sync --all-extras

# Check environment status
check-env:
	@echo "=== METPO Environment Status ==="
	@echo ""
	@echo "Python:"
	@which python3 || echo "  ✗ python3 not found"
	@python3 --version 2>/dev/null || true
	@echo ""
	@echo "UV:"
	@which uv || echo "  ✗ uv not found (install: curl -LsSf https://astral.sh/uv/install.sh | sh)"
	@uv --version 2>/dev/null || true
	@echo ""
	@echo "Virtual Environment:"
	@test -d .venv && echo "  ✓ .venv exists" || echo "  ✗ .venv not found (run: make install)"
	@test -f .venv/bin/python && .venv/bin/python --version || true
	@echo ""
	@echo "MongoDB:"
	@which mongosh || echo "  ✗ mongosh not found"
	@mongosh --version 2>/dev/null || true
	@echo ""
	@echo "ROBOT:"
	@which robot || echo "  ✗ robot not found"
	@robot --version 2>/dev/null || true
	@echo ""
	@echo "Environment Variables:"
	@test -f .env && echo "  ✓ .env file exists" || echo "  ✗ .env file not found"
	@test -n "$$BIOPORTAL_API_KEY" && echo "  ✓ BIOPORTAL_API_KEY set" || echo "  ✗ BIOPORTAL_API_KEY not set"
	@test -n "$$OPENAI_API_KEY" && echo "  ✓ OPENAI_API_KEY set" || echo "  ✗ OPENAI_API_KEY not set (required for literature mining)"

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
	rm -rf external/metpo_historical/
	rm -rf metadata/ontology/historical_submissions/entity_extracts/
	rm -rf downloads/sheets/
	rm -f data/mappings/metatraits_cards.tsv
	rm -f data/mappings/metatraits_in_sheet_resolution.tsv
	rm -f data/mappings/metatraits_in_sheet_resolution_report.md
	rm -f data/mappings/demo_metatraits_mongo_kgx_*.*sv
	@echo "All generated data files cleaned"

# ==============================================================================
# MetaTraits MongoDB Demo
# ==============================================================================

# Build helper files used by deterministic MetaTraits -> KGX transforms.
# Runtime code should consume these files directly, with no fuzzy matching.
$(METATRAITS_CARDS):
	uv run fetch-metatraits -o $(METATRAITS_CARDS)

# Note: resolver writes both $(METATRAITS_RESOLUTION_TABLE) and
# $(METATRAITS_RESOLUTION_REPORT) in one pass.
$(METATRAITS_RESOLUTION_TABLE): $(METATRAITS_CARDS) metpo/scripts/resolve_metatraits_in_sheets.py src/templates/metpo-properties.tsv src/templates/metpo_sheet.tsv
	uv run resolve-metatraits-in-sheets \
		-m $(METATRAITS_CARDS) \
		-o $(METATRAITS_RESOLUTION_TABLE) \
		-r $(METATRAITS_RESOLUTION_REPORT)

.PHONY: metatraits-helper-files
metatraits-helper-files: $(METATRAITS_RESOLUTION_TABLE)
	@test -f "$(METATRAITS_RESOLUTION_REPORT)" || (echo "Missing $(METATRAITS_RESOLUTION_REPORT) after resolver run" && exit 1)
	@echo "Helper files ready:"
	@echo "  - $(METATRAITS_CARDS)"
	@echo "  - $(METATRAITS_RESOLUTION_TABLE)"
	@echo "  - $(METATRAITS_RESOLUTION_REPORT)"

.PHONY: clean-metatraits-helper-files
clean-metatraits-helper-files:
	rm -f data/mappings/metatraits_cards.tsv
	rm -f data/mappings/metatraits_in_sheet_resolution.tsv
	rm -f data/mappings/metatraits_in_sheet_resolution_report.md
	@echo "MetaTraits helper files cleaned"

.PHONY: demo-metatraits-mongo
demo-metatraits-mongo: $(METATRAITS_RESOLUTION_TABLE)
	uv run demo-metatraits-mongo-to-kgx \
		--mongo-uri $(METATRAITS_MONGO_URI) \
		--db $(METATRAITS_DB) \
		--collection $(METATRAITS_COLLECTION) \
		--resolution-table $(METATRAITS_RESOLUTION_TABLE) \
		--limit $(METATRAITS_LIMIT) \
		--format $(METATRAITS_DEMO_FORMAT) \
		--output-prefix $(METATRAITS_DEMO_OUTPUT_PREFIX)
	@echo ""
	@echo "Wrote KGX files with prefix: $(METATRAITS_DEMO_OUTPUT_PREFIX)"
	@echo "Tip: override defaults, e.g."
	@echo "  make demo-metatraits-mongo METATRAITS_COLLECTION=genome_traits METATRAITS_LIMIT=200"

.PHONY: clean-metatraits-demo
clean-metatraits-demo:
	rm -f data/mappings/demo_metatraits_mongo_kgx_*.*sv
	@echo "MetaTraits demo outputs cleaned"

# ==============================================================================
# METPO Quality Control Report
# ==============================================================================

# Generate ROBOT quality control report from the main release file
# Usage: make metpo-report.tsv
# Note: This file is gitignored and can be regenerated anytime
metpo-report.tsv: metpo.owl
	@echo "Generating ROBOT quality control report..."
	robot report -i $< \
		-l true \
		--fail-on None \
		--base-iri https://w3id.org/metpo/METPO_ \
		--base-iri https://w3id.org/metpo/metpo \
		--print 5 \
		-o $@
	@echo "Report generated: $@"
	@echo ""
	@wc -l $@ | awk '{print "Total issues:", $$1-1}'
	@grep "^ERROR" $@ | wc -l | awk '{print "Errors:", $$1}'
	@grep "^WARN" $@ | wc -l | awk '{print "Warnings:", $$1}'
	@grep "^INFO" $@ | wc -l | awk '{print "Info:", $$1}'

# ==============================================================================
# Taxonomy Data
# ==============================================================================

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

# Extract terms from external ontologies for embedding generation
# Pattern: data/pipeline/non-ols-terms/<ontology-id>_terms.tsv
# Usage: make data/pipeline/non-ols-terms/D3O.tsv
# Make calls robot directly with catalog to handle broken imports
# Python validates output
data/pipeline/non-ols-terms/%.tsv: external/ontologies/bioportal/%.owl sparql/extract_for_embeddings.rq
	@mkdir -p $(dir $@)
	@echo "Querying $* with ROBOT..."
	-@robot query --input $< --catalog catalog-v001.xml --query $(word 2,$^) $@ 2>&1 | tee -a .robot_query.log
	-@uv run validate-tsv $* --tsv $@

data/pipeline/non-ols-terms/%.tsv: external/ontologies/bioportal/%.ttl sparql/extract_for_embeddings.rq
	@mkdir -p $(dir $@)
	@echo "Querying $* with ROBOT..."
	-@robot query --input $< --catalog catalog-v001.xml --query $(word 2,$^) $@ 2>&1 | tee -a .robot_query.log
	-@uv run validate-tsv $* --tsv $@

# Manual ontologies (like n4l_merged.owl)
data/pipeline/non-ols-terms/%.tsv: external/ontologies/manual/%.owl sparql/extract_for_embeddings.rq
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

# ==============================================================================
# Definition Analysis Reports
# ==============================================================================
# These reports analyze definition coverage and quality in METPO.
# Most require the SSSOM mappings file from the alignment pipeline.

reports/definition_improvement_opportunities.tsv: src/templates/metpo_sheet.tsv notebooks/metpo_relevant_mappings.sssom.tsv
	uv run analyze-definition-opportunities \
		--template $< \
		--mappings $(word 2,$^) \
		--output $@

reports/definition_coverage_by_parent.tsv: src/templates/metpo_sheet.tsv
	uv run analyze-definition-coverage-by-subtree \
		--metpo-tsv $< \
		--output $@ \
		--sort-by stragglers

# Note: find-best-definitions requires chromadb optional dependency
# Install with: uv sync --extra notebooks
reports/best_definitions_per_term.tsv: src/templates/metpo_sheet.tsv
	uv run find-best-definitions \
		--metpo-tsv $< \
		--output $@

reports/definition_comparison_with_hierarchy.tsv: reports/best_definitions_per_term.tsv src/templates/metpo_sheet.tsv
	uv run compare-definitions-with-hierarchy \
		--best-definitions $< \
		--metpo-terms $(word 2,$^) \
		--output $@

.PHONY: definition-reports
definition-reports: reports/definition_improvement_opportunities.tsv reports/definition_coverage_by_parent.tsv
	@echo "Definition analysis reports generated"

.PHONY: clean-definition-reports
clean-definition-reports:
	rm -f reports/definition_improvement_opportunities.tsv
	rm -f reports/definition_coverage_by_parent.tsv
	rm -f reports/best_definitions_per_term.tsv
	rm -f reports/definition_comparison_with_hierarchy.tsv
	@echo "Definition reports cleaned"

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
import-bactotraits-metadata: metadata/databases/bactotraits/bactotraits_field_mappings.json metadata/databases/bactotraits/bactotraits_files.json
	jq '.mappings' metadata/databases/bactotraits/bactotraits_field_mappings.json | \
		mongoimport --db bactotraits --collection field_mappings \
		--jsonArray --drop
	mongoimport --db bactotraits --collection files \
		--file metadata/databases/bactotraits/bactotraits_files.json \
		--jsonArray --drop
	@echo "BactoTraits metadata collections imported"

.PHONY: import-madin-metadata
import-madin-metadata: metadata/databases/madin/madin_files.json
	mongoimport --db madin --collection files \
		--file metadata/databases/madin/madin_files.json \
		--jsonArray --drop
	@echo "Madin metadata collections imported"

reports/bactotraits-metpo-set-diff.yaml: metpo/bactotraits/bactotraits_metpo_set_difference.py reports/synonym-sources.tsv local/bactotraits/BactoTraits.tsv
	uv run bactotraits-metpo-set-difference \
		--bactotraits-file $(word 3, $^) \
		--synonyms-file $(word 2, $^) \
		--format yaml \
		--output $@

reports/bactotraits-metpo-reconciliation.yaml: metpo/bactotraits/reconcile_bactotraits_coverage.py reports/synonym-sources.tsv
	uv run reconcile-bactotraits-coverage \
		--mode field_names \
		--tsv $(word 2, $^) \
		--format yaml \
		--output $@

# BactoTraits field mappings - generates JSON and loads to MongoDB
metadata/databases/bactotraits/bactotraits_field_mappings.json: local/bactotraits/BactoTraits_databaseV2_Jun2022.csv local/bactotraits/BactoTraits.tsv
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
GID_MINIMAL_CLASSES = 121955004
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
download-all-bioportal-submissions: $(foreach sub,$(METPO_SUBMISSIONS),external/metpo_historical/metpo_submission_$(word 1,$(subst :, ,$(sub))).owl)
	@echo "All BiPortal METPO submissions downloaded to external/metpo_historical/"

# Individual submission download targets
external/metpo_historical/metpo_submission_%.owl: | external/metpo_historical
	@echo "Downloading METPO submission $*..."
	@curl -L -s "$(BIOPORTAL_SUBMISSION_BASE)/$*/download?apikey=$$BIOPORTAL_API_KEY" -o $@
	@if [ -s $@ ]; then \
		echo "✓ Successfully downloaded submission $*"; \
		grep -m1 "versionInfo" $@ || echo "No version info found"; \
	else \
		echo "✗ Failed to download submission $*"; \
		rm -f $@; \
	fi

# Ensure metpo_historical directory exists
external/metpo_historical:
	mkdir -p $@

# Clean downloaded BiPortal submissions

# =====================================================
# Non-OLS BioPortal Ontology Download Targets
# =====================================================



# List of external ontologies to process from BioPortal
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
NON_OLS_BIOPORTAL_ONTOLOGIES = D3O MPO OMP

.PHONY: download-external-bioportal-ontologies clean-external-bioportal-ontologies

download-external-bioportal-ontologies: $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),external/ontologies/bioportal/$(ont).owl)
	@echo ""
	@echo "=========================================="
	@echo "Download phase complete"
	@echo "=========================================="
	@echo "Run 'make scan-manifest' to update tracking"
	@echo "Run 'make view-logs' to see any failures"


# Download ontology from BioPortal
# Python script handles all error checking, logging, and validation
# Exit code 0 = success, 1 = failure
external/ontologies/bioportal/%.owl: | external/ontologies/bioportal
	-@uv run download-ontology $* --output $@

external/ontologies/bioportal/%.ttl: | external/ontologies/bioportal
	-@uv run download-ontology $* --output $@

external/ontologies/bioportal:
	mkdir -p $@

clean-external-bioportal-ontologies:
	@echo "Cleaning downloaded external BioPortal ontologies..."
	@echo "Keeping manually added files in external/ontologies/manual/"
	rm -f $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),external/ontologies/bioportal/$(ont).owl)
	@echo "Cleaned external BioPortal ontologies"

clean-external-pipeline:
	@echo "Cleaning pipeline-generated files (keeping manual downloads)..."
	@echo "Removing BioPortal downloads..."
	rm -f $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),external/ontologies/bioportal/$(ont).owl)
	@echo "Removing ROBOT query outputs..."
	rm -f data/pipeline/non-ols-terms/*.tsv
	@echo "Removing logs and manifest..."
	rm -f .ontology_manifest.json .ontology_fetch.log .robot_query.log
	@echo ""
	@echo "✓ Cleaned pipeline files"
	@echo "✓ Kept manual files: external/ontologies/manual/n4l_merged.owl"

clean-bioportal-submissions:
	rm -rf external/metpo_historical/
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
	@echo "To download specific submission: make external/metpo_historical/metpo_submission_5.owl"

# =====================================================
# METPO Entity Extraction Targets
# =====================================================

.PHONY: extract-all-metpo-entities clean-entity-extracts

# Extract METPO entities from all submissions
extract-all-metpo-entities: $(foreach sub,$(METPO_SUBMISSIONS),metadata/ontology/historical_submissions/entity_extracts/metpo_submission_$(word 1,$(subst :, ,$(sub)))_all_entities.tsv)
	@echo "All METPO entities extracted to metadata/ontology/historical_submissions/entity_extracts/"

# Individual entity extraction targets
metadata/ontology/historical_submissions/entity_extracts/metpo_submission_%_all_entities.tsv: external/metpo_historical/metpo_submission_%.owl | metadata/ontology/historical_submissions/entity_extracts
	@echo "Extracting entities from METPO submission $*..."
	robot query -i $< -s sparql/query_metpo_entities.sparql $@

# Ensure entity_extracts directory exists
metadata/ontology/historical_submissions/entity_extracts:
	mkdir -p $@

# Clean extracted entity files
clean-entity-extracts:
	rm -rf metadata/ontology/historical_submissions/entity_extracts/
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

notebooks/ontology_catalog.csv: data/ontology_assessments/ontology_sizes.csv
	@echo "Fetching ontology metadata from OLS4 API..."
	uv run python metpo/pipeline/fetch_ontology_names.py \
		--sizes-csv data/ontology_assessments/ontology_sizes.csv \
		--output-csv notebooks/ontology_catalog.csv

alignment-categorize-ontologies: notebooks/ontologies_very_appealing.csv

notebooks/ontologies_very_appealing.csv: notebooks/ontology_catalog.csv
	@echo "Categorizing ontologies by relevance..."
	uv run python metpo/pipeline/categorize_ontologies.py \
		--input-csv notebooks/ontology_catalog.csv \
		--output-prefix notebooks/ontologies

alignment-query-metpo-terms: notebooks/metpo_relevant_mappings.sssom.tsv

notebooks/metpo_relevant_mappings.sssom.tsv: notebooks/metpo_relevant_chroma
	@echo "Generating SSSOM mappings from METPO terms via ChromaDB..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "ERROR: OPENAI_API_KEY environment variable not set"; \
		exit 1; \
	fi
	uv run python metpo/pipeline/chromadb_semantic_mapper.py \
		--metpo-tsv src/templates/metpo_sheet.tsv \
		--chroma-path notebooks/metpo_relevant_chroma \
		--collection-name metpo_relevant_embeddings \
		--output notebooks/metpo_relevant_mappings.sssom.tsv \
		--top-n 10 \
		--label-only \
		--distance-cutoff 0.35

alignment-analyze-matches: notebooks/metpo_relevant_mappings.sssom.tsv
	@echo "Analyzing match quality..."
	uv run python metpo/pipeline/analyze_matches.py \
		--input-csv notebooks/metpo_relevant_mappings.sssom.tsv \
		--good-match-threshold 0.9

alignment-analyze-coherence: notebooks/full_coherence_results.csv

notebooks/full_coherence_results.csv: notebooks/metpo_relevant_mappings.sssom.tsv
	@echo "Computing structural coherence (this may take a while)..."
	uv run python metpo/pipeline/analyze_sibling_coherence.py \
		--input-csv notebooks/metpo_relevant_mappings.sssom.tsv \
		--metpo-owl src/ontology/metpo.owl \
		--output-csv notebooks/full_coherence_results.csv

alignment-identify-candidates: notebooks/alignment_candidates.csv

notebooks/alignment_candidates.csv: notebooks/full_coherence_results.csv
	@echo "Identifying alignment candidates..."
	uv run python metpo/pipeline/analyze_coherence_results.py \
		--results-csv notebooks/full_coherence_results.csv \
		--matches-csv notebooks/metpo_relevant_mappings.sssom.tsv

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

NON_OLS_TSV_FILES = $(foreach ont,$(NON_OLS_BIOPORTAL_ONTOLOGIES),data/pipeline/non-ols-terms/$(ont).tsv)

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
	uv run python metpo/pipeline/embed_ontology_to_chromadb.py \
		$(foreach tsv,$(wildcard data/pipeline/non-ols-terms/*.tsv),--tsv-file $(tsv)) \
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

# ==============================================================================
# Sub-Makefile Integration
# ==============================================================================
# Literature mining (including ICBO examples) has its own Makefile.
# Run from root using: make -C literature_mining <target>
#
# Examples:
#   make -C literature_mining help
#   make -C literature_mining pmids SOURCE=ijsem
#   make -C literature_mining extract TEMPLATE=growth_conditions
#   make -C literature_mining icbo-phenotypes
#   make -C literature_mining icbo-chemicals
#   make -C literature_mining icbo-analyze
#
# See literature_mining/Makefile for full documentation.
# ==============================================================================
