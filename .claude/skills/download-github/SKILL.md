---
name: download-github
description: Download GitHub repositories, issues and pull requests (with READMEs and comments) through the official GitHub MCP server and store them locally in dataExports/github/ following localStorageFormats.md. Use whenever the user asks to download, export, save, back up or sync GitHub repos, issues, pull requests or code projects.
---

# Download GitHub data

Store items **exactly** as specified in `localStorageFormats.md` (sections 1–3 and 6). Never hand-write files into `dataExports/`: always build envelopes and save them with `tools/save_export.py`.

## Rules

- **Read-only.** Use only GitHub tools that get, list or search: e.g. `get_me`, `search_repositories`, `get_file_contents`, `list_issues`, `search_issues`, `issue_read`, `list_pull_requests`, `pull_request_read`. The tools may appear with a prefix, e.g. `mcp__github__search_repositories`, and names can differ slightly between server versions; pick the read tool that matches. Never create, update, merge, comment on or delete anything in this workflow.
- Never invent values. A field GitHub did not return is `null` (or `[]`).
- Never write the personal access token or any other credential anywhere in the repo. It lives only in the `GITHUB_PAT` environment variable.

## Steps

1. **Check the connection.** The `github` MCP tools must be available. If they are not, stop and tell the user to follow `docs/setup-github.md`: create a token, set `GITHUB_PAT`, restart Claude Code, then check `/mcp`.

2. **Work out the request.** Determine:
   - which account: default is the signed-in user (`get_me`),
   - which repositories: default is **all repositories owned by that user**,
   - whether to include issues and pull requests: default is **yes, every state** (open and closed),
   - any text filter (e.g. "anything mentioning Sarah Kim").

   Say the defaults you used. Write the user's request as one short sentence. This is the `--query` used in step 6.

3. **List items.**
   - **Repositories:** `search_repositories` with `user:<login>` (plus any text filter). Follow pagination until no more results.
   - **Issues and pull requests:** for each repository, list issues (state `all`) and pull requests (state `all`), following pagination. For a text filter, `search_issues` with `repo:<owner>/<name> <text>` is fine; also match the text yourself against title, body, labels and comments.

   Remove duplicates (GitHub may list a pull request as an issue too: keep it once, as `pull_request`). If more than 50 items match, ask the user before downloading all of them.

4. **Fill in details.**
   - For each repository, read its README with `get_file_contents` (path `README.md`, default branch). If there is none, `readme` is `null`.
   - For each issue or pull request, get the full item if the list result lacks the body, labels, assignees or merge state, and get its comments (e.g. `issue_read` with the comments method, or the comments tool your server offers).

5. **Build one envelope per item** (spec section 2 + 6).

   Repository:

   ```json
   {
     "service": "github",
     "id": "<node_id, or html_url if missing>",
     "title": "<owner>/<repo>",
     "date": "<updated_at>",
     "url": "<https://github.com/owner/repo>",
     "source": { "mcpServer": "github", "tools": ["search_repositories", "get_file_contents"], "query": "<the request>" },
     "data": {
       "kind": "repo",
       "fullName": "owner/repo", "owner": "owner", "name": "repo",
       "description": null, "visibility": "public", "defaultBranch": "main",
       "language": null, "topics": [], "stars": 0, "forks": 0, "openIssues": 0,
       "license": null, "homepage": null,
       "readme": "<README Markdown or null>",
       "createdAt": "...", "updatedAt": "...", "pushedAt": "...",
       "raw": { "...the unmodified repository object..." }
     }
   }
   ```

   Issue or pull request:

   ```json
   {
     "service": "github",
     "id": "<node_id, or html_url if missing>",
     "title": "<issue title or (untitled)>",
     "date": "<updated_at>",
     "url": "<https://github.com/owner/repo/issues/7>",
     "source": { "mcpServer": "github", "tools": ["list_issues", "issue_read"], "query": "<the request>" },
     "data": {
       "kind": "issue",
       "repo": "owner/repo", "number": 7,
       "body": null, "state": "open", "stateReason": null,
       "author": "login", "assignees": [], "labels": [], "milestone": null,
       "merged": null, "draft": null,
       "comments": [ { "id": "...", "author": "login", "body": "...", "createdAt": "..." } ],
       "createdAt": "...", "updatedAt": "...", "closedAt": null,
       "raw": { "...the unmodified issue or pull request object..." }
     }
   }
   ```

   - Use the actual tool names you called in `source.tools`.
   - `merged` and `draft` are booleans for pull requests and `null` for issues.
   - Sort `comments` oldest first.
   - Leave out `schemaVersion`, `exportedAt` and `searchText`. The script adds them.

6. **Save.** Write all envelopes as a JSON list to `.tmp/github-batch.json`, then run from the project root:

   ```bash
   python tools/save_export.py --input .tmp/github-batch.json --query "<the request>"
   ```

   Delete `.tmp/github-batch.json` afterwards.

7. **Verify and report.** Read `dataExports/github/_manifest.json` and confirm the latest entry in `runs` lists every item id. Spot-check one repository file to make sure `readme` was filled in when the repo has a README. Then tell the user how many repositories and how many issues or pull requests were saved, and the file names.

   If fewer than 5 items matched, say so and suggest a broader request.
