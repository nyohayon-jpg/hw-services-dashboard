# Dashboard

A small local website that searches everything downloaded into `dataExports/`.

## Run it

From the project root (Python 3, no packages needed):

```bash
python dashboard/server.py
```

Then open http://localhost:8000. Use `--port 9000` to pick another port. Stop it with Ctrl+C.

## What it does

- **Search** across all services at once. Every word you type must match; results that match in the title come first.
- **Filter** by service with the chips under the search box, and sort by best match, newest or title.
- **Each result shows its service** (badge), date, parent page and properties (for example a task's status, owner and due date).
- **Click a result** to read the full item and open it in the original service.
- **Links keep the view:** the search, filter, sort and open item are stored in the address, e.g.
  `http://localhost:8000/#q=sarah+kim&service=notion`, so a view can be bookmarked or shared.

## How it reads the data

`server.py` scans every folder in `dataExports/` that has a `_manifest.json` and loads each item listed there,
using the common envelope from `localStorageFormats.md` (section 2). It searches the `searchText` field that
`tools/save_export.py` builds. So a new service (Gmail, GitHub, …) shows up automatically once its data is saved
in that format, with no dashboard changes.

- Folder items (Notion): `metadata.json` plus the body from `content.md`.
- File items (Linear and others): the `.json` file; the body shown is `data.description` when present.

The data is re-read on every page load, so refresh the page after a new download.
