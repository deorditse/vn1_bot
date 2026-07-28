from __future__ import annotations

import html
import re

_FENCE_PATTERN = re.compile(r"^([`~]{3,})(.*)$")
_HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", flags=re.DOTALL)
_HTML_BLOCK_PATTERN = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", flags=re.IGNORECASE | re.DOTALL)
_HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s[^>\n]*)?/?>")
_INLINE_CODE_PATTERN = re.compile(r"(`+)([^`\n]*?)(\1)")


def normalize_generated_markdown(value: object) -> str:
    """Conservatively repair Markdown commonly returned by LLMs.

    This is not a Markdown renderer or a security sanitizer. It preserves valid
    Markdown as much as possible and only fixes transport/LLM artifacts that make
    downstream renderers fail or show raw escaped structure.
    """
    markdown = _coerce_to_text(value)
    markdown = _normalize_newlines(markdown).strip("\ufeff")
    markdown = _unwrap_markdown_code_fence(markdown)
    markdown = html.unescape(markdown)
    markdown = _normalize_lines(markdown)

    return markdown.strip()


def sanitize_markdown_inline(value: object) -> str:
    """Escape a short untrusted string so it can be embedded inside Markdown text."""
    text = _coerce_to_text(value)
    text = html.unescape(text)
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


def _normalize_newlines(markdown: str) -> str:
    return markdown.replace("\r\n", "\n").replace("\r", "\n")


def _unwrap_markdown_code_fence(markdown: str) -> str:
    stripped = markdown.strip()
    match = re.fullmatch(
        r"(?P<fence>`{3,}|~{3,})(?:markdown|md)?[ \t]*\n(?P<body>.*?)\n(?P=fence)",
        stripped,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        return match.group("body")
    return markdown


def _remove_html(markdown: str) -> str:
    protected_code_spans: list[str] = []

    def protect_code_span(match: re.Match[str]) -> str:
        protected_code_spans.append(match.group(0))
        return f"\x00CODE{len(protected_code_spans) - 1}\x00"

    markdown = _INLINE_CODE_PATTERN.sub(protect_code_span, markdown)
    markdown = _HTML_COMMENT_PATTERN.sub("", markdown)
    markdown = _HTML_BLOCK_PATTERN.sub("", markdown)
    markdown = _HTML_TAG_PATTERN.sub("", markdown)

    for index, code_span in enumerate(protected_code_spans):
        markdown = markdown.replace(f"\x00CODE{index}\x00", code_span)

    return markdown


def _normalize_lines(markdown: str) -> str:
    lines = _normalize_newlines(markdown).split("\n")
    normalized_lines: list[str] = []
    previous_blank = False
    fence_marker: str | None = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        fence_match = _FENCE_PATTERN.match(stripped)
        if fence_match:
            marker = fence_match.group(1)
            if fence_marker is None:
                fence_marker = marker
                normalized_lines.append(_normalize_opening_fence(stripped))
            elif marker.startswith(fence_marker[0]) and len(marker) >= len(fence_marker):
                fence_marker = None
                normalized_lines.append("```")
            else:
                normalized_lines.append(line)
            previous_blank = False
            continue

        if fence_marker is not None:
            normalized_lines.append(raw_line.rstrip())
            previous_blank = False
            continue

        if not stripped:
            if not previous_blank and normalized_lines:
                normalized_lines.append("")
            previous_blank = True
            continue

        line = _normalize_markdown_line(_remove_html(line))
        normalized_lines.append(line)
        previous_blank = False

    if fence_marker is not None:
        normalized_lines.append("```")

    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()

    return "\n".join(normalized_lines)


def _normalize_markdown_line(line: str) -> str:
    leading_match = re.match(r"^([ \t]*)(.*)$", line)
    indent = _normalize_indent(leading_match.group(1) if leading_match else "")
    content = leading_match.group(2) if leading_match else line
    content = _unescape_structural_prefix(content)
    repaired_content = _repair_broken_section_heading(content)
    if repaired_content != content:
        return f"{indent}{repaired_content}"
    content = repaired_content

    heading_match = re.match(r"^(#{1,6})(?!#)\s*(.+)$", content)
    if heading_match:
        return f"{heading_match.group(1)} {heading_match.group(2).strip()}"

    unordered_list_match = re.match(r"^([*+-])\s+(.+)$", content)
    if unordered_list_match:
        return f"{indent}- {unordered_list_match.group(2).strip()}"

    ordered_list_match = re.match(r"^(\d+)[.)]\s*(.+)$", content)
    if ordered_list_match:
        return f"{indent}{ordered_list_match.group(1)}. {ordered_list_match.group(2).strip()}"

    return f"{indent}{re.sub(r'[ \t]{2,}', ' ', content)}"


def _normalize_indent(indent: str) -> str:
    return indent.replace("\t", "    ")


def _normalize_opening_fence(line: str) -> str:
    match = _FENCE_PATTERN.match(line)
    if not match:
        return line

    language = match.group(2).strip()
    language = re.sub(r"\s+", " ", language)
    return f"```{language}" if language else "```"


def _unescape_structural_prefix(content: str) -> str:
    content = re.sub(r"^\\(#{1,6})(\s+)", r"\1\2", content)
    content = re.sub(r"^\\([*+-])(\s+)", r"\1\2", content)
    content = re.sub(r"^(\d+)\\[.)](\s+)", r"\1.\2", content)
    return content


def _repair_broken_section_heading(content: str) -> str:
    match = re.match(r"^[-*+]\s+[*_]{1,2}([^*_\n:][^*_\n:]{1,80})[*_]{1,2}\s*$", content)
    if not match:
        return content

    return f"**{match.group(1).strip()}**"
