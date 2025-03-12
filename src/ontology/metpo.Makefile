## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

SRC_URL = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv'

metpo-robot-template.tsv:
	curl -L -s $(SRC_URL) > $@

metpo-robot-template.owl: metpo-robot-template.tsv
	# the prefix METPO is used in the Google Sheet so we provide an expansion here
	# check the -edit.owl and other sources of prefix expansion!
	robot template \
	  --add-prefix 'METPO: https://w3id.org/metpo/' \
	  --add-prefix 'oio: http://www.geneontology.org/formats/oboInOwl#' \
	  --template $< \
	  -o $@

# 	  -t $< \
  #	  annotate --annotation-file aio-annotations.ttl \