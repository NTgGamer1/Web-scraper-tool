"""Core package API."""

from __future__ import annotations

from .detector import detect_technologies
from .fetcher import FetchError, fetch_url
from .motto import extract_motto_candidates
from .parser import parse_page


RESULT_KEYS = (
    "input_url",
    "final_url",
    "status_code",
    "fetched_at",
    "title",
    "description",
    "motto_best",
    "motto_candidates",
    "technologies",
    "page_details",
    "warnings",
    "error",
)


def _ordered_result(values: dict) -> dict:
    return {key: values.get(key) for key in RESULT_KEYS}


def analyze_url(url: str, timeout: int = 15) -> dict:
    """Analyze a URL and return structured output."""
    try:
        fetched = fetch_url(url, timeout=timeout)
    except FetchError as exc:
        return _ordered_result(
            {
                "input_url": url,
                "final_url": None,
                "status_code": None,
                "fetched_at": None,
                "title": None,
                "description": None,
                "motto_best": None,
                "motto_candidates": [],
                "technologies": [],
                "page_details": {},
                "warnings": [],
                "error": exc.to_dict(),
            }
        )

    try:
        parsed = parse_page(fetched.html)
    except Exception as exc:  # pragma: no cover - defensive envelope
        return _ordered_result(
            {
                "input_url": fetched.input_url,
                "final_url": fetched.final_url,
                "status_code": fetched.status_code,
                "fetched_at": fetched.fetched_at,
                "title": None,
                "description": None,
                "motto_best": None,
                "motto_candidates": [],
                "technologies": [],
                "page_details": {},
                "warnings": [],
                "error": {
                    "code": "parse_error",
                    "message": "Failed to parse HTML.",
                    "details": {"exception": str(exc)},
                },
            }
        )

    technologies = detect_technologies(fetched.html, fetched.headers)
    motto = extract_motto_candidates(fetched.html)

    warnings: list[str] = []
    if not parsed.get("title"):
        warnings.append("title_missing")
    if not parsed.get("description"):
        warnings.append("description_missing")
    if not technologies:
        warnings.append("technology_unknown")
    if not motto.get("motto_best"):
        warnings.append("motto_not_found")

    return _ordered_result(
        {
            "input_url": fetched.input_url,
            "final_url": fetched.final_url,
            "status_code": fetched.status_code,
            "fetched_at": fetched.fetched_at,
            "title": parsed.get("title"),
            "description": parsed.get("description"),
            "motto_best": motto.get("motto_best"),
            "motto_candidates": motto.get("motto_candidates", []),
            "technologies": technologies,
            "page_details": parsed.get("page_details", {}),
            "warnings": warnings,
            "error": None,
        }
    )
