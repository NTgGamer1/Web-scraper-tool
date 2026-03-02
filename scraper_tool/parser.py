"""HTML parsing and metadata extraction."""

from __future__ import annotations

from bs4 import BeautifulSoup


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned if cleaned else None


def _meta_content(soup: BeautifulSoup, key: str, *, attr: str = "name") -> str | None:
    tag = soup.find("meta", attrs={attr: key})
    if tag:
        return _clean(tag.get("content"))
    return None


def parse_page(html: str) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")

    title_tag = soup.find("title")
    title = _clean(title_tag.get_text(" ", strip=True) if title_tag else None)
    og_title = _meta_content(soup, "og:title", attr="property")
    description = _meta_content(soup, "description")
    og_description = _meta_content(soup, "og:description", attr="property")

    canonical_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
    canonical_url = _clean(canonical_tag.get("href")) if canonical_tag else None

    html_tag = soup.find("html")
    language = _clean(html_tag.get("lang")) if html_tag else None

    h1_values = [_clean(item.get_text(" ")) for item in soup.find_all("h1")]
    h2_values = [_clean(item.get_text(" ")) for item in soup.find_all("h2")]
    h1_values = [v for v in h1_values if v]
    h2_values = [v for v in h2_values if v]

    text = _clean(soup.get_text(" ")) or ""
    counts = {
        "links": len(soup.find_all("a")),
        "images": len(soup.find_all("img")),
        "forms": len(soup.find_all("form")),
        "scripts": len(soup.find_all("script")),
        "words": len(text.split()),
    }

    return {
        "title": title or og_title,
        "description": description or og_description,
        "page_details": {
            "canonical_url": canonical_url,
            "language": language,
            "h1": h1_values,
            "h2": h2_values,
            "counts": counts,
            "meta": {
                "og_title": og_title,
                "og_description": og_description,
            },
        },
    }
