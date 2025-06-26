# artl-cli --help
# artl-cli get-abstract-from-pubmed-id --help

#Sideroxyarcus emersonii gen. nov. sp. nov., a neutrophilic, microaerobic iron- and thiosulfate-oxidizing bacterium isolated from iron-rich wetland sediment
#Shingo Kato 1, Takashi Itoh 1, Takao Iino 1, Moriya Ohkuma 1
#Affiliations Expand
#PMID: 35476601
#DOI: 10.1099/ijsem.0.005347

.PHONY:  clean all

clean:
	rm -f *-abstract.txt

all: clean 35476601-abstract.txt

35476601-abstract.txt:
	# abstract body on one line
	poetry run artl-cli get-abstract-from-pubmed-id --pmid "35476601" > $@
