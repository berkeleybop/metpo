## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

.PHONY: squeaky-clean clean-templates diff-release

#../templates/metpo-synonyms.tsv:
#	curl -L -s "$(SRC_URL_SYNONYMS)" > $@

squeaky-clean: clean clean-templates

# Remove generated component outputs while preserving committed TSV templates.
clean-templates:
	rm -rf components/metpo_sheet.owl
	rm -rf components/metpo-properties.owl

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
	python3 ../../metpo/bactotraits/create_stubs.py -o $@ ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv

# Repo-only — not in Google Sheets.
# IMPORTANT: ../templates/deprecated.tsv is hand-maintained source-of-truth.
# Intentionally no prerequisites: Make builds this file only if it is missing.
# The generation rule exists ONLY as a recovery/bootstrap tool from historical
# BioPortal submissions + tagged releases. Run `make regenerate-deprecated`
# to rebuild it deliberately; it removes the target first.
../templates/deprecated.tsv:
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

components/metpo_sheet.owl: ../templates/stubs.tsv ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv $(DEPRECATED_PREREQ)
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
