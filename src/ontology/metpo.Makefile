## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

# Sheet IDs (spreadsheet: 1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU):
# gid=1427185859 = comprehensive classes sheet (disabled - too comprehensive for current build)
# gid=355012485 = minimal set of classes (previous)
# gid=121955004 = cleaned definition sources (currently used for download)
# gid=907926993 = synonyms sheet
# gid=2094089867 = properties sheet (currently used for download)
# gid=681401984 = properties-2026-03-24 (updated 2026-03-24, matches PR #355)
# gid=1569766102 = classes-2026-03-24 (updated 2026-03-24, matches PR #355)

SRC_URL_MAIN = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=121955004'
# SRC_URL_SYNONYMS = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=907926993'
SRC_URL_PROPERTIES = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=2094089867'

# Disabled comprehensive classes sheet:
# SRC_URL_COMPREHENSIVE = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=1427185859'

DRAFTS_DIR = ../templates/drafts

.PHONY: squeaky-clean clean-templates save-drafts install-drafts diff-drafts diff-sheets diff-release

# Save current templates to drafts (before squeaky-clean)
save-drafts:
	mkdir -p $(DRAFTS_DIR)
	cp ../templates/metpo_sheet.tsv $(DRAFTS_DIR)/metpo_sheet.tsv
	cp ../templates/metpo-properties.tsv $(DRAFTS_DIR)/metpo-properties.tsv
	@echo "Templates saved to $(DRAFTS_DIR)/"

# Install drafts over Google Sheets downloads (after squeaky-clean + curl)
install-drafts: ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv
	cp $(DRAFTS_DIR)/metpo_sheet.tsv ../templates/metpo_sheet.tsv
	cp $(DRAFTS_DIR)/metpo-properties.tsv ../templates/metpo-properties.tsv
	@echo "Draft templates installed over Google Sheets versions"

# Show what changed between Google Sheets and drafts
diff-drafts: ../templates/metpo_sheet.tsv ../templates/metpo-properties.tsv
	@diff $(DRAFTS_DIR)/metpo_sheet.tsv ../templates/metpo_sheet.tsv || true
	@diff $(DRAFTS_DIR)/metpo-properties.tsv ../templates/metpo-properties.tsv || true

../templates/metpo_sheet.tsv:
	curl -L -s $(SRC_URL_MAIN) > $@

#../templates/metpo-synonyms.tsv:
#	curl -L -s $(SRC_URL_SYNONYMS) > $@

../templates/metpo-properties.tsv:
	curl -L -s $(SRC_URL_PROPERTIES) > $@

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

components/metpo_sheet.owl: ../templates/stubs.tsv ../templates/metpo-properties.tsv ../templates/metpo_sheet.tsv
	$(ROBOT) template \
		--add-prefix 'METPO: https://w3id.org/metpo/' \
		--add-prefix 'qudt: http://qudt.org/schema/qudt/' \
		--template ../templates/stubs.tsv \
		--template ../templates/metpo_sheet.tsv \
		--template ../templates/metpo-properties.tsv \
		annotate --ontology-iri $(ONTBASE)/$@ \
		annotate -V $(ONTBASE)/releases/$(TODAY)/$@ \
		--annotation owl:versionInfo $(TODAY) \
		convert -f ofn --output $@.tmp.owl && mv $@.tmp.owl $@
