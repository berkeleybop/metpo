## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

# Sheet IDs:
# gid=1427185859 = comprehensive classes sheet (disabled - too comprehensive for current build)
# gid=355012485 = minimal set of classes (currently used)
# gid=907926993 = synonyms sheet
# gid=2094089867 = properties sheet

SRC_URL_MAIN = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=355012485'
SRC_URL_SYNONYMS = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=907926993'
SRC_URL_PROPERTIES = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=2094089867'

# Disabled comprehensive classes sheet:
# SRC_URL_COMPREHENSIVE = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=1427185859'

.PHONY: squeaky-clean clean-templates

../templates/metpo_sheet.tsv:
	curl -L -s $(SRC_URL_MAIN) > $@

../templates/metpo-synonyms.tsv:
	curl -L -s $(SRC_URL_SYNONYMS) > $@

../templates/metpo-properties.tsv:
	curl -L -s $(SRC_URL_PROPERTIES) > $@

squeaky-clean: clean clean-templates

clean-templates:
	rm -rf ../templates/metpo_sheet.tsv
	rm -rf ../templates/metpo-synonyms.tsv
	rm -rf ../templates/metpo-properties.tsv
	rm -rf components/metpo_sheet.owl
	rm -rf components/metpo-synonyms.owl
	rm -rf components/metpo-properties.owl

#$(MIRRORDIR)/mpo.owl: ../../assets/mpo_v0.74.en_only.owl
#	cp $^ $@
#
#$(MIRRORDIR)/micro.owl: ../../assets/MicrO-for-metpo.owl.gz
#	robot remove \
#			-i $< \
#			--axioms equivalent \
#			--output $@
