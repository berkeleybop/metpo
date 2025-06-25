.PHONY: all bacdive_utilization_all bacdive_utilization_clean

all: bacdive_utilization_all

bacdive_utilization_all: bacdive_utilization_clean bacdive_utilization_enum.yaml bacdive_utilization_template.yaml

bacdive_utilization_clean:
	rm -rf bacdive_utilization.tsv
	rm -rf bacdive_utilization.ttl
	rm -rf bacdive_utilization_enum.yaml
	rm -rf bacdive_utilization_template.yaml

bacdive_utilization.tsv:
	wget -O $@ 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=619442214'

bacdive_utilization.ttl: bacdive_utilization.tsv
	robot template --template $< --output $@

bacdive_utilization_enum.yaml: bacdive_utilization.tsv
	poetry run python make_bacdive_utilization_enum.py \
		--default-prefix bacdive_utilizations \
		--enum-name RelationshipTypeEnum \
		--id-prefix "https://example.org/bacdive_utilizations" \
		--no-preview \
		--no-stats \
		--output $@ $<

bacdive_utilization_template.yaml: bacdive_utilizations_template_legacy.yaml bacdive_utilization_enum.yaml
	yq eval-all ' select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.RelationshipTypeEnum as $$enum | $$base.enums.RelationshipTypeEnum = $$enum | $$base ' $^ | cat > $@

pmid.21602360.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=21602360&rettype=abstract&retmode=text" \
		-o $@

pmid.21602360.abstract.output.yaml: pmid.21602360.abstract.txt
	poetry run ontogpt extract -t bacdive_utilization_template.yaml -i $< > $@