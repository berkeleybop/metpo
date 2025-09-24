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
