"""Search academic papers across free APIs."""
import concurrent.futures
import random
import re
import time
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from config import Config
from pdf_utils import extract_arxiv_id


def _headers() -> Dict[str, str]:
    return {"User-Agent": Config.USER_AGENT, "Accept": "application/json"}


def search_openalex(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search OpenAlex for papers."""
    url = "https://api.openalex.org/works"
    params: Dict[str, Any] = {
        "search": query,
        "per-page": min(max_results, 25),
        "mailto": Config.CROSSREF_MAILTO or Config.UNPAYWALL_EMAIL,
    }
    if Config.OPENALEX_API_KEY:
        params["api_key"] = Config.OPENALEX_API_KEY

    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("results", []):
            bib = item.get("biblio", {})
            authorships = item.get("authorships", [])
            authors = [a.get("author", {}).get("display_name", "") for a in authorships]
            oa = item.get("open_access", {})
            pub_year = item.get("publication_year")
            results.append({
                "title": item.get("display_name", ""),
                "authors": ", ".join(filter(None, authors)),
                "year": str(pub_year) if pub_year is not None else "",
                "doi": item.get("doi", ""),
                "source": "openalex",
                "pdf_url": oa.get("oa_url", ""),
                "is_oa": oa.get("is_oa", False),
                "paper_id": item.get("id", ""),
            })
        return results
    except Exception as e:
        return [{"error": f"OpenAlex: {e}", "source": "openalex"}]


def search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Semantic Scholar for papers."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params: Dict[str, Any] = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": "title,authors,year,doi,openAccessPdf",
    }
    headers = _headers()
    if Config.SEMANTIC_API_KEY:
        headers["x-api-key"] = Config.SEMANTIC_API_KEY

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("data", []):
            authors = item.get("authors", [])
            author_names = [a.get("name", "") for a in authors]
            oa_pdf = item.get("openAccessPdf", {}) or {}
            year = item.get("year")
            results.append({
                "title": item.get("title", ""),
                "authors": ", ".join(filter(None, author_names)),
                "year": str(year) if year is not None else "",
                "doi": item.get("doi", ""),
                "source": "semantic_scholar",
                "pdf_url": oa_pdf.get("url", ""),
                "is_oa": bool(oa_pdf.get("url")),
                "paper_id": item.get("paperId", ""),
            })
        return results
    except Exception as e:
        return [{"error": f"Semantic Scholar: {e}", "source": "semantic_scholar"}]


def search_crossref(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Crossref for papers."""
    url = "https://api.crossref.org/works"
    params: Dict[str, Any] = {
        "query": query,
        "rows": min(max_results, 25),
        "sort": "relevance",
        "order": "desc",
    }
    if Config.CROSSREF_MAILTO:
        params["mailto"] = Config.CROSSREF_MAILTO

    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("message", {}).get("items", []):
            authors = item.get("author", [])
            author_names = []
            for a in authors:
                given = a.get("given", "")
                family = a.get("family", "")
                author_names.append(f"{given} {family}".strip())
            year = ""
            published = item.get("published-print") or item.get("published-online")
            if published:
                year = str(published.get("date-parts", [[""]])[0][0])
            results.append({
                "title": item.get("title", [""])[0] if isinstance(item.get("title"), list) else item.get("title", ""),
                "authors": ", ".join(filter(None, author_names)),
                "year": year,
                "doi": item.get("DOI", ""),
                "source": "crossref",
                "pdf_url": "",
                "is_oa": item.get("is-referenced-by-count", 0) > 0,
                "paper_id": item.get("DOI", ""),
            })
        return results
    except Exception as e:
        return [{"error": f"Crossref: {e}", "source": "crossref"}]


def search_arxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search arXiv for preprints."""
    import xml.etree.ElementTree as ET

    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": min(max_results, 50),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.findtext("atom:title", "", ns).replace("\n", " ").strip()
            authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
            doi = ""
            for cat in entry.findall("arxiv:doi", ns):
                doi = cat.text or ""
            arxiv_id = entry.findtext("atom:id", "", ns).split("/abs/")[-1]
            year = ""
            published = entry.findtext("atom:published", "", ns)
            if published:
                year = published[:4]
            results.append({
                "title": title,
                "authors": ", ".join(filter(None, authors)),
                "year": year,
                "doi": doi,
                "source": "arxiv",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "is_oa": True,
                "paper_id": arxiv_id,
            })
        return results
    except Exception as e:
        return [{"error": f"arXiv: {e}", "source": "arxiv"}]


def lookup_unpaywall(doi: str) -> Optional[Dict[str, Any]]:
    """Lookup a DOI on Unpaywall to find OA PDF URLs."""
    if not Config.UNPAYWALL_EMAIL:
        return None
    url = f"https://api.unpaywall.org/v2/{doi}"
    params = {"email": Config.UNPAYWALL_EMAIL}
    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        best = data.get("best_oa_location", {}) or {}
        return {
            "title": data.get("title", ""),
            "doi": doi,
            "year": str(data.get("year", "")),
            "authors": "",
            "source": "unpaywall",
            "pdf_url": best.get("url_for_pdf", ""),
            "is_oa": data.get("is_oa", False),
            "paper_id": doi,
        }
    except Exception:
        return None


def search_biorxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search bioRxiv for preprints."""
    base_url = "https://api.biorxiv.org/details/biorxiv"
    date_range_pattern = re.compile(
        r"^\s*(\d{4}-\d{2}-\d{2})\s*(?:/|:|\.\.|to)\s*(\d{4}-\d{2}-\d{2})\s*$",
        re.IGNORECASE,
    )

    normalized_query = (query or "").strip()
    doi = None
    # Simple DOI check
    if "/" in normalized_query and any(
        normalized_query.lower().startswith(p)
        for p in ["10.", "doi:", "https://doi.org/"]
    ):
        doi = normalized_query.replace("doi:", "").replace("https://doi.org/", "").strip()

    date_match = date_range_pattern.match(normalized_query)

    try:
        if doi:
            url = f"{base_url}/{doi}/na/json"
        elif date_match:
            start, end = date_match.group(1), date_match.group(2)
            url = f"{base_url}/{start}/{end}/0/json"
        else:
            # Default: last 30 days
            from datetime import datetime, timedelta
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            url = f"{base_url}/{start}/{end}/0/json"

        resp = requests.get(url, headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("collection", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "authors": item.get("authors", "").replace("; ", ", "),
                "year": item.get("date", "")[:4] if item.get("date") else "",
                "doi": item.get("doi", ""),
                "source": "biorxiv",
                "pdf_url": f"https://www.biorxiv.org/content/{item.get('doi', '')}v{item.get('version', '1')}.full.pdf",
                "is_oa": True,
                "paper_id": item.get("doi", ""),
            })
        return results
    except Exception as e:
        return [{"error": f"bioRxiv: {e}", "source": "biorxiv"}]


def search_google_scholar(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google Scholar via HTML scraping."""
    scholar_url = "https://scholar.google.com/scholar"
    browsers = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    ]

    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(browsers),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    # Avoid consent interstitial pages
    session.cookies.set("CONSENT", "YES+", domain=".google.com")

    papers = []
    start = 0
    results_per_page = 10
    consent_retry_attempted = False
    max_retries = 3

    while len(papers) < max_results:
        try:
            params = {"q": query, "start": start, "hl": "en", "as_sdt": "0,5"}
            response = None

            for attempt in range(max_retries):
                session.headers.update({"User-Agent": random.choice(browsers)})
                time.sleep(random.uniform(1.0, 2.5))
                response = session.get(scholar_url, params=params, timeout=30)
                if response.status_code == 200:
                    break
                if response.status_code in (403, 429, 503):
                    wait_time = 2.0 * (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(wait_time)
                    continue
                break

            if response is None or response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(" ", strip=True).lower()

            # Check for consent page
            if soup.find("form", {"action": re.compile(r"consent\.google", re.IGNORECASE)}) or \
               "before you continue to google scholar" in page_text:
                if not consent_retry_attempted:
                    consent_retry_attempted = True
                    session.cookies.set("CONSENT", "YES+", domain=".google.com")
                    continue
                break

            # Check for captcha
            if soup.find("form", {"id": "gs_captcha_f"}) or \
               soup.find("input", {"name": "captcha"}) or \
               "please show you're not a robot" in page_text:
                break

            results = soup.find_all("div", class_="gs_ri")
            if not results:
                break

            for item in results:
                if len(papers) >= max_results:
                    break
                title_elem = item.find("h3", class_="gs_rt")
                info_elem = item.find("div", class_="gs_a")
                abstract_elem = item.find("div", class_="gs_rs")

                if not title_elem or not info_elem:
                    continue

                title = title_elem.get_text(strip=True).replace("[PDF]", "").replace("[HTML]", "")
                link = title_elem.find("a", href=True)
                url = link["href"] if link else ""

                info_text = info_elem.get_text()
                authors = [a.strip() for a in info_text.split("-")[0].split(",")]
                year = None
                for word in info_text.split():
                    if word.isdigit() and 1900 <= int(word) <= 2100:
                        year = int(word)
                        break

                # Try to extract DOI from URL, title, or info text
                doi = ""
                for text in [url, title, info_text]:
                    m = re.search(r"10\.\d{4,}[\/\.][^\s\"<>]+", text)
                    if m:
                        doi = m.group(0)
                        break

                papers.append({
                    "title": title,
                    "authors": ", ".join(filter(None, authors)),
                    "year": str(year) if year else "",
                    "doi": doi,
                    "source": "google_scholar",
                    "pdf_url": "",
                    "is_oa": False,
                    "paper_id": f"gs_{hash(url) & 0xFFFFFFFF}",
                })

            start += results_per_page

        except Exception as e:
            return [{"error": f"Google Scholar: {e}", "source": "google_scholar"}]

    return papers[:max_results]


def search_all(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search across all free APIs in parallel with per-source timeouts."""
    all_results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    sources = [
        ("openalex", search_openalex),
        ("semantic_scholar", search_semantic_scholar),
        ("crossref", search_crossref),
        ("arxiv", search_arxiv),
        ("biorxiv", search_biorxiv),
        ("google_scholar", search_google_scholar),
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {
            executor.submit(fn, query, max_results): name
            for name, fn in sources
        }
        for future in concurrent.futures.as_completed(future_map):
            source_name = future_map[future]
            try:
                results = future.result(timeout=45)
                for r in results:
                    if "error" in r:
                        errors.append(r)
                    else:
                        all_results.append(r)
            except concurrent.futures.TimeoutError:
                errors.append({"error": f"{source_name}: search timed out after 45s", "source": source_name})
            except Exception as e:
                errors.append({"error": f"{source_name}: {e}", "source": source_name})

    # Deduplicate by DOI, then by title
    seen_doi: set[str] = set()
    seen_title: set[str] = set()
    deduped: List[Dict[str, Any]] = []

    for paper in all_results:
        doi = (paper.get("doi") or "").lower().strip()
        title = (paper.get("title") or "").lower().strip()
        if doi and doi in seen_doi:
            continue
        if title and title in seen_title:
            continue
        if doi:
            seen_doi.add(doi)
        if title:
            seen_title.add(title)
        deduped.append(paper)

    deduped.extend(errors)
    return deduped
