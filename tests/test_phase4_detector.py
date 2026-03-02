from __future__ import annotations

from scraper_tool.detector import detect_technologies


def _names(items: list[dict]) -> set[str]:
    return {item["name"] for item in items}


def test_detect_wordpress() -> None:
    html = """
    <html><head>
      <meta name="generator" content="WordPress 6.2" />
      <link rel="stylesheet" href="/wp-content/themes/main.css" />
    </head></html>
    """
    found = detect_technologies(html, {})
    assert "WordPress" in _names(found)


def test_detect_react() -> None:
    html = """
    <html><body>
      <div data-reactroot=""></div>
      <script src="/static/js/react-dom.production.min.js"></script>
    </body></html>
    """
    found = detect_technologies(html, {})
    assert "React" in _names(found)


def test_detect_bootstrap() -> None:
    html = '<link rel="stylesheet" href="https://cdn.example.com/bootstrap.min.css" />'
    found = detect_technologies(html, {})
    assert "Bootstrap" in _names(found)


def test_detect_google_analytics() -> None:
    html = """
    <script async src="https://www.googletagmanager.com/gtm.js?id=GTM-123"></script>
    <script>gtag('config', 'G-12345');</script>
    """
    found = detect_technologies(html, {})
    assert "Google Analytics" in _names(found)


def test_unknown_site_returns_empty() -> None:
    html = "<html><head><title>Plain site</title></head><body>Hello</body></html>"
    found = detect_technologies(html, {})
    assert found == []
