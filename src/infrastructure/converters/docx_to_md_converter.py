from typing import Iterable, Tuple

from common import ApiMode, env
from domain.services.converter import Converter

import subprocess
import tempfile
import os


class DocxToMdConverter(Converter):
    mode: ApiMode = env.api_mode()

    async def convert(self, file_bytes: bytes) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "input.docx")

            # 1. Записываем DOCX (pandoc принимает файл)
            with open(docx_path, "wb") as f:
                f.write(file_bytes)

            # 2. Pandoc → Markdown через stdout
            result = subprocess.run(
                ["pandoc", docx_path, "-t", "markdown"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            raw_md = result.stdout

        return normalize_markdown(raw_md)


import re

NORMALIZATION_RULES: Iterable[Tuple[str, str]] = [
    # Collapse 2+ hyphens into one
    (r"-{2,}", "-"),

    # Collapse 2+ spaces into one space
    (r" {2,}", " "),
]


def normalize_markdown(md: str) -> str:
    """
    Apply deterministic markdown normalization rules.
    Order of rules is significant.
    """
    normalized = md

    for pattern, replacement in NORMALIZATION_RULES:
        normalized = re.sub(pattern, replacement, normalized)

    with open("result.md", "w") as f:
        f.write(normalized)
    return normalized
