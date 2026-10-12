#!/usr/bin/env python3
"""Package reviewed social content without changing source bytes. Offline."""

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def sha256_stream(source):
    digest = hashlib.sha256()
    for block in iter(lambda: source.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def file_sha256(path):
    with path.open("rb") as source:
        return sha256_stream(source)


def safe_title(title):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", title).strip(" .")
    while len(name.encode("utf-8")) > 160:
        name = name[:-1]
    name = name.strip(" .")
    if not name:
        raise ValueError("Title produces an empty archive name")
    return name


def package_post(args):
    if not args.title.strip():
        raise ValueError("Title must contain non-whitespace text")
    inputs = [(f"media-{i:02d}{p.suffix}", p)
              for i, p in enumerate(args.media, 1)]
    if args.cover:
        inputs.append((f"cover{args.cover.suffix}", args.cover))
    inputs.append((f"copy{args.copy_path.suffix}", args.copy_path))
    records = []
    for entry, path in inputs:
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty input: {path}")
        records.append({"entry": entry, "source": str(path.resolve()),
                        "bytes": path.stat().st_size,
                        "sha256": file_sha256(path)})

    now = (datetime.now(ZoneInfo(args.timezone)) if args.timezone
           else datetime.now().astimezone())
    stamp = args.timestamp or now.strftime("%Y%m%d_%H%M")
    if not re.fullmatch(r"\d{8}_\d{4}", stamp):
        raise ValueError("Timestamp must be YYYYMMDD_HHMM")
    datetime.strptime(stamp, "%Y%m%d_%H%M")
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"{safe_title(args.title)}_{stamp}.zip"
    report = target.with_suffix(".qa.json")
    if target.exists() or report.exists():
        raise ValueError("Output exists; choose a new timestamp or directory")

    created = []
    try:
        with tempfile.TemporaryDirectory(dir=args.out) as scratch:
            pending = Path(scratch) / "package.zip"
            with zipfile.ZipFile(pending, "w", zipfile.ZIP_DEFLATED) as archive:
                for entry, path in inputs:
                    archive.write(path, entry)
            with zipfile.ZipFile(pending) as archive:
                expected = [record["entry"] for record in records]
                if archive.testzip() is not None or archive.namelist() != expected:
                    raise ValueError("Archive integrity or entry order failed")
                for record in records:
                    with archive.open(record["entry"]) as content:
                        if sha256_stream(content) != record["sha256"]:
                            raise ValueError("Source changed during packaging")

            summary = {
                "archive": target.name, "title": args.title,
                "timestamp": stamp,
                "timezone": args.timezone or str(now.tzinfo),
                "files": records, "zip_sha256": file_sha256(pending),
                "zip_integrity_passed": True, "source_bytes_preserved": True,
                "media_decoding": "NOT_CHECKED_BY_SCRIPT",
                "visual_review": "NOT_CHECKED_BY_SCRIPT",
                "audio_listening": "NOT_CHECKED_BY_SCRIPT",
                "copy_and_platform_requirements": "NOT_CHECKED_BY_SCRIPT",
            }
            with target.open("xb") as output:
                created.append(target)
                with pending.open("rb") as source:
                    shutil.copyfileobj(source, output)
            with report.open("x", encoding="utf-8") as output:
                created.append(report)
                output.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--media", action="append", required=True, type=Path,
                        help="Repeat in the intended media order")
    parser.add_argument("--cover", type=Path, help="Optional separate cover")
    parser.add_argument("--copy", dest="copy_path", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--timezone", help="Optional IANA time zone")
    parser.add_argument("--timestamp", help="Local YYYYMMDD_HHMM")
    args = parser.parse_args()
    try:
        result = package_post(args)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
