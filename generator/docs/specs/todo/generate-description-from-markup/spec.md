# Generate description from markup

## Contract

`POST /generate-description` accepts exactly one source: an XLS/XLSX upload with two columns (`id`, raw markup; header optional for compatibility with the supplied example), or JSON fields `id` and `raw_description`. It always returns an XLSX attachment with the nine columns from the supplied output example.

Each input row is sent independently to the configured OpenAI-backed LLM with the generation policy in `src/app/policies/prompts/generation/from_markup.md`. Up to four rows are processed concurrently while output order remains identical to input order. A failed call or invalid model JSON is retried twice. If all attempts fail, that row is retained: `Описание` contains the generation error and the remaining generated fields contain `Нет данных.`. Invalid request input produces HTTP 422.

Limits: 10 MB per file, 100 data rows, 100,000 markup characters per row, 1,000,000 markup characters total, and 5 requests per user per minute. Formula-like text values are escaped before writing XLSX cells.
