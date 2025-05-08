#
#local/salinity_parsed_llm.tsv: metpo/salinity_raw_text_input.csv local/.env
#	poetry run python metpo/parse_salinity_llm.py \
#		--input-csv $< \
#		--output-tsv $@ \
#		--env-file local/.env \
#		--batch-size 40 \
#		--max-rows 400

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

## Parse temperature text from CSV into structured RDF
##local/n4l-temperature.ttl: local/n4l-temperature.csv
##	poetry run parse-temperatures --input $< --output $@ --format turtle

.PHONY: clean-temperature              # ⇐  phony so it always runs
clean-temperature:
	@echo "→ removing generated temperature artefacts …"
	rm -rf local/n4l-temperature.csv \
		local/n4l-temperature.ttl \
		local/flattened_n4l_temperature_components.tsv

# ------------------------------------------------------------------
# GraphDB connection parameters
ENDPOINT = http://localhost:7200/repositories/n4l_tables

ACCEPT   = text/csv

local/n4l-temperature.csv: sparql/temperature_query.rq
	@echo "→ querying GraphDB ($(ENDPOINT)) …"
	curl -f -X POST \
	     -H "Content-Type: application/sparql-query" \
	     -H "Accept: text/csv"          \
	     --data-binary @$<      \
	     $(ENDPOINT) > $@

# Parse temperature text from CSV into structured RDF
local/n4l-temperature.ttl: local/n4l-temperature.csv
	poetry run python metpo/regex_parse_n4l_temperatures_2.py $< > $@

# Flatten parsed temperature components into simplified triples
local/flattened_n4l_temperature_components.tsv: local/n4l-temperature.ttl sparql/flatten_n4l_parsing_components.rq
	robot query --input $(word 1,$^) --query $(word 2,$^) $@
