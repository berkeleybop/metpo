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
