from __future__ import annotations

from scraper_tool.parser import parse_page


def test_parse_page_extracts_canonical_and_lang() -> None:
    html = """
    <html lang="en-US">
      <head>
        <title>Example Site</title>
        <meta name="description" content="Best tools for teams" />
        <link rel="canonical" href="https://example.com/home" />
      </head>
      <body>
        <h1>Build Faster</h1>
        <h2>Trusted by engineers</h2>
        <a href="/a">a</a><a href="/b">b</a>
        <img src="a.png" />
        <form></form>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed["title"] == "Example Site"
    assert parsed["description"] == "Best tools for teams"
    assert parsed["page_details"]["canonical_url"] == "https://example.com/home"
    assert parsed["page_details"]["language"] == "en-US"
    assert parsed["page_details"]["counts"]["links"] == 2
    assert parsed["page_details"]["counts"]["images"] == 1
    assert parsed["page_details"]["counts"]["forms"] == 1


def test_parse_page_handles_missing_title() -> None:
    html = """
    <html>
      <head>
        <meta property="og:title" content="Fallback OG Title" />
      </head>
      <body><h1>Hello</h1></body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed["title"] == "Fallback OG Title"


def test_parse_page_handles_missing_description() -> None:
    html = """
    <html>
      <head><title>Only Title</title></head>
      <body>No description meta</body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed["description"] is None


def test_parse_page_malformed_html() -> None:
    html = "<html><head><title>Broken<title></head><body><h1>Open"
    parsed = parse_page(html)
    assert parsed["title"] is not None
    assert parsed["page_details"]["counts"]["words"] >= 1
