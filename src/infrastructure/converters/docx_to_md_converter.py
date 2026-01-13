from typing import Iterable, Tuple

from domain.services.converter import Converter

import subprocess
import tempfile
import os


class DocxToMdConverter(Converter):
    async def convert(self, file_bytes: bytes) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "input.docx")
            md_path = os.path.join(tmpdir, "output.md")

            # Записываем DOCX на диск
            with open(docx_path, "wb") as f:
                f.write(file_bytes)

            # pandoc → markdown
            subprocess.run(
                ["pandoc", docx_path, "-t", "markdown", "-o", md_path],
                check=True
            )

            # read markdown
            with open(md_path, "r", encoding="utf-8") as f:
                raw_md = f.read()

            # normalize markdown
            return normalize_markdown(raw_md)


import re

NORMALIZATION_RULES: Iterable[Tuple[str, str]] = [
    # Long dashes → hyphen
    (r"[—–]", "-"),

    # HTML dash entities → hyphen
    (r"&mdash;|&ndash;|&#8212;", "-"),

    # Collapse 2+ hyphens into one
    (r"-{2,}", "-"),
]


def normalize_markdown(md: str) -> str:
    """
    Apply deterministic markdown normalization rules.
    Order of rules is significant.
    """
    normalized = md

    for pattern, replacement in NORMALIZATION_RULES:
        normalized = re.sub(pattern, replacement, normalized)

    return normalized
