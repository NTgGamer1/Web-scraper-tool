from __future__ import annotations

import subprocess
import sys


def test_module_import() -> None:
    module = __import__("scraper_tool")
    assert hasattr(module, "analyze_url")


def test_cli_help() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "scraper_tool", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Extract website metadata" in proc.stdout
