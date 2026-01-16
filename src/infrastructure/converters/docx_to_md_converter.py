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


def normalize_markdown(md: str) -> str:
    """
    Deterministic markdown normalization.
    - Normalizes hyphens and spaces
    - Preserves tables verbatim
    - Converts bold-only lines into Markdown headings
    - Removes empty headings followed immediately by another heading
    """
    lines = md.splitlines()
    normalized_lines: list[str] = []

    in_table = False

    # ---------- PASS 1: normalisation ----------
    for line in lines:
        stripped = line.strip()

        # table detection
        if stripped.startswith("<table"):
            in_table = True
        if in_table:
            normalized_lines.append(line)
            if stripped.startswith("</table"):
                in_table = False
            continue

        # hyphen normalization
        for pattern, repl in HYPHEN_RULES:
            line = re.sub(pattern, repl, line)

        # space normalization
        for pattern, repl in SPACE_RULES:
            line = re.sub(pattern, repl, line)

        # bold-only → heading
        m = re.match(r"^\s*\*\*(.+?)\*\*\s*$", line)
        if m:
            heading_text = m.group(1).strip()
            line = f"# {heading_text}"

        normalized_lines.append(line)

    # ---------- PASS 2: empty heading suppression ----------
    result: list[str] = []
    i = 0

    while i < len(normalized_lines):
        line = normalized_lines[i]

        if is_heading(line):
            j = i + 1

            # ищем следующий НЕпустой блок
            while j < len(normalized_lines) and is_empty(normalized_lines[j]):
                j += 1

            # если следующий блок — заголовок → пропускаем текущий
            if j < len(normalized_lines) and is_heading(normalized_lines[j]):
                i += 1
                continue

        result.append(line)
        i += 1

    return "\n".join(result)


HYPHEN_RULES: Iterable[Tuple[str, str]] = [
    (r"[—–]", "-"),  # длинные тире
    (r"&mdash;|&ndash;", "-"),
    (r"-{2,}", "-"),

]
SPACE_RULES: Iterable[Tuple[str, str]] = [
    (r"[ \t]{2,}", " "),
]


def is_heading(line: str) -> bool:
    return bool(re.match(r"^\s*#+\s+\S+", line))


def is_empty(line: str) -> bool:
    return line.strip() == ""
