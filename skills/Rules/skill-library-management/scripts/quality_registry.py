#!/usr/bin/env python3
"""Read-only score/selection validation; Agent supplies semantic and evidence judgments."""
import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

WEIGHTS = {"effect": 25, "reliability": 20, "capability": 15, "maintenance": 10,
           "github": 15, "ownership": 15}
STATUSES = {"verified", "partial", "unverified", "stale", "not_applicable"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, maximum, label):
    require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= maximum,
            f"{label}: expected finite number in [0, {maximum}]")
    return value


def day(value):
    require(isinstance(value, str), "Expected ISO date")
    parsed = date.fromisoformat(value)
    require(parsed.isoformat() == value, "Expected YYYY-MM-DD")
    return parsed


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}")


def star_points(stars, scope):
    require(type(stars) is int and stars >= 0, "Stars must be a non-negative integer")
    require(scope in {"dedicated", "collection"}, "Unknown repository scope")
    # Continuous decade bands: strictly increasing before display rounding,
    # approaching 15 without assigning every large repository the same score.
    level = math.log10(1 + stars)
    return 15 * level / (level + 1) * (1 if scope == "dedicated" else 0.5)


def record_state(record, profile, today, dimension):
    require(isinstance(record, dict), f"{dimension}: expected record")
    state = record.get("status")
    require(state in STATUSES, f"{dimension}: invalid verification status")
    require(isinstance(record.get("evidence"), list), f"{dimension}: expected evidence list")
    if state in {"verified", "not_applicable"}:
        require(bool(record["evidence"]), f"{dimension}: evidence required")
    for item in record["evidence"]:
        require(isinstance(item, dict), "Expected evidence object")
        for key in ("source", "version"):
            text(item.get(key), "evidence " + key)
        require(item.get("verification") in {"tested", "inspected", "reported"}, "Invalid evidence verification")
        require(day(item.get("observed_at")) <= today, "Future evidence is not valid")
        require(day(item["observed_at"]) <= day(profile["evaluated_at"]), "Evidence postdates this evaluation; refresh evaluated_at")
    if state in {"verified", "not_applicable"}:
        require(any(e["verification"] != "reported" for e in record["evidence"]), "Reported claims alone cannot be verified")
        due = day(record.get("review_after"))
        require(due >= max(day(e["observed_at"]) for e in record["evidence"]), "Review date precedes evidence")
        if record.get("assessed_version") != profile["version"] or today > due:
            return "stale"
    if state == "verified" and dimension in {"effect", "reliability"}:
        require(any(e["verification"] == "tested" for e in record["evidence"]), f"{dimension}: actual test evidence required")
    return state


def score(profile, today):
    for key in ("id", "name", "entry", "version", "revision", "scenario"):
        text(profile.get(key), key)
    require(day(profile.get("evaluated_at")) <= today, "Future evaluation")
    metrics = profile.get("metrics")
    require(isinstance(metrics, dict) and set(metrics) == set(WEIGHTS) - {"github", "ownership"}, "Expected four qualitative metrics")
    parts = {}
    for key, maximum in WEIGHTS.items():
        record = profile.get(key) if key in {"github", "ownership"} else metrics[key]
        state = record_state(record, profile, today, key)
        points = None
        if key not in {"github", "ownership"}:
            if record.get("points") is not None:
                number(record["points"], maximum, key)
            if state == "verified":
                points = number(record.get("points"), maximum, key)
            require(state != "not_applicable", f"{key}: use unverified rather than excluding a core metric")
        elif key == "github" and state == "verified":
            repo = record.get("repository")
            require(isinstance(repo, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo), "Invalid GitHub repository")
            require(repo.lower() == str(profile.get("upstream_repository", "")).lower(), "Star repository does not match assessed original repository")
            require(record.get("attribution") == "confirmed", "Repository attribution must be confirmed by Agent evidence")
            points = star_points(record.get("stars"), record.get("scope"))
        elif key == "ownership" and state == "verified":
            kind = record.get("kind")
            require(kind in {"original", "deep_adapted", "collected"}, "Unknown authorship kind")
            if kind == "original":
                points = 15
            elif kind == "deep_adapted":
                contribution = number(record.get("contribution"), 1, "contribution")
                require(0 < contribution < 1, "Deep adaptation contribution must be between 0 and 1; original alone receives 15")
                points = 15 * contribution
            else:
                points = 0
        if state == "not_applicable":
            require(key == "github" and record.get("repository") is None and record.get("stars") is None,
                    "Only a confirmed absence of GitHub origin may be not_applicable")
            points = 0
        parts[key] = {"status": state, "points": points, "maximum": maximum,
                      "evidence": record["evidence"], "assessed_version": record.get("assessed_version"),
                      "review_after": record.get("review_after")}
    known = sum(p["points"] for p in parts.values() if p["points"] is not None)
    unknown = sum(p["maximum"] for p in parts.values() if p["points"] is None)
    runs = profile.get("runs", [])
    require(isinstance(runs, list), "Expected runs list")
    ids, successes, attempts = set(), 0, 0
    for run in runs:
        require(isinstance(run, dict), "Expected run object")
        for key in ("id", "source", "version", "scenario"):
            text(run.get(key), "run " + key)
        require(run["id"] not in ids, "Duplicate run ID")
        ids.add(run["id"])
        require(run.get("status") in STATUSES - {"not_applicable"}, "Invalid run verification")
        require(run.get("outcome") in {"success", "failure"}, "Invalid run outcome")
        require(day(run.get("observed_at")) <= today, "Future run")
        if run["status"] == "verified" and run["version"] == profile["version"] and run["scenario"] == profile["scenario"]:
            attempts += 1
            successes += run["outcome"] == "success"
    return {"id": profile["id"], "scenario": profile["scenario"], "version": profile["version"],
            "revision": profile["revision"], "evaluated_at": profile["evaluated_at"], "dimensions": parts,
            "github": {k: profile["github"].get(k) for k in ("repository", "stars", "scope", "attribution")},
            "ownership": {k: profile["ownership"].get(k) for k in ("kind", "contribution")},
            "total": round(known, 4) if unknown == 0 else None, "known_points": round(known, 4),
            "possible_max": round(known + unknown, 4), "verified_weight": 100 - unknown,
            "runs": {"attempts": attempts, "successes": successes}}


def catalog(data, today):
    require(isinstance(data, dict) and data.get("schema_version") == 1 and type(data["schema_version"]) is int, "Unsupported schema version")
    require(isinstance(data.get("profiles"), list), "Expected profiles list")
    result = {}
    for profile in data["profiles"]:
        require(isinstance(profile, dict), "Expected profile object")
        scored = score(profile, today)
        key = (profile["id"], profile["scenario"])
        require(key not in result, "Duplicate profile ID/scenario")
        result[key] = (profile, scored)
    return result


def select(data, request, today):
    profiles = catalog(data, today)
    text(request.get("scenario"), "request scenario")
    near = number(request.get("near_points", 3), 100, "near_points")
    require(isinstance(request.get("candidates"), list), "Expected candidate list")
    explicit = request.get("explicit_id")
    require(explicit is None or isinstance(explicit, str) and explicit.strip(), "Invalid explicit ID")
    ready, pending, excluded, seen = [], [], [], set()
    for candidate in request["candidates"]:
        require(isinstance(candidate, dict), "Expected candidate object")
        identity = candidate.get("id")
        text(identity, "candidate ID")
        require(identity not in seen, "Duplicate candidate ID")
        seen.add(identity)
        require(candidate.get("fit") in {"exact", "related", "none", "unknown"}, "Invalid semantic fit")
        require(candidate.get("conditions") in {"ready", "blocked", "unknown"}, "Invalid runtime condition")
        require(isinstance(candidate.get("evidence"), list) and candidate["evidence"], "Candidate gate evidence required")
        for evidence in candidate["evidence"]:
            text(evidence, "candidate gate evidence")
        key = (identity, request["scenario"])
        require(key in profiles, "Missing profile for candidate and requested scenario")
        profile, scored = profiles[key]
        item = {"id": identity, "entry": profile["entry"], "fit": candidate["fit"], "score": scored}
        if candidate["fit"] == "none" or candidate["conditions"] == "blocked":
            item["reason"] = "Task mismatch or blocked runtime conditions"
            excluded.append(item)
        elif candidate["fit"] == "unknown" or candidate["conditions"] == "unknown":
            item["reason"] = "Task fit or runtime conditions need verification"
            pending.append(item)
        elif candidate.get("version") != profile["version"] or candidate.get("revision") != profile["revision"]:
            item["reason"] = "Current version/revision differs from assessed profile"
            item["score"] = dict(scored, total=None, known_points=0, possible_max=100, verified_weight=0)
            # Explicit use may proceed after current task/runtime gates pass;
            # an old score must not overrule the user's named skill.
            (ready if identity == explicit else pending).append(item)
        else:
            ready.append(item)
    if explicit is not None:
        require(explicit in seen, "Explicit Skill is missing from candidate input; do not silently substitute")
        chosen = next((item for item in ready if item["id"] == explicit), None)
        return {"status": "explicit" if chosen else "blocked_explicit", "selected": chosen,
                "pending": pending, "excluded": excluded}
    complete = [item for item in ready if item["score"]["total"] is not None]
    pending += [dict(item, reason="Incomplete or stale score evidence") for item in ready if item["score"]["total"] is None]
    ranked = sorted(complete, key=lambda item: (-item["score"]["total"], item["id"]))
    if not ranked:
        return {"status": "needs_review" if pending else "no_match", "selected": None, "ranked": [], "pending": pending, "excluded": excluded}
    top = ranked[0]["score"]["total"]
    # A close or potentially better unverified candidate prevents a false winner.
    if any(item["score"]["possible_max"] >= top - near for item in pending):
        return {"status": "needs_review", "selected": None, "ranked": ranked, "pending": pending, "excluded": excluded}
    pool = [item for item in ranked if top - item["score"]["total"] <= near]

    def tie_key(item):
        profile, scored = profiles[(item["id"], request["scenario"])]
        kind = profile["ownership"].get("kind")
        origin = {"original": 2, "deep_adapted": 1}.get(kind, 0)
        return (-origin, -scored["runs"]["successes"], -(item["fit"] == "exact"), -scored["total"], item["id"])

    chosen = min(pool, key=tie_key)
    return {"status": "selected", "selected": chosen, "ranked": ranked, "pending": pending,
            "excluded": excluded, "near_points": near, "tie_policy": "authorship, verified successful runs, task specificity, score, stable ID"}


def github_snapshot(repository):
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is not None, "Use owner/repo, not an arbitrary URL")
    require(not any(part in {".", ".."} for part in repository.split("/")), "Repository path segments cannot be traversal markers")
    url = "https://api.github.com/repos/" + repository
    req = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "skill-library-management", "X-GitHub-Api-Version": "2022-11-28"})
    transport = "urllib"
    try:
        with urlopen(req, timeout=15) as response:
            require(response.status == 200, "GitHub response was not successful")
            payload = json.load(response)
    except URLError:
        # Some macOS Python distributions lack the system CA bundle. Reuse an
        # existing authenticated CLI, never disable TLS or inspect its credentials.
        if shutil.which("gh") is None:
            raise
        response = subprocess.run(["gh", "api", "repos/" + repository,
                                   "-H", "X-GitHub-Api-Version: 2022-11-28"],
                                  capture_output=True, text=True, timeout=15)
        require(response.returncode == 0, "GitHub CLI request failed; Star remains unknown")
        payload = json.loads(response.stdout)
        transport = "gh"
    require(isinstance(payload, dict), "Invalid GitHub response")
    count = payload.get("stargazers_count")
    require(type(count) is int and count >= 0, "GitHub did not return a real stargazers_count")
    text(payload.get("full_name"), "canonical repository")
    return {"status": "verified", "repository": payload["full_name"], "requested_repository": repository,
            "stars": count, "source": url, "transport": transport, "observed_at": datetime.now(timezone.utc).isoformat(),
            "archived": payload.get("archived"), "fork": payload.get("fork"),
            "pushed_at": payload.get("pushed_at"), "scope": "unknown", "attribution": "unknown"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["score", "select", "github"])
    parser.add_argument("input", help="Registry JSON file, or owner/repo for github")
    parser.add_argument("--request", type=Path, help="Agent-reviewed candidate gate JSON for select; - reads stdin")
    parser.add_argument("--as-of", type=day, default=date.today())
    args = parser.parse_args()
    if (args.command == "select") != (args.request is not None):
        parser.error("--request is required only for select")
    try:
        if args.command == "github":
            result = github_snapshot(args.input)
        else:
            data = json.loads(Path(args.input).read_text(encoding="utf-8"))
            if args.command == "score":
                result = {"schema_version": 1, "as_of": args.as_of.isoformat(), "profiles": [item[1] for item in catalog(data, args.as_of).values()]}
            else:
                request = json.load(sys.stdin) if str(args.request) == "-" else json.loads(args.request.read_text(encoding="utf-8"))
                require(isinstance(request, dict), "Expected request object")
                result = select(data, request, args.as_of)
    except (OSError, ValueError, TypeError, URLError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"ok": False, "status": "unverified", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
