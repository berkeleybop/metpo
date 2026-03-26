# METPO Term Deprecation Workflow

**Purpose:** How to deprecate terms and allocate new IDs in METPO, and how the
deprecated-term machinery works.

---

## The Short Version

- `src/templates/deprecated.tsv` is the **authoritative list of all deprecated METPO terms**.
  It is committed to the repo and merged into `metpo.owl` on every release build.
- **Never reuse a burned ID.** Check `reports/id-allocation-audit.md` for the full list.
- When you deprecate a term, edit `deprecated.tsv` directly — do not re-run the research tools.
- When you add a new term, use the next safe ID from the audit report.

---

## Background: Three Eras of METPO IDs

METPO has gone through three numbering schemes. All are burned and must never be reused.

| Era | Format | Range | Status |
|-----|--------|-------|--------|
| Era 1 | 6-digit with leading zeros | `000001`–`000274` | Abandoned (submissions 2–3) |
| Era 2 | 7-digit with leading zeros | `0000001`–`0000351` | Abandoned (submissions 4–5) |
| Era 3 | `1xxxxxx` classes, `2xxxxxx` properties | `1000001`+ / `2000001`+ | Current scheme |

Within Era 3, IDs `1000001`–`1000327` were used for literature-mining terms (derived from
OntoGPT/IJSEM extraction) and retired in BioPortal submission 9. They must not be reused.

---

## Allocating New IDs

Run `make audit-ids` to regenerate `reports/id-allocation-audit.md` and get current
"next safe ID" values. As of the last regeneration:

- **Next safe class ID:** `METPO:1005041` (highest active class + 1)
- **Next safe property ID:** `METPO:2000735` (highest active property + 1)

Always use `make audit-ids` for current values — the numbers above go stale as terms are added.

---

## Deprecating a Term

When a term is removed from the active templates (`src/templates/metpo_sheet.tsv` or
`src/templates/metpo-properties.tsv`), it must be added to `src/templates/deprecated.tsv`.

### Step 1 — Remove from the active template

Delete the row from `metpo_sheet.tsv` or `metpo-properties.tsv`. This is typically done
by editing the upstream Google Sheet and running `make download-sheets`.

### Step 2 — Add a row to `src/templates/deprecated.tsv`

The file is a ROBOT template. Column layout:

```
ID            label                    TYPE              deprecated      obsolescence reason
ID            LABEL                    TYPE              A owl:deprecated  AI IAO:0000231
METPO:XXXXXXX obsolete <former label>  owl:Class         true            OMO:0001000
```

Add one row per deprecated term. Use:
- **label**: `obsolete ` + the former rdfs:label (e.g. `obsolete lyses`)
- **TYPE**: `owl:Class` for classes, `owl:ObjectProperty` / `owl:DataProperty` /
  `owl:AnnotationProperty` for properties
- **deprecated**: always `true`
- **obsolescence reason**: use `OMO:0001000` (out of scope) or `IAO:0000226`
  (placeholder removed) — see the existing rows for precedent. When in doubt, use
  `IAO:0000226`.

### Step 3 — Commit both changes together

The removal from the active template and the addition to `deprecated.tsv` should be in
the same commit so the ontology is never in a state where an ID simply vanishes.

### Step 4 — Verify

```bash
# Check the deprecated template is valid ROBOT input
uv run generate-deprecated-template --help   # confirms the CLI is available

# Regenerate the audit report to confirm the ID now shows as burned
make audit-ids
grep "METPO:XXXXXXX" reports/id-allocation-audit.md
```

---

## How `deprecated.tsv` Gets Into the Ontology

`src/ontology/metpo.Makefile` passes `deprecated.tsv` to ROBOT alongside the main
templates when building `components/metpo_sheet.owl`:

```makefile
components/metpo_sheet.owl: ... ../templates/deprecated.tsv
    $(ROBOT) template \
        --template ../templates/deprecated.tsv \
        ...
```

The resulting component is then merged into `metpo.owl` during `prepare_release`.
Every deprecated term in the file becomes a real OWL entity with:
- `owl:deprecated true`
- `rdfs:label "obsolete ..."`
- `IAO:0000231` (has obsolescence reason) annotation

---

## The Audit and Bootstrap Tools (Research Machinery)

Two CLI tools support this workflow:

### `audit-id-allocation` → `reports/id-allocation-audit.md`

```bash
make audit-ids
# or directly:
uv run audit-id-allocation -o reports/id-allocation-audit.md
```

Scans current templates, all BioPortal entity extracts under
`metadata/ontology/historical_submissions/entity_extracts/`, and all tagged git releases.
Produces a markdown report with active counts, burned ID lists, provenance chains, and
next safe IDs. **Run this before allocating any new ID.**

### `generate-deprecated-template` → `src/templates/deprecated.tsv`

```bash
make -C src/ontology -f metpo.Makefile regenerate-deprecated
# or directly:
uv run generate-deprecated-template -o src/templates/deprecated.tsv
```

Regenerates `deprecated.tsv` from scratch by rerunning the same scan as the audit tool.
**This is a bootstrap/recovery tool.** Under normal maintenance you should not need to
run it — just edit `deprecated.tsv` by hand when deprecating a term. Run it only if you
suspect `deprecated.tsv` has drifted from reality (e.g. after a large batch deprecation
or if the file is corrupted).

### How `deprecated.tsv` was originally created

`generate-deprecated-template` was run once (March 2026, PR #375) after a comprehensive
scan of all 9 BioPortal submissions and 13 tagged releases. It found 1,168 burned IDs
across all three eras and wrote them into `deprecated.tsv` with labels recovered from
the same historical sources. That file is now the source of truth — the scan tools exist
as a safety net, not as a required step in the maintenance loop.

If the BioPortal submission extracts or the `generate-deprecated-template` script are
ever removed, the methodology is documented in `docs/metpo_id_ranges_research.md` and
the full provenance is in `reports/id-allocation-audit.md`.

---

## Never-Reuse Checklist

Before allocating any new ID, verify it does not appear in:

1. `src/templates/metpo_sheet.tsv` or `src/templates/metpo-properties.tsv`
2. `src/templates/deprecated.tsv`
3. `reports/id-allocation-audit.md`

```bash
ID=1005041
grep "$ID" src/templates/*.tsv src/templates/deprecated.tsv reports/id-allocation-audit.md
```

If any of those grep hits, pick a different ID.
