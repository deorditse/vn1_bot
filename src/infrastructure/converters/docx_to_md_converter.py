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
                [
                    "pandoc",
                    docx_path,
                    "-t",
                    "markdown_strict",
                    "--wrap=none",
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

        res = normalize_markdown(result.stdout)
        with open("result_normalize_markdown.md", "w") as f:
            f.write(res)
        return res


import re

HYPHEN_RULES: Iterable[Tuple[str, str]] = [
    (r"[—–]", "-"),  # длинные тире
    (r"&mdash;|&ndash;", "-"),
    (r"-{2,}", "-"),

]
SPACE_RULES: Iterable[Tuple[str, str]] = [
    (r"[ \t]{2,}", " "),
]


def normalize_markdown(md: str) -> str:
    """
    Deterministic markdown normalization.
    Tables are preserved verbatim.
    """
    lines = md.splitlines()
    normalized_lines = []

    in_table = False

    for line in lines:
        stripped = line.strip()

        # crude but deterministic table detection
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
        elif in_table and stripped == "":
            in_table = False

        if not in_table:
            for pattern, repl in HYPHEN_RULES:
                line = re.sub(pattern, repl, line)

            for pattern, repl in SPACE_RULES:
                line = re.sub(pattern, repl, line)

        normalized_lines.append(line)

    return "\n".join(normalized_lines)
