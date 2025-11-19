from domain.services.converter import Converter

import subprocess
import tempfile
import os

class DocxConverter(Converter):
    def convert(self, file_bytes: bytes) -> str:
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

            # Читаем markdown
            with open(md_path, "r", encoding="utf-8") as f:
                return f.read()
    