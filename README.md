# Third-Party Services Dashboard

This project connects **Claude Code** to several online services through their **official MCP servers**. It then downloads data from each service into local files with a documented format, and searches across all of it in a small local dashboard website.

Services: **Notion** and **GitHub** (required), plus **Linear** (the extra service).
**Gmail** was skipped with the professor's approval: Google's official Gmail MCP server is only available through a developer preview program that does not accept Gmail test accounts.
All accounts are test accounts created for this project. No personal data is stored here.

## Repository layout

| Path | What it is |
|---|---|
| `.mcp.json` | MCP server configuration (no secrets) |
| `.claude/skills/` | Claude Code skills that download each service's data in a repeatable way |
| `dataExports/` | The downloaded data, one sub-folder per service |
| `localStorageFormats.md` | The specification of how downloaded data is stored |
| `tools/save_export.py` | Writes downloaded items to disk following the spec (used by the skills) |
| `dashboard/` | The local dashboard website (see its own README for how to run it) |
| `docs/` | Setup guides for connecting each service (`setup-notion-linear.md`, `setup-github.md`) |
| `presentation/` | PowerPoint, demo video and screenshots |

## How it works

1. **Connect:** each service is added to Claude Code as an MCP server (`.mcp.json`) and authorized with OAuth.
2. **Download:** you ask Claude Code for data, e.g. "download all my Linear issues". The matching skill fetches the data and saves it under `dataExports/<service>/`. Every item gets a common JSON envelope (`service`, `id`, `title`, `date`, `url`, `searchText`, `data`, …), so all services can be searched the same way.
3. **Search:** the dashboard reads `dataExports/` and lets you search one service or all of them at once. Each result shows which service it came from.

To run the dashboard: `python dashboard/server.py`, then open http://localhost:8000 (details in `dashboard/README.md`).

## Team

| Member | Responsibilities |
|---|---|
| Nadav Ohayon | **Notion** and **GitHub** (required services) and **Linear** (extra service; replaced Google Calendar, see `docs/setup-notion-linear.md`): test data, MCP setup, download skills, storage formats, save script and dashboard |

### Adding a service (for a teammate who joins)

Each service is self-contained, so a new one does not change anyone else's work:

1. Add the vendor's **official** MCP server to `.mcp.json` (secrets only through environment variables, as GitHub does).
2. Add a section for it to `localStorageFormats.md` using the common envelope.
3. Add a download skill in `.claude/skills/download-<service>/`, modeled on an existing one.
4. Save downloads with `tools/save_export.py`. The dashboard picks up the new `dataExports/<service>/` folder automatically.
5. Add yourself and your extra service to the table above.

## Security

Passwords, API keys, OAuth tokens and client secrets are **not** in this repository. OAuth credentials live in each developer's OS keychain (managed by Claude Code). See `.gitignore`.
