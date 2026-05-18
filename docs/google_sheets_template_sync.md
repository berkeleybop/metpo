# Google Sheets ↔ Repo Template Sync Guide

## Spreadsheet Reference

- **Spreadsheet:** [METPO - growth_condition_terms](https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/)
- **Spreadsheet ID:** `1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU`

### Active sheet tabs

| Sheet tab | gid | Repo file | Role |
|---|---|---|---|
| `classes-2026-03-24` | `1569766102` | `src/templates/metpo_sheet.tsv` | Current classes template (281 IDs) |
| `properties-2026-03-24` | `681401984` | `src/templates/metpo-properties.tsv` | Current properties template (135 IDs) |
| `relabeled classes` | `121955004` | — | Previous classes sheet (used by `squeaky-clean` download) |
| `properties` | `2094089867` | — | Previous properties sheet (used by `squeaky-clean` download) |

**Note:** The `squeaky-clean` download targets in `metpo.Makefile` still point at the old gids (`121955004`, `2094089867`). Update these to the new gids when the new sheets are promoted to primary.

## Downloading from Google Sheets (sheet → repo)

Automated via `metpo.Makefile`:
```bash
cd src/ontology
sh run.sh make squeaky-clean   # deletes local templates
sh run.sh make all             # re-downloads from Google Sheets + builds
```

Or manually:
```bash
curl -sL 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=1569766102' > src/templates/metpo_sheet.tsv
curl -sL 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=681401984' > src/templates/metpo-properties.tsv
```

## Uploading to Google Sheets (repo → sheet)

There is no API-based upload. Use **File → Import** in Google Sheets.

### Critical: use Import, not Paste

**Pasting TSV content into Google Sheets mangles data:**
- Bare `+` and `-` values are interpreted as formulas (`=+`, `=-`)
- Leading single quotes (used in Manchester OWL syntax like `'GC content' and ...`) are stripped — Sheets treats `'` as a "force text" prefix and removes it from the stored value
- Find-and-replace workarounds are fragile and error-prone

**Import preserves data correctly** when configured properly.

### Import procedure

1. Create a **new sheet tab** in the spreadsheet (don't overwrite the existing tab — keep it as a reference until the new one is verified)
2. Navigate to the new tab
3. **File → Import → Upload** → select the `.tsv` file from your local filesystem
4. Configure the import dialog:
   - **Import location:** "Replace current sheet" (NOT "Replace spreadsheet" — that wipes ALL tabs)
   - **Separator type:** Tab
   - **Convert text to numbers, dates, and formulas:** **UNCHECKED** (this is the critical setting)
5. Click "Import data"
6. Verify with `diff-templates`:
   ```bash
   curl -sL 'https://docs.google.com/spreadsheets/d/.../export?exportFormat=tsv&gid=NEW_GID' > /tmp/verify.tsv
   uv run diff-templates -a /tmp/verify.tsv -b HEAD -t classes --cell-diffs
   ```
7. Once verified, note the new gid (visible in the URL bar) and update `metpo.Makefile`

### Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| "Replace spreadsheet" instead of "Replace current sheet" | All other tabs deleted | Restore from File → Version history |
| "Convert text to numbers..." checked | `+`/`-` become formulas, leading `'` stripped | Re-import with checkbox unchecked |
| Pasting instead of importing | Same as above | Use Import instead |
| Not backing up first | No recovery if something goes wrong | Download TSV backup before making changes |

## Diffing templates

```bash
# Google Sheet vs current HEAD
uv run diff-templates

# Google Sheet vs last release
uv run diff-templates -a gsheet -b 2025-12-12

# Current branch vs main, with cell-level diffs
uv run diff-templates -a HEAD -b main --cell-diffs

# Makefile shortcuts (from src/ontology/)
make diff-sheets    # Google Sheet vs HEAD
make diff-release   # last tag vs HEAD
```

## Backing up before changes

```bash
mkdir -p downloads/sheets/backups
curl -sL 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=121955004' > downloads/sheets/backups/classes_backup_$(date +%Y-%m-%d).tsv
curl -sL 'https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/export?exportFormat=tsv&gid=2094089867' > downloads/sheets/backups/properties_backup_$(date +%Y-%m-%d).tsv
```

Google Sheets also maintains version history (File → Version history) which can restore any prior state.

## Build-time URL resolution (host vs ODK container)

The Makefile rules that download templates from the Google Sheet need to resolve the export URL at parse time. Resolution has to work in two environments:

| Environment | python3 | pyyaml | uv | metpo package importable |
|---|---|---|---|---|
| ODK container (`sh run.sh make ...`) | yes | yes | **no** | no |
| Host with active uv venv | yes (venv) | yes | yes | yes (editable install) |
| Host plain (`python3` from Homebrew or system) | yes | usually **no** | maybe | no |

`src/ontology/metpo.Makefile` uses a two-tier fallback:

1. **Hardcoded defaults** (`SPREADSHEET_ID`, `SRC_URL_MAIN`, `SRC_URL_PROPERTIES` at the top of the file) — always work regardless of environment.
2. **Override from sheets.yaml** — runs `python3 ../../metpo/sheets_config.py classes` (and `properties`). If python3 + pyyaml are present, this prints the URL derived from `sheets.yaml`, and Make overrides the hardcoded default. If anything fails (`ModuleNotFoundError`, missing file, etc.), stderr is swallowed and the hardcoded default stands.

`metpo/sheets_config.py` is **both** an importable module (used by Python scripts in the repo) **and** a runnable script (used by Makefiles). The `if __name__ == "__main__":` block at the bottom calls `export_url(sys.argv[1])`.

### Why two tiers instead of one

Earlier, the Makefile invoked `uv run python -c "from metpo.sheets_config import export_url; ..."`. That worked on host but failed silently inside the ODK container with `/bin/sh: 1: uv: not found`, returning an empty URL and producing a zero-byte `metpo_sheet.tsv`. The two-tier setup keeps the central-source-of-truth benefit of `sheets.yaml` (issue [#372](https://github.com/berkeleybop/metpo/issues/372)) while making the build robust to environments that lack `uv` or `pyyaml`.

### When sheet GIDs change

Update both `sheets.yaml` AND the hardcoded `SRC_URL_MAIN` / `SRC_URL_PROPERTIES` defaults in `src/ontology/metpo.Makefile`. The yaml-derived value is preferred when available, but the hardcoded fallback should not drift far from reality.

## Related issues

- [#366](https://github.com/berkeleybop/metpo/issues/366) — Template lifecycle: diff, sync, and push workflow
- [#365](https://github.com/berkeleybop/metpo/issues/365) — Properties template needs per-source synonym columns
- [#372](https://github.com/berkeleybop/metpo/issues/372) — Centralize Google Sheets GIDs in single config file (introduced `sheets.yaml`)
- [#433](https://github.com/berkeleybop/metpo/issues/433) — Umbrella: SoT switch + agentic-maintenance guardrails
