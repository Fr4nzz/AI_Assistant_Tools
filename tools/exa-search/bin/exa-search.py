#!/usr/bin/env python3
"""Agent-friendly Exa Search API CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


SEARCH_URL = "https://api.exa.ai/search"
CONTENTS_URL = "https://api.exa.ai/contents"


def _load_env_file(path: str | None) -> None:
    if not path:
        return
    env_path = Path(path).expanduser()
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _api_key(args: argparse.Namespace) -> str:
    _load_env_file(args.env_file)
    key = args.api_key or os.environ.get("EXA_API_KEY", "")
    if not key:
        raise SystemExit("Set EXA_API_KEY, add it to the Exa .env file, or pass --api-key.")
    return key


def _post_json(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "User-Agent": "AI_Assistant_Tools exa-search",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Exa API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Exa request failed: {exc}") from exc


def _split_csv(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        items.extend(part.strip() for part in value.split(",") if part.strip())
    return items


def _content_config(args: argparse.Namespace) -> dict[str, Any]:
    contents: dict[str, Any] = {}
    if args.highlights:
        contents["highlights"] = True
    if args.text:
        contents["text"] = {"maxCharacters": args.max_characters}
    if args.summary:
        contents["summary"] = True
    if args.max_age_hours is not None:
        contents["maxAgeHours"] = args.max_age_hours
    return contents


def _print_results(response: dict[str, Any]) -> None:
    for index, item in enumerate(response.get("results") or [], 1):
        print(f"{index}. {item.get('title') or '(untitled)'}")
        if item.get("url"):
            print(f"   url: {item['url']}")
        if item.get("publishedDate"):
            print(f"   date: {item['publishedDate']}")
        highlights = item.get("highlights") or []
        if highlights:
            print(f"   highlight: {str(highlights[0]).replace(chr(10), ' ')[:500]}")
        summary = item.get("summary")
        if summary:
            print(f"   summary: {str(summary).replace(chr(10), ' ')[:500]}")
        text = item.get("text")
        if text:
            print(f"   text: {str(text).replace(chr(10), ' ')[:500]}")
        print()


def cmd_search(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {
        "query": args.query,
        "type": args.type,
        "numResults": args.num_results,
    }
    contents = _content_config(args)
    if contents:
        payload["contents"] = contents
    if args.category:
        payload["category"] = args.category
    include_domains = _split_csv(args.include_domain)
    exclude_domains = _split_csv(args.exclude_domain)
    if include_domains:
        payload["includeDomains"] = include_domains
    if exclude_domains:
        payload["excludeDomains"] = exclude_domains
    if args.output_schema:
        payload["outputSchema"] = json.loads(Path(args.output_schema).read_text(encoding="utf-8"))

    started = time.perf_counter()
    response = _post_json(SEARCH_URL, payload, _api_key(args))
    response["_elapsedSeconds"] = round(time.perf_counter() - started, 3)
    if args.json:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(f"elapsed: {response['_elapsedSeconds']:.3f}s")
        _print_results(response)
    return 0


def cmd_contents(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {"urls": args.urls}
    if args.highlights:
        payload["highlights"] = True
    if args.text:
        payload["text"] = {"maxCharacters": args.max_characters}
    if args.max_age_hours is not None:
        payload["maxAgeHours"] = args.max_age_hours

    started = time.perf_counter()
    response = _post_json(CONTENTS_URL, payload, _api_key(args))
    response["_elapsedSeconds"] = round(time.perf_counter() - started, 3)
    if args.json:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(f"elapsed: {response['_elapsedSeconds']:.3f}s")
        _print_results(response)
    return 0


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", default="")
    parser.add_argument("--env-file", default=os.environ.get("EXA_SEARCH_ENV_FILE", ""))
    parser.add_argument("--json", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search with Exa's current Search API.")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search the web with Exa")
    _add_common(search)
    search.add_argument("query")
    search.add_argument("-n", "--num-results", type=int, default=10)
    search.add_argument("--type", default="auto", choices=["auto", "fast", "instant", "deep-lite", "deep", "deep-reasoning"])
    search.add_argument("--category", default="")
    search.add_argument("--include-domain", action="append", default=[])
    search.add_argument("--exclude-domain", action="append", default=[])
    search.add_argument("--highlights", action="store_true", default=True)
    search.add_argument("--no-highlights", dest="highlights", action="store_false")
    search.add_argument("--text", action="store_true")
    search.add_argument("--summary", action="store_true")
    search.add_argument("--max-characters", type=int, default=5000)
    search.add_argument("--max-age-hours", type=int)
    search.add_argument("--output-schema", default="", help="Path to JSON schema file for structured output")
    search.set_defaults(func=cmd_search)

    contents = sub.add_parser("contents", help="Fetch contents for known URLs")
    _add_common(contents)
    contents.add_argument("urls", nargs="+")
    contents.add_argument("--highlights", action="store_true", default=True)
    contents.add_argument("--no-highlights", dest="highlights", action="store_false")
    contents.add_argument("--text", action="store_true")
    contents.add_argument("--max-characters", type=int, default=5000)
    contents.add_argument("--max-age-hours", type=int)
    contents.set_defaults(func=cmd_contents)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
