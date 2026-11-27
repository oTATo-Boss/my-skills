"""Draw real library references for zero-input briefs; the agent still designs from the images.

Run from the skill root:
    python3 scripts/draw_refs.py              # random draw
    python3 scripts/draw_refs.py --seed 7     # reproducible draw
    python3 scripts/draw_refs.py --exclude R12 --exclude R40   # redraw without rejected images

Use only when the user gave no usable scene, styling or mood. Library images are for
analysis only and are never uploaded to the image generator.
"""
import argparse
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
SCENE_CLASSES = ("室内", "室外", "车内")

# role: (facets that must be visible, facets reported to the agent, what to borrow)
ROLES = {
    "主参考": (("scene", "background", "lighting"), ("scene", "background", "lighting", "finish"),
             "定场景类型、背景层次和主光关系；按自己的人物重新设计，不复制原图人物与穿搭"),
    "造型参考": (("styling",), ("styling",),
             "只借妆发、配色、剪裁或饰品中的一两处关系，与主参考的场景光色协调"),
    "姿态表情参考": (("pose", "expression"), ("pose", "expression", "composition"),
               "只借身体支撑、手的位置、视线和表情状态，不借原场景"),
    "质感参考": (("finish", "lighting"), ("finish", "lighting"),
             "只借色彩、反差、颗粒与皮肤反射，和主参考同属室内／室外／车内"),
}


def scene_class(record):
    tags = record["visual"]["facets"]["scene"]["tags"]
    return next((tag for tag in tags if tag in SCENE_CLASSES), None)


def visible(record, facets):
    return all(record["visual"]["facets"][name]["evidence"] != "not_visible" for name in facets)


def eligible(record, role, primary_class=None):
    required = ROLES[role][0]
    if not visible(record, required):
        return False
    if role == "主参考":
        return scene_class(record) is not None and record.get("partial") is not True
    if role == "姿态表情参考":
        return record.get("partial") is not True
    if role == "质感参考":
        return scene_class(record) == primary_class
    return True


def describe(record, role):
    facets = record["visual"]["facets"]
    return {
        "role": role,
        "id": record["id"],
        "title": record["title"],
        "file": str((ROOT / record["file"]).resolve()),
        "borrow": ROLES[role][2],
        "observations": {name: facets[name]["observation"] for name in ROLES[role][1]
                         if facets[name]["evidence"] != "not_visible"},
        "transferable_mechanism": record["visual"]["transferable_mechanism"],
        "limitations": record["visual"]["limitations"],
    }


def draw(records, rng, exclude=()):
    used = set(exclude)
    picks = []
    primary_class = None
    for role in ROLES:
        pool = [r for r in records if r["id"] not in used and eligible(r, role, primary_class)]
        if not pool:
            if role == "主参考":
                raise ValueError("No eligible primary reference; reduce --exclude")
            continue
        chosen = rng.choice(pool)
        used.add(chosen["id"])
        if role == "主参考":
            primary_class = scene_class(chosen)
        picks.append(describe(chosen, role))
    return picks


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, help="Repeat a previous draw")
    parser.add_argument("--exclude", action="append", default=[], metavar="R_ID",
                        help="Skip a rejected reference; repeatable")
    args = parser.parse_args()
    records = json.loads((ROOT / "assets/reference-covers/manifest.json").read_text())
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1, 10**9)
    try:
        picks = draw(records, random.Random(seed), args.exclude)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({
        "seed": seed,
        "next_steps": [
            "用读图工具逐张打开下面每个 file，亲眼确认再使用；文字观察只帮助定位。",
            "主参考不衬人或明显不适合时，加 --exclude 该编号重抽，最多重抽两次。",
            "画面中心和主导气质从这几张图里看出来，不另编咖啡馆、窗边等默认场景。",
            "库图只用于分析，不上传给生图工具。",
        ],
        "references": picks,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
