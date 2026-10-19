---
name: download-linear
description: Download Linear issues (with comments) through the official Linear MCP server and store them locally in dataExports/linear/ following localStorageFormats.md. Use whenever the user asks to download, export, save, back up or sync Linear issues, tasks, tickets or projects.
---

# Download Linear issues

Store issues **exactly** as specified in `localStorageFormats.md` (sections 1–3 and 5). Never hand-write files into `dataExports/`: always build envelopes and save them with `tools/save_export.py`.

## Rules

- **Read-only.** Use only the Linear tools that list or get things: issues, comments, teams, projects, labels, users. The tools may appear with a prefix, e.g. `mcp__linear__list_issues`. Never create, update or delete anything in this workflow.
- Never invent values. A field Linear did not return is `null` (or `[]`).
- Never write OAuth tokens, API keys or other credentials anywhere in the repo.

## Steps

1. **Check the connection.** The `linear` MCP tools must be available. If they are not, stop and tell the user to run `/mcp` and authenticate `linear`.

2. **Work out the request.** Determine:
   - any text filter (e.g. "issues mentioning Joe Smith"),
   - which team or project to include,
   - which states to include. The default is **all issues in all teams, any state**. Say so.

   Write the user's request as one short sentence. This is the `--query` used in step 6.

3. **List issues.** Call the list-issues tool with the filters it supports. Follow pagination (cursor / `after`) until every matching issue is retrieved. If the tool can't filter by text, match the text yourself against title, description, labels, assignee and comments.

4. **Fill in details.** For each issue, call the get-issue tool if the list result lacks the description, labels, project or other fields. Call the list-comments tool to get the issue's comments.

5. **Build one envelope per issue** (spec section 2 + 5):

   ```json
   {
     "service": "linear",
     "id": "<issue UUID>",
     "title": "<issue title or (untitled)>",
     "date": "<updatedAt>",
     "url": "<https://linear.app/... issue URL or null>",
     "source": { "mcpServer": "linear", "tools": ["list_issues", "get_issue", "list_comments"], "query": "<the request>" },
     "data": {
       "identifier": "HW-12",
       "description": null,
       "state": null, "priority": null, "priorityLabel": null,
       "team": { "id": null, "key": null, "name": null },
       "project": null,
       "assignee": null, "creator": null,
       "labels": [],
       "dueDate": null, "estimate": null, "cycle": null, "parentId": null,
       "comments": [ { "id": "...", "author": "...", "body": "...", "createdAt": "..." } ],
       "createdAt": "...", "updatedAt": "...", "completedAt": null,
       "raw": { "...the unmodified issue object from the tool..." }
     }
   }
   ```

   - Use the actual tool names you called in `source.tools`.
   - Sort `comments` oldest first.
   - Leave out `schemaVersion`, `exportedAt` and `searchText`. The script adds them.

6. **Save.** Write all envelopes as a JSON list to `.tmp/linear-batch.json`, then run from the project root:

   ```bash
   python tools/save_export.py --input .tmp/linear-batch.json --query "<the request>"
   ```

   Delete `.tmp/linear-batch.json` afterwards.

7. **Verify and report.** Read `dataExports/linear/_manifest.json` and confirm the latest entry in `runs` lists every issue id. Then tell the user how many issues were saved and the file names.

   If fewer than 5 issues matched, say so and suggest a broader filter.
