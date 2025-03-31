Questions:

- where are the links between N4L phenotypes and N4L taxa?
- are there N4L/METPO classes that represent the same thing but are hard to lexmatch? "Flagellum feature" 
- what proportion of lexmatch time is index building? esp for GO and OBA

Notes

- multiple asserted hierarchy
    - check biological veracity
    - use subsets when that would be purer or easier to define than class hierarchy
- missing inter-class axioms

Repeat lexmatch -> SSSOM TSV
- 00 bacdive D3O file, esp distinguish questions from answers/values 320 KB. look for uncovered classes. roundtrip
through robot first. in 30 seconds DONE
- 00 fao file 220 KB fast
- 00 ido 2 MB in 20 seconds DONE
- 01 mpo 160 KB file in 1 minutes DONE
- 01 n4l file 3 MB in 1 minutes DONE
- 01 obi 37 MB in 1 minute DONE
- 01 omp 11 MB in 1 minute DONE
- 02 mco file 17 MB in 2 minute DONE
- 02 metpo legacy file from Google Sheet 1.2 MB ... esp look for uncovered classes in 2 minutes DONE
- 02 pato 144 MB in 2 minutes DONE
- 02 so 13 MB in 2 minutes DONE
- 03 micro file 5 MB in 3 minutes DONE
- 04 fypo 300 MB in 4 minutes DONE
- 14 oba 1.8 GB in 14 minutes DONE
- 17 go 1.7 GB in 17 minutes DONE

- examples
  - date && time poetry run runoak -i metpo-cleanroom.ttl -a metpo.owl lexmatch -o metpo-vs-legacy.tsv i^http://example.org/metpo-cleanroom @ .classes && date
  - date && time poetry run runoak -i metpo-cleanroom.ttl -a sqlite:obo:pato lexmatch -o metpo-vs-pato.tsv i^http://example.org/metpo-cleanroom @ .classes && date
- rank filter and sort with 
