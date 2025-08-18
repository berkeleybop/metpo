# METPO Literature Mining Pipeline - Simplified Makefile
# Core targets focused on essential workflow steps

# Configuration
N_PMIDS ?= 10
N_ABSTRACTS ?= 5
SOURCE ?= ijsem
TEMPLATE ?= growth_conditions

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
	@echo "  assess         - Assess templates and extractions"
	@echo "  clean          - Cleanup with different levels"
	@echo "  clean-workspace - Remove working files (preserve outputs/abstracts)"
	@echo ""
	@echo "Parameters: SOURCE=$(SOURCE) TEMPLATE=$(TEMPLATE) N_PMIDS=$(N_PMIDS) N_ABSTRACTS=$(N_ABSTRACTS)"
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

abstracts: abstracts-$(SOURCE)

abstracts-$(SOURCE): inputs/random-$(SOURCE)-pmids.txt | abstracts
	@echo "📄 Fetching $(N_ABSTRACTS) abstracts from $(SOURCE)..."
	head -n $(N_ABSTRACTS) $< | while read pmid; do \
		if [ ! -f "abstracts/$$pmid-abstract.txt" ]; then \
			echo "Fetching PMID $$pmid"; \
			uv run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt" 2>/dev/null || rm -f "abstracts/$$pmid-abstract.txt"; \
		fi; \
	done

# =============================================================================
# 3. INTERMEDIATE FILES
# =============================================================================

intermediates: intermediates/db/metpo.db intermediates/yaml/chem_interaction_props_enum.yaml

# METPO database
intermediates/db/metpo.db: ../metpo.owl | intermediates
	@echo "🗄️ Building METPO database..."
	mkdir -p intermediates/db
	cp $< intermediates/db/metpo.owl
	cd intermediates/db && uv run semsql make metpo.db
	rm -f intermediates/db/metpo.owl intermediates/db/metpo-relation-graph.tsv.gz

# Chemical utilization predicates (ONLY for chemical_utilization template)
intermediates/tsv/chem_interaction_props.tsv: ../metpo.owl | intermediates
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
	yq '.classes.ChemicalUtilization.attributes.utilization_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
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
	uv run ontogpt -v \
		--cache-db cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $< \
		-i $$input_dir \
		-o $@ \
		2>&1 | tee logs/$(TEMPLATE)_$(TIMESTAMP).log

# =============================================================================
# 8. ASSESSMENT
# =============================================================================

assess: assess-templates assess-extractions

assess-templates: metpo_assessor.py | assessments
	@echo "📊 Assessing template designs..."
	uv run python metpo_assessor.py analyze-templates templates/ --pattern "*_base.yaml" --output assessments/template_analysis_$(TIMESTAMP).md

assess-extractions: metpo_assessor.py | assessments 
	@echo "📈 Assessing extraction performance..."
	uv run python metpo_assessor.py analyze-extractions outputs/ --output assessments/extraction_analysis_$(TIMESTAMP).md

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