---
name: download-notion
description: Download Notion pages (and database rows) through the official Notion MCP server and store them locally in dataExports/notion/ following localStorageFormats.md. Use whenever the user asks to download, export, save, back up or sync Notion pages, notes or databases.
---

# Download Notion pages

Store pages **exactly** as specified in `localStorageFormats.md` (sections 1–3 and 4). Never hand-write files into `dataExports/`: always build envelopes and save them with `tools/save_export.py`.

## Rules

- **Read-only.** Use only `notion-search` and `notion-fetch`. The tools may appear with a prefix, e.g. `mcp__notion__notion-search`. Never create, update, move or comment on pages in this workflow.
- Never invent values. A field Notion did not return is `null` (or `{}` / `[]`).
- Never write OAuth tokens or other credentials anywhere in the repo.

## Steps

1. **Check the connection.** The `notion` MCP tools must be available. If they are not, stop and tell the user to run `/mcp` and authenticate `notion`.

2. **Work out the request.** Is it a text search ("pages that mention Apollo"), a specific page or database, or "everything"? Write the user's request as one short sentence. This is the `--query` used in step 6.

3. **Find pages.**
   - **Text search:** call `notion-search` with the user's text.
   - **"Everything":** search with broad queries until no new pages appear.
   - **A database:** fetch the database and collect its rows.
   - **A page "and everything under it":** fetch the page and follow every `<page url=...>` sub-page and every `<database ...>` block, recursively. Collect the database rows too. Prefer this over search for newly created pages, because Notion's search index can lag a few minutes behind.

   Remove duplicate page ids. If more than 25 pages match, ask the user before downloading all of them.

4. **Fetch every page** with `notion-fetch` (by id or URL). From each result, take:
   - the page body as Markdown. This becomes `content`.
   - title, URL, parent, icon, created/last-edited time and user, archived flag, properties (for database rows), and links to child pages.

5. **Build one envelope per page** (spec section 2 + 4):

   ```json
   {
     "service": "notion",
     "id": "<page UUID with dashes>",
     "title": "<page title or (untitled)>",
     "date": "<lastEditedTime>",
     "url": "<https://www.notion.so/... page URL>",
     "source": { "mcpServer": "notion", "tools": ["notion-search", "notion-fetch"], "query": "<the request>" },
     "content": "<the page body as Notion-flavored Markdown>",
     "data": {
       "objectType": "page",
       "parent": { "type": "workspace|page|database", "id": null, "title": null },
       "icon": null,
       "createdTime": "...", "lastEditedTime": "...",
       "createdBy": null, "lastEditedBy": null,
       "archived": false,
       "properties": { "Status": "In progress", "Tags": ["design", "q4"], "Due": "2026-10-30" },
       "childPages": [ { "id": "...", "title": "..." } ],
       "raw": { "...the notion-fetch result without the Markdown body..." }
     }
   }
   ```

   - `properties` holds **plain values**: text as a string, select as its name, multi-select and people as lists of names, dates as ISO strings, checkboxes as booleans. Use `{}` for regular pages.
   - If `notion-fetch` does not return created/edited times or authors, set them to `null`. Then use the best date available for `date`, in this order: last edited, created, today. Note the choice in `data.dateSource`.
   - `content` is a top-level field. The script moves it to `content.md`. Leave out `schemaVersion`, `exportedAt` and `searchText`.

6. **Save.** Write all envelopes as a JSON list to `.tmp/notion-batch.json`, then run from the project root:

   ```bash
   python tools/save_export.py --input .tmp/notion-batch.json --query "<the request>"
   ```

   Delete `.tmp/notion-batch.json` afterwards.

7. **Verify and report.** Read `dataExports/notion/_manifest.json` and confirm the latest entry in `runs` lists every page id. Spot-check one `content.md` to make sure it isn't empty unless the page really is. Then tell the user how many pages were saved and the folder names.

   If fewer than 5 pages matched, say so and suggest a broader search.
