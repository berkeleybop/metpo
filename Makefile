WGET=wget
UNZIP=unzip

# see https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt regarding nodes.dmp

downloads/taxdmp.zip:
	$(WGET) -O $@ "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"

local/taxdmp: downloads/taxdmp.zip
	$(UNZIP) $< -d $@

local/taxdmp/nodes.dmp: local/taxdmp

# Extract taxonomy rank triples from NCBI nodes.dmp file to a TTL file
local/noderanks.ttl: local/taxdmp/nodes.dmp
	poetry run extract-rank-triples --input-file $< --output-file $@
