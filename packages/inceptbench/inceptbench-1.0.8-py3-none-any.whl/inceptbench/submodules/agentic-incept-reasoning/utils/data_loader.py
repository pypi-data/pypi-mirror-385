"""
Utilities for loading and caching markdown files from the data/ folder.
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Dict


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _assert_data_dir_exists() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Expected data directory at {DATA_DIR}.")


@functools.lru_cache(maxsize=None)
def load_markdown_file(file_path: str | Path) -> str:
    """Return raw markdown text for a single file (cached)."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    return file_path.read_text(encoding="utf-8")


@functools.lru_cache(maxsize=None)
def load_markdown_files(data_dir: str | Path | None = None) -> Dict[str, str]:
    """
    Read all markdown files in `data_dir` (defaults to project data folder).

    Returns
    -------
    dict
        Key   = filename stem (without extension)
        Value = raw markdown string
    """
    _assert_data_dir_exists()
    base = Path(data_dir) if data_dir else DATA_DIR
    markdowns: Dict[str, str] = {}

    for md in base.glob("*.md"):
        markdowns[md.stem] = md.read_text(encoding="utf-8")

    return markdowns 