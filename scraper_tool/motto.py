"""Motto/tagline extraction and ranking."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup


_NOISY_PATTERNS = (
    "buy now",
    "limited time",
    "click here",
    "subscribe",
    "sale",
    "discount",
)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    cleaned = cleaned.strip("-:| ")
    return cleaned if cleaned else None


def _is_noisy(text: str) -> bool:
    lowered = text.lower()
    if any(pattern in lowered for pattern in _NOISY_PATTERNS):
        return True
    if lowered.count("!") >= 2:
        return True
    return False


def _score_text(base: float, text: str) -> float:
    score = base
    length = len(text)
    if length < 12:
        score -= 0.20
    elif 18 <= length <= 95:
        score += 0.10
    elif length > 150:
        score -= 0.25

    if _is_noisy(text):
        score -= 0.35

    return round(score, 3)


def extract_motto_candidates(html: str) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")

    raw_candidates: list[tuple[str, str, float]] = []

    meta_description = soup.find("meta", attrs={"name": "description"})
    if meta_description and meta_description.get("content"):
        raw_candidates.append((meta_description.get("content"), "meta_description", 0.95))

    og_description = soup.find("meta", attrs={"property": "og:description"})
    if og_description and og_description.get("content"):
        raw_candidates.append((og_description.get("content"), "og_description", 0.90))

    h1 = soup.find("h1")
    if h1:
        raw_candidates.append((h1.get_text(" "), "h1", 0.85))

    for h2 in soup.find_all("h2")[:2]:
        raw_candidates.append((h2.get_text(" "), "h2", 0.70))

    intro_p = soup.find("p")
    if intro_p:
        raw_candidates.append((intro_p.get_text(" "), "intro_paragraph", 0.68))

    dedup: dict[str, dict] = {}
    for text, source, base in raw_candidates:
        cleaned = _clean_text(text)
        if not cleaned:
            continue

        key = cleaned.lower()
        scored = _score_text(base, cleaned)
        existing = dedup.get(key)
        if existing is None or scored > existing["score"]:
            dedup[key] = {
                "text": cleaned,
                "source": source,
                "score": scored,
            }

    candidates = sorted(dedup.values(), key=lambda item: item["score"], reverse=True)

    if not candidates or candidates[0]["score"] < 0.45:
        return {
            "motto_best": None,
            "motto_candidates": [],
        }

    return {
        "motto_best": candidates[0]["text"],
        "motto_candidates": candidates,
    }
