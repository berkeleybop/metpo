pubmed.39465541.ttl: pubmed.39465541.tsv
	robot template \
		--template $< \
		--prefix 'pubmed.39465541: http://example.com/pubmed.39465541/' \
		--output $@

#ijsem.0.006558.pdf:
#	curl -L \
#		"https://www.microbiologyresearch.org/content/journal/ijsem/10.1099/ijsem.0.006558?crawler=true&mimetype=application/pdf" \
#		-o $@
#
## then convert to abstract text, or just fetch abstract only in the first place?
#
#ijsem.0.006558.txt: ijsem.0.006558.pdf
#	pdftotext -layout $< $@

pubmed.39465541.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=39465541&rettype=abstract&retmode=text" \
		-o $@

pubmed.21602360.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=21602360&rettype=abstract&retmode=text" \
		-o $@

pubmed.17684263.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=17684263&rettype=abstract&retmode=text" \
		-o $@

pubmed.39465541.abstract.output.yaml: pubmed.39465541.abstract.txt pubmed.39465541.ttl
	poetry run ontogpt extract -t pubmed.39465541.template.yaml -i $< > $@

#pubmed.17684263.abstract.output.yaml: pubmed.17684263.abstract.txt
#	poetry run ontogpt extract -t microbial_phenotype_relations_template.yaml -i $< > $@

pubmed.17684263.abstract.output.yaml: pubmed.17684263.abstract.txt
	poetry run ontogpt extract -t microbial_phenotype_relations_template.yaml -i $< > $@

