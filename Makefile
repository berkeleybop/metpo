
local/salinity_parsed_llm.tsv: metpo/salinity_raw_text_input.csv local/.env
	poetry run python metpo/parse_salinity_llm.py \
		--input-csv $< \
		--output-tsv $@ \
		--env-file local/.env \
		--batch-size 20
