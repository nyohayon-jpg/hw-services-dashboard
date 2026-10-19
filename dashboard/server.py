"""Local search dashboard for dataExports/ (see localStorageFormats.md).

Usage:
    python dashboard/server.py            # then open http://localhost:8000
    python dashboard/server.py --port 9000

Reads every service folder under dataExports/ through its _manifest.json, so any service that
follows the common envelope (section 2) shows up automatically. Standard library only.
"""

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "dataExports"
STATIC = Path(__file__).resolve().parent / "static"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_record(service_dir, rel_path):
    """Return (envelope, content) for a manifest path: a folder (metadata.json + content file) or a .json file."""
    target = service_dir / rel_path
    if target.is_dir():
        record = read_json(target / "metadata.json")
        content_file = target / record.get("data", {}).get("contentFile", "content.md")
        content = content_file.read_text(encoding="utf-8") if content_file.exists() else ""
        return record, content
    record = read_json(target)
    data = record.get("data", {})
    # Body text per service: GitHub issue body or README, Linear description.
    return record, data.get("body") or data.get("readme") or data.get("description") or ""


# Fields shown as tags for file-based services (Linear, GitHub), which have no Notion-style properties.
SUMMARY_FIELDS = {
    "kind": "Kind", "repo": "Repo", "number": "Number", "identifier": "Key", "state": "State",
    "priorityLabel": "Priority", "assignee": "Assignee", "assignees": "Assignees", "author": "Author",
    "labels": "Labels", "dueDate": "Due", "language": "Language", "topics": "Topics", "visibility": "Visibility",
}


def plain_value(value):
    """Reduce an object to its readable name (e.g. an assignee object to its name)."""
    if isinstance(value, dict):
        return value.get("name") or value.get("key") or value.get("login") or value.get("title")
    if isinstance(value, list):
        return [v for v in (plain_value(x) for x in value) if v]
    return value


def summary_properties(data):
    if data.get("properties"):
        return data["properties"]
    props = {}
    for key, label in SUMMARY_FIELDS.items():
        value = plain_value(data.get(key))
        if value not in (None, "", []):
            props[label] = value
    return props


def parent_title(data):
    parent = data.get("parent")
    if isinstance(parent, dict) and parent.get("title"):
        return parent["title"]
    project = data.get("project")
    if isinstance(project, dict) and project.get("name"):
        return project["name"]
    team = data.get("team")
    if isinstance(team, dict) and team.get("name"):
        return team["name"]
    return data.get("repo")


def load_items():
    items, services = [], []
    if not EXPORTS.exists():
        return {"services": services, "items": items}
    for service_dir in sorted(p for p in EXPORTS.iterdir() if p.is_dir()):
        manifest_path = service_dir / "_manifest.json"
        if not manifest_path.exists():
            continue
        manifest = read_json(manifest_path)
        runs = manifest.get("runs", [])
        count = 0
        for item_id, entry in manifest.get("items", {}).items():
            try:
                record, content = load_record(service_dir, entry["path"])
            except (OSError, ValueError, KeyError):
                continue  # listed in the manifest but missing or unreadable on disk
            data = record.get("data", {})
            items.append({
                "service": record.get("service", service_dir.name),
                "id": record.get("id", item_id),
                "title": record.get("title") or "(untitled)",
                "date": record.get("date"),
                "url": record.get("url"),
                "searchText": record.get("searchText", ""),
                "exportedAt": record.get("exportedAt"),
                "path": f"{service_dir.name}/{entry['path']}",
                "icon": data.get("icon") if isinstance(data.get("icon"), str) else None,
                "properties": summary_properties(data),
                "parent": parent_title(data),
                "content": content,
            })
            count += 1
        services.append({
            "name": service_dir.name,
            "count": count,
            "lastExportedAt": runs[-1]["at"] if runs else None,
        })
    return {"services": services, "items": items}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/items":
            body = json.dumps(load_items(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--exports", help="folder to read instead of dataExports/ (for testing)")
    args = parser.parse_args()
    if args.exports:
        global EXPORTS
        EXPORTS = Path(args.exports).resolve()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Dashboard running at http://localhost:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
