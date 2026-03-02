"""Technology detection based on deterministic heuristics."""

from __future__ import annotations

from collections.abc import Iterable

from bs4 import BeautifulSoup

_CONF_ORDER = {"low": 0, "medium": 1, "high": 2}


def _merge_confidence(current: str, new: str) -> str:
    return new if _CONF_ORDER[new] > _CONF_ORDER[current] else current


def _add_detection(
    store: dict[str, dict],
    *,
    name: str,
    category: str,
    confidence: str,
    evidence: str,
) -> None:
    current = store.get(name)
    if current is None:
        store[name] = {
            "name": name,
            "category": category,
            "confidence": confidence,
            "evidence": [evidence],
        }
        return

    if evidence not in current["evidence"]:
        current["evidence"].append(evidence)
    current["confidence"] = _merge_confidence(current["confidence"], confidence)


def _all_sources(soup: BeautifulSoup, attr: str, tags: Iterable[str]) -> list[str]:
    values: list[str] = []
    for tag in tags:
        for node in soup.find_all(tag):
            value = node.get(attr)
            if value:
                values.append(value.lower())
    return values


def detect_technologies(html: str, headers: dict[str, str]) -> list[dict]:
    soup = BeautifulSoup(html or "", "html.parser")
    content = (html or "").lower()
    normalized_headers = {k.lower(): v.lower() for k, v in (headers or {}).items()}
    detections: dict[str, dict] = {}

    server = normalized_headers.get("server", "")
    if "nginx" in server:
        _add_detection(
            detections,
            name="Nginx",
            category="server",
            confidence="high",
            evidence=f"server header: {server}",
        )
    if "apache" in server:
        _add_detection(
            detections,
            name="Apache",
            category="server",
            confidence="high",
            evidence=f"server header: {server}",
        )
    if "cloudflare" in server:
        _add_detection(
            detections,
            name="Cloudflare",
            category="cdn",
            confidence="high",
            evidence=f"server header: {server}",
        )

    powered_by = normalized_headers.get("x-powered-by", "")
    if "php" in powered_by:
        _add_detection(
            detections,
            name="PHP",
            category="backend",
            confidence="high",
            evidence=f"x-powered-by: {powered_by}",
        )
    if "asp.net" in powered_by:
        _add_detection(
            detections,
            name="ASP.NET",
            category="backend",
            confidence="high",
            evidence=f"x-powered-by: {powered_by}",
        )
    if "express" in powered_by:
        _add_detection(
            detections,
            name="Express",
            category="backend",
            confidence="high",
            evidence=f"x-powered-by: {powered_by}",
        )

    generator = soup.find("meta", attrs={"name": "generator"})
    generator_text = (generator.get("content", "").lower() if generator else "")
    if "wordpress" in generator_text or "wp-content" in content or "wp-includes" in content:
        _add_detection(
            detections,
            name="WordPress",
            category="cms",
            confidence="high",
            evidence="meta generator or wordpress asset path signature",
        )

    sources = _all_sources(soup, "src", ("script",)) + _all_sources(soup, "href", ("link", "a"))

    if any("react" in src for src in sources) or "data-reactroot" in content:
        _add_detection(
            detections,
            name="React",
            category="frontend-framework",
            confidence="high",
            evidence="react script or data-reactroot signature",
        )

    if "__next_data__" in content or any("_next/" in src for src in sources):
        _add_detection(
            detections,
            name="Next.js",
            category="frontend-framework",
            confidence="medium",
            evidence="next.js data or asset path signature",
        )

    if any("bootstrap" in src for src in sources):
        _add_detection(
            detections,
            name="Bootstrap",
            category="ui-library",
            confidence="high",
            evidence="bootstrap asset reference",
        )

    if any("jquery" in src for src in sources):
        _add_detection(
            detections,
            name="jQuery",
            category="ui-library",
            confidence="high",
            evidence="jquery asset reference",
        )

    if (
        "googletagmanager.com/gtm.js" in content
        or "google-analytics.com" in content
        or "gtag(" in content
    ):
        _add_detection(
            detections,
            name="Google Analytics",
            category="analytics",
            confidence="high",
            evidence="gtag/gtm/google-analytics signature",
        )

    return sorted(detections.values(), key=lambda item: item["name"].lower())
