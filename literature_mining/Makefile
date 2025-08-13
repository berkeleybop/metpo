# requires robot and Mike Farah's GO yq as system dependencies

# Number of random PMIDs to sample (can be overridden from command line)
N_PMIDS ?= 10

# PMID file to use for extraction (can be overridden from command line)
PMID_FILE ?= random-n4l-pmids.txt

# Source for pipeline (can be overridden from command line)
SOURCE ?= ijsem
N_ABSTRACTS ?= 5

.PHONY: clean all validate-base-template clean-abstracts clean-pmids full-pipeline quick-test

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

# Chemical properties extraction
chem_interaction_props.tsv: ../metpo.owl
	robot query \
		--query chem_interaction_props.rq $@ \
		--input $<

chem_interaction_props_enum.yaml: chem_interaction_props.tsv
	poetry run convert-chem-props -i $< -o $@

# Database creation
metpo.db: ../metpo.owl
	# for very latest version
	# OAK should also be able to get this automatically, but it might be an older version
	cp $< metpo.owl
	poetry run semsql make $@
	rm -rf metpo.owl
	rm -rf metpo-relation-graph.tsv.gz

# Template validation and creation
validate-base-template: ontogpt_template_base.yaml
	poetry run linkml validate --schema $<

ontogpt_template.yaml: ontogpt_template_base.yaml chem_interaction_props_enum.yaml
	yq eval-all ' select(fileIndex == 0) as $$base | select(fileIndex == 1).enums.ChemicalInteractionPropertyEnum as $$enum | $$base.enums.ChemicalInteractionPropertyEnum = $$enum | $$base ' $^ | cat > $@.tmp
	yq '.classes.OrganismCompoundRelationship.attributes.relationship_type.range = "ChemicalInteractionPropertyEnum"' $@.tmp > $@
	rm -f $@.tmp

# Individual abstract fetching (pattern rule)
abstracts/%-abstract.txt:
	mkdir -p abstracts
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "$*" > $@

# Individual extraction (pattern rule)  
%-output.yaml: ontogpt_template.yaml abstracts/%-abstract.txt metpo.db
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts/$*-abstract.txt > $@

# PMID file generation
random-n4l-pmids.txt: n4l/reference_id_mapping.csv
	cut -f3 -d, $< | sort | uniq | grep '^[0-9]*$$' | shuf -n $(N_PMIDS) > $@

random-bacdive-pmids.txt:
	mongosh --quiet bacdive --eval "db.strains_api.aggregate([{\$$unwind: '\$$External links.literature'}, {\$$match: {'External links.literature.Pubmed-ID': {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$group: {_id: '\$$External links.literature.Pubmed-ID'}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc._id); })" > $@

random-ijsem-pmids.txt:
	mongosh --quiet europepmc --eval "db.ijsem_articles.aggregate([{\$$match: {pmid: {\$$exists: true, \$$ne: null, \$$ne: ''}}}, {\$$sample: {size: $(N_PMIDS)}}]).forEach(function(doc) { print(doc.pmid); })" > $@

# Abstract directory creation based on PMID file
abstracts/.built: $(PMID_FILE)
	rm -rf abstracts
	mkdir -p abstracts
	head -n $(N_ABSTRACTS) $< | while read pmid; do \
		echo "Fetching abstract for PMID: $$pmid"; \
		poetry run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt"; \
	done
	touch $@

# Extraction from all abstracts in directory
all-extractions.yaml: ontogpt_template.yaml metpo.db abstracts/.built
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts -o $@

# Legacy targets for backwards compatibility
extract-all: all-extractions.yaml

fetch-abstracts: abstracts/.built

extract-random: random-extractions.yaml

random-extractions.yaml: ontogpt_template.yaml metpo.db $(PMID_FILE)
	rm -rf abstracts
	mkdir -p abstracts
	while read pmid; do \
		echo "Fetching abstract for PMID: $$pmid"; \
		poetry run artl-cli get-abstract-from-pubmed-id --pmid "$$pmid" > "abstracts/$$pmid-abstract.txt"; \
	done < $(PMID_FILE)
	poetry run ontogpt extract -t ontogpt_template.yaml -i abstracts -o $@

# Cleanup targets
clean-abstracts:
	rm -rf abstracts

clean-pmids:
	rm -f random-*-pmids.txt

# Pipeline targets
full-pipeline: PMID_FILE = random-$(SOURCE)-pmids.txt
full-pipeline: all-extractions.yaml

quick-test: PMID_FILE = random-$(SOURCE)-pmids.txt
quick-test: N_PMIDS = 5  
quick-test: N_ABSTRACTS = 3
quick-test: all-extractions.yaml