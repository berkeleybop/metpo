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
#      required). The shell command's stderr is redirected to
#      $(SHEETS_CONFIG_WARN_LOG) so a missing python3 or pyyaml still falls
#      through silently to the hardcoded defaults, but errors are preserved
#      for debugging.
#
# If the sheet's GIDs ever change, update both the hardcoded defaults here
# AND sheets.yaml. See docs/google_sheets_template_sync.md.
SPREADSHEET_ID := 1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU
SRC_URL_MAIN := https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export?exportFormat=tsv&gid=1569766102
SRC_URL_PROPERTIES := https://docs.google.com/spreadsheets/d/$(SPREADSHEET_ID)/export?exportFormat=tsv&gid=681401984
SHEETS_CONFIG_WARN_LOG := ../templates/sheets_config_warnings.log
$(shell : > $(SHEETS_CONFIG_WARN_LOG))

SRC_URL_MAIN_FROM_YAML := $(shell python3 ../../metpo/sheets_config.py classes 2>>$(SHEETS_CONFIG_WARN_LOG))
ifneq ($(SRC_URL_MAIN_FROM_YAML),)
SRC_URL_MAIN := $(SRC_URL_MAIN_FROM_YAML)
endif

SRC_URL_PROPERTIES_FROM_YAML := $(shell python3 ../../metpo/sheets_config.py properties 2>>$(SHEETS_CONFIG_WARN_LOG))
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

# Intentionally no prerequisites: Make fetches this file only if it is missing.
# This preserves committed/local snapshots by default; run `make squeaky-clean`
# (or delete the file) to force re-download from Google Sheets.
../templates/metpo_sheet.tsv:
	curl -L -s "$(SRC_URL_MAIN)" > $@

#../templates/metpo-synonyms.tsv:
#	curl -L -s "$(SRC_URL_SYNONYMS)" > $@

# Intentionally no prerequisites: Make fetches this file only if it is missing.
# This preserves committed/local snapshots by default; run `make squeaky-clean`
# (or delete the file) to force re-download from Google Sheets.
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
	@command -v uv >/dev/null 2>&1 || { echo "Error: 'uv' is required for diff-sheets. Run this target on a host with uv installed."; exit 1; }
	cd ../.. && uv run diff-templates -a gsheet -b HEAD --cell-diffs

# Diff current working templates against the last tagged release
diff-release:
	@command -v uv >/dev/null 2>&1 || { echo "Error: 'uv' is required for diff-release (host-only target)."; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "Error: 'git' is required for diff-release."; exit 1; }
	@git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Error: diff-release must be run from within a git work tree."; exit 1; }
	@release_ref=$$(git describe --tags --abbrev=0 2>/dev/null); \
	if [ -z "$$release_ref" ]; then \
		echo "Warning: No git tags found; falling back to 'main'."; \
		release_ref=main; \
	fi; \
	cd ../.. && uv run diff-templates -a "$$release_ref" -b HEAD --cell-diffs

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

# Repo-only — not in Google Sheets.
# IMPORTANT: ../templates/deprecated.tsv is hand-maintained source-of-truth.
# The generation rule below exists ONLY as a recovery/bootstrap tool from
# historical BioPortal submissions + tagged releases, and should not be used
# for routine maintenance.
../templates/deprecated.tsv: ../../metpo/scripts/generate_deprecated_template.py
	cd ../.. && uv run generate-deprecated-template -o $(abspath $@)

.PHONY: regenerate-deprecated
# WARNING: recovery-only helper. Do not run as part of normal updates; prefer
# manual edits to ../templates/deprecated.tsv.
regenerate-deprecated:
	rm -f ../templates/deprecated.tsv
	$(MAKE) -f metpo.Makefile ../templates/deprecated.tsv

# Emission control for deprecated/obsolete terms (berkeleybop/metpo#378).
# INCLUDE_OBSOLETE=true (default) merges ../templates/deprecated.tsv into the build,
# so the release OWL carries the obsolete classes (current behaviour; the committed
# artifacts and the artifact-freshness check reproduce with the default).
# INCLUDE_OBSOLETE=false omits that template, producing an obsolete-free build, e.g.
#   sh run.sh make INCLUDE_OBSOLETE=false prepare_release
INCLUDE_OBSOLETE ?= true
ifeq ($(INCLUDE_OBSOLETE),true)
DEPRECATED_TEMPLATE_ARG := --template ../templates/deprecated.tsv
DEPRECATED_PREREQ := ../templates/deprecated.tsv
else
DEPRECATED_TEMPLATE_ARG :=
DEPRECATED_PREREQ :=
endif

components/metpo_sheet.owl: ../templates/stubs.tsv ../templates/metpo-properties.tsv ../templates/metpo_sheet.tsv $(DEPRECATED_PREREQ)
	$(ROBOT) template \
		--add-prefix 'METPO: https://w3id.org/metpo/' \
		--add-prefix 'qudt: http://qudt.org/schema/qudt/' \
		--add-prefix 'oboInOwl: http://www.geneontology.org/formats/oboInOwl#' \
		--template ../templates/stubs.tsv \
		--template ../templates/metpo_sheet.tsv \
		--template ../templates/metpo-properties.tsv \
		$(DEPRECATED_TEMPLATE_ARG) \
		annotate --ontology-iri $(ONTBASE)/$@ \
		annotate -V $(ONTBASE)/releases/$(TODAY)/$@ \
		--annotation owl:versionInfo $(TODAY) \
		convert -f ofn --output $@.tmp.owl && mv $@.tmp.owl $@

# CURRENT_RELEASE is used by release_diff to download the live OWL for comparison.
# The generated value $(ONTBASE).owl = https://w3id.org/metpo.owl (404).
# Correct URL is https://w3id.org/metpo/metpo.owl = $(ONTBASE)/$(ONT).owl.
CURRENT_RELEASE = $(ONTBASE)/$(ONT).owl

# The generated $(ONT).owl and $(ONT).json recipes use $(URIBASE)/$@ which
# expands to https://w3id.org/metpo.owl — wrong (missing /metpo/ path segment).
# The correct IRI is https://w3id.org/metpo/metpo.owl = $(ONTBASE)/$@.
# Root cause: metpo-odk.yaml sets uribase: https://w3id.org (the bare domain)
# because the ODK Python tooling derives ONTBASE as $(URIBASE)/$(id), and
# changing uribase to https://w3id.org/metpo would give ONTBASE
# https://w3id.org/metpo/metpo (double segment) and break all sub-artifact IRIs.
# These recipe overrides are the correct long-term fix until ODK provides a way
# to set URIBASE and ONTBASE independently in the config.
# Tracked at: https://github.com/berkeleybop/metpo/issues/465

$(ONT).owl: $(ONT)-full.owl
	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert -o $@.tmp.owl && mv $@.tmp.owl $@

$(ONT).json: $(ONT).owl
	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert --check false -f json -o $@.tmp.json &&\
		mv $@.tmp.json $@

# The generated $(ONT)-base.owl recipe uses --base-iri $(URIBASE)/METPO (uppercase)
# which matches no METPO terms (all IRIs are lowercase https://w3id.org/metpo/<id>),
# silently producing empty base artifacts. Fixed in https://github.com/berkeleybop/metpo/issues/463
# and tracked as a known ODK upgrade regression in https://github.com/berkeleybop/metpo/issues/465.
$(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
	reason --reasoner $(REASONER) --equivalent-classes-allowed asserted-only --exclude-tautologies structural --annotate-inferred-axioms false \
	relax $(RELAX_OPTIONS) \
	reduce -r $(REASONER) $(REDUCE_OPTIONS) \
	remove --base-iri $(URIBASE)/metpo --axioms external --preserve-structure false --trim false \
	$(SHARED_ROBOT_COMMANDS) \
	annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
		--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $@.tmp.owl && mv $@.tmp.owl $@
