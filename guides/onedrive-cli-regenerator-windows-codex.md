# OneDrive CLI transferable setup for Codex Desktop on Windows, Linux, and WSL

This Markdown file contains setup notes plus the live `onedrive.py` script and Codex skill so another Codex Desktop user can recreate the OneDrive/Microsoft Graph file-access setup without a zip.

## What this does

This CLI gives access to OneDrive/Microsoft 365 files through Microsoft Graph using the same persistent browser profile used by the Outlook CLI. It extracts a Graph access token from Outlook/Office web localStorage and calls Microsoft Graph file APIs.

The CLI is read-first: list, search, shared-with-me, metadata, thumbnails, preview, versions, permissions, delta, and download. Upload is available but should be used only when explicitly requested.

## Platform behavior

- Reuses Outlook browser profile:
  - Windows: `%LOCALAPPDATA%\outlook-cli\browser-data`
  - Linux/WSL: `~/.local/share/outlook-cli/browser-data`
- OneDrive token/cache path:
  - Windows: `%LOCALAPPDATA%\onedrive-cli`
  - Linux/WSL: `~/.local/share/onedrive-cli`
- Token cache: `graph-token.json` inside the OneDrive cache path.
- Token refresh lock: `graph-token.lock`, so parallel chats do not open the same Chromium profile at the same time.
- Windows launcher: `onedrive.cmd`.
- Linux/WSL launcher: install `onedrive.py` as executable `onedrive`.

## Prerequisites

Set up the Outlook browser profile first, then log into Outlook Web once with a visible browser. The OneDrive CLI uses that same signed-in browser profile to find a Graph token.

Install dependencies:

```powershell
python --version
python -m pip install playwright
python -m playwright install chromium
```

```bash
python3 --version
python3 -m pip install playwright
python3 -m playwright install chromium
```

## Create the files

Windows example:

```powershell
mkdir D:\VSCodeProjs2\_codex_onedrive_setup
cd D:\VSCodeProjs2\_codex_onedrive_setup
```

Linux/WSL example:

```bash
mkdir -p ~/onedrive-cli-setup ~/.local/bin
cd ~/onedrive-cli-setup
```

Create `onedrive.py` from the block below. On Windows also create `onedrive.cmd`.

## Install the command

Windows: run from the setup folder with `onedrive.cmd`, add the setup folder to PATH, or create a shim at `%USERPROFILE%\.local\bin\onedrive.cmd` because Codex Desktop normally includes `.local\bin` in its process PATH.

```bat
@echo off
call D:\VSCodeProjs2\_codex_onedrive_setup\onedrive.cmd %*
```

Linux/WSL:

```bash
cp onedrive.py ~/.local/bin/onedrive
chmod +x ~/.local/bin/onedrive
onedrive --help
```

## Verify use

```powershell
.\onedrive.cmd profile
.\onedrive.cmd drive
.\onedrive.cmd ls -n 10
.\onedrive.cmd shared -n 10
```

```bash
onedrive profile
onedrive drive
onedrive ls -n 10
onedrive shared -n 10
```

## Install as a global Codex Desktop skill

The skill can stay generic with `bins: ["onedrive"]` if `onedrive` is on PATH.

```powershell
$skillDir = Join-Path $HOME ".codex\skills\onedrive"
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
Copy-Item -LiteralPath ".\onedrive_SKILL.md" -Destination (Join-Path $skillDir "SKILL.md") -Force
```

```bash
mkdir -p ~/.codex/skills/onedrive
cp onedrive_SKILL.md ~/.codex/skills/onedrive/SKILL.md
```

New Codex Desktop chats should load the skill automatically. If an already-open chat does not see it, start a new chat or fully restart Codex Desktop.

## Useful commands

```powershell
onedrive profile
onedrive drive
onedrive ls
onedrive ls "Folder Name"
onedrive search "query words" -n 50
onedrive search-all "query words" -n 25
onedrive recent -n 50
onedrive shared -n 50
onedrive shared --include-own -n 50
onedrive meta ITEM_ID_OR_PATH
onedrive thumbnails ITEM_ID_OR_PATH
onedrive preview ITEM_ID_OR_PATH
onedrive versions ITEM_ID_OR_PATH
onedrive permissions ITEM_ID_OR_PATH
onedrive delta --reset -n 200
onedrive delta -n 200
onedrive download ITEM_ID_OR_PATH ./downloads/
onedrive upload LOCAL_PATH REMOTE_PATH --conflict replace
```

Prefer `--json` when parsing output programmatically.

## Agent workflow tips

- For file context, start with `onedrive search`, then use `onedrive search-all` if normal search is weak.
- For shared files, use `onedrive shared -n 50`; use `--include-own` only when files from the user's own OneDrive should also appear.
- Use `meta`, `permissions`, and `versions` before replacing or working with sensitive shared files.
- Use `thumbnails` or `preview` to identify visual Office/PDF/image files before downloading when useful.
- Use `delta --reset` once to establish a baseline and `delta` later to find changed files.
- Download files before using local document/spreadsheet/presentation tooling.
- Upload/replace only when explicitly requested.

## Future Graph capabilities

Microsoft Graph also supports copy, move, rename, create sharing links, invite users, and Excel workbook range/table APIs. These are intentionally not first-line commands because they are write-heavy or domain-specific. If needed later, implement them deliberately with confirmation and use Microsoft Graph DriveItem or Workbook APIs.

## Security notes

- Do not hardcode passwords.
- Do not share `graph-token.json`.
- Do not share the reused `browser-data` profile; it contains credentials/session state.
- Be careful with preview/thumbnail URLs because they can contain short-lived access tokens.

## File: `onedrive.py`

```python
#!/usr/bin/env python3
"""
OneDrive/Microsoft Graph CLI -- files.

Uses the existing Outlook Web persistent Chromium profile to extract a
Microsoft Graph access token, then calls Graph file APIs. Read-first by
default; upload is explicit.
"""

import argparse
import asyncio
import base64
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform.startswith("win"):
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
OWA_URL = "https://outlook.cloud.microsoft/mail/"
TOKEN_BOOTSTRAP_URLS = [
    "https://www.office.com/launch/onedrive",
    "https://www.office.com/",
    OWA_URL,
]

if sys.platform.startswith("win"):
    OUTLOOK_SHARE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "outlook-cli"
    SHARE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "onedrive-cli"
else:
    OUTLOOK_SHARE_DIR = Path.home() / ".local/share/outlook-cli"
    SHARE_DIR = Path.home() / ".local/share/onedrive-cli"

BROWSER_DATA_DIR = OUTLOOK_SHARE_DIR / "browser-data"
BROWSER_LOCK_FILE = OUTLOOK_SHARE_DIR / "browser.lock"
TOKEN_FILE = SHARE_DIR / "graph-token.json"
TOKEN_LOCK_FILE = SHARE_DIR / "graph-token.lock"
ID_MAP_FILE = SHARE_DIR / "id_map.json"
DELTA_TOKEN_FILE = SHARE_DIR / "delta_link.txt"
ID_MAP_MAX = 3000

SELECT_ITEM_LIST = "id,name,folder,file,size,webUrl,lastModifiedDateTime,parentReference,createdBy,lastModifiedBy"
SELECT_ITEM_FULL = SELECT_ITEM_LIST + ",createdDateTime,description,eTag,cTag,shared,remoteItem,specialFolder"


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


def _decode_claims(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload.encode()))
    except Exception:
        return {}


def _token_valid(tok: dict) -> bool:
    try:
        if time.time() >= int(tok.get("expiresOn", 0)) - 120:
            return False
    except Exception:
        return False
    claims = _decode_claims(tok.get("secret", ""))
    return claims.get("aud") == "https://graph.microsoft.com"


def _load_cached_token() -> dict | None:
    if not TOKEN_FILE.exists():
        return None
    try:
        tok = json.loads(TOKEN_FILE.read_text())
        return tok if _token_valid(tok) else None
    except Exception:
        return None


def _save_token(tok: dict) -> None:
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tok))


def _acquire_lock(timeout: int = 90) -> int:
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
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
                raise RuntimeError("Timed out waiting for OneDrive token refresh lock")
            time.sleep(0.5)


def _release_lock(fd: int) -> None:
    try:
        os.close(fd)
    finally:
        try:
            TOKEN_LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _acquire_browser_lock(timeout: int = 90) -> int:
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


async def _fetch_graph_token_from_browser() -> dict:
    from playwright.async_api import async_playwright

    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    pw = await async_playwright().start()
    browser = None
    try:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            headless=True,
            executable_path=_find_chromium(),
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        for url in TOKEN_BOOTSTRAP_URLS:
            await page.goto(url, timeout=30000)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            await asyncio.sleep(2)

            for _ in range(12):
                try:
                    tok = await page.evaluate("""() => {
                const now = Math.floor(Date.now() / 1000);
                const fresh = (v) => {
                    const exp = Number(v.expiresOn || 0);
                    return v.secret && exp && exp > now + 120;
                };
                for (let i = 0; i < localStorage.length; i++) {
                    const k = localStorage.key(i);
                    if (!k || !k.startsWith('msal.') || !k.toLowerCase().includes('accesstoken')) continue;
                    try {
                        const v = JSON.parse(localStorage.getItem(k));
                        const target = (v.target || '').toLowerCase();
                        if (fresh(v) && target.includes('https://graph.microsoft.com/') && target.includes('files.readwrite')) return v;
                    } catch {}
                }
                for (let i = 0; i < localStorage.length; i++) {
                    const k = localStorage.key(i);
                    if (!k || !k.startsWith('msal.') || !k.toLowerCase().includes('accesstoken')) continue;
                    try {
                        const v = JSON.parse(localStorage.getItem(k));
                        const target = (v.target || '').toLowerCase();
                        if (fresh(v) && target.includes('https://graph.microsoft.com/')) return v;
                    } catch {}
                }
                return null;
            }""")
                except Exception:
                    tok = None
                if tok and tok.get("secret"):
                    return tok
                await asyncio.sleep(1)
        raise RuntimeError("Could not extract Microsoft Graph token from browser MSAL cache")
    finally:
        if browser is not None:
            await browser.close()
        await pw.stop()


def get_token() -> str:
    cached = _load_cached_token()
    if cached:
        return cached["secret"]
    fd = _acquire_lock()
    try:
        cached = _load_cached_token()
        if cached:
            return cached["secret"]
        print("Refreshing OneDrive Graph token...", file=sys.stderr)
        browser_fd = _acquire_browser_lock()
        try:
            tok = asyncio.run(_fetch_graph_token_from_browser())
            _save_token(tok)
            return tok["secret"]
        finally:
            _release_browser_lock(browser_fd)
    finally:
        _release_lock(fd)


def _api_url(path: str) -> str:
    if path.startswith("http"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return GRAPH_BASE + path


def graph_get(path: str, params: dict | None = None, *, raw: bool = False) -> dict:
    url = _api_url(path)
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, safe=",$'()/:")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {get_token()}",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
        if raw:
            return {"_content": data, "_content_type": resp.headers.get("Content-Type", "")}
        return json.loads(data) if data else {}


def graph_post(path: str, payload: dict | None = None, *, raw_response: bool = False) -> dict:
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(_api_url(path), data=data, method="POST", headers={
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = resp.read()
        if raw_response:
            return {"status": resp.status, "headers": dict(resp.headers), "body": body.decode("utf-8", errors="replace")}
        return json.loads(body) if body else {"status": resp.status, "headers": dict(resp.headers)}


def graph_bytes(path: str) -> bytes:
    req = urllib.request.Request(_api_url(path), headers={"Authorization": f"Bearer {get_token()}"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def graph_put_bytes(path: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
    req = urllib.request.Request(_api_url(path), data=data, method="PUT", headers={
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": content_type,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def put_upload_chunk(upload_url: str, chunk: bytes, start: int, end: int, total: int) -> dict:
    req = urllib.request.Request(upload_url, data=chunk, method="PUT", headers={
        "Content-Length": str(len(chunk)),
        "Content-Range": f"bytes {start}-{end - 1}/{total}",
    })
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = resp.read()
        return json.loads(body) if body else {"status": resp.status}


def paginate(path: str, params: dict | None = None, limit: int = 200) -> list:
    items = []
    next_url = path
    first = True
    while next_url and len(items) < limit:
        data = graph_get(next_url, params if first else None)
        first = False
        items.extend(data.get("value", []))
        next_url = data.get("@odata.nextLink")
        if not next_url:
            break
    return items[:limit]


def _load_id_map() -> dict:
    if not ID_MAP_FILE.exists():
        return {}
    try:
        return json.loads(ID_MAP_FILE.read_text())
    except Exception:
        return {}


def _save_id_map(m: dict) -> None:
    if len(m) > ID_MAP_MAX:
        m = dict(list(m.items())[-ID_MAP_MAX:])
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
    ID_MAP_FILE.write_text(json.dumps(m))


def short_id(full_id: str, id_map: dict) -> str:
    import hashlib
    if not full_id:
        return ""
    base = hashlib.md5(full_id.encode()).hexdigest()
    short = base[:6]
    i = 6
    while short in id_map and id_map[short] != full_id and i < 32:
        i += 1
        short = base[:i]
    id_map[short] = full_id
    return short


def resolve_id(arg: str) -> str:
    if arg and re.match(r"^[0-9a-f]{6,32}$", arg):
        return _load_id_map().get(arg, arg)
    return arg


def record_ids(items: list) -> None:
    id_map = _load_id_map()
    changed = False
    for it in items:
        if isinstance(it, dict) and it.get("id"):
            short_id(it["id"], id_map)
            changed = True
    if changed:
        _save_id_map(id_map)


def item_path(path: str | None) -> str:
    if not path or path in ("/", "root"):
        return "/me/drive/root"
    item = resolve_id(path)
    if item != path:
        return f"/me/drive/items/{urllib.parse.quote(item, safe='')}"
    clean = path.strip().replace("\\", "/").strip("/")
    return f"/me/drive/root:/{urllib.parse.quote(clean, safe='/')}:"


def children_path(path: str | None) -> str:
    if not path or path in ("/", "root"):
        return "/me/drive/root/children"
    return item_path(path) + "/children"


def fmt_size(n: int | None) -> str:
    n = int(n or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n} B"


def cmd_profile(args):
    return graph_get("/me", {"$select": "displayName,userPrincipalName,mail,id"})


def cmd_drive(args):
    return graph_get("/me/drive", {"$select": "id,driveType,name,webUrl,owner,quota"})


def cmd_ls(args):
    params = {"$select": SELECT_ITEM_LIST, "$top": str(min(args.count, 200))}
    items = paginate(children_path(args.path), params, limit=args.count)
    record_ids(items)
    return items


def cmd_meta(args):
    return graph_get(item_path(args.path), {"$select": SELECT_ITEM_FULL})


def cmd_search(args):
    q = args.query.replace("'", "''")
    params = {"$select": SELECT_ITEM_LIST, "$top": str(min(args.count, 200))}
    items = paginate(f"/me/drive/root/search(q='{urllib.parse.quote(q, safe='')}')", params, limit=args.count)
    record_ids(items)
    return items


def cmd_search_all(args):
    payload = {
        "requests": [
            {
                "entityTypes": ["driveItem"],
                "query": {"queryString": args.query},
                "from": 0,
                "size": min(args.count, 100),
                "fields": ["id", "name", "webUrl", "size", "lastModifiedDateTime", "file", "folder", "parentReference"],
            }
        ]
    }
    data = graph_post("/search/query", payload)
    hits = []
    for response in data.get("value", []):
        for container in response.get("hitsContainers", []):
            for hit in container.get("hits", []):
                resource = hit.get("resource") or {}
                if resource:
                    resource["_rank"] = hit.get("rank")
                    resource["_summary"] = hit.get("summary")
                    hits.append(resource)
    record_ids(hits)
    return hits


def cmd_recent(args):
    items = paginate("/me/drive/recent", {"$select": SELECT_ITEM_LIST, "$top": str(min(args.count, 200))}, limit=args.count)
    record_ids(items)
    return items


def _shared_owner_email(item: dict) -> str:
    ri = item.get("remoteItem") or item
    shared = ((ri.get("shared") or {}).get("sharedBy") or {}).get("user") or {}
    return (shared.get("email") or "").lower()


def _shared_site_url(item: dict) -> str:
    ri = item.get("remoteItem") or item
    return ((ri.get("sharepointIds") or {}).get("siteUrl") or ri.get("webUrl") or item.get("webUrl") or "").lower()


def cmd_shared(args):
    fetch_count = args.count if args.include_own else min(max(args.count * 4, 50), 200)
    items = paginate("/me/drive/sharedWithMe", {"$top": str(fetch_count)}, limit=fetch_count)
    if not args.include_own:
        profile = graph_get("/me", {"$select": "mail,userPrincipalName"})
        me = (profile.get("mail") or profile.get("userPrincipalName") or "").split("@", 1)[0].lower()
        marker = f"/personal/{me}_"
        items = [it for it in items if marker not in _shared_site_url(it)]
    record_ids([(it.get("remoteItem") or it) for it in items])
    return items[: args.count]


def cmd_thumbnails(args):
    data = graph_get(item_path(args.path) + "/thumbnails")
    return data.get("value", [])


def cmd_preview(args):
    return graph_post(item_path(args.path) + "/preview", {})


def cmd_versions(args):
    data = graph_get(item_path(args.path) + "/versions", {"$top": str(min(args.count, 200))})
    return data.get("value", [])


def cmd_permissions(args):
    data = graph_get(item_path(args.path) + "/permissions", {"$top": str(min(args.count, 200))})
    return data.get("value", [])


def cmd_delta(args):
    if args.reset and DELTA_TOKEN_FILE.exists():
        DELTA_TOKEN_FILE.unlink()
    path = DELTA_TOKEN_FILE.read_text().strip() if DELTA_TOKEN_FILE.exists() and not args.reset else "/me/drive/root/delta"
    items = []
    next_url = path
    while next_url and len(items) < args.count:
        data = graph_get(next_url, None)
        items.extend(data.get("value", []))
        next_url = data.get("@odata.nextLink")
        delta_link = data.get("@odata.deltaLink")
        if delta_link:
            DELTA_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            DELTA_TOKEN_FILE.write_text(delta_link)
            break
    items = items[:args.count]
    record_ids(items)
    return items


def cmd_download(args):
    meta = graph_get(item_path(args.path), {"$select": "id,name,file,folder,size"})
    if meta.get("folder"):
        raise RuntimeError("download expects a file, not a folder")
    data = graph_bytes(item_path(args.path) + "/content")
    dest = Path(args.output or ".").expanduser()
    if dest.is_dir():
        dest = dest / (meta.get("name") or "download.bin")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"path": str(dest), "size": len(data)}


def cmd_upload(args):
    src = Path(args.local_path).expanduser()
    if not src.is_file():
        raise RuntimeError(f"Local file not found: {src}")
    remote = args.remote_path or src.name
    data = src.read_bytes()
    if len(data) <= 4 * 1024 * 1024:
        return graph_put_bytes(item_path(remote) + "/content", data)

    session = graph_post(item_path(remote) + "/createUploadSession", {
        "item": {
            "@microsoft.graph.conflictBehavior": args.conflict,
            "name": Path(remote).name,
        }
    })
    upload_url = session["uploadUrl"]
    chunk_size = 5 * 1024 * 1024
    last = {}
    for start in range(0, len(data), chunk_size):
        end = min(start + chunk_size, len(data))
        last = put_upload_chunk(upload_url, data[start:end], start, end, len(data))
    return last


def cmd_raw(args):
    params = dict(urllib.parse.parse_qsl(args.query)) if args.query else None
    return graph_get(args.path, params)


def cmd_token(args):
    tok = get_token()
    claims = _decode_claims(tok)
    if args.full:
        print(tok)
    else:
        print(f"{tok[:40]}...")
        print(f"aud: {claims.get('aud', '')}")
        scopes = (claims.get("scp") or "").split()
        print("scopes: " + ", ".join(scopes[:20]) + (" ..." if len(scopes) > 20 else ""))
    return None


def print_items(items: list):
    if not items:
        print("  (no items)")
        return
    id_map = _load_id_map()
    for it in items:
        sid = short_id(it.get("id", ""), id_map)
        kind = "dir " if it.get("folder") else "file"
        size = "" if it.get("folder") else fmt_size(it.get("size"))
        mod = (it.get("lastModifiedDateTime") or "")[:16].replace("T", " ")
        name = it.get("name") or it.get("webUrl") or "(unnamed item)"
        print(f"{kind:4s} {mod:16s} {size:>10s} [{sid}] {name}")
    _save_id_map(id_map)


def print_shared(items: list):
    if not items:
        print("  (no shared items)")
        return
    id_map = _load_id_map()
    for item in items:
        it = item.get("remoteItem") or item
        sid = short_id(it.get("id", ""), id_map)
        kind = "dir " if it.get("folder") else "file"
        size = "" if it.get("folder") else fmt_size(it.get("size"))
        mod = (it.get("lastModifiedDateTime") or "")[:10]
        shared = ((it.get("shared") or {}).get("sharedBy") or {}).get("user") or {}
        shared_by = shared.get("displayName") or shared.get("email") or "?"
        shared_at = ((it.get("shared") or {}).get("sharedDateTime") or "")[:10]
        name = it.get("name") or "(unnamed item)"
        print(f"{kind:4s} shared {shared_at:10s} modified {mod:10s} {size:>10s} [{sid}] {name}")
        print(f"     by {shared_by}")
    _save_id_map(id_map)


def print_thumbnails(sets: list):
    if not sets:
        print("  (no thumbnails)")
        return
    for s in sets:
        print(f"Set: {s.get('id', '')}")
        for key in ("small", "medium", "large", "source"):
            thumb = s.get(key)
            if thumb:
                print(f"  {key:7s} {thumb.get('width', '')}x{thumb.get('height', '')} {thumb.get('url', '')}")


def print_versions(versions: list):
    if not versions:
        print("  (no versions)")
        return
    for v in versions:
        mod = v.get("lastModifiedDateTime", "")
        by = (((v.get("lastModifiedBy") or {}).get("user") or {}).get("displayName") or "")
        size = fmt_size(v.get("size"))
        print(f"{v.get('id', ''):20s} {mod[:19]:19s} {size:>10s} {by}")


def print_permissions(perms: list):
    if not perms:
        print("  (no explicit permissions)")
        return
    for p in perms:
        roles = ",".join(p.get("roles") or [])
        link = (p.get("link") or {}).get("webUrl", "")
        granted = p.get("grantedToV2") or p.get("grantedTo") or {}
        user = ((granted.get("user") or {}).get("displayName") or (granted.get("user") or {}).get("email") or "")
        print(f"{p.get('id', ''):24s} {roles:12s} {user}")
        if link:
            print(f"  link: {link}")


def print_preview(p: dict):
    print(p.get("getUrl") or p.get("postUrl") or json.dumps(p, indent=2, ensure_ascii=False))


def print_meta(item: dict):
    id_map = _load_id_map()
    sid = short_id(item.get("id", ""), id_map) if item.get("id") else ""
    _save_id_map(id_map)
    print(f"Name:    {item.get('name', '')}")
    print(f"Type:    {'folder' if item.get('folder') else 'file'}")
    print(f"Size:    {fmt_size(item.get('size'))}")
    print(f"Modified:{' ' + item.get('lastModifiedDateTime', '') if item.get('lastModifiedDateTime') else ''}")
    if sid:
        print(f"ID:      {sid}")
    if item.get("webUrl"):
        print(f"Web:     {item['webUrl']}")
    parent = item.get("parentReference") or {}
    if parent.get("path"):
        print(f"Parent:  {parent['path']}")


def print_drive(d: dict):
    print(f"Name: {d.get('name', '')}")
    print(f"Type: {d.get('driveType', '')}")
    print(f"Web:  {d.get('webUrl', '')}")
    quota = d.get("quota") or {}
    if quota:
        used = fmt_size(quota.get("used"))
        total = fmt_size(quota.get("total"))
        print(f"Quota: {used} used / {total}")


def build_parser():
    p = argparse.ArgumentParser(
        description="OneDrive/Microsoft Graph CLI -- files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  onedrive ls\n"
            "  onedrive ls 'Class Presentations'\n"
            "  onedrive search intillacta -n 20\n"
            "  onedrive search-all intillacta -n 20\n"
            "  onedrive shared -n 50\n"
            "  onedrive meta <item_id_or_path>\n"
            "  onedrive permissions <item_id_or_path>\n"
            "  onedrive download <item_id_or_path> ./downloads/\n"
        ),
    )
    p.add_argument("--json", action="store_true", help="Raw JSON output")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("profile", help="Current Microsoft Graph user profile")
    sub.add_parser("drive", help="Current OneDrive drive metadata")

    ls = sub.add_parser("ls", help="List a folder")
    ls.add_argument("path", nargs="?", default="", help="Remote path or short item id")
    ls.add_argument("-n", "--count", type=int, default=50)

    meta = sub.add_parser("meta", help="File/folder metadata")
    meta.add_argument("path", help="Remote path or short item id")

    search = sub.add_parser("search", help="Search OneDrive files by name/content")
    search.add_argument("query")
    search.add_argument("-n", "--count", type=int, default=50)

    search_all = sub.add_parser("search-all", help="Richer Microsoft Search over accessible drive items")
    search_all.add_argument("query")
    search_all.add_argument("-n", "--count", type=int, default=25)

    recent = sub.add_parser("recent", help="Recent OneDrive files")
    recent.add_argument("-n", "--count", type=int, default=50)

    shared = sub.add_parser("shared", help="Files shared with you, excluding your own OneDrive by default")
    shared.add_argument("-n", "--count", type=int, default=50)
    shared.add_argument("--include-own", action="store_true", help="Include items from your own OneDrive")

    thumbs = sub.add_parser("thumbnails", help="List thumbnail URLs for an item")
    thumbs.add_argument("path", help="Remote path or short item id")

    preview = sub.add_parser("preview", help="Get a short-lived Office preview URL")
    preview.add_argument("path", help="Remote path or short item id")

    versions = sub.add_parser("versions", help="List file versions")
    versions.add_argument("path", help="Remote path or short item id")
    versions.add_argument("-n", "--count", type=int, default=50)

    perms = sub.add_parser("permissions", help="List sharing permissions")
    perms.add_argument("path", help="Remote path or short item id")
    perms.add_argument("-n", "--count", type=int, default=50)

    delta = sub.add_parser("delta", help="List changes since the last delta scan")
    delta.add_argument("-n", "--count", type=int, default=200)
    delta.add_argument("--reset", action="store_true", help="Start a fresh delta baseline")

    dl = sub.add_parser("download", help="Download a file")
    dl.add_argument("path", help="Remote path or short item id")
    dl.add_argument("output", nargs="?", default=".", help="Destination directory or filename")

    up = sub.add_parser("upload", help="Upload/replace a small file (<=4 MB)")
    up.add_argument("local_path")
    up.add_argument("remote_path", nargs="?", help="Remote path, default: local filename at drive root")
    up.add_argument("--conflict", choices=["replace", "rename", "fail"], default="replace")

    raw = sub.add_parser("raw", help="Raw Microsoft Graph GET")
    raw.add_argument("path")
    raw.add_argument("--query")

    tok = sub.add_parser("token", help="Show current Graph token info")
    tok.add_argument("--full", action="store_true", help="Print full token (sensitive)")
    return p


def main():
    args = build_parser().parse_args()
    handlers = {
        "profile": (cmd_profile, lambda r: print(json.dumps(r, indent=2, ensure_ascii=False))),
        "drive": (cmd_drive, print_drive),
        "ls": (cmd_ls, print_items),
        "meta": (cmd_meta, print_meta),
        "search": (cmd_search, print_items),
        "search-all": (cmd_search_all, print_items),
        "recent": (cmd_recent, print_items),
        "shared": (cmd_shared, print_shared),
        "thumbnails": (cmd_thumbnails, print_thumbnails),
        "preview": (cmd_preview, print_preview),
        "versions": (cmd_versions, print_versions),
        "permissions": (cmd_permissions, print_permissions),
        "delta": (cmd_delta, print_items),
        "download": (cmd_download, lambda r: print(f"Saved {r['size']} bytes to {r['path']}")),
        "upload": (cmd_upload, print_meta),
        "raw": (cmd_raw, lambda r: print(json.dumps(r, indent=2, ensure_ascii=False))),
        "token": (cmd_token, lambda _: None),
    }
    fn, formatter = handlers[args.command]
    result = fn(args)
    if args.json and result is not None:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif result is not None:
        formatter(result)


if __name__ == "__main__":
    main()
```

## File: `onedrive.cmd`

```bat
@echo off
python "%~dp0onedrive.py" %*
```

## File: `onedrive_SKILL.md`

```markdown
---
name: onedrive
description: Use this skill whenever the user asks to access, list, search, summarize, inspect, download, or upload OneDrive, Microsoft 365 files, SharePoint-backed personal files, Office files, Word documents, PowerPoint decks, Excel files, PDFs, class files, shared cloud files, or attachments saved in OneDrive. This skill uses the local `onedrive` CLI command backed by Microsoft Graph.
metadata:
  requires:
    bins: ["onedrive"]
---

# OneDrive / Microsoft Graph CLI

Use the local `onedrive` command for OneDrive/Microsoft 365 file access. It uses the same persistent browser profile as the Outlook skill to obtain a Microsoft Graph token, but it is a separate CLI and skill.

Do not say there is no OneDrive connector before trying this CLI.

## Core Commands

```powershell
onedrive profile
onedrive drive
onedrive ls
onedrive ls "Folder Name"
onedrive search "query words" -n 50
onedrive search-all "query words" -n 25
onedrive recent -n 50
onedrive shared -n 50
onedrive shared --include-own -n 50
onedrive meta ITEM_ID_OR_PATH
onedrive thumbnails ITEM_ID_OR_PATH
onedrive preview ITEM_ID_OR_PATH
onedrive versions ITEM_ID_OR_PATH
onedrive permissions ITEM_ID_OR_PATH
onedrive delta -n 200
onedrive download ITEM_ID_OR_PATH ./downloads/
```

Prefer `--json` when parsing results programmatically:

```powershell
onedrive --json ls "Class Presentations" -n 100
onedrive --json search "intillacta" -n 50
onedrive --json search-all "intillacta field report" -n 25
onedrive --json meta ITEM_ID_OR_PATH
```

## Search Strategy

For file context:

1. Start with `onedrive search "main phrase" -n 50`.
2. If normal search is weak, use `onedrive search-all "main phrase" -n 25` for Microsoft Search over accessible drive items.
3. Search 2-3 variants using project names, course names, report titles, people names, or likely attachment filenames.
4. Use `onedrive thumbnails ITEM` or `onedrive preview ITEM` to identify visual Office/PDF/image files before downloading when that helps.
5. Use `onedrive versions ITEM` and `onedrive permissions ITEM` before replacing or sharing-sensitive files.
6. Use short IDs from listing/search output for follow-up `meta` or `download` commands.
7. Download only files needed for the task, then inspect them with the appropriate local file/document/spreadsheet/presentation tools.
8. For vague requests, check relevant folders with `onedrive ls`; use `onedrive recent -n 50` as a secondary clue because Graph recent can include sparse unnamed items.

For shared files:

1. Use `onedrive shared -n 50` to list files/folders shared with the user by other people.
2. Use `onedrive shared --include-own -n 50` only when the user also wants files from their own OneDrive that they shared or collaborated on.
3. Follow up with `onedrive meta`, `onedrive permissions`, or `onedrive download` using the short ID.

For repeated monitoring:

1. Use `onedrive delta --reset -n 200` once to establish or refresh the baseline.
2. Use `onedrive delta -n 200` later to find changed files since the previous delta scan.

## Write Safety

`onedrive upload` can upload or replace a file. It uses a simple upload for small files and a resumable upload session for larger files. Use it only when the user explicitly asks to upload or replace a OneDrive file. Before replacing an existing cloud file, state the target path clearly.

Do not delete, move, or rename OneDrive files through this skill unless those commands are explicitly added and the user asks for that action.

## Future Graph Capabilities

Microsoft Graph also supports copy, move, rename, create sharing links, invite users, and Excel workbook range/table APIs. These are intentionally not first-line commands because they are write-heavy or domain-specific. If the user explicitly asks for one of these workflows, implement it deliberately with confirmation and use Microsoft Graph DriveItem or Workbook APIs.

For Word/PowerPoint editing, the practical workflow is: download the `.docx`/`.pptx`, edit locally with document/presentation tooling, then upload/replace only when the user explicitly wants the cloud file updated.
```
