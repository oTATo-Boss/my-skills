#!/usr/bin/env python3
"""Small real example: normalize supplied notes, then write a Markdown report."""
import json
from pathlib import Path
import sys

job = json.load(sys.stdin)
if sys.argv[1] == "prepare":
    notes = [str(note).strip() for note in job["inputs"]["notes"] if str(note).strip()]
    if not notes:
        raise SystemExit("No nonempty notes")
    print(json.dumps({"title": job["inputs"]["title"].strip(), "notes": notes}, ensure_ascii=False))
else:
    material = job["inputs"]["material"]
    text = "# " + material["title"] + "\n\n" + "\n".join("- " + n for n in material["notes"]) + "\n"
    path = Path(job["output_dir"]) / "report.md"
    path.write_text(text)
    print(json.dumps({"report": "report.md", "note_count": len(material["notes"])}))
