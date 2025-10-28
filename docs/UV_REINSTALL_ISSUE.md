# UV Package Reinstall Issue

## Summary
Every `uv run python` command shows "Uninstalled 2 packages" and "Installed 1 package", even for consecutive runs of the same script.

## Observed Behavior

```bash
$ uv run python script1.py
Uninstalled 2 packages in 0.65ms
Installed 1 package in 13ms
[script output]

$ uv run python script2.py
Uninstalled 2 packages in 0.57ms
Installed 1 package in 11ms
[script output]
```

This happens every single time, even running the same script twice.

## Environment
- uv version: (need to check)
- Python: 3.11.10
- Project: /home/mark/gitrepos/metpo
- Working directory: /home/mark/gitrepos/metpo/notebooks

## Investigation Needed

1. Check uv version
2. Check if this is related to running from notebooks/ subdirectory
3. Check if uv.lock has issues
4. Check if there's a conflict in dependencies
5. Look at uv logs (if available)

## Hypotheses

1. Dependency conflict causing constant resolution
2. Running from subdirectory confuses uv
3. Lock file corruption
4. Known uv bug in this version
5. Something with inline script dependencies

## Root Cause (SOLVED)

Using `uv run --verbose` revealed:
```
DEBUG Uninstalled metpo (0 files, 0 directories)
DEBUG Uninstalled metpo (18 files, 1 directory)
Uninstalled 2 packages in 0.55ms
Installed 1 package in 4ms
 - metpo==0.1.0
 ~ metpo==0.3.0
```

**Two versions of the metpo package were installed** (0.1.0 and 0.3.0), causing uv to remove both and reinstall on every run.

**Likely cause:** The notebooks/ scripts use optional dependencies defined in `[project.optional-dependencies]`:
- `notebooks = ["chromadb", "jupyter", "tqdm", "python-dotenv", ...]`

These weren't installed initially, causing dependency conflicts.

## Solution

```bash
cd /home/mark/gitrepos/metpo
rm -rf .venv
uv sync --extra notebooks  # Or --all-extras for everything
```

After this, `uv run python` commands no longer reinstall packages on every run.

## Environment Details
- uv version: 0.6.12
- Project version: metpo 0.3.0
- Python: 3.11.10
