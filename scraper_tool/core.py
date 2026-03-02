"""Core package API."""

from __future__ import annotations

from .detector import detect_technologies
from .fetcher import FetchError, fetch_url
from .motto import extract_motto_candidates
from .parser import parse_page


def analyze_url(url: str, timeout: int = 15) -> dict:
    """Analyze a URL and return structured output."""
    try:
        fetched = fetch_url(url, timeout=timeout)
    except FetchError as exc:
        return {
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

    parsed = parse_page(fetched.html)
    technologies = detect_technologies(fetched.html, fetched.headers)
    motto = extract_motto_candidates(fetched.html)

    return {
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
        "warnings": [],
        "error": None,
    }
