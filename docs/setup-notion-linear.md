# Setup: Notion and Linear MCP servers

Both servers are the **official** ones run by the vendors and are listed in `.mcp.json`. Use the **test accounts** only (`nadavohayon29@gmail.com`), never personal ones.

## Notion (official hosted server)

1. Create a Notion account and workspace with the test email.
2. From the project folder, run `claude mcp login notion` (or `/mcp` → `notion` → **Authenticate** inside Claude Code).
3. In the browser, sign in with the test account and select the pages Claude may access.
4. Check: ask Claude to "search my Notion for anything". It should call `notion-search`.

Endpoint: `https://mcp.notion.com/mcp` (Streamable HTTP, OAuth). Docs: <https://developers.notion.com/docs/get-started-with-mcp>

## Linear (official hosted server)

1. Create a free Linear workspace at <https://linear.app> with the test email.
2. From the project folder, run `claude mcp login linear` (or `/mcp` → `linear` → **Authenticate**).
3. In the browser, sign in to the test workspace and approve access.
4. Check: ask Claude to "list my Linear issues".

Endpoint: `https://mcp.linear.app/mcp` (Streamable HTTP, OAuth with dynamic client registration, so no client ID or secret needed). Docs: <https://linear.app/docs/mcp>

## Why not Google Calendar?

Google Calendar was the original extra service. Google's official Calendar MCP server (`https://calendarmcp.googleapis.com/mcp/v1`) only works for Cloud projects enrolled in the **Google Workspace Developer Preview Program**. That program does not accept Gmail addresses and takes days to approve, so it can't be used with a test Gmail account. Google's Gmail MCP server is in the same program.

## Downloading

After both are connected, just ask, e.g. "download all my Linear issues" or "download every Notion page that mentions Apollo".
The `download-linear` and `download-notion` skills (in `.claude/skills/`) take over and save the data per `localStorageFormats.md`.
