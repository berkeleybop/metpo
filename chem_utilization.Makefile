chem_utilization_abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=21602364&rettype=abstract&retmode=text" \
		-o $@

pmid_33936009_abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=33936009&rettype=abstract&retmode=text" \
		-o $@

chem_utilization_abstract_output.yaml: chem_utilization_template_with_phenotypes.yaml chem_utilization_abstract.txt
	poetry run ontogpt extract -t $(word 1, $^) -i $(word 2, $^) > $@

pmid_33936009_abstract_output.yaml: chem_utilization_template_with_phenotypes.yaml pmid_33936009_abstract.txt
	poetry run ontogpt extract -t $(word 1, $^) -i $(word 2, $^) > $@
