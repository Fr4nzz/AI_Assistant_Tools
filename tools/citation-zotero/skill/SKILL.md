---
name: citation-zotero
description: Use when the user wants Zotero-backed citations, bibliographies, citation keys, BibTeX/CSL export, or safe citation preparation for docx, ODT, Google Docs, or Markdown manuscripts.
triggers:
  - zotero
  - citation
  - bibliography
  - bibtex
  - docx citations
  - word citations
argument-hint: "<document path or citation task>"
metadata:
  optional_bins: ["pandoc"]
---

# Citation Zotero

Use this skill to connect literature metadata with manuscript citation work.
Do not promise fully automatic live Zotero fields in arbitrary Word or Google
Docs files. Prepare reliable citation workflows first; use active-citation
conversion only through verified Zotero integrations.

## Capability Levels

1. Safe library work: pyzotero/Zotero API can create, update, search,
   tag, and export Zotero items. This is good for building a library from DOIs.
2. Citation placeholders: insert Pandoc-style keys such as `[@smith2020]` only
   after validating the key against Zotero, Better BibTeX, or an exported
   bibliography.
3. Static document citations: Pandoc can generate `.docx` files with formatted
   citations and bibliographies from Markdown plus CSL/BibTeX/CSL JSON. These
   are reliable but not live Zotero fields.
4. User-finalized active citations: ODF/DOCX Scan for Zotero can convert
   markers into active Zotero citations when the user has Zotero, the relevant
   word-processor plugin, and the scan plugin installed.
5. Google Docs live Zotero citations: no stable public Google Docs API path is
   assumed. Prepare sources/markers and let Zotero Connector handle final
   insertion unless the user explicitly approves UI automation.

## Recommended Workflow

For manuscript drafting:

1. Use `literature-search` to find candidate papers.
2. Use `paper-search metadata-dois` to enrich DOI metadata.
3. Add confirmed papers to Zotero or export BibTeX/CSL JSON.
4. Draft in Markdown with citation keys, or work in `.docx` with an explicitly
   configured Zotero route.
5. Render/check the `.docx` visually before delivery.

## Automatic `.docx` Citation Policy

Before editing a `.docx`, inspect the document and ask what output is desired:

- live Zotero fields
- static formatted citations and bibliography
- comments/placeholders for manual Zotero insertion

If live fields are requested, first verify the installed automation path on a
throwaway document. If verification fails, fall back to static citations or
placeholders and explain the limitation.

Never claim active Zotero fields were created unless Word/LibreOffice/Zotero or
the official plugin workflow was used and verified.

## Zotero Setup Notes

Useful setup options:

- Zotero desktop for the library and Word/LibreOffice plugins.
- Better BibTeX for stable citation keys and auto-exported `.bib` files.
- pyzotero plus a Zotero web API key for library management.
- A maintained Zotero MCP/automation bridge only after reviewing its security
  and document-writing behavior.

Keep citation keys stable. Never invent a citation for a claim; add a TODO or
comment when the source is missing.
