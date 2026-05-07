"""Configuration and environment variable management."""
import os
from pathlib import Path
from typing import List, Optional

SKILL_DIR = Path(__file__).resolve().parent


def _load_dotenv() -> None:
    env_file = SKILL_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val


_load_dotenv()


class Config:
    UNPAYWALL_EMAIL: str = os.getenv("PAPER_FETCH_UNPAYWALL_EMAIL", "")

    OPENALEX_API_KEY: Optional[str] = os.getenv("PAPER_FETCH_OPENALEX_API_KEY") or None
    SEMANTIC_API_KEY: Optional[str] = os.getenv("PAPER_FETCH_SEMANTIC_API_KEY") or None
    CORE_API_KEY: Optional[str] = os.getenv("PAPER_FETCH_CORE_API_KEY") or None

    CROSSREF_MAILTO: str = os.getenv("PAPER_FETCH_CROSSREF_MAILTO", "")

    PREFERRED_MIRROR: Optional[str] = os.getenv("PAPER_FETCH_PREFERRED_MIRROR") or None
    MIRRORS_OVERRIDE: List[str] = [
        m.strip()
        for m in (os.getenv("PAPER_FETCH_MIRRORS", "")).split(",")
        if m.strip()
    ]

    DOWNLOAD_DIR: Path = Path(
        os.getenv("PAPER_FETCH_DOWNLOAD_DIR", "~/Downloads/papers")
    ).expanduser()

    MIRROR_CACHE_TTL: int = int(os.getenv("PAPER_FETCH_MIRROR_CACHE_TTL", "21600"))
    MIRROR_CACHE_FILE: Path = Path("/tmp/paper-fetch-mirrors-cache.json")
    MIRROR_DISCOVERY_TIMEOUT: float = float(os.getenv("PAPER_FETCH_MIRROR_DISCOVERY_TIMEOUT", "5"))
    MIRROR_PROBE_TIMEOUT: float = float(os.getenv("PAPER_FETCH_MIRROR_PROBE_TIMEOUT", "4"))
    MIRROR_PROBE_WORKERS: int = int(os.getenv("PAPER_FETCH_MIRROR_PROBE_WORKERS", "8"))

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @classmethod
    def validate(cls) -> List[str]:
        missing = []
        if not cls.UNPAYWALL_EMAIL:
            missing.append("PAPER_FETCH_UNPAYWALL_EMAIL")
        return missing

    @classmethod
    def ensure_download_dir(cls) -> Path:
        cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return cls.DOWNLOAD_DIR


def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)
