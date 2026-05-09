#!/usr/bin/env python3
"""
D2L/Brightspace LMS CLI — read-only access to courses, assignments, grades,
announcements, and deadlines at USFQ's D2L instance.

Manages its own headless Chromium with a persistent profile for session cookies.
Auto-logs in via Microsoft SSO when the session expires.
Talks directly to the D2L Valence REST API.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
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
D2L_BASE = "https://miusfv.usfq.edu.ec"
# Use a dedicated local CDP port for the D2L helper. Port 18800 is also used by
# Franz-PC SSH forwarding in this environment; when that tunnel is up, the old
# hard-coded port accepts TCP but does not serve Chrome DevTools, so d2l thinks
# the browser is dead and then cannot start Chromium on the occupied port.
CDP_PORT = int(os.environ.get("D2L_CDP_PORT", "18801"))
AUTO_LOGIN_TIMEOUT = int(os.environ.get("D2L_AUTO_LOGIN_TIMEOUT", "3"))
D2L_ACCOUNT_EMAIL = os.environ.get("D2L_ACCOUNT_EMAIL", "fchandi@estud.usfq.edu.ec")
LP_VER = "1.47"  # Learning Platform API version
LE_VER = "1.80"  # Learning Environment API version

# ---------------------------------------------------------------------------
# HTML-to-plain-text helper
# ---------------------------------------------------------------------------
class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def strip_html(html: str) -> str:
    if not html:
        return ""
    s = _HTMLStripper()
    s.feed(html)
    return s.get_text()


# ---------------------------------------------------------------------------
# Self-contained headless browser (no OpenClaw dependency)
# ---------------------------------------------------------------------------
if sys.platform.startswith("win"):
    LOCAL_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    SHARE_DIR = LOCAL_DATA / "d2l-cli"
    DEFAULT_BROWSER_DATA_DIR = LOCAL_DATA / "outlook-cli" / "browser-data"
else:
    SHARE_DIR = Path.home() / ".local/share/d2l-cli"
    DEFAULT_BROWSER_DATA_DIR = Path.home() / ".local/share/outlook-cli/browser-data"
BROWSER_DATA_DIR = Path(os.environ.get("D2L_BROWSER_DATA_DIR", str(DEFAULT_BROWSER_DATA_DIR)))
BROWSER_LOCK_FILE = BROWSER_DATA_DIR.parent / "browser.lock"

_chrome_proc = None


def _find_chromium() -> str:
    """Find a usable Chromium/Chrome binary."""
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
    raise RuntimeError("No Chromium/Chrome binary found. Install playwright: python -m playwright install chromium")


def _acquire_browser_lock(timeout: int = 10) -> int:
    import time
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
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
                raise RuntimeError("Timed out waiting for D2L browser lock")
            time.sleep(0.5)


def _release_browser_lock(fd: int) -> None:
    try:
        os.close(fd)
    finally:
        try:
            BROWSER_LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _browser_start():
    """Start a headless Chromium with persistent profile on CDP_PORT."""
    global _chrome_proc
    import subprocess
    os.makedirs(str(BROWSER_DATA_DIR), exist_ok=True)
    chrome = _find_chromium()
    _chrome_proc = subprocess.Popen(
        [chrome, "--headless", "--no-sandbox", "--disable-gpu",
         "--disable-dev-shm-usage", "--disable-software-rasterizer",
         f"--remote-debugging-port={CDP_PORT}",
         f"--user-data-dir={BROWSER_DATA_DIR}",
         "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _browser_stop():
    """Stop the headless helper browser started by this process."""
    global _chrome_proc
    if _chrome_proc is None:
        return
    try:
        _chrome_proc.terminate()
        _chrome_proc.wait(timeout=5)
    except Exception:
        try:
            _chrome_proc.kill()
        except Exception:
            pass
    finally:
        _chrome_proc = None


def _browser_open_visible():
    """Open the D2L helper profile in a visible Chromium for manual login."""
    import subprocess
    os.makedirs(str(BROWSER_DATA_DIR), exist_ok=True)
    chrome = _find_chromium()
    args = [
        chrome,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={BROWSER_DATA_DIR}",
        f"{D2L_BASE}/d2l/home",
    ]
    if sys.platform.startswith("win"):
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Auto-login via Microsoft SSO (Playwright over CDP — fast)
# ---------------------------------------------------------------------------
def _auto_login() -> bool:
    """Attempt automatic login to D2L via Microsoft SSO using Playwright.

    Connects to the OpenClaw browser via CDP, navigates through SSO,
    and returns True if D2L loads successfully.
    """
    print("Session expired. Attempting auto-login...", file=sys.stderr)
    return asyncio.run(_auto_login_async())


async def _auto_login_async() -> bool:
    from playwright.async_api import async_playwright

    async def click_first_visible(page, labels: list[str], timeout: int = 2500) -> bool:
        import time
        deadline = time.time() + (timeout / 1000)
        for label in labels:
            locators = [
                page.get_by_role("button", name=re.compile(label, re.I)).first,
                page.get_by_role("link", name=re.compile(label, re.I)).first,
                page.locator("input[type=submit]", has_text=re.compile(label, re.I)).first,
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
                await field.wait_for(state="visible", timeout=800)
                value = await field.input_value()
                if not value:
                    await field.fill(D2L_ACCOUNT_EMAIL)
                return await submit_if_visible(page) or await click_first_visible(page, [r"next", r"siguiente"], timeout=800)
            except Exception:
                pass
        return False

    async def submit_password_if_autofilled(page) -> bool:
        try:
            field = page.locator("input[type=password]").first
            await field.wait_for(state="visible", timeout=800)
            value = await field.input_value()
            if value:
                return await submit_if_visible(page) or await field.press("Enter")
        except Exception:
            pass
        return False

    pw = await async_playwright().start()
    browser = None
    try:
        browser = await pw.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()

        # Always create a new tab — never touch existing tabs
        page = await context.new_page()

        try:
            await page.goto(f"{D2L_BASE}/d2l/home", wait_until="domcontentloaded", timeout=3000)

            # Already on D2L?
            if "/d2l/" in page.url and "logout" not in page.url and "login" not in page.url:
                print("Auto-login successful.", file=sys.stderr)
                return True

            # Follow Microsoft SSO prompts that can appear with cached accounts.
            await click_first_visible(page, [r"estud\.usfq\.edu\.ec", r"franz\.chandi", r"use another account", r"usar otra cuenta"], timeout=800)
            for _ in range(4):
                if "/d2l/" in page.url and "logout" not in page.url and "login" not in page.url:
                    print("Auto-login successful.", file=sys.stderr)
                    return True
                clicked = False
                clicked |= await fill_email_if_needed(page)
                clicked |= await submit_password_if_autofilled(page)
                clicked |= await click_first_visible(page, [r"sign in", r"iniciar sesi[oó]n", r"siguiente", r"next", r"continuar", r"continue"], timeout=800)
                clicked |= await submit_if_visible(page)
                clicked |= await click_first_visible(page, [r"yes", r"s[ií]", r"mantener.*sesi[oó]n", r"stay signed in"], timeout=800)
                if not clicked:
                    break
                await asyncio.sleep(0.5)

            # Wait for D2L to load
            try:
                await page.wait_for_url("**/d2l/**", timeout=1000)
            except Exception:
                pass

            if "/d2l/" in page.url and "logout" not in page.url:
                print("Auto-login successful.", file=sys.stderr)
                return True

            print(f"Auto-login: unexpected page — {page.url}", file=sys.stderr)
            return False
        finally:
            # Always close the tab we created
            try:
                await page.close()
            except Exception:
                pass
    except Exception as e:
        print(f"Auto-login error: {e}", file=sys.stderr)
        return False
    finally:
        if browser:
            await browser.close()
        await pw.stop()


# ---------------------------------------------------------------------------
# Cookie extraction via CDP (with auto-login fallback)
# ---------------------------------------------------------------------------
def _ensure_browser(locked: bool = False) -> bool:
    """Make sure a headless Chromium is running on CDP_PORT."""
    import time
    try:
        req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
        with urllib.request.urlopen(req, timeout=1) as resp:
            tabs = json.loads(resp.read())
        if tabs:
            return True
    except Exception:
        pass
    # Browser not running — start our own headless instance
    print("Browser not running, starting headless Chromium...", file=sys.stderr)
    fd = None if locked else _acquire_browser_lock()
    try:
        try:
            req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
            with urllib.request.urlopen(req, timeout=1) as resp:
                if json.loads(resp.read()):
                    return True
        except Exception:
            pass
        _browser_start()
        for _ in range(3):
            try:
                req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
                with urllib.request.urlopen(req, timeout=1) as resp:
                    if json.loads(resp.read()):
                        return True
            except Exception:
                pass
            time.sleep(1)
        return False
    finally:
        if fd is not None:
            _release_browser_lock(fd)


def _get_cookies_sync() -> dict[str, str]:
    """Return D2L session cookies. Starts browser and auto-logs in if needed."""
    fd = _acquire_browser_lock()
    try:
        return _get_cookies_sync_locked()
    finally:
        _release_browser_lock(fd)


def _get_cookies_sync_locked() -> dict[str, str]:
    # Ensure browser is running first
    if not _ensure_browser(locked=True):
        raise RuntimeError("Could not start browser on CDP port " + str(CDP_PORT))

    cookies = _try_get_cookies()
    if cookies:
        # Verify cookies are still valid with a quick API probe
        if _test_cookies(cookies):
            _browser_stop()
            return cookies

    # Cookies missing or expired — try auto-login
    if _auto_login():
        cookies = _try_get_cookies()
        if cookies:
            _browser_stop()
            return cookies

    _browser_stop()
    raise RuntimeError(
        "No D2L cookies found. Auto-login failed. "
        "Please log in manually in the D2L helper browser."
    )


def _try_get_cookies() -> dict[str, str] | None:
    """Try to extract D2L cookies. Returns None if not found."""
    try:
        req = urllib.request.Request(f"http://localhost:{CDP_PORT}/json")
        with urllib.request.urlopen(req, timeout=5) as resp:
            tabs = json.loads(resp.read())
    except Exception:
        return None
    if not tabs:
        return None

    ws_url = tabs[0]["webSocketDebuggerUrl"]
    try:
        return asyncio.run(_fetch_cookies(ws_url))
    except RuntimeError:
        return None


def _test_cookies(cookies: dict[str, str]) -> bool:
    """Quick check if cookies are still valid (non-redirect response from D2L API)."""
    cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
    url = D2L_BASE + f"/d2l/api/lp/{LP_VER}/users/whoami"
    req = urllib.request.Request(url)
    req.add_header("Cookie", cookie_header)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


async def _fetch_cookies(ws_url: str) -> dict[str, str]:
    import websockets  # type: ignore

    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps({
            "id": 1,
            "method": "Network.getAllCookies",
            "params": {},
        }))
        result = json.loads(await ws.recv())
        cookies = result.get("result", {}).get("cookies", [])
        out: dict[str, str] = {}
        for c in cookies:
            if c.get("domain", "") == "miusfv.usfq.edu.ec":
                out[c["name"]] = c["value"]
        if not out:
            raise RuntimeError("No D2L cookies")
        return out


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
_cookies: dict[str, str] | None = None
_login_attempted: bool = False


def _get_cookie_header() -> str:
    global _cookies
    if _cookies is None:
        _cookies = _get_cookies_sync()
    return "; ".join(f"{k}={v}" for k, v in _cookies.items())


def api_get(path: str) -> any:
    """GET a D2L API path. Auto-retries with fresh login on auth failure."""
    global _cookies, _login_attempted
    url = D2L_BASE + path
    req = urllib.request.Request(url)
    req.add_header("Cookie", _get_cookie_header())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        # 401/403 = session expired — try auto-login once
        if exc.code in (401, 403) and not _login_attempted:
            _login_attempted = True
            _cookies = None
            print("Session expired, re-authenticating...", file=sys.stderr)
            fd = _acquire_browser_lock()
            try:
                if _ensure_browser(locked=True) and _auto_login():
                    _cookies = _try_get_cookies()
                    if _cookies:
                        _browser_stop()
                        return api_get(path)
            finally:
                _release_browser_lock(fd)
            print(f"Error: HTTP {exc.code} — auto-login failed.", file=sys.stderr)
            sys.exit(1)
        body = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"Error: HTTP {exc.code} from {url}\n{body}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error fetching {url}: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Data fetchers
# ---------------------------------------------------------------------------

def get_enrollments() -> list[dict]:
    """Return list of enrolled course offerings (type 3 = Course Offering)."""
    data = api_get(f"/d2l/api/lp/{LP_VER}/enrollments/myenrollments/")
    items = data.get("Items", [])
    # Filter to course offerings only (type id 3) and sort by access date
    courses = [
        it for it in items
        if it.get("OrgUnit", {}).get("Type", {}).get("Id") == 3
    ]
    return courses


def get_active_courses() -> list[dict]:
    """Return courses where CanAccess is True."""
    return [
        c for c in get_enrollments()
        if c.get("Access", {}).get("CanAccess")
    ]


def get_news(org_unit_id: int) -> list[dict]:
    return api_get(f"/d2l/api/le/{LE_VER}/{org_unit_id}/news/")


def get_dropbox_folders(org_unit_id: int) -> list[dict]:
    return api_get(f"/d2l/api/le/{LE_VER}/{org_unit_id}/dropbox/folders/")


def get_grades(org_unit_id: int) -> list[dict]:
    return api_get(f"/d2l/api/le/{LE_VER}/{org_unit_id}/grades/values/myGradeValues/")


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


def short_name(full_name: str) -> str:
    """Extract the short course name, e.g. 'METC 6103E Behavioral Ecology'."""
    # Pattern: "202520.1.XXXX - COURSE NAME - Professor"
    parts = full_name.split(" - ", 2)
    if len(parts) >= 2:
        return parts[1].strip()
    return full_name


def course_id_from_name(name: str) -> int | None:
    """Extract the org unit id from a course name URL or return None."""
    return None


def wrap(text: str, width: int = 80, indent: str = "  ") -> str:
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_classes(args):
    courses = get_enrollments()
    if args.json:
        print(json.dumps(courses, indent=2, ensure_ascii=False))
        return

    active = [c for c in courses if c["Access"]["CanAccess"]]
    inactive = [c for c in courses if not c["Access"]["CanAccess"]]

    print("=== Active Courses ===\n")
    for c in active:
        ou = c["OrgUnit"]
        acc = c["Access"]
        print(f"  ID: {ou['Id']}")
        print(f"  Name: {short_name(ou['Name'])}")
        print(f"  Full: {ou['Name']}")
        print(f"  Code: {ou.get('Code', '—')}")
        if acc.get("StartDate"):
            print(f"  Period: {fmt_date(acc['StartDate'])} → {fmt_date(acc.get('EndDate'))}")
        print()

    if inactive:
        print("=== Past / Inactive Courses ===\n")
        for c in inactive:
            ou = c["OrgUnit"]
            acc = c["Access"]
            print(f"  ID: {ou['Id']}  |  {short_name(ou['Name'])}  |  {ou.get('Code', '—')}")
        print()


def _resolve_courses(course_id: int | None) -> list[dict]:
    """If course_id given, return single-element list; otherwise all active courses."""
    if course_id is not None:
        # Try to find the real name from enrollments
        for c in get_enrollments():
            if c["OrgUnit"]["Id"] == course_id:
                return [c]
        # Fallback: use the ID directly
        return [{"OrgUnit": {"Id": course_id, "Name": f"Course {course_id}"}}]
    return get_active_courses()


def cmd_announcements(args):
    courses = _resolve_courses(args.course)
    all_news: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            news = get_news(oid)
        except Exception:
            continue
        for n in news:
            n["_course_id"] = oid
            n["_course_name"] = short_name(c["OrgUnit"]["Name"])
        all_news.extend(news)

    # Sort newest first
    all_news.sort(key=lambda n: n.get("StartDate", "") or "", reverse=True)

    if args.json:
        print(json.dumps(all_news, indent=2, ensure_ascii=False))
        return

    if not all_news:
        print("No announcements found.")
        return

    print(f"=== Announcements ({len(all_news)}) ===\n")
    for n in all_news:
        print(f"  [{n['_course_name']}]  {n['Title']}")
        print(f"  Date: {fmt_date(n.get('StartDate'))}")
        body_text = n.get("Body", {}).get("Text", "").strip()
        if body_text:
            # Show first 200 chars
            summary = body_text[:200].replace("\n", " ").replace("\r", "")
            if len(body_text) > 200:
                summary += "..."
            print(f"  {summary}")
        print()


def cmd_notifications(args):
    # D2L doesn't have a clean notifications API for students.
    # We aggregate recent announcements across all active courses as a proxy.
    courses = get_active_courses()
    all_news: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            news = get_news(oid)
        except Exception:
            continue
        for n in news:
            n["_course_id"] = oid
            n["_course_name"] = short_name(c["OrgUnit"]["Name"])
        all_news.extend(news)

    # Only recent (last 14 days)
    now = datetime.now(timezone.utc)
    recent = []
    for n in all_news:
        sd = n.get("StartDate")
        if sd:
            try:
                dt = datetime.fromisoformat(sd.replace("Z", "+00:00"))
                if (now - dt).days <= 14:
                    recent.append(n)
            except Exception:
                pass

    recent.sort(key=lambda n: n.get("StartDate", "") or "", reverse=True)

    if args.json:
        print(json.dumps(recent, indent=2, ensure_ascii=False))
        return

    if not recent:
        print("No recent notifications (last 14 days).")
        return

    print(f"=== Recent Notifications ({len(recent)}, last 14 days) ===\n")
    for n in recent:
        print(f"  [{n['_course_name']}]  {n['Title']}")
        print(f"  Date: {fmt_date(n.get('StartDate'))}")
        print()


def cmd_assignments(args):
    courses = _resolve_courses(args.course)
    all_assignments: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            folders = get_dropbox_folders(oid)
        except Exception:
            continue
        for f in folders:
            f["_course_id"] = oid
            f["_course_name"] = short_name(c["OrgUnit"]["Name"])
        all_assignments.extend(folders)

    # Sort by due date
    def _due_key(a):
        d = a.get("DueDate") or ""
        return d if d else "9999"

    all_assignments.sort(key=_due_key)

    if args.json:
        print(json.dumps(all_assignments, indent=2, ensure_ascii=False))
        return

    if not all_assignments:
        print("No assignments found.")
        return

    now = datetime.now(timezone.utc)
    upcoming = []
    past = []
    for a in all_assignments:
        dd = a.get("DueDate")
        if dd:
            try:
                dt = datetime.fromisoformat(dd.replace("Z", "+00:00"))
                if dt > now:
                    upcoming.append(a)
                else:
                    past.append(a)
            except Exception:
                upcoming.append(a)
        else:
            upcoming.append(a)

    if upcoming:
        print(f"=== Upcoming Assignments ({len(upcoming)}) ===\n")
        for a in upcoming:
            print(f"  ID: {a['Id']}  |  {a['Name']}")
            print(f"  Course: {a['_course_name']}")
            print(f"  Due: {fmt_date(a.get('DueDate'))}")
            print()

    if past:
        print(f"=== Past Assignments ({len(past)}) ===\n")
        for a in past:
            print(f"  ID: {a['Id']}  |  {a['Name']}")
            print(f"  Course: {a['_course_name']}  |  Due: {fmt_date(a.get('DueDate'))}")
        print()


def cmd_assignment(args):
    assignment_id = args.id
    # We need to find which course this assignment belongs to.
    # Search across all active courses.
    courses = get_active_courses()
    found = None
    course_name = ""

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            folders = get_dropbox_folders(oid)
        except Exception:
            continue
        for f in folders:
            if f["Id"] == assignment_id:
                found = f
                course_name = short_name(c["OrgUnit"]["Name"])
                break
        if found:
            break

    if not found:
        print(f"Assignment {assignment_id} not found.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        found["_course_name"] = course_name
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return

    print(f"=== Assignment Details ===\n")
    print(f"  ID: {found['Id']}")
    print(f"  Name: {found['Name']}")
    print(f"  Course: {course_name}")
    print(f"  Due: {fmt_date(found.get('DueDate'))}")
    print(f"  Type: {'Group' if found.get('DropboxType') == 2 else 'Individual'}")

    instructions_html = found.get("CustomInstructions", {}).get("Html", "")
    instructions_text = found.get("CustomInstructions", {}).get("Text", "")
    instructions = instructions_text if instructions_text else strip_html(instructions_html)

    if instructions:
        print(f"\n  Instructions:")
        print(wrap(instructions, width=78, indent="    "))
    else:
        print(f"\n  (No instructions provided)")

    attachments = found.get("Attachments", [])
    if attachments:
        print(f"\n  Attachments:")
        for att in attachments:
            print(f"    - {att.get('FileName', 'unknown')} ({att.get('Size', 0)} bytes)")

    print()


def cmd_grades(args):
    courses = _resolve_courses(args.course)
    all_grades: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            grades = get_grades(oid)
        except Exception:
            continue
        for g in grades:
            g["_course_id"] = oid
            g["_course_name"] = short_name(c["OrgUnit"]["Name"])
        all_grades.extend(grades)

    if args.json:
        print(json.dumps(all_grades, indent=2, ensure_ascii=False))
        return

    if not all_grades:
        print("No grades found.")
        return

    # Group by course
    by_course: dict[str, list[dict]] = {}
    for g in all_grades:
        cn = g["_course_name"]
        by_course.setdefault(cn, []).append(g)

    print("=== Grades ===\n")
    for cn, grades in sorted(by_course.items()):
        print(f"  [{cn}]")
        for g in grades:
            pts_n = g.get("PointsNumerator")
            pts_d = g.get("PointsDenominator")
            displayed = g.get("DisplayedGrade", "—")
            name = g.get("GradeObjectName", "?")
            if pts_n is not None and pts_d is not None:
                score = f"{pts_n:g}/{pts_d:g}"
            else:
                score = "—"
            print(f"    {name}: {score} ({displayed})")
        print()


def cmd_deadlines(args):
    courses = get_active_courses()
    now = datetime.now(timezone.utc)
    deadlines: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        cname = short_name(c["OrgUnit"]["Name"])
        try:
            folders = get_dropbox_folders(oid)
        except Exception:
            continue
        for f in folders:
            dd = f.get("DueDate")
            if dd:
                try:
                    dt = datetime.fromisoformat(dd.replace("Z", "+00:00"))
                    if dt > now:
                        deadlines.append({
                            "id": f["Id"],
                            "name": f["Name"],
                            "course": cname,
                            "course_id": oid,
                            "due": dd,
                            "due_dt": dt,
                        })
                except Exception:
                    pass

    deadlines.sort(key=lambda d: d["due_dt"])

    if args.json:
        out = [{k: v for k, v in d.items() if k != "due_dt"} for d in deadlines]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    if not deadlines:
        print("No upcoming deadlines.")
        return

    print(f"=== Upcoming Deadlines ({len(deadlines)}) ===\n")
    for d in deadlines:
        days_left = (d["due_dt"] - now).days
        urgency = ""
        if days_left <= 1:
            urgency = " [TODAY/TOMORROW]"
        elif days_left <= 3:
            urgency = " [THIS WEEK]"
        print(f"  {fmt_date(d['due'])}  |  {d['name']}{urgency}")
        print(f"    Course: {d['course']}  |  ID: {d['id']}  |  {days_left}d left")
        print()


# ---------------------------------------------------------------------------
# New subcommands: content, calendar, feedback, download, schedule, unread
# ---------------------------------------------------------------------------

def _print_toc_tree(modules, indent=0):
    """Recursively print a content tree with indentation."""
    prefix = "  " * indent
    for mod in modules:
        title = mod.get("Title", mod.get("Name", "Untitled"))
        mod_type = mod.get("TypeIdentifier", "")
        # Module header
        if mod.get("Modules") is not None or mod.get("Topics") is not None:
            print(f"{prefix}[Module] {title}")
        else:
            # It's a topic
            url = mod.get("Url", "")
            topic_type = mod.get("TypeIdentifier", "")
            extra = ""
            if url:
                extra = f"  -> {url}"
            elif topic_type:
                extra = f"  ({topic_type})"
            print(f"{prefix}  - {title}{extra}")

        # Recurse into sub-modules
        sub_modules = mod.get("Modules", [])
        if sub_modules:
            _print_toc_tree(sub_modules, indent + 1)

        # Print topics
        topics = mod.get("Topics", [])
        for topic in topics:
            t_title = topic.get("Title", "Untitled")
            t_url = topic.get("Url", "")
            t_type = topic.get("TypeIdentifier", "")
            t_id = topic.get("TopicId", "")
            extra_parts = []
            if t_id:
                extra_parts.append(f"id:{t_id}")
            if t_type:
                extra_parts.append(t_type)
            if t_url:
                extra_parts.append(t_url)
            extra = f"  ({', '.join(extra_parts)})" if extra_parts else ""
            print(f"{prefix}    - {t_title}{extra}")


def cmd_content(args):
    courses = _resolve_courses(args.course)

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        cname = short_name(c["OrgUnit"]["Name"])
        try:
            toc = api_get(f"/d2l/api/le/{LE_VER}/{oid}/content/toc")
        except SystemExit:
            print(f"  Could not fetch content for {cname} (ID: {oid})", file=sys.stderr)
            continue

        if args.json:
            toc["_course_id"] = oid
            toc["_course_name"] = cname
            print(json.dumps(toc, indent=2, ensure_ascii=False))
            continue

        print(f"=== Content: {cname} (ID: {oid}) ===\n")
        modules = toc.get("Modules", [])
        if not modules:
            print("  (No content modules found)\n")
        else:
            _print_toc_tree(modules, indent=1)
            print()


def cmd_calendar(args):
    now = datetime.now(timezone.utc)
    days = args.days if args.days else 14
    start = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end = (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def _calendar_items(resp):
        if isinstance(resp, list):
            return resp
        if isinstance(resp, dict):
            return resp.get("Objects") or resp.get("Items") or []
        return []

    def _calendar_query(start_dt, end_dt):
        return urllib.parse.urlencode({
            "startDateTime": start_dt,
            "endDateTime": end_dt,
            "association": "Any",
        })

    def _course_events(oid, cname):
        resp = api_get(f"/d2l/api/le/{LE_VER}/{oid}/calendar/events/myEvents/?{_calendar_query(start, end)}")
        events = _calendar_items(resp)
        for e in events:
            e["_course_name"] = cname
            e["_course_id"] = oid
        return events

    if args.course is not None:
        # Per-course calendar
        courses = _resolve_courses(args.course)
        all_events = []
        for c in courses:
            oid = c["OrgUnit"]["Id"]
            cname = short_name(c["OrgUnit"]["Name"])
            try:
                all_events.extend(_course_events(oid, cname))
            except SystemExit:
                continue
    else:
        # Aggregate calendar events across all active courses.
        all_events = []
        courses_list = get_active_courses()
        course_names = {c["OrgUnit"]["Id"]: short_name(c["OrgUnit"]["Name"]) for c in courses_list}
        ids = ",".join(str(c["OrgUnit"]["Id"]) for c in courses_list)
        try:
            query = urllib.parse.urlencode({
                "orgUnitIdsCSV": ids,
                "startDateTime": start,
                "endDateTime": end,
                "association": "Any",
            }, safe=",")
            resp = api_get(f"/d2l/api/le/{LE_VER}/calendar/events/myEvents/?{query}")
            all_events = _calendar_items(resp)
            for e in all_events:
                oid = e.get("OrgUnitId")
                if oid in course_names:
                    e["_course_name"] = course_names[oid]
                    e["_course_id"] = oid
        except SystemExit:
            for c in courses_list:
                oid = c["OrgUnit"]["Id"]
                cname = short_name(c["OrgUnit"]["Name"])
                try:
                    all_events.extend(_course_events(oid, cname))
                except SystemExit:
                    continue

    if args.json:
        print(json.dumps(all_events, indent=2, ensure_ascii=False))
        return

    if not all_events:
        print(f"No calendar events in the next {days} days.")
        return

    # Sort by start date
    all_events.sort(key=lambda e: e.get("StartDateTime", "") or "")

    print(f"=== Calendar Events (next {days} days) ===\n")
    for e in all_events:
        title = e.get("Title", e.get("CalendarEventId", "Untitled"))
        start_dt = fmt_date(e.get("StartDateTime"))
        end_dt = fmt_date(e.get("EndDateTime"))
        cname = e.get("_course_name", "")
        course_label = f"[{cname}] " if cname else ""
        print(f"  {course_label}{title}")
        print(f"    {start_dt} -> {end_dt}")
        desc = e.get("Description", "")
        if isinstance(desc, dict):
            desc = desc.get("Text", "") or strip_html(desc.get("Html", ""))
        elif isinstance(desc, str) and "<" in desc:
            desc = strip_html(desc)
        if desc:
            summary = desc[:200].replace("\n", " ").replace("\r", "")
            if len(desc) > 200:
                summary += "..."
            print(f"    {summary}")
        print()


def cmd_feedback(args):
    assignment_id = args.id
    courses = get_active_courses()
    found_course = None
    found_folder = None

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        try:
            folders = get_dropbox_folders(oid)
        except Exception:
            continue
        for f in folders:
            if f["Id"] == assignment_id:
                found_course = c
                found_folder = f
                break
        if found_folder:
            break

    if not found_folder or not found_course:
        print(f"Assignment {assignment_id} not found.", file=sys.stderr)
        sys.exit(1)

    oid = found_course["OrgUnit"]["Id"]
    cname = short_name(found_course["OrgUnit"]["Name"])

    # Try multiple feedback endpoints
    feedback = None

    # Try 1: submissions endpoint (get my submissions which include feedback)
    submissions = _api_get_safe(
        f"/d2l/api/le/{LE_VER}/{oid}/dropbox/folders/{assignment_id}/submissions/mysubmissions/"
    )
    if submissions and isinstance(submissions, list) and len(submissions) > 0:
        # The latest submission may contain feedback
        latest = submissions[-1]
        fb = latest.get("Feedback", {})
        score = latest.get("Score")
        feedback = {
            "Feedback": fb if fb else {},
            "Score": score,
            "Submissions": submissions,
        }
    else:
        # Try 2: direct feedback endpoint
        feedback = _api_get_safe(
            f"/d2l/api/le/{LE_VER}/{oid}/dropbox/folders/{assignment_id}/feedback/myFeedback"
        )

    if not feedback:
        print(f"No feedback found for assignment {assignment_id}.", file=sys.stderr)
        print("(The professor may not have provided feedback yet, or you may not have submitted.)", file=sys.stderr)
        return

    if args.json:
        feedback["_course_name"] = cname
        feedback["_assignment_name"] = found_folder["Name"]
        print(json.dumps(feedback, indent=2, ensure_ascii=False))
        return

    print(f"=== Feedback: {found_folder['Name']} ===")
    print(f"  Course: {cname}\n")

    # Navigate nested feedback structure
    fb_obj = feedback.get("Feedback", {})
    # Some responses nest feedback inside Feedback.Feedback
    inner_fb = fb_obj.get("Feedback", fb_obj)
    fb_html = inner_fb.get("Html", "")
    fb_text = inner_fb.get("Text", "")
    fb_content = fb_text if fb_text else strip_html(fb_html)
    if fb_content:
        print(f"  Feedback:")
        print(wrap(fb_content, width=78, indent="    "))
    else:
        print("  (No written feedback)")

    # Score can be at top level or inside Feedback
    score = feedback.get("Score") or fb_obj.get("Score")
    if score is not None:
        out_of = feedback.get("OutOf", "")
        score_str = f"{score}"
        if out_of:
            score_str += f"/{out_of}"
        print(f"\n  Score: {score_str}")

    is_graded = fb_obj.get("IsGraded")
    graded_symbol = fb_obj.get("GradedSymbol")
    if is_graded and graded_symbol:
        print(f"\n  Grade: {graded_symbol}")

    rubric = fb_obj.get("RubricAssessments", feedback.get("RubricAssessments", []))
    if rubric:
        print(f"\n  Rubric Assessments:")
        for r in rubric:
            r_name = r.get("RubricName", "Rubric")
            r_score = r.get("Score", "—")
            r_out_of = r.get("OutOf", "")
            print(f"    {r_name}: {r_score}" + (f"/{r_out_of}" if r_out_of else ""))

    attachments = fb_obj.get("Files", feedback.get("Files", []))
    if attachments:
        print(f"\n  Feedback Files:")
        for att in attachments:
            print(f"    - {att.get('FileName', 'unknown')} ({att.get('Size', 0)} bytes)")

    # Show submission info if available
    subs = feedback.get("Submissions", [])
    if subs:
        latest_sub = subs[-1] if isinstance(subs, list) else subs
        sub_files = latest_sub.get("Submissions", [])
        if isinstance(sub_files, list) and sub_files:
            last = sub_files[-1]
            print(f"\n  Last Submission: {fmt_date(last.get('SubmissionDate'))}")
            for sf in last.get("Files", []):
                print(f"    Submitted: {sf.get('FileName', 'unknown')}")

    print()


def cmd_download(args):
    target = args.target
    output_path = args.output

    from urllib.parse import quote, urlparse, unquote

    # Determine if target is a URL or a topic ID
    if target.startswith("http://") or target.startswith("https://") or target.startswith("/"):
        # Direct URL download — URL-encode the path if needed
        if target.startswith("/"):
            url = D2L_BASE + quote(target, safe="/:@!$&'()*+,;=")
        else:
            url = target
    else:
        # Assume it's a topic ID — we need to find it in content
        # Try to parse as int
        try:
            topic_id = int(target)
        except ValueError:
            print(f"Invalid target: {target}. Provide a URL or numeric topic ID.", file=sys.stderr)
            sys.exit(1)

        # Search across courses for this topic ID
        courses = get_active_courses()
        topic_url = None
        topic_title = None
        for c in courses:
            oid = c["OrgUnit"]["Id"]
            try:
                toc = api_get(f"/d2l/api/le/{LE_VER}/{oid}/content/toc")
            except SystemExit:
                continue
            # Search the toc tree for the topic
            found = _find_topic_in_toc(toc, topic_id, oid)
            if found:
                topic_url = found.get("url")
                topic_title = found.get("title", "download")
                break

        if not topic_url:
            print(f"Topic ID {topic_id} not found in any course content.", file=sys.stderr)
            sys.exit(1)

        url = topic_url if topic_url.startswith("http") else D2L_BASE + topic_url

    # Download the file
    req = urllib.request.Request(url)
    req.add_header("Cookie", _get_cookie_header())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            # Determine filename
            if output_path:
                filename = output_path
            else:
                # Try Content-Disposition header
                cd = resp.headers.get("Content-Disposition", "")
                if "filename=" in cd:
                    filename = cd.split("filename=")[-1].strip('"').strip("'")
                else:
                    # Use last part of URL path
                    path = urlparse(url).path
                    filename = unquote(path.split("/")[-1]) or "download"

            data = resp.read()
            with open(filename, "wb") as f:
                f.write(data)
            print(f"Downloaded: {filename} ({len(data)} bytes)")
    except urllib.error.HTTPError as exc:
        print(f"Error downloading: HTTP {exc.code}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error downloading: {exc}", file=sys.stderr)
        sys.exit(1)


def _find_topic_in_toc(toc, topic_id, org_unit_id):
    """Recursively search TOC for a topic by ID. Returns dict with url/title or None."""
    modules = toc.get("Modules", [])
    for mod in modules:
        topics = mod.get("Topics", [])
        for t in topics:
            if t.get("TopicId") == topic_id or t.get("Identifier") == str(topic_id):
                url = t.get("Url", "")
                if not url:
                    # Try to construct download URL
                    url = f"/d2l/api/le/{LE_VER}/{org_unit_id}/content/topics/{t.get('TopicId', topic_id)}/file"
                return {"url": url, "title": t.get("Title", "download")}
        # Recurse into sub-modules
        sub = mod.get("Modules", [])
        if sub:
            result = _find_topic_in_toc({"Modules": sub}, topic_id, org_unit_id)
            if result:
                return result
    return None


def cmd_schedule(args):
    now = datetime.now(timezone.utc)
    # Get this week's events (Monday to Sunday)
    weekday = now.weekday()  # 0=Monday
    monday = now - timedelta(days=weekday)
    sunday = monday + timedelta(days=6, hours=23, minutes=59)
    start = monday.strftime("%Y-%m-%dT00:00:00.000Z")
    end = sunday.strftime("%Y-%m-%dT23:59:59.000Z")

    events = []
    def _calendar_items(resp):
        if isinstance(resp, list):
            return resp
        if isinstance(resp, dict):
            return resp.get("Objects") or resp.get("Items") or []
        return []

    for c in get_active_courses():
        oid = c["OrgUnit"]["Id"]
        cname = short_name(c["OrgUnit"]["Name"])
        try:
            query = urllib.parse.urlencode({
                "startDateTime": start,
                "endDateTime": end,
                "association": "Any",
            })
            resp = api_get(f"/d2l/api/le/{LE_VER}/{oid}/calendar/events/myEvents/?{query}")
        except SystemExit:
            continue
        items = _calendar_items(resp)
        for e in items:
            e["_course_name"] = cname
            e["_course_id"] = oid
        events.extend(items)

    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return

    if not events:
        print("No scheduled events this week.")
        # Also show enrolled courses as a fallback
        print("\nEnrolled active courses (check D2L for class times):")
        for c in get_active_courses():
            print(f"  - {short_name(c['OrgUnit']['Name'])}")
        return

    # Group by day of week
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day: dict[int, list] = {i: [] for i in range(7)}

    for e in events:
        sd = e.get("StartDateTime", "")
        if sd:
            try:
                dt = datetime.fromisoformat(sd.replace("Z", "+00:00"))
                by_day[dt.weekday()].append(e)
            except Exception:
                pass

    print("=== Weekly Schedule ===\n")
    for day_idx in range(7):
        day_events = by_day[day_idx]
        if day_events:
            day_date = monday + timedelta(days=day_idx)
            print(f"  {day_names[day_idx]} ({day_date.strftime('%Y-%m-%d')}):")
            day_events.sort(key=lambda e: e.get("StartDateTime", ""))
            for e in day_events:
                title = e.get("Title", "Untitled")
                s = fmt_date(e.get("StartDateTime"))
                en = fmt_date(e.get("EndDateTime"))
                # Extract time part
                s_time = s.split(" ")[-1] if " " in s else s
                e_time = en.split(" ")[-1] if " " in en else en
                print(f"    {s_time}-{e_time}  {title}")
            print()


def _api_get_safe(path: str):
    """Like api_get but returns None on error instead of sys.exit."""
    global _cookies, _login_attempted
    url = D2L_BASE + path
    req = urllib.request.Request(url)
    req.add_header("Cookie", _get_cookie_header())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw)
    except Exception:
        return None


def cmd_unread(args):
    courses = get_active_courses()
    all_unread: list[dict] = []

    for c in courses:
        oid = c["OrgUnit"]["Id"]
        cname = short_name(c["OrgUnit"]["Name"])

        # Try unread count endpoint
        data = _api_get_safe(f"/d2l/api/le/{LE_VER}/{oid}/content/myUnreadCount")
        if data is not None:
            count = 0
            if isinstance(data, dict):
                count = data.get("UnreadCount", data.get("Count", 0))
            elif isinstance(data, int):
                count = data
            if count > 0:
                all_unread.append({
                    "course_id": oid,
                    "course_name": cname,
                    "unread_count": count,
                })
            continue

        # Fallback: check recent news (announcements from last 7 days as proxy)
        news = _api_get_safe(f"/d2l/api/le/{LE_VER}/{oid}/news/")
        if news and isinstance(news, list):
            now = datetime.now(timezone.utc)
            recent_count = 0
            for n in news:
                sd = n.get("StartDate", "")
                if sd:
                    try:
                        dt = datetime.fromisoformat(sd.replace("Z", "+00:00"))
                        if (now - dt).days <= 7:
                            # Check if not read (IsRead field if available)
                            if not n.get("IsRead", True):
                                recent_count += 1
                    except Exception:
                        pass
            if recent_count > 0:
                all_unread.append({
                    "course_id": oid,
                    "course_name": cname,
                    "unread_count": recent_count,
                    "type": "announcements",
                })

    if args.json:
        print(json.dumps(all_unread, indent=2, ensure_ascii=False))
        return

    if not all_unread:
        print("No unread items detected across your courses.")
        return

    print("=== Unread Items ===\n")
    for item in all_unread:
        t = f" ({item['type']})" if "type" in item else ""
        print(f"  [{item['course_name']}]  {item['unread_count']} unread item(s){t}")
    print()


def cmd_login(args):
    _browser_open_visible()
    print("Opened the D2L helper browser.")
    print("Sign in to D2L/Microsoft, choose Stay signed in if prompted, wait for D2L to load, then close that browser before using headless d2l commands.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="d2l",
        description="Read-only CLI for D2L/Brightspace LMS at USFQ",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable text")
    sub = parser.add_subparsers(dest="command", required=True)

    # login helper
    sub.add_parser("login", help="Open visible helper browser for manual D2L login")

    # classes
    sub.add_parser("classes", help="List enrolled courses")

    # announcements
    p_ann = sub.add_parser("announcements", help="Get course announcements")
    p_ann.add_argument("--course", type=int, default=None, help="Course/OrgUnit ID (default: all active)")

    # notifications
    sub.add_parser("notifications", help="Get recent notifications (last 14 days)")

    # assignments
    p_asgn = sub.add_parser("assignments", help="List assignments with deadlines")
    p_asgn.add_argument("--course", type=int, default=None, help="Course/OrgUnit ID (default: all active)")

    # assignment (single)
    p_asgn1 = sub.add_parser("assignment", help="Get details for a single assignment")
    p_asgn1.add_argument("id", type=int, help="Assignment (dropbox folder) ID")

    # grades
    p_grd = sub.add_parser("grades", help="Get grades")
    p_grd.add_argument("--course", type=int, default=None, help="Course/OrgUnit ID (default: all active)")

    # deadlines
    sub.add_parser("deadlines", help="List upcoming deadlines across all courses")

    # content
    p_content = sub.add_parser("content", help="List course content modules and topics (table of contents)")
    p_content.add_argument("--course", type=int, default=None, help="Course/OrgUnit ID (default: all active)")

    # calendar
    p_cal = sub.add_parser("calendar", help="Show calendar events")
    p_cal.add_argument("--course", type=int, default=None, help="Course/OrgUnit ID (default: all)")
    p_cal.add_argument("--days", type=int, default=14, help="Number of days to look ahead (default: 14)")

    # feedback
    p_fb = sub.add_parser("feedback", help="Show professor feedback on a submitted assignment")
    p_fb.add_argument("id", type=int, help="Assignment (dropbox folder) ID")

    # download
    p_dl = sub.add_parser("download", help="Download a course file")
    p_dl.add_argument("target", help="URL or topic ID to download")
    p_dl.add_argument("--output", "-o", default=None, help="Output file path (default: auto-detect)")

    # schedule
    sub.add_parser("schedule", help="Show this week's class schedule")

    # unread
    sub.add_parser("unread", help="Show unread content items across all courses")

    args = parser.parse_args()

    dispatch = {
        "login": cmd_login,
        "classes": cmd_classes,
        "announcements": cmd_announcements,
        "notifications": cmd_notifications,
        "assignments": cmd_assignments,
        "assignment": cmd_assignment,
        "grades": cmd_grades,
        "deadlines": cmd_deadlines,
        "content": cmd_content,
        "calendar": cmd_calendar,
        "feedback": cmd_feedback,
        "download": cmd_download,
        "schedule": cmd_schedule,
        "unread": cmd_unread,
    }

    try:
        dispatch[args.command](args)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
