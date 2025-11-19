




from fastapi import UploadFile
from domain.services.converter import Converter

import subprocess
import tempfile
import os

class DocxConverter(Converter):
        def convert(file: UploadFile) -> str:
    # 1. Создаём временную директорию
            with tempfile.TemporaryDirectory() as tmpdir:
                docx_path = os.path.join(tmpdir, "input.docx")
                md_path = os.path.join(tmpdir, "output.md")
        
                # 2. Сохраняем UploadFile на диск
                with open(docx_path, "wb") as f:
                    f.write(file.file.read())
        
                # 3. DOCX → Markdown (pandoc)
                subprocess.run(
                    ["pandoc", docx_path, "-t", "markdown", "-o", md_path],
                    check=True
                )
        
                # 4. Читаем результат
                with open(md_path, "r", encoding="utf-8") as f:
                    markdown = f.read()

                # 5. Каталог удаляется автоматически
            return markdown
        
    