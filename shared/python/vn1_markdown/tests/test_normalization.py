from __future__ import annotations

import unittest

from vn1_markdown.normalization import normalize_generated_markdown, sanitize_markdown_inline


class MarkdownNormalizationTest(unittest.TestCase):
    def test_unwraps_single_markdown_fence(self) -> None:
        value = "```markdown\n\\### Title\n\\- item\n```"

        self.assertEqual(normalize_generated_markdown(value), "### Title\n- item")

    def test_normalizes_tilde_fence_and_closes_unclosed_fence(self) -> None:
        value = "~~~python\nprint('<keep>')"

        self.assertEqual(normalize_generated_markdown(value), "```python\nprint('<keep>')\n```")

    def test_preserves_inline_code_with_angle_brackets(self) -> None:
        value = "## Репозиторий `<repository_id>`\nФайл `Map<String, dynamic>`"

        self.assertEqual(normalize_generated_markdown(value), value)

    def test_preserves_autolink(self) -> None:
        value = "Смотри <https://example.com/path?a=1&b=2>"

        self.assertEqual(normalize_generated_markdown(value), value)

    def test_removes_html_outside_code_blocks(self) -> None:
        value = "<p>### Заголовок</p>\n<script>bad()</script>\nТекст &amp; ещё"

        self.assertEqual(normalize_generated_markdown(value), "### Заголовок\n\nТекст & ещё")

    def test_preserves_html_inside_code_blocks(self) -> None:
        value = "```html\n<div>keep</div>\n```"

        self.assertEqual(normalize_generated_markdown(value), value)

    def test_sanitized_inline_stays_inline_after_normalization(self) -> None:
        value = f"1. **{sanitize_markdown_inline('- build [x]')}**\n   OK"

        self.assertEqual(normalize_generated_markdown(value), "1. **\\- build \\[x\\]**\n   OK")

    def test_repairs_broken_section_heading_from_llm(self) -> None:
        value = "- *Состав**\n\nВода, сахар.\n\n- *Способ применения**\n\nПринимать внутрь."

        self.assertEqual(
            normalize_generated_markdown(value),
            "**Состав**\n\nВода, сахар.\n\n**Способ применения**\n\nПринимать внутрь.",
        )

    def test_repairs_common_broken_non_medicine_section_headings(self) -> None:
        value = (
            "- *Состав**\n\nВода.\n\n"
            "- _Способ применения__\n\nПринимать внутрь.\n\n"
            "- **Меры предосторожности*\n\nНе применять при непереносимости."
        )

        self.assertEqual(
            normalize_generated_markdown(value),
            (
                "**Состав**\n\nВода.\n\n"
                "**Способ применения**\n\nПринимать внутрь.\n\n"
                "**Меры предосторожности**\n\nНе применять при непереносимости."
            ),
        )


if __name__ == "__main__":
    unittest.main()
