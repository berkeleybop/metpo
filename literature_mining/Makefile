# requires robot and Mike Farah's GO yq as system dependencies


# artl-cli --help
# artl-cli get-abstract-from-pubmed-id --help

#Sideroxyarcus emersonii gen. nov. sp. nov., a neutrophilic, microaerobic iron- and thiosulfate-oxidizing bacterium isolated from iron-rich wetland sediment
#Shingo Kato 1, Takashi Itoh 1, Takao Iino 1, Moriya Ohkuma 1
#Affiliations Expand
#PMID: 35476601
#DOI: 10.1099/ijsem.0.005347

# or PMID:21602360

.PHONY:  clean all

clean:
	rm -f *-abstract.txt
	rm -f *-output.yaml
	rm -f chem_interaction_props.tsv
	rm -f chem_interaction_props_enum.yaml
	rm -f ontogpt_template.yaml*
	rm -rf metpo-relation-graph.tsv.gz
	rm -rf metpo.db
	rm -rf metpo.owl

all: clean 35476601-abstract.txt chem_interaction_props_enum.yaml metpo.db validate-base-template ontogpt_template.yaml 35476601-output.yaml

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
%-abstract.txt:
	# abstract body on one line
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "$*" > $@

%-output.yaml: ontogpt_template.yaml %-abstract.txt
	poetry run ontogpt extract -t ontogpt_template.yaml -i $*-abstract.txt > $@

# Specific targets (kept for backward compatibility)
35476601-abstract.txt:
	# abstract body on one line
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "35476601" > $@

35476601-output.yaml: ontogpt_template.yaml 35476601-abstract.txt
	poetry run ontogpt extract -t ontogpt_template.yaml -i35476601-abstract.txt > $@
