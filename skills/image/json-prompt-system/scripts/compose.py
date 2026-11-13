"""Compose a saved mode template with a JSON action card from stdin."""

import argparse
import json
import re
import sys
from pathlib import Path

from photography import RELATIONSHIPS, validate_card, unique_object


def main():
    modes = Path(__file__).resolve().parents[1] / "references/json-prompt-system/modes"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(path.name for path in modes.iterdir() if path.is_dir()))
    parser.add_argument("--ratio", default="3:4")
    parser.add_argument("--profile-file", type=Path)
    parser.add_argument("--reference-rules-file", type=Path)
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--photography", action="store_true", help="Use the explicit photography card contract")
    parser.add_argument("--resolution", choices=["auto", "1K", "2K", "4K"], default="auto")
    args = parser.parse_args()
    try:
        if args.photography and args.reference_rules_file:
            parser.error("With --photography put reference rules in 参考分工, not a separate file.")
        card = json.load(sys.stdin, object_pairs_hook=unique_object) if args.photography else json.load(sys.stdin)
        template_dir = modes / args.mode
        if args.photography:
            shot = validate_card(card, args.mode)
        else:
            if args.resolution != "auto":
                parser.error("--resolution requires --photography; legacy fixed text is unchanged.")
            schema = json.loads((template_dir / "mode_template.txt").read_text(encoding="utf-8"))
            if not isinstance(card, dict) or card.keys() != schema.keys():
                parser.error("Action card root keys must match the selected mode template.")
        action_json = json.dumps(card, ensure_ascii=False, indent=2, allow_nan=False)
        if args.json_only:
            print(action_json)
            return
        reference_rules = (
            args.reference_rules_file.read_text(encoding="utf-8")
            if args.reference_rules_file
            else "本次无参考图，依据人物档案、任务设定与下方 JSON 生成。"
        )
        if not reference_rules.strip():
            parser.error("Reference rules must not be empty.")
        if args.photography:
            refs = shot["参考分工"]
            reference_rules = "\n".join(
                f'图{r["图号"]}负责{r["负责"]}。保留{r["保留"]}。调整{r["调整"]}。' for r in refs
            ) or "本次无参考图，身份与造型依据摄影设计执行。"
        values = {
            "REFERENCE_RULES": reference_rules,
            "ACTION_JSON": action_json,
            "PROFILE_PROMPT": args.profile_file.read_text(encoding="utf-8") if args.profile_file else "",
            "RATIO": args.ratio,
            "RESOLUTION": "按生成工具实际设置" if args.resolution == "auto" else args.resolution,
            "RELATIONSHIP": RELATIONSHIPS[args.mode],
        }
        template_path = (modes.parent.parent / "photography/fixed.md") if args.photography else (template_dir / "fixed.md")
        template = template_path.read_text(encoding="utf-8")
        print(re.sub(r"{{(RATIO|PROFILE_PROMPT|ACTION_JSON|REFERENCE_RULES|RESOLUTION|RELATIONSHIP)}}", lambda m: values[m[1]], template))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
