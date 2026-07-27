import re


def normalize_generated_markdown(value: object) -> str:
    markdown = _coerce_to_text(value)
    markdown = _unwrap_markdown_code_fence(markdown)
    markdown = _remove_html(markdown)
    markdown = _normalize_lines(markdown)

    return markdown.strip()


def sanitize_markdown_inline(value: object) -> str:
    text = _coerce_to_text(value)
    text = _remove_html(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\\", "\\\\")
    text = text.replace("**", "\\*\\*")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = re.sub(r"^(#{1,6})\s+", r"\\\1 ", text)
    text = re.sub(r"^([*+-])\s+", r"\\\1 ", text)
    text = re.sub(r"^(\d+)[.)]\s+", r"\1\\. ", text)

    return text


def _coerce_to_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _unwrap_markdown_code_fence(markdown: str) -> str:
    stripped = markdown.strip()
    match = re.fullmatch(r"```(?:markdown|md)?\s*\n(?P<body>.*?)\n```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group("body")
    return markdown


def _remove_html(markdown: str) -> str:
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    markdown = re.sub(r"</?[^>\n]+>", "", markdown)

    return markdown


def _normalize_lines(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized_lines: list[str] = []
    previous_blank = False
    in_fenced_block = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fenced_block = not in_fenced_block
            normalized_lines.append(stripped)
            previous_blank = False
            continue

        if in_fenced_block:
            normalized_lines.append(raw_line.rstrip())
            previous_blank = False
            continue

        if not stripped:
            if not previous_blank and normalized_lines:
                normalized_lines.append("")
            previous_blank = True
            continue

        line = _normalize_markdown_line(line)
        normalized_lines.append(line)
        previous_blank = False

    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()

    return "\n".join(normalized_lines)


def _normalize_markdown_line(line: str) -> str:
    leading_match = re.match(r"^([ \t]*)(.*)$", line)
    indent = leading_match.group(1) if leading_match else ""
    content = leading_match.group(2) if leading_match else line

    heading_match = re.match(r"^(#{1,6})(?!#)\s*(.+)$", content)
    if heading_match:
        return f"{heading_match.group(1)} {heading_match.group(2).strip()}"

    unordered_list_match = re.match(r"^([*+-])\s*(.+)$", content)
    if unordered_list_match:
        return f"{indent}- {unordered_list_match.group(2).strip()}"

    ordered_list_match = re.match(r"^(\d+)[.)]\s*(.+)$", content)
    if ordered_list_match:
        return f"{indent}{ordered_list_match.group(1)}. {ordered_list_match.group(2).strip()}"

    return f"{indent}{re.sub(r'[ \t]{2,}', ' ', content)}"
