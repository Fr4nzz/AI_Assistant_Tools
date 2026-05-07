"""Download papers with mirror fallback."""
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import Config
from mirrors import get_working_mirrors
from pdf_utils import extract_doi, is_valid_pdf, save_pdf
from search import lookup_unpaywall, search_all


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": Config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
    })
    return s


def _extract_pdf_url(html: str, base_url: str) -> Optional[str]:
    """Parse mirror HTML to find the direct PDF URL."""
    soup = BeautifulSoup(html, "html.parser")

    # Modern mirror pages: <embed type="application/pdf" src="...">
    embed = soup.find("embed", {"type": "application/pdf"})
    if embed:
        src = embed.get("src")
        if src and isinstance(src, str):
            return _resolve_url(src, base_url)

    # Fallback: <iframe src="...">
    iframe = soup.find("iframe")
    if iframe:
        src = iframe.get("src")
        if src and isinstance(src, str):
            return _resolve_url(src, base_url)

    # Fallback: <div id="pdf"> or other common patterns
    pdf_div = soup.find("div", {"id": "pdf"})
    if pdf_div:
        src = pdf_div.get("src") or pdf_div.get("data-src")
        if src:
            return _resolve_url(src, base_url)

    # Fallback: any link containing .pdf
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower():
            return _resolve_url(href, base_url)

    return None


def _resolve_url(url: str, base_url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return base_url.rstrip("/") + url
    return url


def try_oa_download(doi: str, save_dir: Path) -> Optional[Dict[str, Any]]:
    """Try to download via Unpaywall OA link. Fast path — no mirror needed."""
    result = lookup_unpaywall(doi)
    if not result or not result.get("pdf_url"):
        return None

    pdf_url = result["pdf_url"]
    try:
        resp = requests.get(pdf_url, headers={"User-Agent": Config.USER_AGENT}, timeout=30)
        if resp.status_code == 200 and is_valid_pdf(resp.content):
            path = save_pdf(resp.content, save_dir, doi, result.get("title"))
            return {
                "status": "success",
                "path": str(path),
                "doi": doi,
                "title": result.get("title", ""),
                "source": "unpaywall_oa",
                "mirror": "",
            }
    except Exception:
        pass
    return None


def try_annas_archive_download(identifier: str, save_dir: Path) -> Optional[Dict[str, Any]]:
    """Try to download via Anna's Archive as a fallback."""
    base_url = "https://annas-archive.org"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; paper-fetch/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        search_url = f"{base_url}/search?q={quote_plus(identifier)}"
        resp = session.get(search_url, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        file_page_url = ""
        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if re.search(r"/md5/[0-9a-fA-F]{32}", href):
                file_page_url = urljoin(base_url, href)
                break

        if not file_page_url:
            return None

        resp = session.get(file_page_url, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        pdf_url = ""
        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if not href:
                continue
            lowered = href.lower()
            if "torrent" in lowered:
                continue
            if ".pdf" in lowered or "download" in lowered:
                pdf_url = urljoin(base_url, href)
                break

        if not pdf_url:
            return None

        resp = session.get(pdf_url, stream=True, timeout=60)
        resp.raise_for_status()

        first_chunk = next(resp.iter_content(chunk_size=1024), b"")
        content_type = (resp.headers.get("content-type") or "").lower()
        if "pdf" not in content_type and not first_chunk.startswith(b"%PDF"):
            return None

        content = first_chunk + b"".join(resp.iter_content(chunk_size=8192))
        if not is_valid_pdf(content):
            return None

        safe_hint = re.sub(r"[^a-zA-Z0-9._-]+", "_", identifier)[:80] or "paper"
        digest = hashlib.md5((pdf_url + identifier).encode("utf-8")).hexdigest()[:8]
        path = save_pdf(content, save_dir, doi=identifier, title=f"annas_{safe_hint}_{digest}")
        return {
            "status": "success",
            "path": str(path),
            "doi": identifier,
            "title": safe_hint,
            "source": "annas_archive",
            "mirror": "",
        }
    except Exception:
        return None


def try_mirror_download(doi: str, save_dir: Path) -> Optional[Dict[str, Any]]:
    """Download via academic mirrors, trying each in order."""
    mirrors = get_working_mirrors()
    session = _session()

    for mirror in mirrors:
        try:
            url = f"{mirror}/{doi}"
            resp = session.get(url, timeout=30, verify=False)
            if resp.status_code != 200:
                continue

            # Check for "article not found"
            if "article not found" in resp.text.lower():
                continue

            pdf_url = _extract_pdf_url(resp.text, mirror)
            if not pdf_url:
                continue

            pdf_resp = session.get(pdf_url, timeout=60, verify=False)
            if pdf_resp.status_code != 200:
                continue

            if not is_valid_pdf(pdf_resp.content):
                continue

            # Try to extract title from the mirror page
            soup = BeautifulSoup(resp.text, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else ""
            if title.lower() in ("sci-hub", "loading", "redirect", ""):
                title = ""

            path = save_pdf(pdf_resp.content, save_dir, doi, title)
            return {
                "status": "success",
                "path": str(path),
                "doi": doi,
                "title": title,
                "source": "mirror",
                "mirror": mirror,
            }
        except Exception:
            continue

    return None


def try_direct_pdf_fallback(doi: str, save_dir: Path) -> Optional[Dict[str, Any]]:
    """Try to find a direct PDF via search APIs as last resort."""
    results = search_all(doi, max_results=3)
    for paper in results:
        if "error" in paper:
            continue
        pdf_url = paper.get("pdf_url", "")
        if not pdf_url:
            continue
        try:
            resp = requests.get(pdf_url, headers={"User-Agent": Config.USER_AGENT}, timeout=30)
            if resp.status_code == 200 and is_valid_pdf(resp.content):
                path = save_pdf(resp.content, save_dir, doi, paper.get("title"))
                return {
                    "status": "success",
                    "path": str(path),
                    "doi": doi,
                    "title": paper.get("title", ""),
                    "source": paper.get("source", "direct"),
                    "mirror": "",
                }
        except Exception:
            continue
    return None


def download_paper(identifier: str, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Download a paper by DOI, URL, or identifier.

    Pipeline:
      1. Extract/normalize DOI
      2. Try OA download (Unpaywall) — fastest/cleanest path when email is set
      3. Try academic mirrors — fallback, no email needed
      4. Try Anna's Archive fallback
      5. Try direct PDF fallback — last resort
    """
    save_dir = output_dir or Config.ensure_download_dir()
    doi = extract_doi(identifier)

    if not doi:
        return {
            "status": "error",
            "error": f"Could not extract DOI from: {identifier}",
            "path": "",
            "doi": "",
            "title": "",
            "source": "",
            "mirror": "",
        }

    # Step 2: OA fast path (requires email)
    result = try_oa_download(doi, save_dir)
    if result:
        return result

    # Step 3: Mirror fallback (no email needed)
    result = try_mirror_download(doi, save_dir)
    if result:
        return result

    # Step 4: Anna's Archive fallback
    result = try_annas_archive_download(doi, save_dir)
    if result:
        return result

    # Step 5: Direct PDF fallback
    result = try_direct_pdf_fallback(doi, save_dir)
    if result:
        return result

    return {
        "status": "error",
        "error": f"Failed to download paper: {doi}. Tried OA, academic mirrors, Anna's Archive, and direct PDF fallbacks.",
        "path": "",
        "doi": doi,
        "title": "",
        "source": "",
        "mirror": "",
    }
