from __future__ import annotations

from scraper_tool.motto import extract_motto_candidates


def test_motto_prefers_meta_description() -> None:
    html = """
    <html><head>
      <meta name="description" content="Build reliable systems with confidence." />
    </head><body>
      <h1>We help teams ship software</h1>
    </body></html>
    """
    result = extract_motto_candidates(html)
    assert result["motto_best"] == "Build reliable systems with confidence."
    assert len(result["motto_candidates"]) >= 1


def test_motto_uses_hero_heading_when_meta_missing() -> None:
    html = """
    <html><body>
      <h1>Engineering clarity at startup speed</h1>
      <p>Platform for modern teams.</p>
    </body></html>
    """
    result = extract_motto_candidates(html)
    assert result["motto_best"] == "Engineering clarity at startup speed"


def test_motto_absent_returns_none() -> None:
    html = "<html><body><div></div></body></html>"
    result = extract_motto_candidates(html)
    assert result["motto_best"] is None
    assert result["motto_candidates"] == []


def test_motto_filters_noisy_copy() -> None:
    html = """
    <html><head>
      <meta name="description" content="Buy now!!! Limited time discount!!!" />
    </head><body>
      <h1>Build secure APIs fast</h1>
    </body></html>
    """
    result = extract_motto_candidates(html)
    assert result["motto_best"] == "Build secure APIs fast"
