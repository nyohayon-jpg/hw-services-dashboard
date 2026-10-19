# Setup: GitHub MCP server

The project uses GitHub's **official** MCP server, hosted by GitHub at `https://api.githubcopilot.com/mcp/`.
It is already listed in `.mcp.json`. That file holds **no secret**: it says `Bearer ${GITHUB_PAT}`, and Claude Code
fills in the token from your environment when it starts.

Use a **test GitHub account** only, never a personal one. The repo is public.

## 1. Create a test account

Sign up at <https://github.com/signup> with the test email.

## 2. Create a personal access token

Signed in as the test account: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.

- **Expiration:** 30 days is enough for the project.
- **Repository access:** All repositories.
- **Permissions** (Repository): Administration, Contents, Issues, Pull requests: **Read and write**. Metadata: Read-only.
  Write access is only needed to create the test data. Downloading uses read tools only, so you can make a read-only token afterwards.

Copy the token. **Never paste it into a file in this repo or into a chat.**

## 3. Put the token in an environment variable

Windows (PowerShell), stored for your user account only, outside the repo:

```powershell
setx GITHUB_PAT "paste-token-here"
```

macOS / Linux: add `export GITHUB_PAT="paste-token-here"` to `~/.zshrc` or `~/.bashrc`.

Then **close and reopen** the Claude app or terminal so it sees the new variable.

## 4. Check

In Claude Code, run `/mcp`: `github` should show as connected. Then ask "who am I on GitHub?". It should call `get_me` and answer with the test account's login.
If it fails, check that the token has not expired and that `GITHUB_PAT` is set (`echo $env:GITHUB_PAT` in PowerShell should print something).

## Downloading

Ask, e.g. "download all my GitHub repos with their issues". The `download-github` skill (in `.claude/skills/`) takes over and saves the data per `localStorageFormats.md`, section 6.

Docs: <https://github.com/github/github-mcp-server>
