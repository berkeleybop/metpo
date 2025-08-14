# Literature Mining Pipeline Makefile
# Idiomatic Make with organized filesystem hierarchy and parameterized extractions

# Configuration variables (can be overridden from command line)
N_PMIDS ?= 10
N_ABSTRACTS ?= 5
SOURCE ?= ijsem
TEMPLATE ?= growth_conditions

# Derived variables  
PMID_FILE := inputs/random-$(SOURCE)-pmids.txt
TEMPLATE_FILE := templates/$(TEMPLATE)_template.yaml

# Directory structure
DIRS := inputs intermediates outputs templates abstracts cache logs
INTERMEDIATE_DIRS := intermediates/tsv intermediates/yaml intermediates/db

.PHONY: all clean clean-cache clean-intermediates clean-outputs clean-templates help setup
.PHONY: validate-templates build-templates extract-all quick-test full-pipeline

# Default target
all: help

help:
	@echo "Literature Mining Pipeline"
	@echo ""
	@echo "Main targets:"
	@echo "  setup                    - Create directory structure"
	@echo "  validate-templates       - Validate all template schemas"
	@echo "  build-templates         - Build all templates with METPO predicates"
	@echo "  extract-all             - Extract from abstracts using specified template"
	@echo "  quick-test              - Quick test with 3 abstracts"
	@echo "  full-pipeline           - Complete pipeline with specified source"
	@echo ""
	@echo "Parameters:"
	@echo "  SOURCE=$(SOURCE)        - PMID source: n4l, bacdive, ijsem"
	@echo "  TEMPLATE=$(TEMPLATE)    - Template: ontogpt, growth_conditions, taxa, phylogeny"
	@echo "  N_PMIDS=$(N_PMIDS)      - Number of PMIDs to sample"
	@echo "  N_ABSTRACTS=$(N_ABSTRACTS) - Number of abstracts to process"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean                   - Remove all generated files except abstracts/outputs"
	@echo "  clean-cache             - Remove cache files only"
	@echo "  clean-intermediates     - Remove intermediate files only"
	@echo "  clean-outputs          - Remove output files only" 
	@echo "  clean-templates        - Remove generated templates only"
	@echo ""
	@echo "Examples:"
	@echo "  make extract-all SOURCE=ijsem TEMPLATE=growth_conditions N_ABSTRACTS=10"
	@echo "  make quick-test TEMPLATE=taxa"
	@echo "  make full-pipeline SOURCE=bacdive TEMPLATE=ontogpt"

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
validate-templates: templates/ontogpt_template_base.yaml templates/growth_conditions_template_base.yaml templates/taxa_template.yaml templates/phylogeny_template.yaml | setup
	@echo "Validating template schemas..."
	poetry run linkml validate --schema templates/ontogpt_template_base.yaml
	poetry run linkml validate --schema templates/growth_conditions_template_base.yaml
	poetry run linkml validate --schema templates/taxa_template.yaml
	poetry run linkml validate --schema templates/phylogeny_template.yaml
	@echo "All templates validated successfully"

# Dynamic template building (templates with METPO predicates)
templates/ontogpt_template.yaml: templates/ontogpt_template_base.yaml intermediates/yaml/chem_interaction_props_enum.yaml
	yq eval-all 'select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base' $^ > $@.tmp
	yq '.classes.OrganismCompoundRelationship.attributes.relationship_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

templates/growth_conditions_template.yaml: templates/growth_conditions_template_base.yaml intermediates/yaml/chem_interaction_props_enum.yaml
	yq eval-all 'select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base' $^ > $@.tmp
	yq '.classes.ChemicalUtilization.attributes.utilization_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

# Meta target to build all dynamic templates
build-templates: templates/ontogpt_template.yaml templates/growth_conditions_template.yaml

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
		--cache-db cache/$(SOURCE)-$(TEMPLATE)-cache.db \
		extract \
		--show-prompt \
		-p 0.1 \
		-t $(TEMPLATE_FILE) \
		-i abstracts \
		-o $@ \
		2>&1 | tee logs/$(SOURCE)-$(TEMPLATE)-extraction.log

# Convenience targets
extract-all: outputs/$(SOURCE)-$(TEMPLATE)-extractions.yaml

quick-test: N_PMIDS = 5
quick-test: N_ABSTRACTS = 3  
quick-test: extract-all

full-pipeline: $(PMID_FILE) extract-all

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

clean-cache:
	rm -rf cache/*
	@echo "Cache cleaned"

clean-intermediates:
	rm -rf intermediates/*
	@echo "Intermediate files cleaned"

clean-outputs:
	rm -rf outputs/*
	@echo "Output files cleaned"

clean-templates:
	rm -f templates/*_template.yaml
	@echo "Generated templates cleaned"

# Aggressive cleanup - preserves only expensive abstracts and final outputs
clean: clean-cache clean-intermediates clean-templates
	rm -f inputs/random-*-pmids.txt
	rm -f abstracts/.built
	rm -f logs/*
	@echo "Cleanup complete - preserved abstracts/ and outputs/"

# Nuclear cleanup - removes everything
clean-all: clean clean-outputs
	rm -rf abstracts/* logs/*
	@echo "Complete cleanup - all files removed"

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