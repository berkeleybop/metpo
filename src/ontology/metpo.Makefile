## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

SRC_URL = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=1427185859'

.PHONY: squeaky-clean clean-templates

../templates/metpo_sheet.tsv:
	curl -L -s $(SRC_URL) > $@

squeaky-clean: clean clean-templates

clean-templates:
	rm -rf ../templates/metpo_sheet.tsv
	rm -rf components/metpo_sheet.owl

#$(MIRRORDIR)/mpo.owl: ../../assets/mpo_v0.74.en_only.owl
#	cp $^ $@
#
#$(MIRRORDIR)/micro.owl: ../../assets/MicrO-for-metpo.owl.gz
#	robot remove \
#			-i $< \
#			--axioms equivalent \
#			--output $@
