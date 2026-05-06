"""PDF utilities: validation, filename sanitization, metadata extraction."""
import hashlib
import re
from pathlib import Path
from typing import Optional


def is_valid_pdf(data: bytes) -> bool:
    """Check if bytes start with PDF magic number."""
    return data.startswith(b"%PDF")


def safe_filename(text: str, max_length: int = 120) -> str:
    """Sanitize a string for use as a filename."""
    # Remove or replace characters unsafe for filenames
    safe = re.sub(r'[^\w\s\-_.]', '_', text)
    safe = re.sub(r'\s+', '_', safe).strip('._')
    if not safe:
        safe = "paper"
    return safe[:max_length]


def generate_pdf_filename(
    identifier: str,
    title: Optional[str] = None,
    pdf_data: Optional[bytes] = None,
) -> str:
    """Generate a descriptive, unique filename for a PDF.

    Args:
        identifier: DOI or other identifier (used as fallback).
        title: Paper title (preferred for filename).
        pdf_data: Raw PDF bytes (used for hash suffix).

    Returns:
        A filename like "2023_quantum_entanglement_a1b2c3d4.pdf"
    """
    hash_suffix = ""
    if pdf_data:
        hash_suffix = hashlib.md5(pdf_data).hexdigest()[:8]

    if title:
        base = safe_filename(title)
    else:
        base = safe_filename(identifier)

    if hash_suffix:
        return f"{base}_{hash_suffix}.pdf"
    return f"{base}.pdf"


def save_pdf(
    pdf_data: bytes,
    save_dir: Path,
    identifier: str,
    title: Optional[str] = None,
) -> Path:
    """Save PDF bytes to disk with a safe filename.

    Returns:
        Path to the saved file.
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    filename = generate_pdf_filename(identifier, title, pdf_data)
    file_path = save_dir / filename

    # If file already exists, append a counter
    counter = 1
    original_path = file_path
    while file_path.exists():
        stem = original_path.stem
        suffix = original_path.suffix
        file_path = save_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    file_path.write_bytes(pdf_data)
    return file_path


def extract_doi(text: str) -> Optional[str]:
    """Extract a DOI from arbitrary text or URL.

    Handles:
      - bare DOI: 10.1038/nature12373
      - DOI URL: https://doi.org/10.1038/nature12373
      - dx.doi.org: http://dx.doi.org/10.1038/nature12373
    """
    if not text:
        return None

    # Strip common URL prefixes
    cleaned = text.strip()
    for prefix in ("https://doi.org/", "http://doi.org/",
                   "https://dx.doi.org/", "http://dx.doi.org/"):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break

    # DOI regex: 10. followed by 4+ digits, then /, then any printable chars
    match = re.search(r"10\.\d{4,}[/.][^\s<>\"]+", cleaned)
    if match:
        doi = match.group(0)
        # Trim trailing punctuation
        trailing = '.,;:\'"'
        doi = doi.rstrip(trailing)
        return doi

    return None


def extract_arxiv_id(text: str) -> Optional[str]:
    """Extract an arXiv ID from text."""
    match = re.search(r"arxiv[:\s]*(\d{4}\.\d{4,5}(?:v\d+)?)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Also match old format
    match = re.search(r"arxiv[:\s]*([a-z\-]+/\d{7}(?:v\d+)?)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None
