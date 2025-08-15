# Literature Mining Pipeline Makefile
# Idiomatic Make with organized filesystem hierarchy and parameterized extractions

# Configuration variables (can be overridden from command line)
N_PMIDS ?= 10
N_ABSTRACTS ?= 5
SOURCE ?= ijsem
TEMPLATE ?= growth_conditions
INPUT_DIR ?= abstracts

# Derived variables  
PMID_FILE := inputs/random-$(SOURCE)-pmids.txt
TEMPLATE_FILE := templates/$(TEMPLATE)_populated.yaml

# Directory structure
DIRS := inputs intermediates outputs templates abstracts cache logs test-abstracts assessments
INTERMEDIATE_DIRS := intermediates/tsv intermediates/yaml intermediates/db

.PHONY: all clean clean-cache clean-intermediates clean-outputs clean-templates clean-test help setup
.PHONY: validate-templates build-templates extract-all quick-test full-pipeline setup-test-abstracts

# Default target
all: help

help:
	@echo "Literature Mining Pipeline"
	@echo ""
	@echo "Main targets:"
	@echo "  setup                    - Create directory structure"
	@echo "  validate-templates       - Validate all template schemas"
	@echo "  build-templates         - Build all templates with METPO predicates"
	@echo "  assess-templates         - Assess quality of all templates with file output"
	@echo "  assess-all-outputs       - Assess all extraction outputs with file output"
	@echo "  extract-all             - Extract from abstracts using specified template"
	@echo "  quick-test              - Safe test with 3 abstracts (preserves existing)"
	@echo "  full-pipeline           - Complete pipeline with specified source"
	@echo "  timestamped-extraction   - Extract with timestamped files and assessments"
	@echo "  debug-extraction         - Run extraction with maximum debug verbosity"
	@echo ""
	@echo "Parameters:"
	@echo "  SOURCE=$(SOURCE)        - PMID source: n4l, bacdive, ijsem"
	@echo "  TEMPLATE=$(TEMPLATE)    - Template: growth_conditions, chemical_utilization, taxa, morphology, biochemical"
	@echo "  N_PMIDS=$(N_PMIDS)      - Number of PMIDs to sample"
	@echo "  N_ABSTRACTS=$(N_ABSTRACTS) - Number of abstracts to process"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean                   - Remove generated files (preserves abstracts/outputs/cache)"
	@echo "  clean-cache             - Remove temporary cache files only (preserves ontogpt cache)"
	@echo "  clean-cache-all         - Remove ALL cache files (including expensive ontogpt cache)"
	@echo "  clean-intermediates     - Remove intermediate files only"
	@echo "  clean-outputs          - Remove output files only" 
	@echo "  clean-templates        - Remove generated templates only"
	@echo "  clean-assessments      - Remove assessment files only"
	@echo "  clean-test             - Remove test outputs only (preserves caches)"
	@echo ""
	@echo "Examples:"
	@echo "  make extract-all SOURCE=ijsem TEMPLATE=growth_conditions N_ABSTRACTS=10"
	@echo "  make quick-test TEMPLATE=taxa"
	@echo "  make full-pipeline SOURCE=bacdive TEMPLATE=taxa"

# Directory setup
setup: $(DIRS) $(INTERMEDIATE_DIRS)

$(DIRS) $(INTERMEDIATE_DIRS):
	mkdir -p $@

# =============================================================================
# INTERMEDIATE FILE GENERATION
# =============================================================================

# METPO chemical properties extraction
intermediates/tsv/chem_interaction_props.tsv: ../metpo.owl | intermediates/tsv
	robot query --query sparql/chem_interaction_props.rq $@ --input $<

intermediates/yaml/chem_interaction_props_enum.yaml: intermediates/tsv/chem_interaction_props.tsv | intermediates/yaml
	poetry run convert-chem-props -i $< -o $@

# Database generation
intermediates/db/metpo.db: ../metpo.owl | intermediates/db
	cp $< intermediates/db/metpo.owl
	cd intermediates/db && poetry run semsql make metpo.db
	rm -f intermediates/db/metpo.owl intermediates/db/metpo-relation-graph.tsv.gz

# =============================================================================
# TEMPLATE BUILDING
# =============================================================================

# Template validation  
validate-templates: templates/growth_conditions_template_base.yaml templates/chemical_utilization_template_base.yaml templates/taxa_template_base.yaml templates/morphology_template_base.yaml templates/biochemical_template_base.yaml | setup
	@echo "Validating template schemas..."
	poetry run linkml validate --schema templates/growth_conditions_template_base.yaml
	poetry run linkml validate --schema templates/chemical_utilization_template_base.yaml
	poetry run linkml validate --schema templates/taxa_template_base.yaml
	poetry run linkml validate --schema templates/morphology_template_base.yaml
	poetry run linkml validate --schema templates/biochemical_template_base.yaml
	@echo "All templates validated successfully"

# Dynamic template building (only chemical_utilization needs METPO predicates)
templates/growth_conditions_populated.yaml: templates/growth_conditions_template_base.yaml | templates
	cp $< $@

templates/chemical_utilization_populated.yaml: templates/chemical_utilization_template_base.yaml intermediates/yaml/chem_interaction_props_enum.yaml
	yq eval-all 'select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base' $^ > $@.tmp
	yq '.classes.ChemicalUtilization.attributes.utilization_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

# Static templates (simple copy from base to populated)
templates/taxa_populated.yaml: templates/taxa_template_base.yaml | templates
	cp $< $@

templates/morphology_populated.yaml: templates/morphology_template_base.yaml | templates
	cp $< $@

templates/biochemical_populated.yaml: templates/biochemical_template_base.yaml | templates
	cp $< $@

# Meta target to build all populated templates  
build-templates: templates/growth_conditions_populated.yaml templates/chemical_utilization_populated.yaml templates/taxa_populated.yaml templates/morphology_populated.yaml templates/biochemical_populated.yaml

# =============================================================================
# PMID GENERATION
# =============================================================================

# PMID file generation from different sources
inputs/random-n4l-pmids.txt: inputs/n4l/reference_id_mapping.csv | inputs
	cut -f3 -d, $< | sort | uniq | grep '^[0-9]*$$' | shuf -n $(N_PMIDS) > $@

inputs/random-bacdive-pmids.txt: | inputs
	mongosh --quiet bacdive --eval "db.strains_api.aggregate([{\$$unwind: '\$$External links.literature'}, {\$$match: {'External links.literature.Pubmed-ID': {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$group: {_id: '\$$External links.literature.Pubmed-ID'}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc._id); })" > $@

inputs/random-ijsem-pmids.txt: | inputs
	mongosh --quiet europepmc --eval "db.ijsem_articles.aggregate([{\$$match: {pmid: {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc.pmid); })" > $@

# =============================================================================
# ABSTRACT FETCHING
# =============================================================================

# Abstract directory creation
abstracts/.built: $(PMID_FILE) | abstracts
	@echo "Fetching $(N_ABSTRACTS) abstracts from $(PMID_FILE)..."
	rm -f abstracts/*.txt
	head -n $(N_ABSTRACTS) $< | while read pmid; do \
		echo "Fetching abstract for PMID: $$pmid"; \
		poetry run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt" 2>/dev/null || echo "Failed to fetch PMID $$pmid"; \
	done
	touch $@

# Pattern rule for individual abstracts
abstracts/%-abstract.txt: | abstracts
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "$*" > $@ 2>/dev/null || (echo "Failed to fetch PMID $*" && rm -f $@)

# =============================================================================
# EXTRACTION
# =============================================================================

# Parameterized extraction target
outputs/$(SOURCE)-$(TEMPLATE)-extractions.yaml: $(TEMPLATE_FILE) intermediates/db/metpo.db abstracts/.built | outputs
	@echo "Extracting using template: $(TEMPLATE_FILE)"
	@echo "Processing abstracts from: $(SOURCE)"
	poetry run ontogpt -v \
		--cache-db $(PWD)/cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $(TEMPLATE_FILE) \
		-i abstracts \
		-o $@ \
		2>&1 | tee logs/$(SOURCE)-$(TEMPLATE)-extraction.log

# Convenience targets
extract-all: outputs/$(SOURCE)-$(TEMPLATE)-extractions.yaml

quick-test: N_PMIDS = 15
quick-test: N_ABSTRACTS = 10
quick-test: setup-test-abstracts
	@echo "Running quick test with $(N_ABSTRACTS) abstracts..."
	poetry run ontogpt -v \
		--cache-db $(PWD)/cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $(TEMPLATE_FILE) \
		-i test-abstracts \
		-o outputs/test-$(TEMPLATE)-extractions.yaml \
		2>&1 | tee logs/test-$(TEMPLATE)-extraction.log

# Setup test abstracts directory
setup-test-abstracts: $(PMID_FILE) | test-abstracts
	@echo "Setting up test abstracts directory..."
	@if [ $$(ls test-abstracts/*.txt 2>/dev/null | wc -l) -ge $(N_ABSTRACTS) ]; then \
		echo "Test abstracts already available: $$(ls test-abstracts/*.txt | wc -l) files"; \
	elif [ $$(ls abstracts/*.txt 2>/dev/null | wc -l) -ge $(N_ABSTRACTS) ]; then \
		echo "Copying $(N_ABSTRACTS) abstracts from production abstracts/"; \
		ls abstracts/*.txt | head -n $(N_ABSTRACTS) | while read file; do \
			cp "$$file" test-abstracts/; \
		done; \
	else \
		echo "Fetching $(N_ABSTRACTS) fresh abstracts for testing..."; \
		head -n $(N_ABSTRACTS) $(PMID_FILE) | while read pmid; do \
			echo "Fetching abstract for PMID: $$pmid"; \
			poetry run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "test-abstracts/$$pmid-abstract.txt" 2>/dev/null || echo "Failed to fetch PMID $$pmid"; \
		done; \
	fi

full-pipeline: $(PMID_FILE) extract-all

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

clean-cache:
	@echo "Selectively cleaning cache files..."
	@echo "Preserving unified ontogpt cache (expensive to rebuild)"
	@echo "Removing temporary and stale cache files only"
	rm -f cache/*.tmp cache/*.lock cache/*-temp-*
	@echo "Cache cleaned (preserved ontogpt-cache.db)"

clean-cache-all:
	rm -rf cache/*
	@echo "All cache files removed (including expensive ontogpt cache)"

clean-intermediates:
	rm -rf intermediates/*
	@echo "Intermediate files cleaned"

clean-tsv:
	rm -f intermediates/tsv/*.tsv
	@echo "TSV intermediate files cleaned"

clean-yaml:
	rm -f intermediates/yaml/*.yaml
	@echo "YAML intermediate files cleaned"

clean-db:
	rm -f intermediates/db/*.db
	@echo "Database intermediate files cleaned"

clean-outputs:
	rm -rf outputs/*
	@echo "Output files cleaned"

clean-templates:
	rm -f templates/*_populated.yaml
	@echo "Generated templates cleaned"

clean-test:
	rm -rf test-abstracts/*.txt
	rm -f outputs/test-*-extractions.yaml
	rm -f logs/test-*-extraction.log
	@echo "Test files cleaned (cache preserved for efficiency)"

clean-assessments:
	rm -rf assessments/*
	@echo "Assessment files cleaned"

# Aggressive cleanup - preserves only expensive abstracts, final outputs, and template caches
clean: clean-cache clean-intermediates clean-templates
	rm -f inputs/random-*-pmids.txt
	rm -f abstracts/.built
	rm -f logs/*
	@echo "Cleanup complete - preserved abstracts/, outputs/, and template caches"

# Nuclear cleanup - removes everything
clean-all: clean clean-outputs
	rm -rf abstracts/* logs/*
	@echo "Complete cleanup - all files removed"

# =============================================================================
# TIMESTAMPED EXTRACTION AND ASSESSMENT
# =============================================================================

# Variables for timestamped extraction
TIMESTAMP := $(shell date +"%Y%m%d_%H%M%S")
TIMESTAMPED_OUTPUT := outputs/$(TEMPLATE)_$(TIMESTAMP).yaml
TIMESTAMPED_LOG := logs/$(TEMPLATE)_$(TIMESTAMP).log

# Run timestamped extraction with assessment
timestamped-extraction: $(TEMPLATE_FILE) entity_relationship_assessment.py template_quality_assessor.py
	@echo "Running timestamped extraction: $(TEMPLATE) at $(TIMESTAMP)"
	@echo "Input directory: $(INPUT_DIR)"
	@echo "Template file: $(TEMPLATE_FILE)"
	@mkdir -p outputs logs assessments
	poetry run ontogpt -v \
		--cache-db $(PWD)/cache/ontogpt-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $(TEMPLATE_FILE) \
		-i $(INPUT_DIR) \
		-o $(TIMESTAMPED_OUTPUT) \
		2>&1 | tee $(TIMESTAMPED_LOG)
	@echo "Running entity-relationship assessment on $(TIMESTAMPED_OUTPUT)"
	poetry run python entity_relationship_assessment.py $(TIMESTAMPED_OUTPUT) \
		--template $(TEMPLATE_FILE) \
		--output assessments/entity_assessment_$(TEMPLATE)_$(TIMESTAMP).txt \
		--format text
	@echo "Running template quality assessment on $(TEMPLATE_FILE)"
	poetry run python template_quality_assessor.py $(TEMPLATE_FILE) \
		--output assessments/template_assessment_$(TEMPLATE)_$(TIMESTAMP).txt \
		--format text

# Run all templates with timestamped extraction
run-all-templates:
	$(MAKE) timestamped-extraction TEMPLATE=biochemical INPUT_DIR=test-biochemical-rich
	$(MAKE) timestamped-extraction TEMPLATE=growth_conditions INPUT_DIR=test-growth-rich  
	$(MAKE) timestamped-extraction TEMPLATE=chemical_utilization INPUT_DIR=test-chemical-rich
	$(MAKE) timestamped-extraction TEMPLATE=morphology INPUT_DIR=test-morphology-rich
	$(MAKE) timestamped-extraction TEMPLATE=taxa INPUT_DIR=test-taxa-rich

# Compare before/after template improvements
compare-extractions:
	@echo "Available extraction outputs:"
	@ls -la outputs/*_2*.yaml | tail -10
	@echo ""
	@echo "Run assessment on specific files:"
	@echo "  poetry run python entity_relationship_assessment.py outputs/<filename>"

# Run assessment on a specific output file
assess-output:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make assess-output FILE=outputs/filename.yaml [TEMPLATE_FILE=templates/template.yaml]"; \
		echo "Available files:"; \
		ls -1 outputs/*.yaml | head -10; \
	else \
		echo "Assessing $(FILE)..."; \
		mkdir -p assessments; \
		if [ -n "$(TEMPLATE_FILE)" ]; then \
			poetry run python entity_relationship_assessment.py $(FILE) \
				--template $(TEMPLATE_FILE) \
				--output assessments/entity_assessment_$$(basename $(FILE) .yaml)_$$(date +%Y%m%d_%H%M%S).txt \
				--format text; \
		else \
			poetry run python entity_relationship_assessment.py $(FILE) \
				--output assessments/entity_assessment_$$(basename $(FILE) .yaml)_$$(date +%Y%m%d_%H%M%S).txt \
				--format text; \
		fi \
	fi

# Quick timestamped extraction with default settings
quick-timestamped:
	$(MAKE) timestamped-extraction TEMPLATE=$(TEMPLATE) INPUT_DIR=$(INPUT_DIR)

# Debug extraction with maximum verbosity
debug-extraction:
	@echo "Running debug extraction with maximum verbosity..."
	@echo "Template: $(TEMPLATE_FILE)"
	@echo "Input: $(INPUT_DIR)"
	@mkdir -p outputs logs cache
	LITELLM_LOG=DEBUG poetry run ontogpt -vv \
		--cache-db $(PWD)/cache/debug-cache \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $(TEMPLATE_FILE) \
		-i $(INPUT_DIR) \
		-o outputs/debug-$(TEMPLATE)-$(shell date +%Y%m%d_%H%M%S).yaml \
		2>&1 | tee logs/debug-$(TEMPLATE)-$(shell date +%Y%m%d_%H%M%S).log

# Assess all templates
assess-templates: build-templates template_quality_assessor.py
	@echo "Assessing all template quality..."
	@mkdir -p assessments
	poetry run python template_quality_assessor.py templates/ \
		--output assessments/all_templates_assessment_$(shell date +%Y%m%d_%H%M%S).txt \
		--format text \
		--verbose

# Assess all extraction outputs
assess-all-outputs: entity_relationship_assessment.py
	@echo "Assessing all extraction outputs..."
	@mkdir -p assessments
	@if [ $$(ls outputs/*.yaml 2>/dev/null | wc -l) -eq 0 ]; then \
		echo "No YAML files found in outputs/ directory"; \
		echo "Available files:"; \
		ls -la outputs/ || echo "No outputs directory"; \
	else \
		poetry run python entity_relationship_assessment.py outputs/ \
			--output assessments/all_outputs_assessment_$(shell date +%Y%m%d_%H%M%S).txt \
			--format text \
			--verbose; \
	fi

# =============================================================================
# VALIDATION AND TESTING
# =============================================================================

# Test individual components
test-pmid-generation: inputs/random-$(SOURCE)-pmids.txt
	@echo "Generated $(shell wc -l < $<) PMIDs from $(SOURCE)"
	@head -5 $<

test-template-build: $(TEMPLATE_FILE)
	@echo "Template $(TEMPLATE) built successfully"
	@echo "Size: $(shell wc -l < $<) lines"

test-abstract-fetch: abstracts/10758868-abstract.txt
	@echo "Test abstract fetched successfully"
	@wc -w $<

# Show pipeline status
status:
	@echo "Pipeline Status:"
	@echo "- PMIDs available: $(shell test -f $(PMID_FILE) && wc -l < $(PMID_FILE) || echo 'None')"
	@echo "- Abstracts cached: $(shell ls abstracts/*.txt 2>/dev/null | wc -l)"
	@echo "- Templates built: $(shell ls templates/*_template.yaml 2>/dev/null | wc -l)"
	@echo "- Outputs generated: $(shell ls outputs/*.yaml 2>/dev/null | wc -l)"
	@echo "- Cache size: $(shell du -sh cache 2>/dev/null | cut -f1 || echo '0')"
# Unified Assessment
unified-assessment:
	@echo "Running unified pipeline assessment..."
	@mkdir -p assessments
	poetry run python unified_assessment.py outputs/ --verbose --include-specialization --output assessments/unified_assessment_$(shell date +%Y%m%d_%H%M%S).json

# Domain-specific grounding analysis
domain-grounding-analysis:
	@echo "Running domain-specific grounding analysis..."
	@mkdir -p assessments
	poetry run python domain_grounding_analysis.py outputs/ --verbose --output assessments/domain_grounding_$(shell date +%Y%m%d_%H%M%S).json

# Template specialization analysis
template-specialization-analysis:
	@echo "Running template specialization analysis..."
	@mkdir -p assessments
	poetry run python template_specialization_analyzer.py outputs/ --verbose --output assessments/template_specialization_$(shell date +%Y%m%d_%H%M%S).json
