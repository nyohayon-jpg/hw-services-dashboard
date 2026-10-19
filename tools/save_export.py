"""Save a batch of downloaded service items into dataExports/ per localStorageFormats.md.

Usage:
    python tools/save_export.py --input .tmp/notion-batch.json --query "pages mentioning Apollo"

The input file holds one envelope object or a list of them (see localStorageFormats.md, section 2).
A Notion envelope may carry a top-level "content" string; it is written to content.md.
Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
REQUIRED = ("service", "id", "title", "date", "data")
# Services stored as one folder per item (metadata.json + content.md); everything else is one file per item.
FOLDER_SERVICES = {"notion": "pages"}
FILE_SERVICES = {"linear": "issues", "github": "issues"}
# GitHub keeps repositories apart from issues and pull requests (data.kind decides).
GITHUB_REPO_FOLDER = "repos"


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text, max_len=40):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:max_len].strip("-")
    return slug or "untitled"


def hash8(item_id):
    return hashlib.sha1(item_id.encode("utf-8")).hexdigest()[:8]


def identifier_prefix(record):
    """Linear issue key such as 'HW-12' (from data.identifier); empty if absent."""
    ident = re.sub(r"[^A-Za-z0-9-]+", "", str(record["data"].get("identifier") or ""))
    return f"{ident}_" if ident else ""


def github_prefix(record):
    """'<repo>-<number>_' for a GitHub issue or pull request (from data.repo and data.number); empty if absent."""
    data = record["data"]
    repo = slugify(str(data.get("repo") or "").split("/")[-1], max_len=40) if data.get("repo") else ""
    number = re.sub(r"[^0-9]+", "", str(data.get("number") or ""))
    return f"{repo}-{number}_" if repo and number else ""


def collect_strings(value, out):
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            collect_strings(v, out)
    elif isinstance(value, list):
        for v in value:
            collect_strings(v, out)


def build_search_text(record, content):
    parts = [record["title"]]
    data = {k: v for k, v in record["data"].items() if k != "raw"}
    collect_strings(data, parts)
    if content:
        parts.append(content)
    return re.sub(r"\s+", " ", " ".join(parts)).strip().lower()


def relative_path(record):
    service = record["service"]
    key = f"{slugify(record['title'])}_{hash8(record['id'])}"
    if service in FOLDER_SERVICES:
        return f"{FOLDER_SERVICES[service]}/{key}"
    sub = FILE_SERVICES.get(service, "items")
    if service == "linear":
        key = identifier_prefix(record) + key
    elif service == "github":
        if record["data"].get("kind") == "repo":
            sub = GITHUB_REPO_FOLDER
        else:
            key = github_prefix(record) + key
    return f"{sub}/{key}.json"


def load_manifest(service_dir, service):
    path = service_dir / "_manifest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"service": service, "schemaVersion": SCHEMA_VERSION, "items": {}, "runs": []}


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def remove_path(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def save(records, root, query):
    exported_at = now_utc()
    by_service = {}
    for record in records:
        missing = [k for k in REQUIRED if not record.get(k)]
        if missing:
            sys.exit(f"Record {record.get('id', '?')!r} is missing required fields: {', '.join(missing)}")
        by_service.setdefault(record["service"], []).append(record)

    summary = []
    for service, items in by_service.items():
        service_dir = root / "dataExports" / service
        manifest = load_manifest(service_dir, service)
        ids = []
        for record in items:
            record = dict(record)
            content = record.pop("content", None)
            record["schemaVersion"] = SCHEMA_VERSION
            record["exportedAt"] = exported_at
            record.setdefault("url", None)
            record.setdefault("source", {})
            record["searchText"] = build_search_text(record, content)

            rel = relative_path(record)
            previous = manifest["items"].get(record["id"])
            if previous and previous["path"] != rel:
                remove_path(service_dir / previous["path"])

            if service in FOLDER_SERVICES:
                folder = service_dir / rel
                record["data"]["contentFile"] = "content.md"
                record["data"]["contentLength"] = len(content or "")
                write_json(folder / "metadata.json", ordered(record))
                (folder / "content.md").write_text(content or "", encoding="utf-8")
            else:
                write_json(service_dir / rel, ordered(record))

            manifest["items"][record["id"]] = {
                "path": rel,
                "title": record["title"],
                "date": record["date"],
                "firstExportedAt": previous["firstExportedAt"] if previous else exported_at,
                "lastExportedAt": exported_at,
            }
            ids.append(record["id"])
            summary.append(f"  {service}/{rel}")

        manifest["runs"].append({"at": exported_at, "query": query, "count": len(ids), "ids": ids})
        write_json(service_dir / "_manifest.json", manifest)

    print(f"Saved {len(records)} item(s) at {exported_at}:")
    print("\n".join(summary))


def ordered(record):
    keys = ["schemaVersion", "service", "id", "title", "date", "url", "searchText", "exportedAt", "source", "data"]
    out = {k: record[k] for k in keys if k in record}
    out.update({k: v for k, v in record.items() if k not in out})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="JSON file with one envelope or a list of envelopes")
    parser.add_argument("--query", default="", help="the user's request, recorded in the manifest run log")
    parser.add_argument("--root", default=".", help="project root containing dataExports/ (default: current dir)")
    args = parser.parse_args()

    records = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if isinstance(records, dict):
        records = [records]
    root = os.path.abspath(args.root)
    if os.name == "nt" and not root.startswith("\\\\?\\"):
        root = "\\\\?\\" + root  # lift Windows' 260-character path limit
    save(records, Path(root), args.query)


if __name__ == "__main__":
    main()
