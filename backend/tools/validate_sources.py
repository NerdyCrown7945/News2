from __future__ import annotations

import json
from pathlib import Path

import feedparser

SOURCES_PATH = Path(__file__).resolve().parents[1] / "sources.json"


def main(auto_disable: bool = False):
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    report = []
    for source in sources:
        if not source.get("enabled", True):
            report.append({"id": source["id"], "ok": False, "reason": "disabled"})
            continue
        try:
            feed = feedparser.parse(source["feed_url"])
            ok = bool(feed.entries) and not feed.bozo
            reason = "ok" if ok else f"parse_error: {getattr(feed, 'bozo_exception', 'empty')}"
        except Exception as exc:
            ok = False
            reason = str(exc)

        if not ok and auto_disable:
            source["enabled"] = False
        report.append({"id": source["id"], "ok": ok, "reason": reason})

    if auto_disable:
        SOURCES_PATH.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")

    success = sum(1 for r in report if r["ok"])
    failed = len(report) - success
    print(json.dumps({"success": success, "failed": failed, "report": report}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-disable", action="store_true")
    args = parser.parse_args()
    main(auto_disable=args.auto_disable)
