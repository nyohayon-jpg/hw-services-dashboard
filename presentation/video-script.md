# Demo video script (under 3 minutes)

The assignment asks the video to show, in this order:
1. logging into at least one of the actual services,
2. downloading that service's data through Claude Code,
3. launching the local website,
4. searching the downloaded data for something that returns results.

This script logs into **Linear**, because three new Linear issues (BLU-14, BLU-15, BLU-16) are waiting to be downloaded, so the download on camera brings in real new data.

**[Brackets]** are actions. Everything else is what you say.

---

## Before you press Record

- Start a **new** Claude Code conversation in the project folder (`/clear`), and check that `/mcp` shows `linear` as connected.
- **Stop** the dashboard if it is running, because you start it on camera.
- Log **out** of Linear in your browser, so you can log in on camera.
- Open a terminal in the project folder.
- Turn on Do Not Disturb and close unrelated tabs.

---

## 1. Intro (0:00–0:15)

**[Show deck slide 1]**

> "Hi, I'm Nadav Ohayon. This project connects Claude Code to online services through their official MCP servers, downloads the data into local files, and searches all of it from one dashboard. I used Notion and GitHub, plus Linear as my extra service."

## 2. Log into Linear (0:15–0:40)

**[Browser: go to linear.app and log in with the test account]**

> "First, I'm logging into Linear with my test account. This is my Project Apollo test project."

**[Open the Project Apollo issue list and point at BLU-14, BLU-15, BLU-16]**

> "These three issues are new. They haven't been downloaded yet."

## 3. Download through Claude Code (0:40–1:30)

**[Switch to Claude Code and type:]** `download my Linear issues from Project Apollo`

> "I ask Claude Code in plain words. It uses my download-linear skill, which is saved in the project's .claude folder. The skill only reads from Linear, and it saves every issue with one script, so the files always follow the format in localStorageFormats.md."

**[Wait for it to finish. Cut the waiting time when you edit.]**

> "It saved twelve issues, including the three new ones."

**[Open `dataExports/linear/issues/` and click the BLU-14 file]**

> "Each issue is one JSON file in the dataExports/linear folder, with all its metadata: status, priority, labels, dates and comments."

## 4. Launch the dashboard (1:30–1:45)

**[Terminal: type]** `python dashboard/server.py` **[then open http://localhost:8000]**

> "Now I start the local dashboard. It reads the downloaded files. It doesn't connect to the services."

## 5. Search (1:45–2:40)

**[Point at the item count at the top]**

> "It has items from three services: Notion, GitHub and Linear."

**[Type `Sarah Kim` in the search box]**

> "Let's search for Sarah Kim, the client contact in my test project. The results come from all three services, and each one is tagged with its service."

**[Click the `linear` chip, then `All services`]**

> "I can filter to one service, or search all of them at once."

**[Click "Alert Sarah Kim when the nightly import fails" (BLU-16)]**

> "And here's one of the Linear issues I just downloaded, with its full details and a link back to Linear."

## 6. Closing (2:40–2:55)

**[Show deck slide 8, or stay on the dashboard]**

> "No passwords or tokens are stored in the repository, and only test accounts were used. Thank you."

---

## If something goes wrong

- **Linear login or download fails:** log into GitHub instead and say "download my GitHub issues". The rest of the script stays the same.
- **You stumble:** pause for two seconds, say the sentence again, and cut the mistake when editing.
- **Over 3 minutes:** shorten the waiting part of the download. It's the easiest part to cut.
