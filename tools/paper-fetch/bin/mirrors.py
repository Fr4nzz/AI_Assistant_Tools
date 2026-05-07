"""Sci-Hub mirror discovery with caching and health probes."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
from typing import List, Optional

import requests

from config import Config


def _normalize_mirror(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url
    return url


def _is_sci_hub_domain(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        netloc = urlparse(url).netloc.lower()
        return "sci-hub" in netloc or "scihub" in netloc
    except Exception:
        return False


def _fetch_sci_hub_now_sh() -> List[str]:
    """Scrape https://sci-hub.now.sh for working mirror URLs."""
    try:
        resp = requests.get(
            "https://sci-hub.now.sh",
            headers={"User-Agent": Config.USER_AGENT},
            timeout=Config.MIRROR_DISCOVERY_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception:
        return []

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text, "html.parser")
    mirrors: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "sci-hub" in href or "sci_hub" in href:
            mirrors.add(_normalize_mirror(href))

    for div in soup.find_all(["div", "span", "p"]):
        text = div.get_text()
        for word in text.split():
            if word.startswith("sci-hub.") or word.startswith("sci_hub."):
                mirrors.add(_normalize_mirror(word))

    return list(mirrors)


def _fetch_wikidata() -> List[str]:
    """Query Wikidata SPARQL for official Sci-Hub URLs."""
    sparql = """
    SELECT ?url WHERE {
      wd:Q21980377 p:P856 [wikibase:rank wikibase:PreferredRank; ps:P856 ?url].
    }
    """
    try:
        resp = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": sparql, "format": "json"},
            headers={"User-Agent": Config.USER_AGENT},
            timeout=Config.MIRROR_DISCOVERY_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        urls = []
        for binding in data.get("results", {}).get("bindings", []):
            url = binding.get("url", {}).get("value", "")
            if url:
                urls.append(_normalize_mirror(url))
        return urls
    except Exception:
        return []


def _fetch_whereisscihub() -> List[str]:
    """Query whereisscihub.now.sh/api for mirror URLs."""
    try:
        resp = requests.get(
            "https://whereisscihub.now.sh/api",
            headers={"User-Agent": Config.USER_AGENT},
            timeout=Config.MIRROR_DISCOVERY_TIMEOUT,
        )
        resp.raise_for_status()
        urls = resp.json()
        return [_normalize_mirror(u) for u in urls if isinstance(u, str)]
    except Exception:
        return []


HARDCODED_MIRRORS = [
    "https://sci-hub.box",
    "https://sci-hub.st",
    "https://sci-hub.ru",
    "https://sci-hub.se",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
    "https://sci-hub.al",
    "https://sci-hub.mk",
    "https://sci-hub.do",
    "https://sci-hub.shop",
]


def discover_mirrors() -> List[str]:
    """Return a deduplicated list of potential mirrors from multiple sources."""
    mirrors: List[str] = []

    if Config.MIRRORS_OVERRIDE:
        mirrors.extend(Config.MIRRORS_OVERRIDE)

    if Config.PREFERRED_MIRROR and Config.PREFERRED_MIRROR not in mirrors:
        mirrors.insert(0, _normalize_mirror(Config.PREFERRED_MIRROR))

    discovery_sources = [
        _fetch_sci_hub_now_sh,
        _fetch_whereisscihub,
        _fetch_wikidata,
    ]
    with ThreadPoolExecutor(max_workers=len(discovery_sources)) as executor:
        for future in as_completed(executor.submit(source) for source in discovery_sources):
            try:
                mirrors.extend(future.result())
            except Exception:
                pass

    mirrors.extend(HARDCODED_MIRRORS)

    seen: set[str] = set()
    unique: List[str] = []
    for m in mirrors:
        if m not in seen and _is_sci_hub_domain(m):
            seen.add(m)
            unique.append(m)
    return unique


def _health_probe(mirror: str) -> Optional[float]:
    """Probe a mirror and return latency in seconds, or None if dead."""
    start = time.time()
    try:
        resp = requests.head(
            mirror,
            headers={"User-Agent": Config.USER_AGENT},
            timeout=Config.MIRROR_PROBE_TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code < 500:
            return time.time() - start
    except Exception:
        return None

    # Some mirrors reject HEAD but serve normal browser requests. Only pay for
    # the fallback GET after the host has already answered the HEAD request.
    if resp.status_code not in (403, 405):
        return None

    try:
        start = time.time()
        resp = requests.get(
            mirror,
            headers={"User-Agent": Config.USER_AGENT},
            timeout=Config.MIRROR_PROBE_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
        if resp.status_code < 500:
            return time.time() - start
    except Exception:
        pass
    return None


def health_check(mirrors: List[str]) -> List[str]:
    """Return only responsive mirrors, sorted by latency (fastest first)."""
    if not mirrors:
        return []

    results = []
    max_workers = max(1, min(Config.MIRROR_PROBE_WORKERS, len(mirrors)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_mirror = {executor.submit(_health_probe, m): m for m in mirrors}
        for future in as_completed(future_to_mirror):
            mirror = future_to_mirror[future]
            try:
                latency = future.result()
            except Exception:
                latency = None
            if latency is not None:
                results.append((latency, mirror))

    results.sort(key=lambda x: x[0])
    return [m for _, m in results]


def load_cached_mirrors() -> Optional[List[str]]:
    """Load mirrors from cache if still valid."""
    try:
        if not Config.MIRROR_CACHE_FILE.exists():
            return None
        data = json.loads(Config.MIRROR_CACHE_FILE.read_text())
        if time.time() - data.get("timestamp", 0) < Config.MIRROR_CACHE_TTL:
            return data.get("mirrors")
    except Exception:
        pass
    return None


def save_cached_mirrors(mirrors: List[str]) -> None:
    """Save mirrors to cache file."""
    try:
        Config.MIRROR_CACHE_FILE.write_text(
            json.dumps({"timestamp": time.time(), "mirrors": mirrors}, indent=2)
        )
    except Exception:
        pass


def get_working_mirrors(force_refresh: bool = False) -> List[str]:
    """Return responsive sci-hub mirrors, using cache when possible."""
    if not force_refresh:
        cached = load_cached_mirrors()
        if cached:
            return cached

    discovered = discover_mirrors()
    working = health_check(discovered)

    if working:
        save_cached_mirrors(working)
        return working

    return HARDCODED_MIRRORS
