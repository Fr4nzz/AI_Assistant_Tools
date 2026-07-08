#!/usr/bin/env python3
"""
Outlook/Microsoft 365 CLI -- institutional email + calendar.

Read-only by default. Uses OWA's own MSAL token (extracted from a headless
Chromium session) to talk to the Outlook REST API v2.0.

Run `outlook --help` to see all commands, or `outlook raw <path>` to hit
arbitrary endpoints with auth + sensible defaults.
"""

import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

if sys.platform.startswith("win"):
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTLOOK_BASE = "https://outlook.office.com/api/v2.0"
OWA_URL = "https://outlook.cloud.microsoft/mail/"

if sys.platform.startswith("win"):
    SHARE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "outlook-cli"
else:
    SHARE_DIR = Path.home() / ".local/share/outlook-cli"
BROWSER_DATA_DIR = SHARE_DIR / "browser-data"
TOKEN_FILE = SHARE_DIR / "token.json"
TOKEN_LOCK_FILE = SHARE_DIR / "token.lock"
BROWSER_LOCK_FILE = SHARE_DIR / "browser.lock"
ID_MAP_FILE = SHARE_DIR / "id_map.json"
CONFIG_FILE = Path(os.environ.get("AI_ASSISTANT_TOOLS_MICROSOFT_ENV", str(Path.home() / ".config/ai-assistant-tools/microsoft.env")))
ID_MAP_MAX = 2000

# User's local timezone (USFQ is in Ecuador)
DEFAULT_TIMEZONE = os.environ.get("OUTLOOK_TIMEZONE", "America/Guayaquil")
TOKEN_REFRESH_TIMEOUT = int(os.environ.get("OUTLOOK_TOKEN_REFRESH_TIMEOUT", "10"))

# Common $select field sets
SELECT_MSG_LIST = "Subject,From,ReceivedDateTime,BodyPreview,IsRead,HasAttachments,Importance,Id,ConversationId,InferenceClassification"
SELECT_MSG_FULL = "Subject,From,ToRecipients,CcRecipients,ReceivedDateTime,Body,HasAttachments,Importance,IsRead,ConversationId,InternetMessageId,WebLink"
SELECT_EVENT_LIST = "Subject,Start,End,Location,IsAllDay,ShowAs,IsCancelled,OnlineMeetingUrl,Organizer,Id"
SELECT_EVENT_FULL = "Subject,Start,End,Location,IsAllDay,ShowAs,IsCancelled,OnlineMeetingUrl,Organizer,Attendees,Body,IsOrganizer,ResponseStatus,SeriesMasterId,WebLink"


# ---------------------------------------------------------------------------
# HTML-to-plain-text helper
# ---------------------------------------------------------------------------
class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in ("br", "p", "div", "tr", "li"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


def strip_html(html: str) -> str:
    if not html:
        return ""
    s = _HTMLStripper()
    s.feed(html)
    text = s.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Short ID system: map long Outlook IDs to 6-char hex for readable CLI use
# ---------------------------------------------------------------------------
def _load_id_map() -> dict:
    if not ID_MAP_FILE.exists():
        return {}
    try:
        return json.loads(ID_MAP_FILE.read_text())
    except Exception:
        return {}


def _save_id_map(m: dict) -> None:
    if len(m) > ID_MAP_MAX:
        # Keep only the most recently inserted entries (Python dicts preserve order)
        items = list(m.items())[-ID_MAP_MAX:]
        m = dict(items)
    ID_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    ID_MAP_FILE.write_text(json.dumps(m))


def short_id(full_id: str, id_map: dict) -> str:
    """Assign or retrieve a 6-char short ID for a full Outlook ID."""
    if not full_id:
        return ""
    base = hashlib.md5(full_id.encode()).hexdigest()
    short = base[:6]
    # Handle collisions by extending until unique (rare)
    i = 6
    while short in id_map and id_map[short] != full_id and i < 32:
        i += 1
        short = base[:i]
    id_map[short] = full_id
    return short


def resolve_id(arg: str) -> str:
    """Resolve a short ID (6-32 hex chars) to a full ID, or return unchanged.

    Long Outlook IDs are ~140 chars of base64url, so anything that looks like
    short hex is treated as a short ID.
    """
    if arg and re.match(r'^[0-9a-f]{6,32}$', arg) and len(arg) < 33:
        id_map = _load_id_map()
        if arg in id_map:
            return id_map[arg]
    return arg


def record_ids(items: list, id_fields: tuple = ("Id",)) -> None:
    """Add short IDs for every item in a list to the persistent id_map.

    Called from command functions so --json output still populates the map,
    letting the agent reference messages by short ID on follow-up calls.
    """
    if not items:
        return
    id_map = _load_id_map()
    changed = False
    for it in items:
        if not isinstance(it, dict):
            continue
        for field in id_fields:
            full = it.get(field)
            if full:
                short_id(full, id_map)
                changed = True
    if changed:
        _save_id_map(id_map)


# ---------------------------------------------------------------------------
# Signature / disclaimer trimming (USFQ and common patterns)
# ---------------------------------------------------------------------------
_SIG_MARKERS = [
    # USFQ-specific
    "Nota de descargo",
    "Disclaimer:",
    "logo_usfq_pieFirma",
    "Diego de Robles y Via Interoceanica",
    "www.usfq.edu.ec",
    "datos@usfq.edu.ec",
    "PoliticaDatosPersonales",
    # Generic email signature markers
    "-- \n",
    "CONFIDENTIALITY NOTICE",
    "This e-mail and any attachments",
    "If you are not the intended recipient",
]

_SIG_LINE_PATTERNS = [
    re.compile(r'^\[http[s]?://.*(?:logo|signature|banner|pieFirma)'),  # embedded logo images
    re.compile(r'^-{5,}\s*$'),  # horizontal rules often before signatures
]


def trim_signature(body: str) -> str:
    """Cut body at first signature/disclaimer marker, with safety checks.

    Strategy: find the earliest signature marker. If the body before it has
    real content, cut there. If the marker is at the very start (body IS
    just a signature), return a short placeholder so the agent knows.
    """
    if not body:
        return body
    lines = body.split("\n")
    cut = len(lines)
    for i, line in enumerate(lines):
        matched = False
        for marker in _SIG_MARKERS:
            if marker in line:
                matched = True
                break
        if not matched:
            for pat in _SIG_LINE_PATTERNS:
                if pat.search(line):
                    matched = True
                    break
        if matched:
            cut = min(cut, i)

    if cut == len(lines):
        return body  # No signature found

    # Check if there's real content before the cut
    content_before = "\n".join(lines[:cut]).strip()
    if content_before:
        return content_before

    # Body is entirely signature: return short placeholder
    return "(no body text: signature/disclaimer only)"


# ---------------------------------------------------------------------------
# Browser binary finder
# ---------------------------------------------------------------------------
def _find_chromium() -> str:
    import glob
    if sys.platform.startswith("win"):
        candidates = (
            sorted(glob.glob(str(Path.home() / "AppData/Local/ms-playwright/chromium-*/chrome-win/chrome.exe")), reverse=True)
            + sorted(glob.glob(str(Path.home() / "AppData/Local/ms-playwright/chromium_headless_shell-*/chrome-win/headless_shell.exe")), reverse=True)
            + [
                str(Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"),
                str(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe"),
                str(Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "Google/Chrome/Application/chrome.exe"),
                str(Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe"),
                str(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe"),
            ]
        )
    else:
        candidates = (
            sorted(glob.glob(str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux/chrome")), reverse=True)
            + ["/snap/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/chromium",
               "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"]
        )
    for c in candidates:
        if os.path.isfile(c) and (sys.platform.startswith("win") or os.access(c, os.X_OK)):
            return c
    raise RuntimeError("No Chromium/Chrome found. Install: python -m playwright install chromium")


# ---------------------------------------------------------------------------
# Token management (MSAL cache in localStorage -> Bearer token)
# ---------------------------------------------------------------------------
def _token_matches_target(tok: dict, needle: str) -> bool:
    needle_l = needle.lower()
    if needle_l in (tok.get("target") or "").lower():
        return True
    claims = _decode_jwt_claims(tok.get("secret") or "")
    return needle_l in str(claims.get("aud") or "").lower()


def _load_local_config() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        for raw in CONFIG_FILE.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            values[key.strip()] = value
    except Exception:
        pass
    return values


def _infer_account_email() -> str | None:
    config = _load_local_config()
    explicit = (
        os.environ.get("MICROSOFT_ACCOUNT_EMAIL")
        or os.environ.get("OUTLOOK_ACCOUNT_EMAIL")
        or config.get("MICROSOFT_ACCOUNT_EMAIL")
        or config.get("OUTLOOK_ACCOUNT_EMAIL")
    )
    if explicit:
        return explicit
    try:
        token = json.loads(TOKEN_FILE.read_text())
        for key in ("username", "login_hint"):
            value = token.get(key)
            if value and "@" in value:
                return value
        secret = token.get("secret") or ""
        if secret.count(".") >= 2:
            payload = secret.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload))
            for key in ("preferred_username", "upn", "email", "unique_name"):
                value = claims.get(key)
                if value and "@" in value:
                    return value
    except Exception:
        pass
    return None


def _infer_account_password() -> str | None:
    config = _load_local_config()
    return (
        os.environ.get("MICROSOFT_ACCOUNT_PASSWORD")
        or os.environ.get("OUTLOOK_ACCOUNT_PASSWORD")
        or config.get("MICROSOFT_ACCOUNT_PASSWORD")
        or config.get("OUTLOOK_ACCOUNT_PASSWORD")
    )


def _token_jwt_exp(tok: dict) -> int | None:
    secret = tok.get("secret") or ""
    if secret.count(".") < 2:
        return None
    try:
        payload = secret.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        exp = claims.get("exp")
        return int(exp) if exp else None
    except Exception:
        return None


def _decode_jwt_claims(secret: str) -> dict:
    if not secret or secret.count(".") < 2:
        return {}
    try:
        payload = secret.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload.encode()))
    except Exception:
        return {}


def _token_is_fresh(tok: dict) -> bool:
    jwt_exp = _token_jwt_exp(tok)
    if jwt_exp is not None:
        return time.time() < jwt_exp - 120
    expires = tok.get("expiresOn", 0)
    try:
        return time.time() < int(expires) - 120
    except Exception:
        return False


def _load_cached_token(target: str = "outlook.office.com") -> dict | None:
    if not TOKEN_FILE.exists():
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        if _token_is_fresh(data) and _token_matches_target(data, target):
            return data
    except Exception:
        pass
    return None


def _save_token(tok: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tok))
    try:
        TOKEN_FILE.chmod(0o600)
    except Exception:
        pass


def _iter_browser_storage_files():
    roots = [
        BROWSER_DATA_DIR / "Default" / "Local Storage" / "leveldb",
        BROWSER_DATA_DIR / "Default" / "Session Storage",
        BROWSER_DATA_DIR / "Default" / "IndexedDB",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                yield path


def _load_cached_refresh_token() -> tuple[str, str] | None:
    """Best-effort read of a fresh MSAL SPA refresh token from Chromium storage."""
    pattern = re.compile(r'\{[^{}]*"credentialType":"RefreshToken"[^{}]*\}')
    candidates: list[tuple[int, str, str]] = []
    for path in _iter_browser_storage_files():
        try:
            text = path.read_bytes().replace(b"\x00", b"").decode("utf-8", errors="ignore")
        except Exception:
            continue
        for m in pattern.finditer(text):
            try:
                item = json.loads(m.group(0))
            except Exception:
                continue
            if item.get("credentialType") != "RefreshToken":
                continue
            secret = item.get("secret")
            client_id = item.get("clientId") or "9199bf20-a13f-4107-85dc-02114787ef48"
            if not secret:
                continue
            try:
                expires = int(item.get("expiresOn") or 0)
            except Exception:
                expires = 0
            if expires <= int(time.time()) + 120:
                continue
            candidates.append((expires, client_id, secret))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    _, client_id, secret = candidates[0]
    return client_id, secret


def _exchange_refresh_token_for_outlook(client_id: str, refresh_token: str) -> dict | None:
    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "https://outlook.office.com/.default openid profile offline_access",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Origin": "https://outlook.cloud.microsoft",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
        except Exception:
            err = {"error_description": body}
        desc = err.get("error_description") or err.get("error") or body
        if "AADSTS700084" in desc:
            raise RuntimeError(
                "The saved Microsoft SPA refresh token is expired (AADSTS700084). "
                "Run `outlook login`, complete a fresh interactive Microsoft sign-in, "
                "choose Stay signed in if prompted, close that browser, then retry."
            ) from exc
        if "interaction_required" in desc or "invalid_grant" in desc:
            raise RuntimeError(
                "Microsoft requires an interactive sign-in before a new Outlook token can be issued: " + desc
            ) from exc
        return None
    access_token = data.get("access_token")
    if not access_token:
        return None
    claims = _decode_jwt_claims(access_token)
    now = int(time.time())
    return {
        "homeAccountId": claims.get("oid", "") + "." + claims.get("tid", ""),
        "credentialType": "AccessToken",
        "secret": access_token,
        "cachedAt": str(now),
        "expiresOn": str(claims.get("exp") or int(data.get("expires_in", 0)) + now),
        "extendedExpiresOn": str(claims.get("exp") or int(data.get("expires_in", 0)) + now),
        "environment": "login.microsoftonline.com",
        "clientId": client_id,
        "realm": claims.get("tid", ""),
        "target": claims.get("scp") or "https://outlook.office.com/.default",
        "tokenType": data.get("token_type", "Bearer"),
        "lastUpdatedAt": str(now * 1000),
        "username": claims.get("preferred_username") or claims.get("upn") or claims.get("email"),
    }


def _acquire_token_lock(timeout: int = 10) -> int:
    TOKEN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    while True:
        try:
            return os.open(str(TOKEN_LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except FileExistsError:
            try:
                if time.time() - TOKEN_LOCK_FILE.stat().st_mtime > timeout:
                    TOKEN_LOCK_FILE.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() >= deadline:
                raise RuntimeError("Timed out waiting for Outlook token refresh lock")
            time.sleep(0.5)


def _release_token_lock(fd: int) -> None:
    try:
        os.close(fd)
    finally:
        try:
            TOKEN_LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _acquire_browser_lock(timeout: int = 10) -> int:
    BROWSER_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    while True:
        try:
            return os.open(str(BROWSER_LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except FileExistsError:
            try:
                if time.time() - BROWSER_LOCK_FILE.stat().st_mtime > timeout:
                    BROWSER_LOCK_FILE.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() >= deadline:
                raise RuntimeError("Timed out waiting for shared browser profile lock")
            time.sleep(0.5)


def _release_browser_lock(fd: int) -> None:
    try:
        os.close(fd)
    finally:
        try:
            BROWSER_LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _browser_open_visible():
    """Open the shared Outlook browser profile for manual Microsoft sign-in."""
    import subprocess

    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        SHARE_DIR.chmod(0o700)
        BROWSER_DATA_DIR.chmod(0o700)
    except Exception:
        pass
    args = [
        _find_chromium(),
        "--new-window",
        "--ozone-platform-hint=auto",
        f"--user-data-dir={BROWSER_DATA_DIR}",
        OWA_URL,
    ]
    if sys.platform.startswith("win"):
        return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.DETACHED_PROCESS)
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def _prime_token_from_refresh_cache() -> dict | None:
    refresh = _load_cached_refresh_token()
    if not refresh:
        return None
    tok = _exchange_refresh_token_for_outlook(*refresh)
    if tok and _token_is_fresh(tok) and _token_matches_target(tok, "outlook.office.com"):
        _save_token(tok)
        return tok
    return None


async def _fetch_token_from_browser() -> dict:
    from playwright.async_api import async_playwright

    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    async def click_first_visible(page, labels: list[str], timeout: int = 2500) -> bool:
        deadline = time.time() + (timeout / 1000)
        for label in labels:
            locators = [
                page.get_by_role("button", name=re.compile(label, re.I)).first,
                page.get_by_role("link", name=re.compile(label, re.I)).first,
                page.get_by_text(re.compile(label, re.I)).first,
            ]
            for locator in locators:
                remaining = max(100, int((deadline - time.time()) * 1000))
                if remaining <= 100:
                    return False
                try:
                    await locator.wait_for(state="visible", timeout=min(remaining, 500))
                    await locator.click()
                    await page.wait_for_load_state("domcontentloaded", timeout=1000)
                    return True
                except Exception:
                    pass
        return False

    async def submit_if_visible(page, timeout: int = 800) -> bool:
        for selector in ("input[type=submit]", "button[type=submit]", "#idSIButton9"):
            try:
                btn = page.locator(selector).first
                await btn.wait_for(state="visible", timeout=timeout)
                await btn.click()
                await page.wait_for_load_state("domcontentloaded", timeout=1000)
                return True
            except Exception:
                pass
        return False

    async def fill_email_if_needed(page) -> bool:
        for selector in ("input[type=email]", "input[name=loginfmt]"):
            try:
                field = page.locator(selector).first
                await field.wait_for(state="visible", timeout=600)
                value = await field.input_value()
                if not value:
                    account_email = _infer_account_email()
                    if not account_email:
                        return False
                    await field.fill(account_email)
                return await submit_if_visible(page) or await click_first_visible(page, [r"next", r"siguiente"], timeout=600)
            except Exception:
                pass
        return False

    async def submit_password_if_available(page) -> bool:
        try:
            field = page.locator("input[type=password]").first
            await field.wait_for(state="visible", timeout=600)
            value = await field.input_value()
            if not value:
                password = _infer_account_password()
                if password:
                    await field.fill(password)
                    value = password
            if value:
                return await submit_if_visible(page) or await field.press("Enter")
        except Exception:
            pass
        return False

    async def extract_outlook_token(page) -> dict | None:
        try:
            return await page.evaluate("""() => {
                const stores = [localStorage, sessionStorage];
                for (const store of stores) {
                    for (let i = 0; i < store.length; i++) {
                        const k = store.key(i);
                        if (k.startsWith('msal.') && k.includes('accesstoken')) {
                            try {
                                const v = JSON.parse(store.getItem(k));
                            if (v.target && v.target.includes('outlook.office.com')) {
                                const secret = v.secret || '';
                                const parts = secret.split('.');
                                if (parts.length >= 3) {
                                    try {
                                        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
                                        if (payload.exp && Date.now() / 1000 > payload.exp - 120) continue;
                                    } catch {}
                                }
                                return v;
                            }
                            } catch {}
                        }
                    }
                }
                return null;
            }""")
        except Exception:
            return None

    pw = await async_playwright().start()
    browser = None
    try:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR), headless=True,
            executable_path=_find_chromium(),
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        await page.goto(OWA_URL, timeout=10000)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        await asyncio.sleep(2)

        if "login.microsoftonline.com" in page.url:
            print("Session expired. Logging in via Microsoft SSO...", file=sys.stderr)
            await click_first_visible(page, [r"estud\.usfq\.edu\.ec", r"franz\.chandi", r"use another account", r"usar otra cuenta"], timeout=1500)
            for _ in range(2):
                clicked = False
                clicked |= await fill_email_if_needed(page)
                clicked |= await submit_password_if_available(page)
                clicked |= await click_first_visible(page, [r"sign in", r"iniciar sesi[oó]n", r"siguiente", r"next", r"continuar", r"continue"], timeout=1500)
                clicked |= await submit_if_visible(page, timeout=800)
                clicked |= await click_first_visible(page, [r"yes", r"s[ií]", r"mantener.*sesi[oó]n", r"stay signed in"], timeout=1500)
                if not clicked:
                    break
                await asyncio.sleep(1)
            try:
                await page.wait_for_url("**outlook.cloud.microsoft**", timeout=5000)
            except Exception:
                pass

        for _ in range(10):
            tok = await extract_outlook_token(page)
            if tok and tok.get("secret"):
                return tok
            if "outlook.office.com" not in page.url and "outlook.cloud.microsoft" not in page.url:
                await fill_email_if_needed(page)
                await submit_password_if_available(page)
                await click_first_visible(page, [r"sign in", r"iniciar sesi[oó]n", r"siguiente", r"next", r"yes", r"s[ií]", r"continuar", r"continue"], timeout=1000)
                await submit_if_visible(page, timeout=800)
            await asyncio.sleep(1)

        raise RuntimeError(
            "Could not extract Outlook token from MSAL cache after 10s; "
            f"last page was {page.url}. Run `outlook login` in a visible "
            "browser, choose Stay signed in if prompted, close that browser, "
            "then retry the read-only command."
        )
    finally:
        if browser is not None:
            await browser.close()
        await pw.stop()


def get_token() -> str:
    cached = _load_cached_token()
    if cached:
        return cached["secret"]
    fd = _acquire_token_lock()
    try:
        cached = _load_cached_token()
        if cached:
            return cached["secret"]
        if _load_cached_refresh_token():
            try:
                tok = _prime_token_from_refresh_cache()
                if tok:
                    return tok["secret"]
            except RuntimeError:
                raise
            except Exception:
                pass
        print("Refreshing Outlook token...", file=sys.stderr)
        browser_fd = _acquire_browser_lock()
        try:
            try:
                tok = asyncio.run(asyncio.wait_for(_fetch_token_from_browser(), timeout=TOKEN_REFRESH_TIMEOUT))
            except asyncio.TimeoutError as exc:
                raise RuntimeError(
                    "Outlook token refresh timed out after "
                    f"{TOKEN_REFRESH_TIMEOUT}s. Run `outlook login` in a visible "
                    "browser, choose Stay signed in if prompted, close that "
                    "browser, then retry the read-only command."
                ) from exc
            _save_token(tok)
            return tok["secret"]
        finally:
            _release_browser_lock(browser_fd)
    finally:
        _release_token_lock(fd)


def _jwt_claim(token: str, *names: str) -> str:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload.encode()))
    except Exception:
        return ""
    for name in names:
        value = claims.get(name)
        if isinstance(value, str) and "@" in value:
            return value
    return ""


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def _default_prefer_headers(for_message_body: bool = False) -> list:
    prefer = [
        'IdType="ImmutableId"',
        f'outlook.timezone="{DEFAULT_TIMEZONE}"',
        'odata.maxpagesize=50',
    ]
    if for_message_body:
        prefer.append('outlook.body-content-type="text"')
    return prefer


def _api_url(path: str) -> str:
    if path.startswith("http"):
        url = path
    else:
        if not path.startswith("/"):
            path = "/" + path
        if not path.startswith("/me/") and not path.startswith("/users/"):
            path = "/me" + path  # Default to /me scope
        url = f"{OUTLOOK_BASE}{path}"

    if "?" in url:
        base, _, query = url.partition("?")
        if query and "%" not in query:
            query = urllib.parse.quote(query, safe="=&$'()")
        url = base + "?" + query if query else base
    return url


def api_get(path: str, params: dict | None = None, *, body_as_text: bool = False,
            raw: bool = False) -> dict:
    """GET from Outlook REST API v2.0 with auth + defaults."""
    url = _api_url(path)

    if params:
        sep = "&" if "?" in url else "?"
        url += sep + urllib.parse.urlencode(params)

    for attempt in (1, 2):
        token = get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        anchor_mailbox = _jwt_claim(token, "preferred_username", "upn", "email")
        if anchor_mailbox:
            headers["X-AnchorMailbox"] = anchor_mailbox
        if not raw:
            headers["Prefer"] = ", ".join(_default_prefer_headers(body_as_text))

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                if not body:
                    return {}
                ct = resp.headers.get("Content-Type", "")
                if "json" in ct:
                    return json.loads(body)
                return {"_content_type": ct, "_raw": body.decode("utf-8", errors="replace")}
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt == 1:
                if TOKEN_FILE.exists():
                    TOKEN_FILE.unlink()
                continue
            err_body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"HTTP {e.code}: {err_body[:500]}")
    raise RuntimeError("Exhausted retries")


def api_get_bytes(path: str) -> bytes:
    """GET raw bytes (for attachment downloads, .eml export)."""
    url = _api_url(path)

    for attempt in (1, 2):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        anchor_mailbox = _jwt_claim(token, "preferred_username", "upn", "email")
        if anchor_mailbox:
            headers["X-AnchorMailbox"] = anchor_mailbox
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt == 1:
                if TOKEN_FILE.exists():
                    TOKEN_FILE.unlink()
                continue
            err = e.read().decode() if e.fp else ""
            raise RuntimeError(f"HTTP {e.code}: {err[:300]}")


def paginate(path: str, params: dict | None = None, *, limit: int = 200,
             body_as_text: bool = False) -> list:
    """Follow @odata.nextLink until limit reached or exhausted."""
    params = dict(params or {})
    results = []
    url_or_path = path
    first = True
    while True:
        if first:
            data = api_get(url_or_path, params, body_as_text=body_as_text)
            first = False
        else:
            data = api_get(url_or_path, None, body_as_text=body_as_text)
        results.extend(data.get("value", []))
        next_link = data.get("@odata.nextLink")
        if not next_link or len(results) >= limit:
            return results[:limit]
        url_or_path = next_link


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def fmt_date(iso: str, fmt: str = "%Y-%m-%d %H:%M") -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except Exception:
        return iso[:16]


def fmt_from(msg: dict) -> str:
    ea = (msg.get("From") or {}).get("EmailAddress") or {}
    return ea.get("Name") or ea.get("Address") or "?"


def fmt_addr(r: dict) -> str:
    ea = (r or {}).get("EmailAddress") or {}
    name = ea.get("Name", "")
    addr = ea.get("Address", "")
    return f"{name} <{addr}>" if name and name != addr else addr


def addrs_list(recips: list) -> list:
    return [(((r or {}).get("EmailAddress") or {}).get("Address") or "") for r in (recips or [])]


def shorten(s: str, n: int) -> str:
    if not s:
        return ""
    s = s.replace("\n", " ").replace("\r", " ").strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def iso_date_expr(expr: str, *, with_z: bool = False) -> str:
    """Parse date expressions: 'today', 'yesterday', '7d', '2026-04-15', etc."""
    expr = expr.strip().lower()
    now = datetime.now()
    suffix = "Z" if with_z else ""
    if expr == "today":
        return now.strftime("%Y-%m-%dT00:00:00") + suffix
    if expr == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00") + suffix
    if expr == "tomorrow":
        return (now + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00") + suffix
    m = re.match(r"^(\d+)([dhwmy])$", expr)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        deltas = {"d": timedelta(days=n), "h": timedelta(hours=n),
                  "w": timedelta(weeks=n), "m": timedelta(days=n*30),
                  "y": timedelta(days=n*365)}
        return (now - deltas[unit]).strftime("%Y-%m-%dT%H:%M:%S") + suffix
    # Assume ISO-ish: add Z if requested and not already present
    if with_z and not expr.endswith("z") and "+" not in expr:
        return expr + "Z"
    return expr


def kql_date(expr: str) -> str:
    """Convert date expressions for KQL $search (received:YYYY-MM-DD)."""
    expr = expr.strip().lower()
    now = datetime.now()
    if expr == "today":
        return now.strftime("%Y-%m-%d")
    if expr == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    m = re.match(r"^(\d+)([dw])$", expr)
    if m:
        n = int(m.group(1))
        delta = timedelta(days=n) if m.group(2) == "d" else timedelta(weeks=n)
        return (now - delta).strftime("%Y-%m-%d")
    return expr


# ---------------------------------------------------------------------------
# Message commands
# ---------------------------------------------------------------------------
def _group_by_thread(msgs: list) -> list:
    """Collapse messages by ConversationId. Keep the most recent per thread.

    Returns list of messages with _thread_count and _thread_unread fields.
    """
    threads: dict = {}
    for m in msgs:
        cid = m.get("ConversationId") or m.get("Id")
        t = threads.setdefault(cid, {"messages": []})
        t["messages"].append(m)

    result = []
    for cid, t in threads.items():
        ms = sorted(t["messages"], key=lambda x: x.get("ReceivedDateTime", ""), reverse=True)
        latest = dict(ms[0])
        latest["_thread_count"] = len(ms)
        latest["_thread_unread"] = sum(1 for x in ms if not x.get("IsRead"))
        result.append(latest)
    result.sort(key=lambda m: m.get("ReceivedDateTime", ""), reverse=True)
    return result


def _message_filters(args, *, dates: bool = False) -> list[str]:
    filters = []
    if dates:
        if getattr(args, "since", None):
            filters.append(f"ReceivedDateTime ge {iso_date_expr(args.since, with_z=True)}")
        if getattr(args, "before", None):
            filters.append(f"ReceivedDateTime le {iso_date_expr(args.before, with_z=True)}")
    if getattr(args, "unread", False):
        filters.append("IsRead eq false")
    if getattr(args, "has_attachments", False):
        filters.append("HasAttachments eq true")
    if getattr(args, "importance", None):
        filters.append(f"Importance eq '{args.importance.capitalize()}'")
    return filters


def _list_messages(path: str, args, *, dates: bool = False, default_count: int = 20) -> list:
    params = {"$select": SELECT_MSG_LIST, "$orderby": "ReceivedDateTime desc"}
    filters = _message_filters(args, dates=dates)
    if filters:
        params["$filter"] = " and ".join(filters)

    limit = getattr(args, "count", None) or default_count
    if getattr(args, "threads", False) or getattr(args, "focused", False):
        limit = max(limit * 3, 60)
    msgs = paginate(path, params, limit=limit)
    if getattr(args, "focused", False):
        msgs = [m for m in msgs if m.get("InferenceClassification") == "Focused"]
    return msgs[: getattr(args, "count", None) or default_count]


def cmd_inbox(args):
    folder = args.folder or "inbox"
    msgs = _list_messages(f"/mailfolders/{folder}/messages", args)
    if getattr(args, "threads", False):
        msgs = _group_by_thread(msgs)[: args.count or 20]
    record_ids(msgs)
    return msgs


def cmd_search(args):
    """Full-text search via KQL. Supports --from, --since, etc. as shortcuts."""
    # If the caller only needs structured/date filters, use OData. Outlook KQL
    # date operators are less reliable through this REST endpoint, and raw
    # OData should not be needed for normal "this week" scans.
    if not args.query and not args.from_addr and not args.to_addr and not args.subject:
        msgs = _list_messages("/messages", args, dates=True)
        record_ids(msgs)
        return msgs

    kql_parts = []
    if args.query:
        kql_parts.append(args.query)
    if args.from_addr:
        kql_parts.append(f"from:{args.from_addr}")
    if args.to_addr:
        kql_parts.append(f"to:{args.to_addr}")
    if args.subject:
        subject = str(args.subject).replace('"', " ").strip()
        kql_parts.append(f"subject:{subject}")
    if args.since:
        kql_parts.append(f"received:>={kql_date(args.since)}")
    if args.before:
        kql_parts.append(f"received:<={kql_date(args.before)}")
    if args.has_attachments:
        kql_parts.append("hasattachment:yes")
    if args.importance:
        kql_parts.append(f"importance:{args.importance.lower()}")
    if args.unread:
        kql_parts.append("isread:false")

    kql = " AND ".join(kql_parts) if kql_parts else "*"
    params = {
        "$top": str(args.count or 15),
        "$select": SELECT_MSG_LIST,
        "$search": f'"{kql}"',
    }
    data = api_get("/messages", params)
    msgs = data.get("value", [])
    record_ids(msgs)
    return msgs


def cmd_read(args):
    msg_id = resolve_id(args.message_id)
    params = {"$select": SELECT_MSG_FULL + ",HasAttachments"}
    m = api_get(f"/messages/{msg_id}", params, body_as_text=not args.html)

    # Auto-fetch attachment metadata if the message has attachments
    # (metadata only, no ContentBytes, so the call stays cheap)
    if m.get("HasAttachments") and not getattr(args, "no_attachments", False):
        att_data = api_get(f"/messages/{msg_id}/attachments",
                           {"$select": "Name,Size,ContentType,IsInline,Id"})
        atts = att_data.get("value", [])
        record_ids(atts)
        m["Attachments"] = atts
    return m


def cmd_thread(args):
    """Fetch all messages in a conversation."""
    msg_id = resolve_id(args.message_id)
    # Step 1: get ConversationId
    m = api_get(f"/messages/{msg_id}", {"$select": "ConversationId,Subject"})
    cid = m.get("ConversationId")
    if not cid:
        raise RuntimeError("Message has no ConversationId")
    # Step 2: filter all messages by conversation
    # Note: Outlook rejects $filter=ConversationId + $orderby combo with
    # "InefficientFilter": sort client-side instead.
    params = {
        "$filter": f"ConversationId eq '{cid}'",
        "$select": SELECT_MSG_LIST,
    }
    msgs = paginate("/messages", params, limit=args.count or 50)
    msgs.sort(key=lambda m: m.get("ReceivedDateTime", ""))
    record_ids(msgs)
    return msgs


def cmd_attachments(args):
    """List attachments on a message."""
    msg_id = resolve_id(args.message_id)
    data = api_get(f"/messages/{msg_id}/attachments",
                   {"$select": "Name,Size,ContentType,IsInline,Id"})
    atts = data.get("value", [])
    record_ids(atts)
    return atts


def cmd_download(args):
    """Download an attachment to a path."""
    msg_id = resolve_id(args.message_id)
    att_id = resolve_id(args.attachment_id)
    dest = Path(args.path or ".").expanduser()

    if dest.is_dir():
        # Fetch metadata to get filename
        meta = api_get(f"/messages/{msg_id}/attachments/{att_id}",
                       {"$select": "Name,ContentType"})
        dest = dest / (meta.get("Name") or f"attachment_{att_id[:8]}.bin")

    bytes_data = api_get_bytes(f"/messages/{msg_id}/attachments/{att_id}/$value")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(bytes_data)
    return {"path": str(dest), "size": len(bytes_data)}


def cmd_eml(args):
    """Export a message as raw .eml (RFC-822)."""
    msg_id = resolve_id(args.message_id)
    mime = api_get_bytes(f"/messages/{msg_id}/$value")
    if args.output:
        path = Path(args.output).expanduser()
        path.write_bytes(mime)
        return {"path": str(path), "size": len(mime)}
    sys.stdout.buffer.write(mime)
    return None


def cmd_folders(args):
    data = api_get("/mailfolders", {"$top": "100"})
    return data.get("value", [])


def cmd_unread(args):
    data = api_get("/mailfolders", {"$top": "100",
                                     "$select": "DisplayName,UnreadItemCount,TotalItemCount"})
    folders = data.get("value", [])
    result = {
        "unread_by_folder": {f.get("DisplayName"): f.get("UnreadItemCount", 0) for f in folders if f.get("UnreadItemCount", 0) > 0},
        "total_unread": sum(f.get("UnreadItemCount", 0) for f in folders),
    }
    return result


def cmd_digest(args):
    """Aggregate stats on recent mail: top senders, unread counts, attachments."""
    since = iso_date_expr(args.since or "7d", with_z=True)
    params = {
        "$select": "From,ReceivedDateTime,HasAttachments,IsRead,Importance",
        "$top": "200",
        "$filter": f"ReceivedDateTime ge {since}",
        "$orderby": "ReceivedDateTime desc",
    }
    msgs = paginate("/messages", params, limit=args.count or 500)

    senders = Counter()
    unread = 0
    with_att = 0
    high_imp = 0
    domains = Counter()

    for m in msgs:
        sender = fmt_from(m)
        senders[sender] += 1
        email = ((m.get("From") or {}).get("EmailAddress") or {}).get("Address", "")
        if "@" in email:
            domains[email.split("@", 1)[1]] += 1
        if not m.get("IsRead"):
            unread += 1
        if m.get("HasAttachments"):
            with_att += 1
        if m.get("Importance") == "High":
            high_imp += 1

    return {
        "period": f"Since {since[:10]}",
        "total_messages": len(msgs),
        "unread": unread,
        "with_attachments": with_att,
        "high_importance": high_imp,
        "top_senders": senders.most_common(10),
        "top_domains": domains.most_common(10),
    }


def cmd_from_sender(args):
    """Shortcut: all messages from a sender."""
    params = {
        "$top": str(args.count or 20),
        "$select": SELECT_MSG_LIST,
        "$search": f'"from:{args.email}"',
    }
    data = api_get("/messages", params)
    msgs = data.get("value", [])
    record_ids(msgs)
    return msgs


# ---------------------------------------------------------------------------
# Calendar commands
# ---------------------------------------------------------------------------
def cmd_calendar(args):
    """Upcoming events (recurrences expanded via calendarview)."""
    start = iso_date_expr(args.since or "today")
    # Default: next 7 days from start
    if args.until:
        end = iso_date_expr(args.until)
    else:
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", ""))
        except Exception:
            start_dt = datetime.now()
        end = (start_dt + timedelta(days=args.days or 7)).strftime("%Y-%m-%dT23:59:59")

    params = {
        "startDateTime": start,
        "endDateTime": end,
        "$select": SELECT_EVENT_LIST,
        "$orderby": "Start/DateTime",
        "$top": str(args.count or 50),
    }
    events = paginate("/calendarview", params, limit=args.count or 100)
    record_ids(events)
    return events


def _calendar_day(days_from_today: int) -> list:
    day = datetime.now() + timedelta(days=days_from_today)
    start = day.strftime("%Y-%m-%dT00:00:00")
    end = day.strftime("%Y-%m-%dT23:59:59")
    params = {
        "startDateTime": start, "endDateTime": end,
        "$select": SELECT_EVENT_LIST,
        "$orderby": "Start/DateTime",
    }
    events = paginate("/calendarview", params, limit=50)
    record_ids(events)
    return events


def cmd_today(args):
    return _calendar_day(0)


def cmd_tomorrow(args):
    return _calendar_day(1)


def cmd_event(args):
    event_id = resolve_id(args.event_id)
    params = {"$select": SELECT_EVENT_FULL}
    return api_get(f"/events/{event_id}", params, body_as_text=not args.html)


def cmd_calendars(args):
    data = api_get("/calendars", {"$top": "50"})
    return data.get("value", [])


# ---------------------------------------------------------------------------
# Meta commands
# ---------------------------------------------------------------------------
def cmd_raw(args):
    """Raw GET at an arbitrary Outlook REST v2.0 path with auth. Full power."""
    # Parse any additional query params
    params = {}
    if args.query:
        params = dict(urllib.parse.parse_qsl(args.query))
    return api_get(args.path, params, body_as_text=args.body_text, raw=args.no_defaults)


def cmd_token(args):
    token = get_token()
    if args.full:
        print(token)
    else:
        print(f"{token[:40]}...")
        cached = _load_cached_token()
        if cached:
            expires = int(cached.get("expiresOn", 0))
            remaining = expires - int(time.time())
            print(f"Expires in: {remaining // 60}m {remaining % 60}s")
    return None


def cmd_settings(args):
    return api_get("/mailboxsettings")


def cmd_profile(args):
    """Basic user profile (who am I)."""
    return api_get("/")  # /me root returns user profile


def cmd_login(args):
    proc = _browser_open_visible()
    print("Sign in to Outlook/Microsoft in the opened Chromium window.")
    print("If prompted, check 'Mantener mi sesion iniciada' / 'Stay signed in'.")
    print("Wait for Outlook to load, then close that browser.")
    print("After it closes, this command will save a token for future automatic refreshes.")
    proc.wait()

    try:
        tok = _prime_token_from_refresh_cache()
    except Exception as exc:
        raise RuntimeError(
            "Sign-in browser closed, but the saved Microsoft session could not be converted "
            f"into an Outlook refreshable token: {exc}"
        ) from exc
    if tok:
        expires = int(tok.get("expiresOn", 0))
        remaining = max(0, expires - int(time.time()))
        print(f"Outlook CLI login saved. Token expires in {remaining // 60}m {remaining % 60}s and can refresh automatically.")
        return None

    raise RuntimeError(
        "Sign-in browser closed, but no Microsoft refresh token was found in the Outlook profile. "
        "Open `outlook login` again, make sure Outlook fully loads, choose Stay signed in if prompted, "
        "then close the browser window."
    )
    return None


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------
def print_message_list(msgs: list, *, minimal: bool = False):
    if not msgs:
        print("  (no messages)")
        return
    id_map = _load_id_map()
    for m in msgs:
        read = "  " if m.get("IsRead") else "* "
        attach = " [att]" if m.get("HasAttachments") else ""
        imp = " [high]" if m.get("Importance") == "High" else ""
        date = fmt_date(m.get("ReceivedDateTime", ""))
        frm = shorten(fmt_from(m), 25)
        subj = shorten(m.get("Subject") or "(no subject)", 55)
        sid = short_id(m.get("Id", ""), id_map)
        sid_str = f" [{sid}]" if sid else ""
        tc = m.get("_thread_count", 1)
        thread_info = f" ({tc} msgs, {m.get('_thread_unread', 0)} unread)" if tc > 1 else ""
        print(f"{read}{date} | {frm:25s} | {subj}{sid_str}{attach}{imp}{thread_info}")
        if not minimal:
            preview = shorten(m.get("BodyPreview") or "", 100)
            if preview:
                print(f"   {preview}")
            print()
    _save_id_map(id_map)


def print_message_full(m: dict, *, trim: bool = True):
    body_obj = m.get("Body", {}) or {}
    body = body_obj.get("Content", "")
    if body_obj.get("ContentType") == "HTML":
        body = strip_html(body)

    if trim:
        body = trim_signature(body)

    # Record short ID so follow-up commands can reference this message
    if m.get("Id"):
        id_map = _load_id_map()
        sid = short_id(m["Id"], id_map)
        _save_id_map(id_map)
    else:
        sid = ""

    print(f"From:    {fmt_addr(m.get('From'))}")
    print(f"Date:    {fmt_date(m.get('ReceivedDateTime', ''))}")
    to = m.get("ToRecipients") or []
    cc = m.get("CcRecipients") or []
    if to:
        print(f"To:      {', '.join(addrs_list(to))}")
    if cc:
        print(f"Cc:      {', '.join(addrs_list(cc))}")
    print(f"Subject: {m.get('Subject', '')}")
    if m.get("Importance") == "High":
        print("         [HIGH IMPORTANCE]")
    if sid:
        print(f"ID:      {sid}")

    # Show attachments inline by default.
    atts = m.get("Attachments") or []
    files = [a for a in atts if not a.get("IsInline")]
    inline = [a for a in atts if a.get("IsInline")]
    if files or inline:
        id_map = _load_id_map()
        if files:
            print(f"\nAttachments ({len(files)}):")
            for a in files:
                asid = short_id(a.get("Id", ""), id_map)
                size_kb = (a.get("Size", 0) or 0) / 1024
                print(f"  [file] {a.get('Name', '?')} ({size_kb:.1f} KB, {a.get('ContentType', '')}) [{asid}]")
        if inline:
            print(f"\nInline images ({len(inline)}, embedded in body):")
            for a in inline[:5]:
                asid = short_id(a.get("Id", ""), id_map)
                size_kb = (a.get("Size", 0) or 0) / 1024
                print(f"  [inline] {a.get('Name', '?')} ({size_kb:.1f} KB) [{asid}]")
            if len(inline) > 5:
                print(f"  ... and {len(inline) - 5} more")
        _save_id_map(id_map)

    print()
    print(body)


def print_event_list(events: list):
    if not events:
        print("  (no events)")
        return
    cur_date = None
    for e in events:
        start = (e.get("Start") or {}).get("DateTime", "")
        end = (e.get("End") or {}).get("DateTime", "")
        start_d = start[:10]
        if start_d != cur_date:
            cur_date = start_d
            try:
                dt = datetime.fromisoformat(start[:19])
                day = dt.strftime("%a, %b %d")
            except Exception:
                day = start_d
            print(f"\n{day}")

        start_t = start[11:16] if "T" in start else ""
        end_t = end[11:16] if "T" in end else ""
        if e.get("IsAllDay"):
            time_range = "all day    "
        else:
            time_range = f"{start_t}-{end_t}"
        cancelled = " [CANCELLED]" if e.get("IsCancelled") else ""
        subj = e.get("Subject") or "(no subject)"
        print(f"  {time_range}  {subj}{cancelled}")
        loc = (e.get("Location") or {}).get("DisplayName")
        if loc:
            print(f"               at {loc}")
        if e.get("OnlineMeetingUrl"):
            print(f"               online: {e['OnlineMeetingUrl'][:60]}")


def print_event_full(e: dict, *, trim: bool = True):
    start = (e.get("Start") or {}).get("DateTime", "")
    end = (e.get("End") or {}).get("DateTime", "")
    print(f"Subject: {e.get('Subject', '')}")
    print(f"Start:   {fmt_date(start)}")
    print(f"End:     {fmt_date(end)}")
    loc = (e.get("Location") or {}).get("DisplayName")
    if loc:
        print(f"Where:   {loc}")
    if e.get("OnlineMeetingUrl"):
        print(f"Online:  {e['OnlineMeetingUrl']}")
    organizer = fmt_addr(e.get("Organizer"))
    if organizer:
        print(f"Organizer: {organizer}")
    attendees = e.get("Attendees") or []
    if attendees:
        print(f"Attendees ({len(attendees)}):")
        for a in attendees[:20]:
            status = (a.get("Status") or {}).get("Response", "")
            print(f"  - {fmt_addr(a)} [{status}]")
    if e.get("IsCancelled"):
        print("\n[CANCELLED]")
    print()
    body = (e.get("Body") or {}).get("Content", "")
    if (e.get("Body") or {}).get("ContentType") == "HTML":
        body = strip_html(body)
    if trim:
        body = trim_signature(body)
    if body:
        print(body)


def print_folders(folders: list):
    for f in folders:
        name = f.get("DisplayName", "?")
        unread = f.get("UnreadItemCount", 0)
        total = f.get("TotalItemCount", 0)
        print(f"  {name:30s} unread: {unread:4d}  total: {total}")


def print_attachments(atts: list):
    id_map = _load_id_map()
    for a in atts:
        size_kb = (a.get("Size", 0) or 0) / 1024
        inline = " [inline]" if a.get("IsInline") else ""
        sid = short_id(a.get("Id", ""), id_map)
        sid_str = f" [{sid}]" if sid else ""
        print(f"  {a.get('Name', '?'):50s} {size_kb:>8.1f} KB  {a.get('ContentType', '')}{inline}{sid_str}")
    _save_id_map(id_map)


def print_event_list_with_ids(events: list):
    """Wrap print_event_list to also record short IDs."""
    if not events:
        print("  (no events)")
        return
    id_map = _load_id_map()
    cur_date = None
    for e in events:
        start = (e.get("Start") or {}).get("DateTime", "")
        end = (e.get("End") or {}).get("DateTime", "")
        start_d = start[:10]
        if start_d != cur_date:
            cur_date = start_d
            try:
                dt = datetime.fromisoformat(start[:19])
                day = dt.strftime("%a, %b %d")
            except Exception:
                day = start_d
            print(f"\n{day}")

        start_t = start[11:16] if "T" in start else ""
        end_t = end[11:16] if "T" in end else ""
        time_range = "all day    " if e.get("IsAllDay") else f"{start_t}-{end_t}"
        cancelled = " [CANCELLED]" if e.get("IsCancelled") else ""
        subj = e.get("Subject") or "(no subject)"
        sid = short_id(e.get("Id", ""), id_map)
        sid_str = f" [{sid}]" if sid else ""
        print(f"  {time_range}  {subj}{sid_str}{cancelled}")
        loc = (e.get("Location") or {}).get("DisplayName")
        if loc:
            print(f"               at {loc}")
        if e.get("OnlineMeetingUrl"):
            print(f"               online: {e['OnlineMeetingUrl'][:60]}")
    _save_id_map(id_map)


def print_digest(d: dict):
    print(f"Period: {d['period']}")
    print(f"Total messages: {d['total_messages']}  (unread: {d['unread']})")
    print(f"With attachments: {d['with_attachments']}  High importance: {d['high_importance']}")
    print(f"\nTop senders:")
    for name, n in d["top_senders"]:
        print(f"  {n:3d}  {name}")
    print(f"\nTop domains:")
    for dom, n in d["top_domains"]:
        print(f"  {n:3d}  {dom}")


def print_unread(d: dict):
    for folder, n in d["unread_by_folder"].items():
        print(f"  {folder:30s} {n}")
    print(f"\nTotal unread: {d['total_unread']}")


# ---------------------------------------------------------------------------
# Main / argparse
# ---------------------------------------------------------------------------
def _add_msg_filters(p):
    p.add_argument("-n", "--count", type=int, default=20)
    p.add_argument("-u", "--unread", action="store_true", help="Only unread")
    p.add_argument("-a", "--has-attachments", action="store_true", dest="has_attachments")
    p.add_argument("--importance", choices=["high", "normal", "low"])
    p.add_argument("--focused", action="store_true", help="Only Focused inbox")
    p.add_argument("-m", "--minimal", action="store_true",
                   help="One line per message (no preview)")


def build_parser():
    p = argparse.ArgumentParser(
        description="Outlook/Microsoft 365 CLI -- read-only email + calendar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  outlook inbox -u -n 10                  # 10 latest unread\n"
            "  outlook search --from prof --since 7d   # from 'prof' last 7 days\n"
            "  outlook calendar --days 14              # next 2 weeks\n"
            "  outlook today                            # today's events\n"
            "  outlook thread <msg_id>                  # full conversation\n"
            "  outlook raw 'messages/$count?$filter=IsRead eq false'\n"
        ),
    )
    p.add_argument("--json", action="store_true", help="Raw JSON output")
    sub = p.add_subparsers(dest="command", required=True)

    # --- Mail ---
    sub.add_parser("login", help="Open visible helper browser for manual Microsoft sign-in")

    i = sub.add_parser("inbox", help="List inbox messages (most recent first)")
    _add_msg_filters(i)
    i.add_argument("--folder", default="inbox", help="Folder name or id (default: inbox)")
    i.add_argument("-t", "--threads", action="store_true",
                   help="Group by conversation; show one entry per thread")

    s = sub.add_parser("search", help="Search messages (KQL + structured filters)")
    s.add_argument("query", nargs="?", default="", help="Free-form KQL query")
    s.add_argument("--from", dest="from_addr", help="From address filter")
    s.add_argument("--to", dest="to_addr", help="To address filter")
    s.add_argument("--subject", help="Subject contains")
    s.add_argument("--since", help="Date expr: '7d', '2026-04-01', 'today'")
    s.add_argument("--before", help="Upper date bound")
    _add_msg_filters(s)

    r = sub.add_parser("read", help="Read a message by ID (lists attachments automatically)")
    r.add_argument("message_id", help="Full or short (6-char) message ID")
    r.add_argument("--html", action="store_true", help="Keep HTML body (default: plain text)")
    r.add_argument("--no-trim", action="store_true", dest="no_trim",
                   help="Don't trim signatures/disclaimers (default: trim)")
    r.add_argument("--no-attachments", action="store_true", dest="no_attachments",
                   help="Skip the extra API call to fetch attachment list")

    t = sub.add_parser("thread", help="Fetch full conversation around a message")
    t.add_argument("message_id", help="Full or short (6-char) message ID")
    t.add_argument("-n", "--count", type=int, default=50)
    t.add_argument("-m", "--minimal", action="store_true",
                   help="One line per message (no preview)")

    att = sub.add_parser("attachments", help="List attachments on a message")
    att.add_argument("message_id", help="Full or short (6-char) message ID")

    dl = sub.add_parser("download", help="Download an attachment")
    dl.add_argument("message_id", help="Full or short message ID")
    dl.add_argument("attachment_id", help="Full or short attachment ID")
    dl.add_argument("path", nargs="?", default=".", help="Dir or filename (default: cwd)")

    e = sub.add_parser("eml", help="Export message as .eml (RFC-822 MIME)")
    e.add_argument("message_id", help="Full or short message ID")
    e.add_argument("-o", "--output", help="Write to file (default: stdout bytes)")

    frm = sub.add_parser("from", help="Messages from a specific sender (shortcut)")
    frm.add_argument("email")
    frm.add_argument("-n", "--count", type=int, default=20)
    frm.add_argument("-m", "--minimal", action="store_true",
                     help="One line per message (no preview)")

    sub.add_parser("folders", help="List all mail folders")
    sub.add_parser("unread", help="Unread counts by folder")

    d = sub.add_parser("digest", help="Aggregate stats: top senders, unread, attachments")
    d.add_argument("--since", default="7d", help="Date expr (default: 7d)")
    d.add_argument("-n", "--count", type=int, default=500, help="Max messages to analyze")

    # --- Calendar ---
    c = sub.add_parser("calendar", help="Upcoming events (calendarview, recurrences expanded)")
    c.add_argument("--since", help="Start date (default: today)")
    c.add_argument("--until", help="End date (overrides --days)")
    c.add_argument("--days", type=int, default=7, help="Days from start (default: 7)")
    c.add_argument("-n", "--count", type=int, default=50)

    sub.add_parser("today", help="Today's calendar events")
    sub.add_parser("tomorrow", help="Tomorrow's calendar events")

    ev = sub.add_parser("event", help="Event details by ID")
    ev.add_argument("event_id", help="Full or short event ID")
    ev.add_argument("--html", action="store_true")
    ev.add_argument("--no-trim", action="store_true", dest="no_trim",
                    help="Don't trim signatures (default: trim)")

    sub.add_parser("calendars", help="List all calendars")

    # --- Meta ---
    rw = sub.add_parser("raw", help="Raw GET at Outlook REST v2.0 path (full flexibility)")
    rw.add_argument("path", help="Path relative to /me (e.g. 'messages/$count')")
    rw.add_argument("--query", help="Extra URL query string params")
    rw.add_argument("--body-text", action="store_true", dest="body_text",
                    help="Add plain-text body Prefer header")
    rw.add_argument("--no-defaults", action="store_true", dest="no_defaults",
                    help="Skip default Prefer headers (timezone, maxpagesize)")

    tok = sub.add_parser("token", help="Show current access token info")
    tok.add_argument("--full", action="store_true", help="Print full token (sensitive!)")

    sub.add_parser("settings", help="Mailbox settings (timezone, working hours, OOF)")
    sub.add_parser("profile", help="User profile (display name, email)")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    minimal = getattr(args, "minimal", False)
    trim = not getattr(args, "no_trim", False)

    def _msg_list(r):
        return print_message_list(r, minimal=minimal)

    def _msg_full(r):
        return print_message_full(r, trim=trim)

    def _event_full(r):
        return print_event_full(r, trim=trim)

    handlers = {
        "login": (cmd_login, lambda _: None),
        "inbox": (cmd_inbox, _msg_list),
        "search": (cmd_search, _msg_list),
        "read": (cmd_read, _msg_full),
        "thread": (cmd_thread, _msg_list),
        "attachments": (cmd_attachments, print_attachments),
        "download": (cmd_download, lambda r: print(f"Saved {r['size']} bytes to {r['path']}")),
        "eml": (cmd_eml, lambda r: print(f"Saved {r['size']} bytes to {r['path']}") if r else None),
        "from": (cmd_from_sender, _msg_list),
        "folders": (cmd_folders, print_folders),
        "unread": (cmd_unread, print_unread),
        "digest": (cmd_digest, print_digest),
        "calendar": (cmd_calendar, print_event_list_with_ids),
        "today": (cmd_today, print_event_list_with_ids),
        "tomorrow": (cmd_tomorrow, print_event_list_with_ids),
        "event": (cmd_event, _event_full),
        "calendars": (cmd_calendars,
                      lambda fs: [print(f"  {f.get('Name','?'):30s} id: {f.get('Id','')[:40]}...") for f in fs]),
        "raw": (cmd_raw, lambda r: print(json.dumps(r, indent=2, ensure_ascii=False))),
        "token": (cmd_token, lambda _: None),
        "settings": (cmd_settings, lambda r: print(json.dumps(r, indent=2, ensure_ascii=False))),
        "profile": (cmd_profile, lambda r: print(json.dumps(r, indent=2, ensure_ascii=False))),
    }

    fn, formatter = handlers[args.command]
    try:
        result = fn(args)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    elif formatter and result is not None:
        formatter(result)


if __name__ == "__main__":
    main()
