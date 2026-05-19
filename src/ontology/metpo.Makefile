## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

# Sheet GIDs and spreadsheet ID are centralized in sheets.yaml at repo root.
# See https://github.com/berkeleybop/metpo/issues/372
#
# Two-tier resolution so the build works on both host and inside the ODK
# container (which does not ship `uv`):
#
#   1. Hardcoded defaults below always work, even if python3 or pyyaml are
#      unavailable, since they require nothing beyond Make itself.
#   2. If python3 + pyyaml ARE available (true in the ODK container, on
#      hosts with `pip install pyyaml`, and inside an active uv venv), we
#      override the defaults by reading sheets.yaml via
#      metpo/sheets_config.py invoked as a script (no package install
#      required). The shell command's stderr is swallowed so a missing
#      python3 or pyyaml falls through silently to the hardcoded defaults.
#
# If the sheet's GIDs ever change, update both the hardcoded defaults here
# AND sheets.yaml. See docs/google_sheets_template_sync.md.
SPREADSHEET_ID := 1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU
SRC_URL_MAIN := https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export?exportFormat=tsv&gid=1569766102
SRC_URL_PROPERTIES := https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export?exportFormat=tsv&gid=681401984

SRC_URL_MAIN_FROM_YAML := $(shell python3 ../../metpo/sheets_config.py classes 2>/dev/null)
ifneq ($(SRC_URL_MAIN_FROM_YAML),)
SRC_URL_MAIN := $(SRC_URL_MAIN_FROM_YAML)
endif

SRC_URL_PROPERTIES_FROM_YAML := $(shell python3 ../../metpo/sheets_config.py properties 2>/dev/null)
ifneq ($(SRC_URL_PROPERTIES_FROM_YAML),)
SRC_URL_PROPERTIES := $(SRC_URL_PROPERTIES_FROM_YAML)
endif

DRAFTS_DIR = ../templates/drafts

.PHONY: squeaky-clean clean-templates save-drafts install-drafts diff-drafts diff-sheets diff-release

# Save current templates to drafts (before squeaky-clean)
save-drafts: ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv
	mkdir -p $(DRAFTS_DIR)
	cp ../templates/metpo_sheet.tsv $(DRAFTS_DIR)/metpo_sheet.tsv
	cp ../templates/metpo-properties.tsv $(DRAFTS_DIR)/metpo-properties.tsv
	@echo "Templates saved to $(DRAFTS_DIR)/"

# Install drafts over Google Sheets downloads (after squeaky-clean + curl)
install-drafts: $(DRAFTS_DIR)/metpo_sheet.tsv $(DRAFTS_DIR)/metpo-properties.tsv
	cp $(DRAFTS_DIR)/metpo_sheet.tsv ../templates/metpo_sheet.tsv
	cp $(DRAFTS_DIR)/metpo-properties.tsv ../templates/metpo-properties.tsv
	@echo "Draft templates installed over Google Sheets versions"

# Show what changed between Google Sheets and drafts
diff-drafts: ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv
	@diff $(DRAFTS_DIR)/metpo_sheet.tsv ../templates/metpo_sheet.tsv || true
	@diff $(DRAFTS_DIR)/metpo-properties.tsv ../templates/metpo-properties.tsv || true

../templates/metpo_sheet.tsv:
	curl -L -s "$(SRC_URL_MAIN)" > $@

#../templates/metpo-synonyms.tsv:
#	curl -L -s "$(SRC_URL_SYNONYMS)" > $@

../templates/metpo-properties.tsv:
	curl -L -s "$(SRC_URL_PROPERTIES)" > $@

squeaky-clean: clean clean-templates

clean-templates:
	rm -rf ../templates/metpo_sheet.tsv
	#rm -rf ../templates/metpo-synonyms.tsv
	rm -rf ../templates/metpo-properties.tsv
	rm -rf components/metpo_sheet.owl
	#rm -rf components/metpo-synonyms.owl
	rm -rf components/metpo-properties.owl

# Diff current working templates against Google Sheets
diff-sheets:
	cd ../.. && uv run diff-templates -a gsheet -b HEAD --cell-diffs

# Diff current working templates against the last tagged release
diff-release:
	cd ../.. && uv run diff-templates -a $(shell git describe --tags --abbrev=0 2>/dev/null || echo "main") -b HEAD --cell-diffs

#$(MIRRORDIR)/mpo.owl: ../../assets/mpo_v0.74.en_only.owl
#	cp $^ $@
#
#$(MIRRORDIR)/micro.owl: ../../assets/MicrO-for-metpo.owl.gz
#	robot remove \
#			-i $< \
#			--axioms equivalent \
#			--output $@

../templates/stubs.tsv: ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv ../../metpo/bactotraits/create_stubs.py
	python ../../metpo/bactotraits/create_stubs.py -o $@ ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv

# Generated from historical BioPortal submissions + tagged releases.
# Repo-only — not in Google Sheets. Regenerate with: make -f metpo.Makefile regenerate-deprecated
../templates/deprecated.tsv: ../../metpo/scripts/generate_deprecated_template.py
	cd ../.. && uv run generate-deprecated-template -o $(abspath $@)

.PHONY: regenerate-deprecated
regenerate-deprecated:
	rm -f ../templates/deprecated.tsv
	$(MAKE) -f metpo.Makefile ../templates/deprecated.tsv

components/metpo_sheet.owl: ../templates/stubs.tsv ../templates/metpo-properties.tsv ../templates/metpo_sheet.tsv ../templates/deprecated.tsv
	$(ROBOT) template \
		--add-prefix 'METPO: https://w3id.org/metpo/' \
		--add-prefix 'qudt: http://qudt.org/schema/qudt/' \
		--template ../templates/stubs.tsv \
		--template ../templates/metpo_sheet.tsv \
		--template ../templates/metpo-properties.tsv \
		--template ../templates/deprecated.tsv \
		annotate --ontology-iri $(ONTBASE)/$@ \
		annotate -V $(ONTBASE)/releases/$(TODAY)/$@ \
		--annotation owl:versionInfo $(TODAY) \
		convert -f ofn --output $@.tmp.owl && mv $@.tmp.owl $@
