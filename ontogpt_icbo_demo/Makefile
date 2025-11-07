# OntoGPT ICBO 2025 Demo
# Demonstrates METPO grounding strengths and weaknesses

# OntoGPT executable
ONTOGPT := uv run ontogpt

# Default model and settings
MODEL ?= gpt-4o
TEMPERATURE ?= 0.0

# Directories
INPUTS_DIR := inputs
OUTPUTS_DIR := outputs
LOGS_DIR := outputs/logs
TEMPLATES_DIR := templates
FIGURES_DIR := figures
SLIDES_DIR := .

# Input abstracts - all abstracts run through both templates
ALL_INPUTS := $(wildcard $(INPUTS_DIR)/*-abstract.txt)

# Templates
PHENOTYPE_TEMPLATE := $(TEMPLATES_DIR)/strain_phenotype_icbo.yaml
CHEMICAL_TEMPLATE := $(TEMPLATES_DIR)/chemical_utilization_icbo.yaml

# Output files - all abstracts through both templates
PHENOTYPE_OUTPUTS := $(patsubst $(INPUTS_DIR)/%-abstract.txt,$(OUTPUTS_DIR)/%-phenotype.yaml,$(ALL_INPUTS))
CHEMICAL_OUTPUTS := $(patsubst $(INPUTS_DIR)/%-abstract.txt,$(OUTPUTS_DIR)/%-chemical.yaml,$(ALL_INPUTS))

.PHONY: all phenotypes chemicals clean clean-all analyze help setup-dirs convert-turtle slides slides-pptx slides-html

# Default target
all: phenotypes chemicals

# Setup directories
setup-dirs:
	@mkdir -p $(LOGS_DIR)

# Extract phenotypes from all selected abstracts
phenotypes: setup-dirs $(PHENOTYPE_OUTPUTS)

# Extract chemical utilizations
chemicals: setup-dirs $(CHEMICAL_OUTPUTS)

# Pattern rule for phenotype extraction
$(OUTPUTS_DIR)/%-phenotype.yaml: $(INPUTS_DIR)/%-abstract.txt $(PHENOTYPE_TEMPLATE)
	@echo "Extracting phenotypes from $< ..."
	@echo "Log will be saved to $(LOGS_DIR)/$(notdir $@).log"
	$(ONTOGPT) extract \
		--template $(PHENOTYPE_TEMPLATE) \
		--inputfile $< \
		--model $(MODEL) \
		--temperature $(TEMPERATURE) \
		--output $@ 2>&1 | tee $(LOGS_DIR)/$(notdir $@).log
	@echo "Saved to $@"

# Pattern rule for chemical utilization extraction
$(OUTPUTS_DIR)/%-chemical.yaml: $(INPUTS_DIR)/%-abstract.txt $(CHEMICAL_TEMPLATE)
	@echo "Extracting chemical utilization from $< ..."
	@echo "Log will be saved to $(LOGS_DIR)/$(notdir $@).log"
	$(ONTOGPT) extract \
		--template $(CHEMICAL_TEMPLATE) \
		--inputfile $< \
		--model $(MODEL) \
		--temperature $(TEMPERATURE) \
		--output $@ 2>&1 | tee $(LOGS_DIR)/$(notdir $@).log
	@echo "Saved to $@"

# Analyze METPO grounding in outputs
analyze:
	@echo "=== METPO Grounding Analysis ==="
	@echo ""
	@echo "Phenotype Extractions:"
	@for f in $(OUTPUTS_DIR)/*-phenotype.yaml; do \
		if [ -f "$$f" ]; then \
			echo "$$f:"; \
			metpo_count=$$(grep -c "w3id.org/metpo/" "$$f" 2>/dev/null || echo 0); \
			auto_count=$$(grep -c "AUTO:" "$$f" 2>/dev/null || echo 0); \
			echo "  METPO URIs: $$metpo_count"; \
			echo "  AUTO terms: $$auto_count"; \
		fi \
	done
	@echo ""
	@echo "Chemical Utilization Extractions:"
	@for f in $(OUTPUTS_DIR)/*-chemical.yaml; do \
		if [ -f "$$f" ]; then \
			echo "$$f:"; \
			metpo_count=$$(grep -c "w3id.org/metpo/" "$$f" 2>/dev/null || echo 0); \
			chebi_count=$$(grep -c "CHEBI:" "$$f" 2>/dev/null || echo 0); \
			echo "  METPO property uses: $$metpo_count"; \
			echo "  ChEBI groundings: $$chebi_count"; \
		fi \
	done

# Clean all outputs
clean:
	@echo "Removing all output files..."
	rm -f $(OUTPUTS_DIR)/*.yaml
	@echo "Clean complete"

# Clean outputs and logs
clean-all: clean
	@echo "Removing log files..."
	rm -rf $(LOGS_DIR)
	@echo "Clean all complete"

# Show help
help:
	@echo "OntoGPT ICBO 2025 Demo - Makefile targets"
	@echo ""
	@echo "Usage: make [target] [MODEL=gpt-4o] [TEMPERATURE=0.0]"
	@echo ""
	@echo "Targets:"
	@echo "  all            - Run all extractions (default)"
	@echo "  phenotypes     - Extract phenotypes only"
	@echo "  chemicals      - Extract chemical utilizations only"
	@echo "  analyze        - Analyze METPO grounding in outputs"
	@echo "  convert-turtle - Convert all outputs to Turtle RDF"
	@echo "  slides         - Generate PDF slides from Markdown (Marp)"
	@echo "  slides-pptx    - Generate PowerPoint slides"
	@echo "  slides-html    - Generate HTML slides for preview"
	@echo "  clean          - Remove all output files (keeps logs)"
	@echo "  clean-all      - Remove all output files and logs"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Logging:"
	@echo "  All extractions save verbose logs to outputs/logs/"
	@echo "  Example: outputs/logs/28879838-phenotype.yaml.log"
	@echo ""
	@echo "Examples:"
	@echo "  make                                    # Run all with defaults"
	@echo "  make phenotypes MODEL=gpt-4o-mini       # Use cheaper model"
	@echo "  make chemicals TEMPERATURE=0.5          # Higher temperature"
	@echo "  make analyze                            # Analyze results"
	@echo "  make convert-turtle                     # Convert all outputs to Turtle"
	@echo "  make slides                             # Generate PDF slides"
	@echo ""

# Convert all YAML outputs to Turtle RDF format
convert-turtle: all
	@echo "=== Converting outputs to Turtle format ==="
	@for f in $(OUTPUTS_DIR)/*-phenotype.yaml; do \
		if [ -f "$$f" ]; then \
			echo "Converting $$f to Turtle..."; \
			$(ONTOGPT) convert -t $(PHENOTYPE_TEMPLATE) -O turtle "$$f" -o "$${f%.yaml}.ttl" 2>&1 | tee $(LOGS_DIR)/$$(basename "$$f" .yaml)-turtle.log; \
		fi \
	done
	@for f in $(OUTPUTS_DIR)/*-chemical.yaml; do \
		if [ -f "$$f" ]; then \
			echo "Converting $$f to Turtle..."; \
			$(ONTOGPT) convert -t $(CHEMICAL_TEMPLATE) -O turtle "$$f" -o "$${f%.yaml}.ttl" 2>&1 | tee $(LOGS_DIR)/$$(basename "$$f" .yaml)-turtle.log; \
		fi \
	done
	@echo "Turtle conversion complete"

# Generate slides from Markdown to PDF
slides:
	@echo "=== Generating slides from Markdown ==="
	@if [ ! -f "$(SLIDES_DIR)/icbo_metpo_slides.md" ]; then \
		echo "Error: icbo_metpo_slides.md not found"; \
		exit 1; \
	fi
	npx @marp-team/marp-cli $(SLIDES_DIR)/icbo_metpo_slides.md --theme-set themes/lbnl.css -o $(SLIDES_DIR)/icbo_metpo_slides.pdf
	@echo "Slides generated: icbo_metpo_slides.pdf"
	@echo ""
	@echo "To also generate PPTX: make slides-pptx"
	@echo "To preview HTML: make slides-html"

# Generate PowerPoint version
slides-pptx:
	@echo "=== Generating PowerPoint slides ==="
	npx @marp-team/marp-cli $(SLIDES_DIR)/icbo_metpo_slides.md --theme-set themes/lbnl.css -o $(SLIDES_DIR)/icbo_metpo_slides.pptx
	@echo "PowerPoint generated: icbo_metpo_slides.pptx"

# Generate HTML version for preview
slides-html:
	@echo "=== Generating HTML slides ==="
	npx @marp-team/marp-cli $(SLIDES_DIR)/icbo_metpo_slides.md --theme-set themes/lbnl.css -o $(SLIDES_DIR)/icbo_metpo_slides.html
	@echo "HTML generated: icbo_metpo_slides.html"
	@echo "Open in browser: file://$(shell pwd)/icbo_metpo_slides.html"
