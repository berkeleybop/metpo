# ICBO 2025 METPO Presentation

.PHONY: slides clean help

# Default target
slides: icbo_metpo_slides.pdf

# Build PDF from markdown
icbo_metpo_slides.pdf: icbo_metpo_slides.md themes/lbnl.css
	npx @marp-team/marp-cli $< --theme themes/lbnl.css --allow-local-files -o $@
	@echo "Slides generated: $@"

# Clean build artifacts
clean:
	rm -f icbo_metpo_slides.pdf
	rm -f icbo_metpo_slides_*_*.pdf

# Show help
help:
	@echo "ICBO 2025 Presentation Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  slides (default)  - Generate PDF slides from Markdown"
	@echo "  clean             - Remove generated PDFs"
	@echo "  help              - Show this help message"
