## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

SRC_URL = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=1905096712'

.PHONY: squeaky-clean clean-templates

../templates/metpo_sheet.tsv:
	curl -L -s $(SRC_URL) > $@

squeaky-clean: clean clean-templates

clean-templates:
	rm -rf ../templates/metpo_sheet.tsv
	rm -rf components/metpo_sheet.owl

$(MIRRORDIR)/mpo.owl: ../../assets/mpo_v0.74.en_only.owl
	cp $^ $@

$(MIRRORDIR)/micro.owl: ../../assets/MicrO-for-metpo.owl.gz
	robot remove \
			-i $< \
			--axioms equivalent \
			--output $@

# \
#		remove \
#			--term MICRO:0001468 \
#			--term MICRO:0001522 \
#			--axioms TransitiveObjectProperty \
#		remove \
#			--term GO:0003674 \
#			--term CHEBI:50906 \
#			--select self \
#			--axioms subclass \
#			--signature true \
#			--trim false \
#		remove \
#			--term GO:0003824 \
#			--term BFO:0000017 \
#			--select self \
#			--axioms subclass \
#			--signature true \
#			--trim false \
#			--output $@
