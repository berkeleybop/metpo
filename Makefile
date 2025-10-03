WGET=wget
UNZIP=unzip

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
	rm -f generated/bacdive_oxygen_phenotype_mappings.tsv
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

generated/bacdive_oxygen_phenotype_mappings.tsv: sparql/bacdive_oxygen_phenotype_mappings.rq src/ontology/metpo.owl
	mkdir -p $(dir $@)
	robot query \
		--query $(word 1,$^) $@ \
		--input $(word 2,$^)

# =====================================================
# Google Sheets Download Targets
# =====================================================

# Default spreadsheet ID (from metpo.Makefile)
SPREADSHEET_ID = 1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU
BASE_URL = https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export

# All sheet gids discovered via Google Apps Script (9 total sheets)
GID_MINIMAL_CLASSES = 355012485
GID_PROPERTIES = 2094089867
GID_BACTOTRAITS = 1192666692
GID_MORE_SYNONYMS = 907926993
GID_MORE_CLASSES = 1427185859
GID_METABOLIC_AND_RESPIRATORY = 499077032
GID_TROPHIC_MAPPING_BACDIVE__TBDELETED = 44169923
GID_ATTIC_CLASSES = 1347388120
GID_ATTIC_PROPERTIES = 565614186

.PHONY: download-all-sheets clean-sheets

# Download all discovered sheets to downloads/sheets/
download-all-sheets: downloads/sheets/minimal_classes.tsv downloads/sheets/properties.tsv downloads/sheets/bactotraits.tsv downloads/sheets/more_synonyms.tsv downloads/sheets/more_classes.tsv downloads/sheets/metabolic_and_respiratory.tsv downloads/sheets/trophic_mapping_bacdive__tbdeleted.tsv downloads/sheets/attic_classes.tsv downloads/sheets/attic_properties.tsv
	@echo "All 9 sheets downloaded to downloads/sheets/"

# Individual sheet download targets
downloads/sheets/minimal_classes.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MINIMAL_CLASSES)' > $@

downloads/sheets/properties.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_PROPERTIES)' > $@

downloads/sheets/bactotraits.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_BACTOTRAITS)' > $@

downloads/sheets/more_synonyms.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MORE_SYNONYMS)' > $@

downloads/sheets/more_classes.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_MORE_CLASSES)' > $@

downloads/sheets/metabolic_and_respiratory.tsv: | downloads/sheets
	curl -L -s '$(BASE_URL)?exportFormat=tsv&gid=$(GID_METABOLIC_AND_RESPIRATORY)' > $@

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
BIOPORTAL_API_KEY = 8b5b7825-538d-40e0-9e9e-5ab9274a9aeb
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
	@curl -L -s "$(BIOPORTAL_SUBMISSION_BASE)/$*/download?apikey=$(BIOPORTAL_API_KEY)" -o $@
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
