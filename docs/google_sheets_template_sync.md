# Google Sheets Template Sync Guide

The Google Sheet was retired as a METPO build input on 2026-09-03.
The committed ROBOT templates in `src/templates/` are now the source of truth.
`src/ontology/metpo.Makefile` builds from those TSVs directly.
`make squeaky-clean` no longer deletes or re-fetches `metpo_sheet.tsv` or `metpo-properties.tsv`.
Edit template rows in `src/templates/` and send changes through pull requests.
Keep review, CI, and history in Git rather than syncing live Sheet tabs.
