"""Command line interface for scraper_tool."""

from __future__ import annotations

import argparse
import json
import sys

from .core import analyze_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scraper_tool",
        description="Extract website metadata and technology hints.",
    )
    parser.add_argument("--url", help="Website URL to analyze.")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds.")
    parser.add_argument("--output", choices=["json"], default="json", help="Output format.")
    parser.add_argument("--save", help="Optional file path for writing output JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.url:
        parser.print_help()
        return 0

    result = analyze_url(args.url, timeout=args.timeout)
    payload = json.dumps(result, indent=2, ensure_ascii=True)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
