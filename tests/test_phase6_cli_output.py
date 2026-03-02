from __future__ import annotations

from pathlib import Path

from scraper_tool import cli


def _sample_result() -> dict:
    return {
        "input_url": "https://example.com",
        "final_url": "https://example.com",
        "status_code": 200,
        "fetched_at": "2026-03-02T00:00:00+00:00",
        "title": "Example",
        "description": "Example description",
        "motto_best": "Build with confidence",
        "motto_candidates": [{"text": "Build with confidence", "source": "h1", "score": 0.9}],
        "technologies": [{"name": "Nginx", "category": "server", "confidence": "high", "evidence": ["server header"]}],
        "page_details": {"canonical_url": "https://example.com", "language": "en", "h1": [], "h2": [], "counts": {}, "meta": {}},
        "warnings": [],
        "error": None,
    }


def test_cli_json_snapshot_compact(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "analyze_url", lambda *_args, **_kwargs: _sample_result())

    code = cli.main(["--url", "https://example.com"])
    output = capsys.readouterr().out.strip()

    expected = '{"input_url":"https://example.com","final_url":"https://example.com","status_code":200,"fetched_at":"2026-03-02T00:00:00+00:00","title":"Example","description":"Example description","motto_best":"Build with confidence","motto_candidates":[{"text":"Build with confidence","source":"h1","score":0.9}],"technologies":[{"name":"Nginx","category":"server","confidence":"high","evidence":["server header"]}],"page_details":{"canonical_url":"https://example.com","language":"en","h1":[],"h2":[],"counts":{},"meta":{}},"warnings":[],"error":null}'

    assert code == 0
    assert output == expected


def test_cli_save_file_and_pretty(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "analyze_url", lambda *_args, **_kwargs: _sample_result())

    target = tmp_path / "result.json"
    code = cli.main(["--url", "https://example.com", "--pretty", "--save", str(target)])
    output = capsys.readouterr().out

    assert code == 0
    assert target.exists()
    assert output.endswith("\n")
    assert target.read_text(encoding="utf-8") == output
    assert '  "input_url": "https://example.com"' in output
