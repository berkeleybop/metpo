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

$(MIRRORDIR)/micro.owl: ../../assets/MicrO-2025-03-20-merged.owl.gz
	gzip -dc $^ > $@
	robot remove -i $@ --axioms equivalent -o micro_temp.owl
	robot remove \
	  --input micro_temp.owl \
	  --term GO:0003674 \
	  --term CHEBI:50906 \
	  --select self \
	  --axioms subclass \
	  --signature true \
	  --trim false \
	  --output $@
	robot remove \
	  --input $@ \
	  --term GO:0003824 \
	  --term BFO:0000017 \
	  --select self \
	  --axioms subclass \
	  --signature true \
	  --trim false \
	  --output micro_temp.owl
	mv micro_temp.owl $@
	rm -rf micro_temp.owl
