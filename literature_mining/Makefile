# METPO Literature Mining Pipeline - Simplified Makefile
# Core targets focused on essential workflow steps

# Configuration
N_PMIDS ?= 10
N_ABSTRACTS ?= 5
SOURCE ?= ijsem
TEMPLATE ?= growth_conditions
MODEL ?= gpt-4o
INPUT_DIR ?= abstracts/test-taxa-minimal

# Core directories
DIRS := inputs intermediates templates abstracts outputs logs assessments cache
TIMESTAMP := $(shell date +"%Y%m%d_%H%M%S")

.PHONY: help setup pmids abstracts intermediates templates validate-templates extract assess clean

help:
	@echo "METPO Literature Mining Pipeline"
	@echo ""
	@echo "Core Workflow:"
	@echo "  pmids          - Get PMIDs from different sources"
	@echo "  abstracts      - Fetch abstracts from PMID lists"
	@echo "  intermediates  - Build intermediate files (METPO DB, chem predicates)"
	@echo "  templates      - Update templates with chemical predicates"
	@echo "  validate       - Validate templates as LinkML schemas"
	@echo "  extract        - Run timestamped extraction and assessment"
	@echo "  benchmark      - Unix-style benchmark (Make + Python calculator)"
	@echo "  benchmark-extract - Run extraction with performance/cost tracking (old bash)"
	@echo "  assess         - Assess templates and extractions"
	@echo "  clean          - Cleanup with different levels"
	@echo "  clean-workspace - Remove working files (preserve outputs/abstracts)"
	@echo ""
	@echo "Parameters: SOURCE=$(SOURCE) TEMPLATE=$(TEMPLATE) MODEL=$(MODEL) INPUT_DIR=$(INPUT_DIR) N_PMIDS=$(N_PMIDS) N_ABSTRACTS=$(N_ABSTRACTS)"
	@echo ""
	@echo "Sources: n4l, bacdive, ijsem | Templates: growth_conditions, chemical_utilization, taxa, morphology, biochemical"

# =============================================================================
# SETUP
# =============================================================================

setup: $(DIRS)
	@echo "✅ Directory structure created"

$(DIRS):
	mkdir -p $@

# =============================================================================
# 1. PMID SOURCES
# =============================================================================

pmids: inputs/random-$(SOURCE)-pmids.txt

inputs/random-n4l-pmids.txt: inputs/n4l/reference_id_mapping.csv | inputs
	cut -f3 -d, $< | sort | uniq | grep '^[0-9]*$$' | shuf -n $(N_PMIDS) > $@

inputs/random-bacdive-pmids.txt: | inputs
	mongosh --quiet bacdive --eval "db.strains_api.aggregate([{\$$unwind: '\$$External links.literature'}, {\$$match: {'External links.literature.Pubmed-ID': {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$group: {_id: '\$$External links.literature.Pubmed-ID'}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc._id); })" > $@

inputs/random-ijsem-pmids.txt: | inputs
	mongosh --quiet europepmc --eval "db.ijsem_articles.aggregate([{\$$match: {pmid: {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc.pmid); })" > $@

# =============================================================================
# 2. ABSTRACT FETCHING
# =============================================================================

PMID_LIST ?= inputs/random-$(SOURCE)-pmids.txt
ABSTRACT_DIR ?= abstracts

abstracts: abstracts-$(SOURCE)

abstracts-$(SOURCE): $(PMID_LIST) | $(ABSTRACT_DIR)
	@echo "📄 Fetching $(N_ABSTRACTS) abstracts from $(PMID_LIST) into $(ABSTRACT_DIR)..."
	head -n $(N_ABSTRACTS) $< | while read pmid; do \
		if [ ! -f "$(ABSTRACT_DIR)/$$pmid-abstract.txt" ]; then \
			echo "Fetching PMID $$pmid"; \
			uv run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "$(ABSTRACT_DIR)/$$pmid-abstract.txt" 2>/dev/null || rm -f "$(ABSTRACT_DIR)/$$pmid-abstract.txt"; \
		fi; \
	done

# =============================================================================
# 3. INTERMEDIATE FILES
# =============================================================================

intermediates: intermediates/db/metpo.db intermediates/yaml/chem_interaction_props_enum.yaml

# METPO database
intermediates/db/metpo.db: ../src/ontology/metpo.owl
	@echo "🗄️ Building METPO database from src/ontology..."
	mkdir -p intermediates/db
	cp $< intermediates/db/metpo.owl
	cd intermediates/db && uv run semsql make metpo.db
	rm -f intermediates/db/metpo.owl intermediates/db/metpo-relation-graph.tsv.gz

# Chemical utilization predicates (ONLY for chemical_utilization template)
intermediates/tsv/chem_interaction_props.tsv: ../src/ontology/metpo.owl
	mkdir -p intermediates/tsv
	robot query --query sparql/chem_interaction_props.rq $@ --input $<

intermediates/yaml/chem_interaction_props_enum.yaml: intermediates/tsv/chem_interaction_props.tsv
	mkdir -p intermediates/yaml
	uv run convert-chem-props -i $< -o $@

# =============================================================================
# 4. TEMPLATE UPDATES
# =============================================================================

templates: templates/$(TEMPLATE)_populated.yaml

# Most templates are static copies
templates/growth_conditions_populated.yaml: templates/growth_conditions_template_base.yaml
	cp $< $@

templates/taxa_populated.yaml: templates/taxa_template_base.yaml
	cp $< $@

templates/morphology_populated.yaml: templates/morphology_template_base.yaml
	cp $< $@

templates/biochemical_populated.yaml: templates/biochemical_template_base.yaml
	cp $< $@

# ONLY chemical_utilization gets METPO predicates injected
templates/chemical_utilization_populated.yaml: templates/chemical_utilization_template_base.yaml intermediates/yaml/chem_interaction_props_enum.yaml
	@echo "💉 Injecting METPO chemical predicates into chemical_utilization template..."
	yq eval-all 'select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base' $^ > $@.tmp
	yq '.classes.ChemicalUtilization.attributes.predicate.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

# =============================================================================
# 5. TEMPLATE VALIDATION
# =============================================================================

validate: validate-templates

validate-templates: templates/growth_conditions_template_base.yaml templates/chemical_utilization_template_base.yaml templates/taxa_template_base.yaml templates/morphology_template_base.yaml templates/biochemical_template_base.yaml
	@echo "✅ Validating LinkML template schemas..."
	uv run linkml validate --schema templates/growth_conditions_template_base.yaml
	uv run linkml validate --schema templates/chemical_utilization_template_base.yaml  
	uv run linkml validate --schema templates/taxa_template_base.yaml
	uv run linkml validate --schema templates/morphology_template_base.yaml
	uv run linkml validate --schema templates/biochemical_template_base.yaml
	@echo "All templates validated ✅"

# =============================================================================
# 6. CURATED ABSTRACT COLLECTIONS
# =============================================================================

# Create template-specific abstract collections that don't change often
setup-curated-abstracts:
	@echo "📂 Setting up curated abstract collections..."
	mkdir -p abstracts/biochemical-rich abstracts/chemical-rich abstracts/growth-rich abstracts/morphology-rich abstracts/taxa-rich
	@echo "Add manually curated abstracts to abstracts/*-rich/ directories"
	@echo "These should be re-evaluated periodically but remain stable"

# =============================================================================
# 7. EXTRACTION WITH TIMESTAMPED OUTPUT
# =============================================================================

extract: outputs/$(TEMPLATE)_$(TIMESTAMP).yaml

outputs/$(TEMPLATE)_$(TIMESTAMP).yaml: templates/$(TEMPLATE)_populated.yaml intermediates/db/metpo.db | outputs logs
	@echo "🚀 Running timestamped extraction: $(TEMPLATE) at $(TIMESTAMP)"
	@input_dir="abstracts"; \
	if [ -d "abstracts/$(TEMPLATE)-rich" ] && [ $$(ls "abstracts/$(TEMPLATE)-rich"/*.txt 2>/dev/null | wc -l) -gt 0 ]; then \
		input_dir="abstracts/$(TEMPLATE)-rich"; \
		echo "Using curated abstracts: $$input_dir"; \
	else \
		echo "Using general abstracts: $$input_dir"; \
	fi; \
	uv run ontogpt -vv \
		--cache-db cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $< \
		-i $$input_dir \
		-o $@ \
		2>&1 | tee logs/$(TEMPLATE)_$(TIMESTAMP).log

# Benchmarked extraction with performance metrics (old bash version)
benchmark-extract: scripts/benchmark_extraction.sh | outputs logs
	@echo "🔬 Running benchmarked extraction with performance tracking..."
	@if [ ! -x scripts/benchmark_extraction.sh ]; then \
		chmod +x scripts/benchmark_extraction.sh; \
	fi
	./scripts/benchmark_extraction.sh $(TEMPLATE) $(MODEL) $(INPUT_DIR)

# Unix-philosophy benchmark: shell tools + pure Python calculator
BENCH_LOG_FILE ?= extraction_benchmarks.tsv
BENCH_TIMESTAMP := $(shell date +"%Y%m%d_%H%M%S")
BENCH_OUTPUT := outputs/$(TEMPLATE)_$(shell echo $(MODEL) | tr '/' '_')_$(BENCH_TIMESTAMP).yaml
BENCH_EXTRACT_LOG := logs/$(TEMPLATE)_$(shell echo $(MODEL) | tr '/' '_')_$(BENCH_TIMESTAMP).log
SYSTEM_MSG := "You are a precise data extraction system. Output ONLY the requested fields in the exact format specified. Do not add explanations, preambles, notes, or any other text. If a field has no value, write 'none' after the colon. Never leave a field completely empty."

benchmark: | outputs logs
	@echo "=========================================="
	@echo "OntoGPT Extraction Benchmark"
	@echo "=========================================="
	@echo "Template: $(TEMPLATE)"
	@echo "Model: $(MODEL)"
	@echo "Input: $(INPUT_DIR)"
	@echo "Timestamp: $(BENCH_TIMESTAMP)"
	@echo ""
	@# Validate
	@if [ ! -f "templates/$(TEMPLATE)_template_base.yaml" ]; then echo "ERROR: Template not found"; exit 1; fi
	@if [ ! -d "$(INPUT_DIR)" ]; then echo "ERROR: Input dir not found"; exit 1; fi
	@if [ -z "$$OPENAI_API_KEY" ]; then echo "ERROR: OPENAI_API_KEY not set"; exit 1; fi
	@# Collect stats
	@echo "Collecting input statistics..."
	@NUM_ABSTRACTS=$$(ls -1 $(INPUT_DIR)/*.txt 2>/dev/null | wc -l | tr -d ' '); \
	TOTAL_CHARS=$$(cat $(INPUT_DIR)/*.txt 2>/dev/null | wc -c | tr -d ' '); \
	TOTAL_WORDS=$$(cat $(INPUT_DIR)/*.txt 2>/dev/null | wc -w | tr -d ' '); \
	AVG_CHARS=$$(($$TOTAL_CHARS / $$NUM_ABSTRACTS)); \
	AVG_WORDS=$$(($$TOTAL_WORDS / $$NUM_ABSTRACTS)); \
	echo "  Abstracts: $$NUM_ABSTRACTS"; \
	echo "  Total chars: $$TOTAL_CHARS"; \
	echo "  Avg chars/abstract: $$AVG_CHARS"; \
	echo "  Total words: $$TOTAL_WORDS"; \
	echo "  Avg words/abstract: $$AVG_WORDS"; \
	echo ""; \
	echo "Querying CBORG account info (before)..."; \
	USER_INFO=$$(curl -s https://api.cborg.lbl.gov/user/info -H "Authorization: Bearer $$OPENAI_API_KEY"); \
	KEY_INFO=$$(curl -s https://api.cborg.lbl.gov/key/info -H "Authorization: Bearer $$OPENAI_API_KEY"); \
	KEY_OWNER=$$(echo "$$USER_INFO" | jq -r '.user_id // "unknown"'); \
	KEY_NAME=$$(echo "$$KEY_INFO" | jq -r '.info.key_name // "unknown"'); \
	MAX_BUDGET=$$(echo "$$USER_INFO" | jq -r '.user_info.max_budget // 0'); \
	SPEND_BEFORE=$$(echo "$$USER_INFO" | jq -r '.user_info.spend // 0'); \
	BUDGET_REMAINING=$$(echo "$$MAX_BUDGET - $$SPEND_BEFORE" | bc); \
	echo "  Key owner: $$KEY_OWNER"; \
	echo "  Key name: $$KEY_NAME"; \
	echo "  Max budget: \$$$$MAX_BUDGET"; \
	echo "  Spend before: \$$$$SPEND_BEFORE"; \
	echo "  Budget remaining: \$$$$BUDGET_REMAINING"; \
	echo ""; \
	echo "Running extraction..."; \
	START_TIME=$$(date +%s); \
	LITELLM_LOG=ERROR uv run ontogpt -vv extract \
		-t templates/$(TEMPLATE)_populated.yaml \
		-i $(INPUT_DIR) \
		-o $(BENCH_OUTPUT) \
		-m $(MODEL) \
		--model-provider openai \
		--api-base "https://api.cborg.lbl.gov" \
		--set-slot-value source_text= \
		--system-message $(SYSTEM_MSG) \
		> $(BENCH_EXTRACT_LOG) 2>&1 || true; \
	END_TIME=$$(date +%s); \
	DURATION=$$(($$END_TIME - $$START_TIME)); \
	echo ""; \
	echo "Extraction completed in $${DURATION}s"; \
	echo ""; \
	echo "Querying CBORG spend (after)..."; \
	USER_INFO_AFTER=$$(curl -s https://api.cborg.lbl.gov/user/info -H "Authorization: Bearer $$OPENAI_API_KEY"); \
	SPEND_AFTER=$$(echo "$$USER_INFO_AFTER" | jq -r '.user_info.spend // 0'); \
	COST=$$(echo "$$SPEND_AFTER - $$SPEND_BEFORE" | bc); \
	echo "  Spend after: \$$$$SPEND_AFTER"; \
	echo "  Cost: \$$$$COST"; \
	echo ""; \
	echo "Parsing log for input size..."; \
	TOTAL_INPUT_CHARS=$$(grep -o 'prompt\[[0-9]*\]' $(BENCH_EXTRACT_LOG) 2>/dev/null | sed 's/prompt\[\([0-9]*\)\]/\1/' | awk '{sum+=$$1} END {if (sum) print sum; else print 1}'); \
	NUM_API_CALLS=$$(grep -c 'prompt\[' $(BENCH_EXTRACT_LOG) 2>/dev/null || echo "0"); \
	echo "  Total input chars: $$TOTAL_INPUT_CHARS (across $$NUM_API_CALLS API calls)"; \
	echo ""; \
	echo "Analyzing extraction results..."; \
	if [ -f "$(BENCH_OUTPUT)" ]; then \
		COUNTS=$$(uv run python scripts/count_extraction_results.py --json $(BENCH_OUTPUT)); \
		ENTITIES=$$(echo "$$COUNTS" | jq -r '.entities'); \
		RELATIONSHIPS=$$(echo "$$COUNTS" | jq -r '.relationships'); \
		echo "  Entities: $$ENTITIES"; \
		echo "  Relationships: $$RELATIONSHIPS"; \
	else \
		echo "  WARNING: Output file not found!"; \
		ENTITIES=0; \
		RELATIONSHIPS=0; \
	fi; \
	echo ""; \
	echo "Calculating metrics..."; \
	METRICS=$$(./scripts/calculate_metrics.py \
		--cost $$COST \
		--abstracts $$NUM_ABSTRACTS \
		--abstract-chars $$TOTAL_CHARS \
		--input-chars $$TOTAL_INPUT_CHARS \
		--duration $$DURATION \
		--entities $$ENTITIES \
		--relationships $$RELATIONSHIPS); \
	COST_PER_ABSTRACT=$$(echo "$$METRICS" | jq -r '.cost_per_abstract'); \
	COST_PER_1K_ABSTRACT=$$(echo "$$METRICS" | jq -r '.cost_per_1k_abstract_chars'); \
	COST_PER_1K_INPUT=$$(echo "$$METRICS" | jq -r '.cost_per_1k_input_chars'); \
	TIME_PER_ABSTRACT=$$(echo "$$METRICS" | jq -r '.time_per_abstract'); \
	TIME_PER_1K_INPUT=$$(echo "$$METRICS" | jq -r '.time_per_1k_input_chars'); \
	ENTITIES_PER_1K=$$(echo "$$METRICS" | jq -r '.entities_per_1k_input'); \
	RELATIONSHIPS_PER_1K=$$(echo "$$METRICS" | jq -r '.relationships_per_1k_input'); \
	echo ""; \
	echo "Logging results to $(BENCH_LOG_FILE)..."; \
	if [ ! -f "$(BENCH_LOG_FILE)" ]; then \
		printf "timestamp\ttemplate\tmodel\tkey_owner\tkey_name\tmax_budget\tbudget_remaining\tnum_abstracts\ttotal_abstract_chars\tavg_abstract_chars\ttotal_words\tavg_words\ttotal_input_chars\tnum_api_calls\ttotal_cost\tcost_per_abstract\tcost_per_1k_abstract_chars\tcost_per_1k_input_chars\ttotal_time_sec\ttime_per_abstract\ttime_per_1k_input_chars\tentities\trelationships\tentities_per_1k_input\trelationships_per_1k_input\toutput_file\tlog_file\n" > $(BENCH_LOG_FILE); \
	fi; \
	printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
		"$(BENCH_TIMESTAMP)" "$(TEMPLATE)" "$(MODEL)" "$$KEY_OWNER" "$$KEY_NAME" "$$MAX_BUDGET" "$$BUDGET_REMAINING" \
		"$$NUM_ABSTRACTS" "$$TOTAL_CHARS" "$$AVG_CHARS" "$$TOTAL_WORDS" "$$AVG_WORDS" "$$TOTAL_INPUT_CHARS" \
		"$$NUM_API_CALLS" "$$COST" "$$COST_PER_ABSTRACT" "$$COST_PER_1K_ABSTRACT" "$$COST_PER_1K_INPUT" \
		"$$DURATION" "$$TIME_PER_ABSTRACT" "$$TIME_PER_1K_INPUT" "$$ENTITIES" "$$RELATIONSHIPS" \
		"$$ENTITIES_PER_1K" "$$RELATIONSHIPS_PER_1K" "$(BENCH_OUTPUT)" "$(BENCH_EXTRACT_LOG)" \
		>> $(BENCH_LOG_FILE); \
	echo ""; \
	echo "✅ Benchmark complete!"; \
	echo ""; \
	echo "Summary:"; \
	echo "  Abstracts: $$NUM_ABSTRACTS ($$TOTAL_CHARS chars, $$TOTAL_INPUT_CHARS input chars across $$NUM_API_CALLS API calls)"; \
	echo "  Cost: \$$$$COST"; \
	echo "    - \$$$$COST_PER_ABSTRACT/abstract"; \
	echo "    - \$$$$COST_PER_1K_ABSTRACT/1K abstract chars"; \
	echo "    - \$$$$COST_PER_1K_INPUT/1K input chars (template + abstract)"; \
	echo "  Time: $${DURATION}s"; \
	echo "    - $${TIME_PER_ABSTRACT}s/abstract"; \
	echo "    - $${TIME_PER_1K_INPUT}s/1K input chars"; \
	echo "  Extraction: $$ENTITIES entities, $$RELATIONSHIPS relationships"; \
	echo "    - $${ENTITIES_PER_1K} entities/1K input chars"; \
	echo "    - $${RELATIONSHIPS_PER_1K} relationships/1K input chars"; \
	echo ""; \
	echo "Results logged to: $(BENCH_LOG_FILE)"; \
	echo "Output: $(BENCH_OUTPUT)"; \
	echo "Log: $(BENCH_EXTRACT_LOG)"

# =============================================================================
# 8. ASSESSMENT
# =============================================================================

assess: assess-templates assess-extractions

assess-templates: metpo_assessor.py | assessments
	@echo "📊 Assessing template designs..."
	uv run python metpo_assessor.py analyze-templates templates/ --pattern "*_base.yaml" --output assessments/template_analysis_$(TIMESTAMP).yaml

assess-extractions: metpo_assessor.py | assessments 
	@echo "📈 Assessing extraction performance..."
	uv run python metpo_assessor.py analyze-extractions outputs/ --output assessments/extraction_analysis_$(TIMESTAMP).yaml

# =============================================================================
# 9. CLEANUP TARGETS
# =============================================================================

clean: clean-intermediates clean-templates
	@echo "🧹 Standard cleanup complete"

clean-intermediates:
	rm -rf intermediates/*
	@echo "Intermediate files cleaned"

clean-templates:
	rm -f templates/*_populated.yaml
	@echo "Generated templates cleaned"

clean-outputs:
	rm -f outputs/*.yaml
	@echo "Output files cleaned"

clean-output-logs:
	rm -f outputs/*.yaml logs/*.log
	@echo "Output and log files cleaned"

clean-cache:
	rm -rf cache/*
	@echo "Cache files cleaned"

clean-workspace: clean
	rm -f inputs/random-*-pmids.txt
	rm -f logs/*.log
	@echo "Workspace cleaned (preserved outputs/ and abstracts/)"

clean-all: clean-workspace clean-outputs clean-cache
	@echo "Complete cleanup - everything removed except abstracts/"

# =============================================================================
# BATCH OPERATIONS
# =============================================================================

# Run all templates in sequence with timestamped outputs
extract-all-templates:
	$(MAKE) extract TEMPLATE=growth_conditions
	$(MAKE) extract TEMPLATE=chemical_utilization  
	$(MAKE) extract TEMPLATE=taxa
	$(MAKE) extract TEMPLATE=morphology
	$(MAKE) extract TEMPLATE=biochemical

# Run each template on its curated rich abstracts and assess results
extract-rich: clean intermediates
	$(MAKE) extract-template-rich TEMPLATE=chemical_utilization RICH_DIR=test-chemical-rich
	$(MAKE) extract-template-rich TEMPLATE=biochemical RICH_DIR=test-biochemical-rich
	$(MAKE) extract-template-rich TEMPLATE=growth_conditions RICH_DIR=test-growth-rich
	$(MAKE) extract-template-rich TEMPLATE=morphology RICH_DIR=test-morphology-rich
	$(MAKE) extract-template-rich TEMPLATE=taxa RICH_DIR=test-taxa-rich
	$(MAKE) assess-extractions

extract-template-rich: templates/$(TEMPLATE)_populated.yaml
	@echo "🚀 Running $(TEMPLATE) on $(RICH_DIR) abstracts at $(TIMESTAMP)"
	uv run ontogpt -vv \
		--cache-db cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t templates/$(TEMPLATE)_populated.yaml \
		-i $(RICH_DIR) \
		-o outputs/$(TEMPLATE)_rich_$(TIMESTAMP).yaml \
		2>&1 | tee logs/$(TEMPLATE)_rich_$(TIMESTAMP).log

# Complete pipeline: setup → build → extract → assess
full-pipeline:
	$(MAKE) setup
	$(MAKE) pmids SOURCE=$(SOURCE)
	$(MAKE) abstracts SOURCE=$(SOURCE)
	$(MAKE) intermediates
	$(MAKE) templates TEMPLATE=$(TEMPLATE)
	$(MAKE) validate
	$(MAKE) extract TEMPLATE=$(TEMPLATE)
	$(MAKE) assess

# Debug mode with maximum verbosity
debug-extract: templates/$(TEMPLATE)_populated.yaml
	@echo "🐛 Debug extraction with maximum verbosity..."
	LITELLM_LOG=DEBUG uv run ontogpt -vv \
		--cache-db cache/debug-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $< \
		-i abstracts \
		-o outputs/debug_$(TEMPLATE)_$(TIMESTAMP).yaml \
		2>&1 | tee logs/debug_$(TEMPLATE)_$(TIMESTAMP).log