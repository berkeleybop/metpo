f_multiformis.ttl: f_multiformis.tsv
	robot template \
		--template $< \
		--prefix 'f_multiformis: http://example.com/f_multiformis/' \
		--output $@

ijsem.0.006558.pdf:
	curl -L \
		"https://www.microbiologyresearch.org/content/journal/ijsem/10.1099/ijsem.0.006558?crawler=true&mimetype=application/pdf" \
		-o $@

# then convert to abstract text, or just fetch abstract only in the first place?

ijsem.0.006558.txt: ijsem.0.006558.pdf
	pdftotext -layout $< $@

ijsem.0.006558.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=39465541&rettype=abstract&retmode=text" \
		-o $@

ijsem.0.030973-0.abstract.txt: # will contain special whitespace and also author, title, etc
	curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi" \
		-d "db=pubmed&id=21602360&rettype=abstract&retmode=text" \
		-o $@

ijsem.0.006558.abstract.output.yaml: ijsem.0.006558.abstract.txt f_multiformis.ttl
	poetry run ontogpt extract -t f_multiformis_template.yaml -i $< > $@

