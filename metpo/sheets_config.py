"""Load METPO Google Sheets configuration from sheets.yaml.

All scripts that reference the METPO spreadsheet should use this module
rather than hardcoding GIDs. See https://github.com/berkeleybop/metpo/issues/372
"""

from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "sheets.yaml"


def _load() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


_config = _load()

SPREADSHEET_ID: str = _config["spreadsheet_id"]

SHEET_GIDS: dict[str, str] = {name: sheet["gid"] for name, sheet in _config["primary"].items()}

TEMPLATE_PATHS: dict[str, str] = {
    name: sheet["template_path"] for name, sheet in _config["primary"].items()
}


def export_url(sheet: str) -> str:
    """Return the Google Sheets TSV export URL for a primary sheet."""
    gid = SHEET_GIDS[sheet]
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?exportFormat=tsv&gid={gid}"
    )


def all_export_urls() -> dict[str, str]:
    """Return export URLs for all sheets (primary + secondary)."""
    urls = {}
    for section in ("primary", "secondary"):
        for name, sheet in _config.get(section, {}).items():
            gid = sheet["gid"]
            urls[name] = (
                f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
                f"/export?exportFormat=tsv&gid={gid}"
            )
    return urls
