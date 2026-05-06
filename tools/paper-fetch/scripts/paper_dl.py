#!/usr/bin/env python3
"""paper-dl: Search and download academic papers."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config, SKILL_DIR
from download import download_paper
from mirrors import get_working_mirrors
from search import lookup_unpaywall, search_all


def cmd_search(args: argparse.Namespace) -> int:
    results = search_all(args.query, max_results=args.limit)
    errors = [r for r in results if "error" in r]
    papers = [r for r in results if "error" not in r]

    output = {
        "query": args.query,
        "total": len(papers),
        "errors": [e["error"] for e in errors],
        "papers": papers[: args.limit],
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Results for: {args.query}\n")
        for i, p in enumerate(papers[: args.limit], 1):
            oa_badge = " [OA]" if p.get("is_oa") else ""
            print(f"{i}. {p.get('title', 'N/A')}{oa_badge}")
            print(f"   Authors: {p.get('authors', 'N/A')}")
            print(f"   Year: {p.get('year', 'N/A')} | Source: {p.get('source', 'N/A')}")
            print(f"   DOI: {p.get('doi', 'N/A')}")
            if p.get("pdf_url"):
                print(f"   PDF: {p['pdf_url']}")
            print()
        if errors:
            print("Errors:")
            for e in errors:
                print(f"  - {e['error']}")
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    output_dir = Path(args.output).expanduser() if args.output else None
    result = download_paper(args.identifier, output_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "success":
            print(f"Downloaded: {result['path']}")
            print(f"  DOI: {result['doi']}")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Source: {result['source']}")
            if result.get("mirror"):
                print(f"  Mirror: {result['mirror']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    return 0 if result["status"] == "success" else 1


def cmd_lookup(args: argparse.Namespace) -> int:
    from pdf_utils import extract_doi

    doi = extract_doi(args.identifier)
    if not doi:
        print(f"Error: Could not extract DOI from: {args.identifier}", file=sys.stderr)
        return 1

    result = lookup_unpaywall(doi)
    if not result:
        print(f"Error: Unpaywall lookup failed for {doi}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"DOI: {result['doi']}")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Year: {result.get('year', 'N/A')}")
        print(f"Open Access: {result.get('is_oa', False)}")
        print(f"PDF URL: {result.get('pdf_url', 'N/A')}")
    return 0


def cmd_mirrors(args: argparse.Namespace) -> int:
    mirrors = get_working_mirrors(force_refresh=args.refresh)

    if args.json:
        print(json.dumps({"mirrors": mirrors, "count": len(mirrors)}, indent=2))
    else:
        print(f"Working mirrors ({len(mirrors)}):")
        for m in mirrors:
            print(f"  - {m}")
    return 0


def cmd_set_key(args: argparse.Namespace) -> int:
    env_file = SKILL_DIR / ".env"
    lines = []
    if env_file.exists():
        lines = env_file.read_text().splitlines()

    key_map = {
        "openalex": "PAPER_FETCH_OPENALEX_API_KEY",
        "semantic": "PAPER_FETCH_SEMANTIC_API_KEY",
        "core": "PAPER_FETCH_CORE_API_KEY",
        "unpaywall-email": "PAPER_FETCH_UNPAYWALL_EMAIL",
        "mailto": "PAPER_FETCH_CROSSREF_MAILTO",
    }

    env_key = key_map.get(args.key_name)
    if not env_key:
        print(f"Error: Unknown key '{args.key_name}'. Valid: {', '.join(key_map.keys())}", file=sys.stderr)
        return 1

    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{env_key}="):
            lines[i] = f"{env_key}={args.key_value}"
            found = True
            break

    if not found:
        lines.append(f"{env_key}={args.key_value}")

    env_file.write_text("\n".join(lines) + "\n")
    print(f"Set {args.key_name} successfully.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="paper-dl",
        description="Search and download academic papers from open access sources and academic mirrors.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    search_p = sub.add_parser("search", help="Search for papers")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("-n", "--limit", type=int, default=10, help="Max results")
    search_p.set_defaults(func=cmd_search)

    download_p = sub.add_parser("download", help="Download a paper by DOI/URL")
    download_p.add_argument("identifier", help="DOI, DOI URL, or PMID")
    download_p.add_argument("-o", "--output", help="Output directory")
    download_p.set_defaults(func=cmd_download)

    lookup_p = sub.add_parser("lookup", help="Lookup DOI metadata via Unpaywall")
    lookup_p.add_argument("identifier", help="DOI or DOI URL")
    lookup_p.set_defaults(func=cmd_lookup)

    mirrors_p = sub.add_parser("mirrors", help="List working academic mirrors")
    mirrors_p.add_argument("--refresh", action="store_true", help="Force refresh mirror list")
    mirrors_p.set_defaults(func=cmd_mirrors)

    setkey_p = sub.add_parser("set-key", help="Set an API key or config value")
    setkey_p.add_argument("key_name", help="Key name: openalex, semantic, core, unpaywall-email, mailto")
    setkey_p.add_argument("key_value", help="The value to set")
    setkey_p.set_defaults(func=cmd_set_key)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
