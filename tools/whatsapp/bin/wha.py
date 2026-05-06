#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import contextlib
import json
import os
import sqlite3
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def db_path():
    return os.environ.get(
        "WHASAPO_DB",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "whasapo", "session.db"),
    )


def alias_path():
    return os.environ.get(
        "WHA_ALIASES",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "whasapo", "aliases.json"),
    )


def load_aliases():
    path = alias_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def save_aliases(aliases):
    path = alias_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2, sort_keys=True)


def alias_name(chat):
    return load_aliases().get(chat, "")


def whasapo_source():
    exe = os.environ.get(
        "WHASAPO_EXE",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "whasapo", "whasapo.exe"),
    )
    if not os.path.exists(exe):
        raise SystemExit(f"Whasapo executable not found: {exe}")
    return f"{exe.replace(os.sep, '/')} serve"


def whasapo_exe():
    exe = os.environ.get(
        "WHASAPO_EXE",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "whasapo", "whasapo.exe"),
    )
    if not os.path.exists(exe):
        raise SystemExit(f"Whasapo executable not found: {exe}")
    return exe


def whasapo_running():
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq whasapo.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return "whasapo.exe" in result.stdout.lower()
    result = subprocess.run(
        ["pgrep", "-f", "whasapo.*serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def start_whasapo_serve():
    if whasapo_running():
        return False
    exe = whasapo_exe()
    if os.name == "nt":
        subprocess.Popen(
            [exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return True


@contextlib.contextmanager
def live_lock():
    path = os.environ.get(
        "WHA_LIVE_LOCK",
        os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "whasapo", "wha-live.lock"),
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a+", encoding="utf-8") as lock_file:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def run_live_tool(*tool_args):
    with live_lock():
        return subprocess.run(
            ["mcp2cli", "--mcp-stdio", whasapo_source(), *tool_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )


def connect():
    path = db_path()
    if not os.path.exists(path):
        raise SystemExit(f"Whasapo database not found: {path}")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def ts_expr(column="timestamp"):
    return f"datetime({column}, 'unixepoch', 'localtime')"


def row_to_dict(row):
    out = dict(row)
    for key in ("is_from_me", "is_group"):
        if key in out:
            out[key] = bool(out[key])
    return out


def print_rows(rows, as_json=False, as_csv=False):
    rows = [row_to_dict(r) if isinstance(r, sqlite3.Row) else r for r in rows]
    aliases = load_aliases()
    for row in rows:
        chat = row.get("chat")
        if chat and aliases.get(chat):
            row["alias"] = aliases[chat]
            if not row.get("name") or row.get("name") == chat:
                row["name"] = aliases[chat]
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if as_csv:
        if not rows:
            return
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        return
    for r in rows:
        parts = []
        if "time" in r:
            parts.append(r["time"])
        if "chat" in r:
            parts.append(r["chat"])
        if "name" in r and r["name"]:
            parts.append(r["name"])
        elif "alias" in r and r["alias"]:
            parts.append(r["alias"])
        if "sender" in r:
            parts.append("me" if r.get("is_from_me") else (r.get("sender") or "them"))
        if "media_type" in r and r["media_type"]:
            parts.append(f"[{r['media_type']}]")
        if "text" in r:
            parts.append((r["text"] or "").replace("\n", " ")[:500])
        elif "last_message" in r:
            parts.append((r["last_message"] or "").replace("\n", " ")[:300])
        print(" | ".join(parts))


def cmd_doctor(args):
    path = db_path()
    info = {"db": path, "exists": os.path.exists(path)}
    if info["exists"]:
        st = os.stat(path)
        info["size_bytes"] = st.st_size
        info["modified"] = dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
        con = connect()
        for table in ("messages", "whatsmeow_contacts"):
            try:
                info[table] = con.execute(f"select count(*) from {table}").fetchone()[0]
            except sqlite3.Error:
                info[table] = None
    aliases = load_aliases()
    info["aliases"] = len(aliases)
    info["aliases_file"] = alias_path()
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cache_counts():
    path = db_path()
    info = {"db": path, "exists": os.path.exists(path), "messages": 0, "whatsmeow_contacts": 0}
    if not info["exists"]:
        return info
    st = os.stat(path)
    info["size_bytes"] = st.st_size
    info["modified"] = dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    con = connect()
    for table in ("messages", "whatsmeow_contacts"):
        try:
            info[table] = con.execute(f"select count(*) from {table}").fetchone()[0]
        except sqlite3.Error:
            info[table] = None
    return info


def cmd_sync(args):
    started = start_whasapo_serve()
    deadline = time.time() + args.wait
    info = cache_counts()
    while args.wait > 0 and time.time() < deadline:
        if (info.get("messages") or 0) > 0 and (info.get("whatsmeow_contacts") or 0) > 0:
            break
        time.sleep(2)
        info = cache_counts()
    info["serve_started"] = started
    info["serve_running"] = whasapo_running()
    info["waited_seconds"] = args.wait
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_search(args):
    con = connect()
    terms = [t.lower() for t in args.terms]
    where = []
    params = []
    for term in terms:
        where.append("(lower(text) like ? or lower(push_name) like ? or lower(chat) like ? or lower(sender) like ?)")
        like = f"%{term}%"
        params.extend([like, like, like, like])
    sql = f"""
        select {ts_expr()} as time, id, chat, sender, push_name, is_from_me, is_group,
               media_type, substr(replace(text, char(10), ' '), 1, ?) as text
        from messages
        where {' and '.join(where)}
        order by timestamp desc
        limit ?
    """
    rows = con.execute(sql, [args.width, *params, args.limit]).fetchall()
    print_rows(rows, args.json, args.csv)


def cmd_chat(args):
    con = connect()
    rows = con.execute(
        f"""
        select {ts_expr()} as time, id, chat, sender, push_name, is_from_me, is_group,
               media_type, substr(replace(text, char(10), ' '), 1, ?) as text
        from messages
        where chat = ?
        order by timestamp desc
        limit ?
        """,
        (args.width, args.chat, args.limit),
    ).fetchall()
    rows = list(reversed(rows)) if args.asc else rows
    print_rows(rows, args.json, args.csv)


def cmd_chats(args):
    con = connect()
    q = None if args.query else None
    limit = args.limit * 20 if args.query else args.limit
    rows = con.execute(
        f"""
        with latest as (
          select chat, max(timestamp) as max_ts from messages group by chat
        )
        select {ts_expr('m.timestamp')} as time,
               m.chat,
               coalesce(nullif(c.full_name,''), nullif(c.push_name,''), nullif(c.business_name,''), nullif(c.first_name,''), m.chat) as name,
               m.is_group,
               substr(replace(m.text, char(10), ' '), 1, ?) as last_message
        from latest l
        join messages m on m.chat = l.chat and m.timestamp = l.max_ts
        left join whatsmeow_contacts c on c.their_jid = m.chat
        where (? is null or lower(m.chat) like ? or lower(coalesce(c.full_name,'') || ' ' || coalesce(c.push_name,'') || ' ' || coalesce(c.business_name,'') || ' ' || coalesce(c.first_name,'')) like ?)
        order by m.timestamp desc
        limit ?
        """,
        (args.width, q, q, q, limit),
    ).fetchall()
    rows = [row_to_dict(r) for r in rows]
    if args.query:
        q_plain = args.query.lower()
        aliases = load_aliases()
        rows = [
            r
            for r in rows
            if q_plain in (r.get("chat") or "").lower()
            or q_plain in (r.get("name") or "").lower()
            or q_plain in aliases.get(r.get("chat") or "", "").lower()
        ]
        seen = {r.get("chat") for r in rows}
        for chat, name in aliases.items():
            if chat in seen or (q_plain not in chat.lower() and q_plain not in name.lower()):
                continue
            latest = con.execute(
                f"""
                select {ts_expr()} as time,
                       chat,
                       ? as name,
                       is_group,
                       substr(replace(text, char(10), ' '), 1, ?) as last_message
                from messages
                where chat = ?
                order by timestamp desc
                limit 1
                """,
                (name, args.width, chat),
            ).fetchone()
            if latest:
                rows.append(row_to_dict(latest))
            else:
                rows.append({"time": "", "chat": chat, "name": name, "is_group": chat.endswith("@g.us"), "last_message": ""})
        rows = rows[: args.limit]
    print_rows(rows, args.json, args.csv)


def cmd_contacts(args):
    con = connect()
    q = f"%{args.query.lower()}%"
    rows = con.execute(
        """
        select their_jid as chat,
               coalesce(nullif(full_name,''), nullif(push_name,''), nullif(business_name,''), nullif(first_name,''), their_jid) as name,
               redacted_phone
        from whatsmeow_contacts
        where lower(their_jid) like ?
           or lower(coalesce(first_name,'') || ' ' || coalesce(full_name,'') || ' ' || coalesce(push_name,'') || ' ' || coalesce(business_name,'')) like ?
        order by name
        limit ?
        """,
        (q, q, args.limit),
    ).fetchall()
    rows = [row_to_dict(r) for r in rows]
    aliases = load_aliases()
    q_plain = args.query.lower()
    seen = {r["chat"] for r in rows}
    for chat, name in aliases.items():
        if chat not in seen and (q_plain in chat.lower() or q_plain in name.lower()):
            rows.append({"chat": chat, "name": name, "redacted_phone": ""})
    print_rows(rows[: args.limit], args.json, args.csv)


def cmd_alias(args):
    aliases = load_aliases()
    if args.alias_cmd == "list":
        rows = [{"chat": chat, "name": name} for chat, name in sorted(aliases.items(), key=lambda x: x[1].lower())]
        print_rows(rows, args.json, False)
        return
    if args.alias_cmd == "import-live":
        result = run_live_tool("list-chats")
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            raise SystemExit(result.returncode)
        imported = 0
        skipped = 0
        chats = json.loads(result.stdout)
        for chat in chats:
            jid = chat.get("jid", "")
            name = (chat.get("name") or "").strip()
            if not jid or not name or name == jid:
                skipped += 1
                continue
            if jid in aliases and not args.overwrite:
                skipped += 1
                continue
            aliases[jid] = name
            imported += 1
        save_aliases(aliases)
        print(json.dumps({"imported": imported, "skipped": skipped, "aliases_file": alias_path()}, indent=2))
        if result.stderr:
            sys.stderr.write(result.stderr)
        return
    if args.alias_cmd == "import-recent-groups":
        con = connect()
        group_rows = con.execute(
            """
            select chat, max(timestamp) as max_ts
            from messages
            where is_group = 1 and chat like '%@g.us'
            group by chat
            order by max_ts desc
            limit ?
            """,
            (args.limit,),
        ).fetchall()
        imported = 0
        skipped = 0
        failed = []
        details = []
        for row in group_rows:
            chat = row["chat"]
            if chat in aliases and not args.refresh and not args.overwrite and aliases[chat] and aliases[chat] != chat:
                skipped += 1
                details.append({"chat": chat, "name": aliases[chat], "status": "kept"})
                continue
            result = run_live_tool("get-chat", "--chat", chat)
            if result.returncode != 0:
                failed.append({"chat": chat, "error": result.stderr.strip()})
                continue
            try:
                info = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                failed.append({"chat": chat, "error": f"invalid JSON: {exc}"})
                continue
            name = (info.get("name") or "").strip()
            if not name or name == chat:
                skipped += 1
                details.append({"chat": chat, "name": name, "status": "no-name"})
                continue
            aliases[chat] = name
            imported += 1
            details.append({"chat": chat, "name": name, "status": "imported"})
        save_aliases(aliases)
        print(
            json.dumps(
                {
                    "checked": len(group_rows),
                    "imported": imported,
                    "skipped": skipped,
                    "failed": len(failed),
                    "aliases_file": alias_path(),
                    "details": details,
                    "errors": failed,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.alias_cmd == "import-recent-directs":
        con = connect()
        rows = con.execute(
            f"""
            select m.chat,
                   max(m.timestamp) as max_ts,
                   coalesce(nullif(c.full_name,''), nullif(c.push_name,''), nullif(c.business_name,''), nullif(c.first_name,''), '') as contact_name
            from messages m
            left join whatsmeow_contacts c on c.their_jid = m.chat
            where m.is_group = 0 and m.chat not like '%@g.us' and m.chat != 'status@broadcast'
            group by m.chat
            order by max_ts desc
            limit ?
            """,
            (args.limit,),
        ).fetchall()
        imported = 0
        skipped = 0
        failed = []
        details = []
        for row in rows:
            chat = row["chat"]
            if chat in aliases and not args.refresh and not args.overwrite and aliases[chat] and aliases[chat] != chat:
                skipped += 1
                details.append({"chat": chat, "name": aliases[chat], "source": "existing", "status": "kept"})
                continue
            name = (row["contact_name"] or "").strip()
            source = "contacts"
            if args.live and (not name or name == chat):
                result = run_live_tool("get-chat", "--chat", chat)
                if result.returncode != 0:
                    failed.append({"chat": chat, "error": result.stderr.strip()})
                    continue
                try:
                    info = json.loads(result.stdout)
                except json.JSONDecodeError as exc:
                    failed.append({"chat": chat, "error": f"invalid JSON: {exc}"})
                    continue
                name = (info.get("name") or "").strip()
                source = "live"
            if not name or name == chat:
                skipped += 1
                details.append({"chat": chat, "name": name, "source": source, "status": "no-name"})
                continue
            aliases[chat] = name
            imported += 1
            details.append({"chat": chat, "name": name, "source": source, "status": "imported"})
        save_aliases(aliases)
        print(
            json.dumps(
                {
                    "checked": len(rows),
                    "imported": imported,
                    "skipped": skipped,
                    "failed": len(failed),
                    "aliases_file": alias_path(),
                    "details": details,
                    "errors": failed,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.alias_cmd == "set":
        aliases[args.chat] = args.name
        save_aliases(aliases)
        print(f"{args.name} -> {args.chat}")
        return
    if args.alias_cmd == "remove":
        removed = aliases.pop(args.chat, None)
        save_aliases(aliases)
        print(f"removed {removed or args.chat}")
        return


def cmd_media(args):
    con = connect()
    clauses = ["media_type != ''"]
    params = []
    if args.chat:
        clauses.append("chat = ?")
        params.append(args.chat)
    if args.query:
        clauses.append("lower(text) like ?")
        params.append(f"%{args.query.lower()}%")
    rows = con.execute(
        f"""
        select {ts_expr()} as time, id, chat, sender, push_name, is_from_me, is_group,
               media_type, substr(replace(text, char(10), ' '), 1, ?) as text
        from messages
        where {' and '.join(clauses)}
        order by timestamp desc
        limit ?
        """,
        [args.width, *params, args.limit],
    ).fetchall()
    print_rows(rows, args.json, args.csv)


def print_live_result(result):
    if result.stdout:
        sys.stdout.write(result.stdout)
        if not result.stdout.endswith("\n"):
            sys.stdout.write("\n")
    if result.stderr:
        sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)


def cmd_download(args):
    result = run_live_tool("download-media", "--chat", args.chat, "--message-id", args.message_id)
    print_live_result(result)


def cmd_send_message(args):
    result = run_live_tool("send-message", "--to", args.to, "--message", args.message)
    print_live_result(result)


def cmd_send_file(args):
    tool_args = ["send-file", "--to", args.to, "--path", args.path]
    if args.caption:
        tool_args.extend(["--caption", args.caption])
    result = run_live_tool(*tool_args)
    print_live_result(result)


def cmd_live(args):
    if not args.args:
        print("usage: wha live --list | wha live TOOL [TOOL_ARGS...]")
        print("debug escape hatch for raw Whasapo MCP tools; prefer wha search/chats/chat/media/download/send-*")
        print("examples:")
        print("  wha live --list")
        print("  wha live download-media --chat CHAT_JID --message-id MESSAGE_ID")
        print("  wha live send-message --to CHAT_JID --message \"text\"")
        return
    with live_lock():
        result = subprocess.run(["mcp2cli", "--mcp-stdio", whasapo_source(), *args.args])
    raise SystemExit(result.returncode)


def main():
    p = argparse.ArgumentParser(description="WhatsApp CLI backed by Whasapo's local SQLite cache")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true")
    common.add_argument("--csv", action="store_true")
    common.add_argument("-n", "--limit", type=int, default=50)
    common.add_argument("--width", type=int, default=500)

    sub.add_parser("doctor").set_defaults(func=cmd_doctor)

    s = sub.add_parser("sync", help="Start Whasapo serve and wait briefly for the SQLite cache to populate")
    s.add_argument("--wait", type=int, default=20, help="Seconds to wait for non-empty messages/contacts (default: 20)")
    s.set_defaults(func=cmd_sync)

    a = sub.add_parser("alias", help="Manage local chat aliases")
    a_sub = a.add_subparsers(dest="alias_cmd", required=True)
    s = a_sub.add_parser("list")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_alias)
    s = a_sub.add_parser("import-live", help="Import live Whasapo chat names into local aliases")
    s.add_argument("--overwrite", action="store_true")
    s.set_defaults(func=cmd_alias)
    s = a_sub.add_parser("import-recent-groups", help="Import subjects for recent cached groups")
    s.add_argument("-n", "--limit", type=int, default=25)
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--refresh", action="store_true", help="Query live Whasapo even when an alias already exists")
    s.set_defaults(func=cmd_alias)
    s = a_sub.add_parser("import-recent-directs", help="Import names for recent cached one-to-one chats")
    s.add_argument("-n", "--limit", type=int, default=50)
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--refresh", action="store_true", help="Query live Whasapo even when an alias already exists")
    s.add_argument("--live", action="store_true", help="Try live get-chat for direct chats without contact-table names")
    s.set_defaults(func=cmd_alias)
    s = a_sub.add_parser("set")
    s.add_argument("chat")
    s.add_argument("name")
    s.set_defaults(func=cmd_alias)
    s = a_sub.add_parser("remove")
    s.add_argument("chat")
    s.set_defaults(func=cmd_alias)

    s = sub.add_parser("search", parents=[common], help="Search message text/push names")
    s.add_argument("terms", nargs="+")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("chat", parents=[common], help="Show messages from one chat JID")
    s.add_argument("chat")
    s.add_argument("--asc", action="store_true", help="Print oldest-to-newest within the selected page")
    s.set_defaults(func=cmd_chat)

    s = sub.add_parser("chats", parents=[common], help="List chats from cached messages")
    s.add_argument("--query", "-q", default="")
    s.set_defaults(func=cmd_chats)

    s = sub.add_parser("contacts", parents=[common], help="Search cached contacts")
    s.add_argument("query")
    s.set_defaults(func=cmd_contacts)

    s = sub.add_parser("media", parents=[common], help="List cached media messages")
    s.add_argument("--chat", default="")
    s.add_argument("--query", "-q", default="")
    s.set_defaults(func=cmd_media)

    s = sub.add_parser("download", help="Download media for a cached message ID")
    s.add_argument("--chat", required=True)
    s.add_argument("--message-id", required=True)
    s.set_defaults(func=cmd_download)

    s = sub.add_parser("send-message", help="Send an exact WhatsApp text message")
    s.add_argument("--to", required=True)
    s.add_argument("--message", required=True)
    s.set_defaults(func=cmd_send_message)

    s = sub.add_parser("send-file", help="Send an exact WhatsApp file")
    s.add_argument("--to", required=True)
    s.add_argument("--path", required=True)
    s.add_argument("--caption", default="")
    s.set_defaults(func=cmd_send_file)

    s = sub.add_parser("live", help="Debug escape hatch for raw Whasapo MCP tools")
    s.add_argument("args", nargs="*")
    s.set_defaults(func=cmd_live)

    args, extra = p.parse_known_args()
    if extra:
        if args.cmd == "live":
            args.args.extend(extra)
        else:
            p.error(f"unrecognized arguments: {' '.join(extra)}")
    args.func(args)


if __name__ == "__main__":
    main()
