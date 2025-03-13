## Customize Makefile settings for metpo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

SRC_URL = 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv'

../templates/metpo_sheet.tsv:
	curl -L -s $(SRC_URL) > $@
