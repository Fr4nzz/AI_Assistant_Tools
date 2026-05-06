---
name: outlook
description: Use this skill whenever the user asks to check, search, summarize, triage, or read Outlook, Microsoft 365, institutional email, mailbox, inbox, unread mail, email threads, attachments, meetings, or calendar events. This skill uses the local read-only `outlook` CLI command, not a connector. If the user asks about Outlook email for a time period such as this week, today, yesterday, pending items, deadlines, or things to reply to, run `outlook` commands from the shell.
metadata:
  requires:
    bins: ["outlook"]
---

# Outlook / Microsoft 365 CLI

Use the local read-only `outlook` command for Outlook/Microsoft 365 mail and calendar. Do not say there is no Outlook connector before trying this CLI.

Do not start by running `outlook --help` unless a command fails.

## Core Commands

```powershell
outlook unread
outlook inbox -n 50
outlook inbox -u -n 50
outlook inbox --focused -n 50
outlook search "topic words" -n 30
outlook search --since 7d "deadline OR reminder OR pending OR solicitud OR urgente OR please" -n 30
outlook search --since 7d -n 80
outlook read MSG_ID
outlook thread MSG_ID -n 20
outlook today
outlook calendar --days 7
```

Prefer `--json` when parsing results programmatically:

```powershell
outlook --json inbox -n 50
outlook --json search "topic words" -n 30
outlook --json search --since 7d -n 80
```

## General Search Strategy

For topic context:

1. Start with one broad `outlook search "main phrase" -n 30`.
2. Run 2-3 targeted variants using key nouns, sender names, course/project names, attachment names, or acronyms.
3. Deduplicate mentally by `ConversationId`, subject, and sender/date.
4. Read only the top representative messages first with `outlook read MSG_ID`; attachment names are usually useful context and are listed automatically.
5. Use `outlook thread MSG_ID -n 20` only when the message body shows the needed context is in prior replies; thread fetches are intentionally slower than reads.
6. Do not call `outlook attachments` after `outlook read`; `read` already lists attachment names.

For time-window summaries:

1. Use `outlook unread`, `outlook inbox --focused -n 50`, and `outlook search --since 7d -n 80`.
2. Search action words separately: `deadline OR reminder OR pending OR favor OR please OR solicitud OR urgente OR reunion OR meeting`.
3. Read only messages that look actionable from subject/preview/sender.
4. Summarize sender, date, topic, pending action, and urgency.

## Microsoft Query Tips

Use `$select` to keep responses small. Include only fields needed for scanning: `Id,Subject,From,ReceivedDateTime,IsRead,Importance,HasAttachments,BodyPreview,ConversationId`.

Use `$top` and pagination deliberately. Avoid asking for huge pages when a scan of 30-100 recent items is enough.

Expect full-text topic searches and conversation threads to be slower than recent/date scans. Topic search uses Microsoft server-side KQL across mail fields, and `thread` must look up the conversation and fetch related messages.

Use `$search`/KQL for text relevance such as subjects, people, body terms, project names, and attachment terms. Microsoft returns message `$search` results sorted by send/received date.

Use `outlook search --since 7d -n 80` for normal date-window scans. The CLI automatically uses OData for structured date-only searches.

Use raw OData only as an escape hatch when you need a custom field set or a query the CLI does not expose:

```powershell
outlook --json raw 'messages' --query '$filter=ReceivedDateTime ge 2026-05-04T00:00:00Z&$orderby=ReceivedDateTime desc&$top=80&$select=Id,Subject,From,ReceivedDateTime,IsRead,Importance,HasAttachments,BodyPreview,ConversationId'
```

Avoid Gmail-style text operators like `after:2026-05-04 before:2026-05-06`; they are not reliable Outlook REST KQL here.

Avoid combining `$search` with `$filter` or `$orderby`. Search results are already ordered by date.

Be careful with `$filter` plus `$orderby` on messages. Microsoft can return `InefficientFilter` unless ordered fields are constrained correctly. If that happens, drop `$orderby`, fetch a small page, and sort/filter client-side.

The CLI handles `inbox --focused` client-side because `InferenceClassification eq 'Focused'` can fail server-side when combined with ordering.

## Safety

The exposed CLI commands are read-only. Do not attempt to send, delete, archive, or modify mail/calendar items through this skill.
