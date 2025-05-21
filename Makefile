WGET=wget
UNZIP=unzip

# see https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt regarding nodes.dmp

downloads/taxdmp.zip:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"

local/taxdmp: downloads/taxdmp.zip
	$(UNZIP) $< -d $@

local/taxdmp/nodes.dmp: local/taxdmp

# Extract taxonomy rank triples from NCBI nodes.dmp file to a TTL file
local/noderanks.ttl: local/taxdmp/nodes.dmp
	poetry run extract-rank-triples --input-file $< --output-file $@

local/n4l-tables.nq: \
    assets/N4L_phenotypic_ontology_2016/ \
    assets/n4l-xlsx-parsing-config.tsv \
    assets/n4l_predicate_mapping_normalization.csv \
    metpo/n4l_tables_to_quads.ipynb
	@echo "▶️ Running n4l_tables_to_quads.ipynb..."
	papermill metpo/n4l_tables_to_quads.ipynb metpo/n4l_tables_to_quads.ran.ipynb \
	  --cwd $(CURDIR)

local/categorized_temperature_range_assignments.tsv: metpo/categorize_temperature_ranges.ipynb \
  local/metpo_classes_temperature_limits.csv \
  local/flattened_n4l_temperature_components.tsv
	papermill metpo/categorize_temperature_ranges.ipynb \
	  metpo/categorize_temperature_ranges.ran.ipynb \
	  --cwd $(CURDIR)

.PHONY: categorized-temperature-assignments
categorized-temperature-assignments: local/categorized_temperature_range_assignments.tsv

local/n4l-temperature.ttl: \
    local/n4l-temperature.csv \
    metpo/classify_temperature_values.ipynb
	@echo "▶️ Running classify_temperature_values.ipynb..."
	papermill metpo/classify_temperature_values.ipynb metpo/classify_temperature_values.ran.ipynb \
	  --cwd $(CURDIR)

.PHONY: n4l-pipeline

n4l-pipeline: \
	n4l-clean \
	local/n4l-tables.nq \
	create-repo \
	load-nquads \
	delete_most_0_value_triples \
	direct_ncbitaxid_same_as \
	property_hierarchy \
	shared_nm_id_same_as \
	load-metpo \
	local/noderanks.ttl \
	load-taxon-ranks \
	local/n4l-temperature.csv \
	local/n4l-temperature.ttl \
	load-temperatures-parsed \
	local/metpo_classes_temperature_limits.csv \
	local/flattened_n4l_temperature_components.tsv \
	local/categorized_temperature_range_assignments.tsv

include graphdb.Makefile
