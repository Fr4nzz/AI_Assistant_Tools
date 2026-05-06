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
