"""Search academic papers across free APIs."""
from typing import Any, Dict, List, Optional

import requests

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


def search_all(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search across all free APIs and merge results."""
    all_results: List[Dict[str, Any]] = []

    all_results.extend(search_openalex(query, max_results))
    all_results.extend(search_semantic_scholar(query, max_results))
    all_results.extend(search_crossref(query, max_results))
    all_results.extend(search_arxiv(query, max_results))

    # Deduplicate by DOI, then by title
    seen_doi: set[str] = set()
    seen_title: set[str] = set()
    deduped: List[Dict[str, Any]] = []

    for paper in all_results:
        if "error" in paper:
            deduped.append(paper)
            continue
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

    return deduped
