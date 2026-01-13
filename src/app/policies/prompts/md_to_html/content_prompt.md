## RULES

### ANCHOR ID.

1. Each section heading must have an anchor ID:
   anchorId = heading text without spaces
1. Maintain case
2. DO NOT change symbols or characters

Usage
CONTENTS: <h3 id="anchorId">
Section wrapper: id="in-anchorId"

### LINKS

Convert [text](url) as:
<a href="url" target="_blank">text</a>
No variations, shortening, or relabeling allowed.

### TABLES

- Do not move tables into other blocks; their physical position in the input Markdown is the only constraint.
- Wrap each row in a <tr>, each cell in a <td><p>...</p></td>
- Preserve the exact order of rows
- Wrap the entire table in exactly one <table> element containing exactly one <tbody>.
- DO NOT create a <thead>.
- Do not treat bolded rows as section headings <li>. The first bolded row (e.g., **Heading** **Heading**) MUST be
  treated as a table row, NOT a section heading.
- Table placement is governed solely by the SECTION CONTEXT rule.

### SECTION DEFINITION

- A section is defined as a Markdown heading (a line beginning with one or more '#' characters followed by a space); do
  not use in tables.

___

## RESPOND VALIDATION

The resulting HTML MUST meet all requirements:

1. All ---, --, —, – are replaced with a single -
2. Blocks must match the order of the incoming MARKDOWN
3. Tables must be within sections in the order of the incoming MARKDOWN
4. Bold font rules:

- **text** → <strong>text</strong>
- Never split or wrap bold span tags

5. There must be no <br>, <style>, or <script> tags
6. A table or bold row must not create or start a new <li> section. Only lines starting with '#' may do so.

___

## OUTPUT FORMAT

- Return HTML only
- No Markdown
- No comments
- ALL section headings MUST be rendered as <h3>. Do NOT generate h1, h2, h4, h5, or h6
- Each <li> section MUST be closed before starting the next section
- Content MUST NOT appear outside of a section wrapper
- Do NOT output stray punctuation

___

## EXAMPLE (ONE SHOT)

### Input Markdown

'''
{markdown_example}
'''

### Output HTML CONTENT

'''
{html_content_example}
'''