"""Read-only discovery of x-girl reference facets; final choices require image inspection."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FACETS = ("styling", "scene", "background", "expression", "pose", "composition", "lighting", "finish")
EVIDENCE = {"observed", "inferred", "not_visible"}
SCENE_CLASSES = {"室内", "室外", "车内", "场景不明"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_visual(record, image_hash=None):
    errors = []
    ref = record.get("id", "unknown")
    visual = record.get("visual")
    if not isinstance(visual, dict) or visual.get("schema_version") != 1:
        return [f"Missing visual index: {ref}"]
    facets = visual.get("facets")
    if not isinstance(facets, dict) or set(facets) != set(FACETS):
        return [f"Expected eight visual facets: {ref}"]
    for name, facet in facets.items():
        if not isinstance(facet, dict):
            errors.append(f"Invalid visual facet: {ref}/{name}")
            continue
        tags = facet.get("tags")
        evidence = facet.get("evidence")
        if (not isinstance(tags, list) or not all(nonempty(tag) for tag in tags)
                or len(set(tags)) != len(tags)):
            errors.append(f"Invalid visual tags: {ref}/{name}")
        if evidence not in EVIDENCE or not nonempty(facet.get("observation")):
            errors.append(f"Missing visual evidence: {ref}/{name}")
        if evidence == "not_visible" and tags:
            errors.append(f"Unseen facet cannot assert tags: {ref}/{name}")
        if evidence in {"observed", "inferred"} and not tags:
            errors.append(f"Visible facet needs searchable tags: {ref}/{name}")
    if not nonempty(visual.get("transferable_mechanism")):
        errors.append(f"Missing transferable mechanism: {ref}")
    limits = visual.get("limitations")
    if not isinstance(limits, list) or not all(nonempty(item) for item in limits):
        errors.append(f"Invalid visual limitations: {ref}")
    review = visual.get("review", {})
    if not isinstance(review, dict):
        return errors + [f"Missing visual review: {ref}"]
    try:
        reviewed = date.fromisoformat(review.get("date", ""))
        if reviewed > date.today():
            errors.append(f"Future visual review: {ref}")
    except (TypeError, ValueError):
        errors.append(f"Invalid visual review date: {ref}")
    digest = review.get("image_sha256", "")
    if review.get("method") != "visual-inspection" or (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
        errors.append(f"Invalid visual review provenance: {ref}")
    if image_hash is not None and digest != image_hash:
        errors.append(f"Visual review image changed: {ref}")
    return errors


def facet_text(facet):
    if facet.get("evidence") == "not_visible":
        return ""
    return " ".join([*facet.get("tags", []), facet.get("observation", "")]).casefold()


def search(records, query="", filters=None, exclude=(), limit=12, mode=None):
    filters = filters or {}
    if set(filters) - set(FACETS):
        raise ValueError("Unknown facet; choose " + ", ".join(FACETS))
    if not all(nonempty(value) for value in filters.values()):
        raise ValueError("Facet terms must be nonempty")
    terms = [term.casefold() for term in re.split(r"[\s,，、;；]+", query.strip()) if term]
    if not terms and not filters:
        raise ValueError("State a visual intent with --query or --facet; there is no default scene")
    if limit < 1:
        raise ValueError("Limit must be positive")
    if mode not in (None, "露点", "擦边"):
        raise ValueError("Unknown mode; choose 露点 or 擦边")
    excluded = set(exclude)
    matches = []
    for record in records:
        if record["id"] in excluded:
            continue
        if mode and record.get("mode") != mode:
            continue
        errors = validate_visual(record)
        if errors:
            raise ValueError(errors[0])
        facets = record["visual"]["facets"]
        texts = {name: facet_text(facet) for name, facet in facets.items()}
        if not all((value in facets[name]["tags"] if name == "scene" and value in SCENE_CLASSES
                    else value.casefold() in texts[name]) for name, value in filters.items()):
            continue
        combined = " ".join(texts.values())
        if not all(term in combined for term in terms):
            continue
        hit_facets = {name: [term for term in terms if term in text]
                      for name, text in texts.items()}
        hit_facets = {name: values for name, values in hit_facets.items() if values}
        score = sum(len(values) for values in hit_facets.values()) + len(filters)
        matches.append((score, record))
    matches.sort(key=lambda item: (-item[0], int(item[1]["id"][1:])))
    return [record for _, record in matches[:limit]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="All keyword terms must have visual support")
    parser.add_argument("--facet", action="append", default=[], metavar="NAME=TERM")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude a reference ID")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--mode", choices=["露点", "擦边"], help="Only return references recorded in this mode")
    parser.add_argument("--show", nargs="+", metavar="P_ID", help="Inspect full metadata for named references")
    parser.add_argument("--vocabulary", choices=FACETS, help="List actual tags in one facet")
    args = parser.parse_args()
    records = json.loads((ROOT / "assets/references/manifest.json").read_text())
    try:
        if args.show:
            by_id = {row["id"]: row for row in records}
            if set(args.show) - set(by_id):
                raise ValueError("Unknown reference ID")
            result = [by_id[ref] for ref in args.show]
        elif args.vocabulary:
            counter = Counter(tag for row in records
                              for tag in row["visual"]["facets"][args.vocabulary]["tags"])
            result = dict(counter.most_common())
        else:
            filters = {}
            for value in args.facet:
                name, separator, term = value.partition("=")
                if not separator or name in filters:
                    raise ValueError("Use one NAME=TERM per facet")
                filters[name] = term
            found = search(records, args.query, filters, args.exclude, args.limit, args.mode)
            result = {"count": len(found), "selection": "candidates-only; open originals before choosing",
                      "candidates": [{"id": row["id"], "title": row["title"], "mode": row.get("mode"), "file": row["file"],
                                      "facets": row["visual"]["facets"],
                                      "transferable_mechanism": row["visual"]["transferable_mechanism"],
                                      "limitations": row["visual"]["limitations"]}
                                     for row in found]}
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
