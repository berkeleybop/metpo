GRAPHDB_HOST := http://localhost:7200
REPO_NAME := metpo_n4l_etc_automated
REPO_CONFIG_TTL := config/$(REPO_NAME).ttl
DATA_FILE := local/n4l-tables.nq
CURL_OPTS := -s -H "Accept: application/json" --connect-timeout 3
METPO_OWL_URL := https://w3id.org/metpo/metpo/releases/2025-04-25/metpo.owl
METPO_GRAPH_URI := <https://w3id.org/metpo/metpo/releases/2025-04-25/metpo.owl>

SHELL := /bin/bash

.PHONY: all check-graphdb-online check-repo-exists create-repo load-nquads

all: create-repo

check-graphdb-online:
	@echo "Checking if GraphDB is online at $(GRAPHDB_HOST)..."
	@curl $(CURL_OPTS) $(GRAPHDB_HOST)/rest/repositories > /dev/null 2>&1; \
	if [ $$? -ne 0 ]; then \
		echo "❌ GraphDB is not accessible"; \
		exit 1; \
	else \
		echo "✅ GraphDB is online"; \
	fi

check-repo-exists: check-graphdb-online
	@echo "Checking for repository '$(REPO_NAME)'..."
	@repos_json=$$(curl $(CURL_OPTS) $(GRAPHDB_HOST)/rest/repositories); \
	if echo "$$repos_json" | jq -e '.[] | select(.id == "$(REPO_NAME)")' > /dev/null; then \
		echo "✅ Repository '$(REPO_NAME)' exists"; \
	else \
		echo "❌ Repository '$(REPO_NAME)' not found"; \
		exit 2; \
	fi

create-repo: check-graphdb-online
	@echo "Checking if repository '$(REPO_NAME)' exists before attempting creation..."
	@repos_json=$$(curl $(CURL_OPTS) $(GRAPHDB_HOST)/rest/repositories); \
	if echo "$$repos_json" | jq -e '.[] | select(.id == "$(REPO_NAME)")' > /dev/null; then \
		echo "✅ Repository '$(REPO_NAME)' already exists. Skipping creation."; \
	else \
		echo "🛠️ Creating repository '$(REPO_NAME)' from $(REPO_CONFIG_TTL)..."; \
		curl -i -X POST \
		     -F "config=@$(REPO_CONFIG_TTL);type=application/x-turtle" \
		     $(GRAPHDB_HOST)/rest/repositories; \
		sleep 1; \
		new_repos_json=$$(curl $(CURL_OPTS) $(GRAPHDB_HOST)/rest/repositories); \
		if echo "$$new_repos_json" | jq -e '.[] | select(.id == "$(REPO_NAME)")' > /dev/null; then \
			echo "✅ Repository '$(REPO_NAME)' created and confirmed registered."; \
		else \
			echo "❌ Repository '$(REPO_NAME)' creation failed or did not register."; \
			exit 3; \
		fi; \
	fi

load-nquads: check-repo-exists
	@echo "🔄 Streaming RDF data from $(DATA_FILE) to repository '$(REPO_NAME)'..."
	@curl -X PUT \
	  -H "Content-Type: application/n-quads" \
	  --data-binary @$(DATA_FILE) \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements


delete_most_0_value_triples: sparql/delete_most_0_value_triples.ru  # check-repo-exists
	@echo "✍️  Running SPARQL UPDATE from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-update" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements

direct_ncbitaxid_same_as: sparql/direct_ncbitaxid_same_as.ru
	@echo "✍️  Running SPARQL UPDATE from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-update" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements

property_hierarchy: sparql/property_hierarchy.ru
	@echo "✍️  Running SPARQL UPDATE from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-update" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements

shared_nm_id_same_as: sparql/shared_nm_id_same_as.ru
	@echo "✍️  Running SPARQL UPDATE from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-update" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements

load-metpo: metpo.owl
	@echo "📌 Forcing load into named graph <https://w3id.org/metpo/metpo/releases/2025-04-25/metpo.owl> using PUT with context..."
	@curl -s -X PUT \
	  -H "Content-Type: application/rdf+xml" \
	  --data-binary @$< \
	  "$(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements?context=%3Chttps%3A%2F%2Fw3id.org%2Fmetpo%2Fmetpo%2Freleases%2F2025-04-25%2Fmetpo.owl%3E"

load-taxon-ranks: local/noderanks.ttl
	@echo "📦 Loading taxon rank triples into graph <http://purl.obolibrary.org/obo/ncbitaxon#has_rank>..."
	@curl -s -X PUT \
	  -H "Content-Type: text/turtle" \
	  --data-binary @$< \
	  "$(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements?context=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2Fncbitaxon%23has_rank%3E"

local/n4l-temperature.csv: sparql/temperature_query.rq
	@echo "🔎 Running SPARQL SELECT from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-query" \
	  -H "Accept: text/csv" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME) > $@

load-temperatures-parsed: local/n4l-temperature.ttl
	@echo "📦 Loading temperature RDF into named graph..."
	curl -s -X PUT \
	  -H "Content-Type: text/turtle" \
	  --data-binary @$< \
	  "$(GRAPHDB_HOST)/repositories/$(REPO_NAME)/statements?context=%3Chttp%3A%2F%2Fexample.com%2Fn4l_temperatures_parsed%3E"

local/flattened_n4l_temperature_components.tsv: sparql/flatten_n4l_parsing_components.rq
	@echo "🔎 Running SPARQL SELECT from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-query" \
	  -H "Accept: text/tab-separated-values" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME) > $@

.PHONY: n4l-clean

n4l-clean:
	@echo "🧹 Removing generated local files..."
	rm -f \
		local/categorized_temperature_range_assignments.tsv \
		local/categorized_temperature_range_summary.tsv \
		local/flattened_n4l_temperature_components.tsv \
		local/metpo_classes_temperature_limits.csv \
		local/n4l-tables.nq \
		local/n4l-temperature-un-parsed.csv \
		local/n4l-temperature.csv \
		local/n4l-temperature.ttl \
		local/noderanks.ttl \
		metpo/categorize_temperature_ranges.ran.ipynb \
		metpo/classify_temperature_values.ran.ipynb \
		metpo/n4l_tables_to_quads.ran.ipynb

	@echo "💥 Dropping GraphDB repository '$(REPO_NAME)'..."
	curl -s -X DELETE "$(GRAPHDB_HOST)/rest/repositories/$(REPO_NAME)"

local/metpo_classes_temperature_limits.csv: sparql/metpo_classes_temperature_limits.rq
	@echo "🔎 Running SPARQL SELECT from $< on repository '$(REPO_NAME)'..."
	@curl -s -X POST \
	  -H "Content-Type: application/sparql-query" \
	  -H "Accept: text/csv" \
	  --data-binary @$< \
	  $(GRAPHDB_HOST)/repositories/$(REPO_NAME) > $@