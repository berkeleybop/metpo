.PHONY: all bacdive_utilization_all bacdive_utilization_clean help

# Default PMID if none specified
PMID ?= 21602360

all: bacdive_utilization_all

help:
	@echo "METPO BacDive Chemical Utilization Analysis"
	@echo ""
	@echo "Single PMID Usage:"
	@echo "  make                           # Process default PMID ($(PMID))"
	@echo "  make PMID=12345678            # Process specific PMID"
	@echo "  make pmid.12345678            # Process specific PMID directly"
	@echo "  make pmid.12345678.html       # Generate just the visualization"
	@echo "  make pmid.12345678.output.yaml # Generate just the OntoGPT output"
	@echo "  make pmid.12345678.abstract.txt # Download just the abstract"
	@echo ""
	@echo "Batch Processing:"
	@echo "  make batch N=10 SEED=42       # Complete workflow: sample + process + summarize"
	@echo "  make sampled_pmids.txt N=10   # Just sample N random PMIDs"
	@echo "  make batch_complete.txt       # Just process existing sampled_pmids.txt"  
	@echo "  make batch_summary.txt        # Just generate summary report"
	@echo "  make batch-clean              # Remove all batch files"
	@echo ""
	@echo "Examples:"
	@echo "  make PMID=21602360            # Single paper analysis"
	@echo "  make batch N=5                # Sample and process 5 random PMIDs"
	@echo "  make batch N=10 SEED=42       # Reproducible batch of 10 PMIDs"
	@echo ""
	@echo "Clean:"
	@echo "  make bacdive_utilization_clean # Remove core generated files"
	@echo "  make batch-clean              # Remove batch processing files"

bacdive_utilization_all: bacdive_utilization_clean pmid.$(PMID).html

bacdive_utilization_clean:
	#rm -rf bacdive_utilization_template.yaml
	#rm -rf bacdive_utilizations_template_legacy.yaml
	rm -rf bacdive_utilization.tsv
	rm -rf bacdive_utilization.ttl
	rm -rf bacdive_utilization_enum.yaml
	#rm -rf pmid*

bacdive_utilization.tsv:
	wget -O $@ 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=619442214'

bacdive_utilization.ttl: bacdive_utilization.tsv
	robot template --template $< --output $@

bacdive_utilization_enum.yaml: bacdive_utilization.tsv
	poetry run python make_bacdive_utilization_enum.py \
		--default-prefix bacdive_utilizations \
		--enum-name RelationshipTypeEnum \
		--id-prefix "https://example.org/bacdive_utilizations" \
		--no-preview \
		--no-stats \
		--output $@ $<

#bacdive_utilization_template.yaml: bacdive_utilizations_template_legacy.yaml bacdive_utilization_enum.yaml
#	yq eval-all ' select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.RelationshipTypeEnum as $$enum | $$base.enums.RelationshipTypeEnum = $$enum | $$base ' $^ | cat > $@

# Pattern rules for any PMID
pmid.%.abstract.txt:
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=$*&rettype=abstract&retmode=text" \
		-o $@

pmid.%.output.yaml: pmid.%.abstract.txt
	poetry run ontogpt extract -t bacdive_utilization_template.yaml -i $< > $@

pmid.%.html: pmid.%.output.yaml
	poetry run python visualize_ner.py $< -o $@

# Prevent Make from deleting intermediate files
.PRECIOUS: pmid.%.abstract.txt pmid.%.output.yaml

# Convenience targets for specific PMIDs
pmid.%: pmid.%.html
	@echo "Generated analysis for PMID $*"

# Batch processing targets
# make -f bacdive_utilizations.Makefile sampled_pmids.txt N=5 SEED=42
sampled_pmids.txt:
	@echo "Sampling $(N) PMIDs..."
	./sample_pmids.sh $(N) $(SEED)

# Process all PMIDs and create a completion marker file
batch_complete.txt: sampled_pmids.txt
	@echo "Processing PMIDs from sampled_pmids.txt..."
	@while read pmid; do \
		echo "Processing PMID $$pmid..."; \
		$(MAKE) -f $(lastword $(MAKEFILE_LIST)) pmid.$$pmid.html || echo "Failed: $$pmid"; \
	done < sampled_pmids.txt
	@echo "Batch processing completed at $$(date)" > $@

# Generate summary report file
batch_summary.txt: batch_complete.txt
	@echo "=== BATCH PROCESSING SUMMARY ===" > $@
	@echo "Generated at: $$(date)" >> $@
	@echo "" >> $@
	@echo "Generated files:" >> $@
	@ls -1 pmid.*.html 2>/dev/null | wc -l | xargs echo "HTML files:" >> $@
	@ls -1 pmid.*.output.yaml 2>/dev/null | wc -l | xargs echo "YAML files:" >> $@
	@ls -1 pmid.*.abstract.txt 2>/dev/null | wc -l | xargs echo "Abstract files:" >> $@
	@echo "" >> $@
	@echo "Coverage analysis (top 10):" >> $@
	@for html in pmid.*.html; do \
		if [[ -f "$$html" ]]; then \
			pmid=$$(basename $$html .html); \
			yaml_file="$$pmid.output.yaml"; \
			if [[ -f "$$yaml_file" ]]; then \
				echo -n "$$pmid: "; \
				python visualize_ner.py "$$yaml_file" --stats-only --quiet 2>/dev/null | grep "coverage_percentage" | cut -d: -f2 | xargs echo -n; \
				echo "% coverage"; \
			fi; \
		fi; \
	done 2>/dev/null | sort -k2 -nr | head -10 >> $@
	@echo "" >> $@
	@echo "Summary saved to $@"
	@cat $@

# Complete batch workflow: sample + process + summarize
batch: batch_summary.txt
	@echo "Batch processing complete! See batch_summary.txt for results."

# Clean up batch files
batch-clean:
	rm -f pmid.*.html pmid.*.output.yaml pmid.*.abstract.txt sampled_pmids.txt batch_complete.txt batch_summary.txt