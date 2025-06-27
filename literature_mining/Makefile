# requires robot and Mike Farah's GO yq as system dependencies

# Number of random PMIDs to sample (can be overridden from command line)
N_PMIDS ?= 10

.PHONY:  clean all validate-base-template extract-all extract-random random-n4l-pmids.txt

clean:
	rm -f *-abstract.txt
	rm -f *-output.yaml
	rm -f chem_interaction_props.tsv
	rm -f chem_interaction_props_enum.yaml
	rm -f ontogpt_template.yaml*
	rm -rf metpo-relation-graph.tsv.gz
	rm -rf metpo.db
	rm -rf metpo.owl
	rm -rf abstracts

all: clean abstracts/35476601-abstract.txt chem_interaction_props_enum.yaml metpo.db validate-base-template ontogpt_template.yaml 21602360-output.yaml 35476601-output.yaml

chem_interaction_props.tsv:
	robot query \
		--query chem_interaction_props.rq $@ \
		--input ../metpo.owl

chem_interaction_props_enum.yaml: chem_interaction_props.tsv
	poetry run convert-chem-props -i $< -o $@

metpo.db:
	# for very latest version
	# OAK should also be able to get this automatically, but it might be an older version
	cp ../metpo.owl .
	poetry run semsql make $@
	rm -rf metpo.owl
	rm -rf metpo-relation-graph.tsv.gz

validate-base-template: ontogpt_template_base.yaml
	poetry run linkml validate --schema $<

ontogpt_template.yaml: ontogpt_template_base.yaml chem_interaction_props_enum.yaml
	yq eval-all ' select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base ' $^ | cat > $@.tmp
	yq '.classes.OrganismCompoundRelationship.attributes.relationship_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

# Pattern rules for arbitrary PMIDs
abstracts/%-abstract.txt:
	# abstract body on one line
	mkdir -p abstracts
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "$*" > $@

%-output.yaml: ontogpt_template.yaml abstracts/%-abstract.txt
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts/$*-abstract.txt > $@

# Extract from all abstracts in directory
extract-all: ontogpt_template.yaml
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts -o all-extractions.yaml

# Download abstracts for random PMIDs and extract
# Usage: make extract-random (uses default 10 PMIDs) or make extract-random N_PMIDS=25 (uses 25 PMIDs)
extract-random: ontogpt_template.yaml
	rm -f random-n4l-pmids.txt
	rm -rf abstracts
	$(MAKE) random-n4l-pmids.txt
	mkdir -p abstracts
	while read pmid; do \
		echo "Fetching abstract for PMID: $$pmid"; \
		poetry run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt"; \
	done < random-n4l-pmids.txt
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts -o random-extractions.yaml

random-n4l-pmids.txt: n4l/reference_id_mapping.csv
	cut -f3 -d, $< | sort | uniq |  grep '^[0-9]*$$' |  shuf -n $(N_PMIDS) > $@
