"""
utils.py
~~~~~~~~~

General-purpose helper functions for the automated test generation project.
Here utilities are included for normalizing text, creating slugs, writing
temporary files and packaging multiple files into a ZIP.

These functions have been designed to be purely operational and contain no
business logic.  If you need additional utilities, extend this module as
requirements grow.
"""

from __future__ import annotations

import os
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Tuple


def slugify(value: str, allow_unicode: bool = False) -> str:
    """Converts a string into a *slug*-type identifier.

    Removes or replaces any character that is not alphanumeric or underscores.
    This identifier is useful for safely naming files.

    :param value: Source text.
    :param allow_unicode: Whether to allow preserving Unicode characters.
    :return: String converted to slug.
    """
    value = str(value)
    if not allow_unicode:
        # Normalize to ASCII by removing accents or other diacritics
        value = (
            value
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"[^\w_]", "", value)
    return value.lower().strip("_")


def write_json(data: Dict, path: str) -> None:
    """Writes a dictionary as JSON to the specified path.

    :param data: Dictionary serializable to JSON.
    :param path: Destination file path.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(path: str) -> Dict:
    """Reads a JSON file and returns its content as a dictionary.

    :param path: Path of the file to read.
    :return: Dictionary with the JSON content.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_temp_file(suffix: str = "", prefix: str = "tmp", text: bool = True) -> Tuple[str, os.PathLike]:
    """Creates a temporary file and returns its path and context descriptor.

    This function uses :func:`tempfile.NamedTemporaryFile` to generate a
    temporary file that is automatically deleted when its descriptor is closed.

    :param suffix: File name suffix (for example, ``.py``).
    :param prefix: File name prefix.
    :param text: Whether the file is opened in text mode (``True``) or binary.
    :return: Tuple with the file path and the ``NamedTemporaryFile`` object.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix, mode="w+t" if text else "w+b")
    return tmp.name, tmp


def make_zipfile(files: Iterable[Tuple[str, str]], output_path: str) -> None:
    """Packages multiple files into a ZIP.

    :param files: Iterable of tuples ``(path_in_zip, system_path)`` where
      ``path_in_zip`` is the name the file will have inside the ZIP and
      ``system_path`` is the path of the file to be added.
    :param output_path: Output ZIP path.
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, filename in files:
            zf.write(filename, arcname)