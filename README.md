# Web-scraper-tool

Python 3.11+ CLI and library for extracting website intelligence from HTML pages.

## What it extracts

- Core metadata: title, description, canonical URL, language.
- Page details: heading lists, links/images/forms/scripts/word counts.
- Technology hints: CMS/framework/analytics/server/backend signatures.
- Motto/tagline: best candidate + ranked candidate list.
- Structured warnings and machine-readable error envelope.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage

```bash
python3 -m scraper_tool --url https://example.com
python3 -m scraper_tool --url https://example.com --pretty
python3 -m scraper_tool --url https://example.com --save result.json --pretty
```

### CLI arguments

- `--url`: target website URL.
- `--timeout`: HTTP timeout in seconds (default `15`).
- `--output`: currently `json` only.
- `--pretty`: pretty-print JSON in console/file.
- `--save`: write JSON output to file.

## Python API

```python
from scraper_tool import analyze_url

result = analyze_url("https://example.com", timeout=15)
print(result["technologies"])
```

## Output schema

Stable top-level keys (in order):

- `input_url`
- `final_url`
- `status_code`
- `fetched_at`
- `title`
- `description`
- `motto_best`
- `motto_candidates`
- `technologies`
- `page_details`
- `warnings`
- `error`

## Testing

Run full test suite:

```bash
python3 -m pytest -q
```

## Limitations

- HTML-only scraping (no JavaScript rendering/browser execution).
- Technology detection is heuristic and may miss custom stacks.
- Network-dependent scraping can be affected by bot protection/rate limits.

## Troubleshooting

- If requests time out, increase `--timeout`.
- If output has `validation_error`, verify URL scheme/domain format.
- If tech detection is empty, check if the site loads key assets only via JavaScript.
