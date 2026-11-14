"""Compose a saved mode template with a JSON action card from stdin."""

import argparse
import json
import re
import sys
from pathlib import Path


def main():
    modes = Path(__file__).resolve().parents[1] / "references/json-prompt-system/modes"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(path.name for path in modes.iterdir() if path.is_dir()))
    parser.add_argument("--ratio", default="3:4")
    parser.add_argument("--profile-file", type=Path)
    parser.add_argument("--reference-rules-file", type=Path)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()
    try:
        card = json.load(sys.stdin)
        template_dir = modes / args.mode
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
        values = {
            "REFERENCE_RULES": reference_rules,
            "ACTION_JSON": action_json,
            "PROFILE_PROMPT": args.profile_file.read_text(encoding="utf-8") if args.profile_file else "",
            "RATIO": args.ratio,
        }
        template = (template_dir / "fixed.md").read_text(encoding="utf-8")
        print(re.sub(r"{{(RATIO|PROFILE_PROMPT|ACTION_JSON|REFERENCE_RULES)}}", lambda m: values[m[1]], template))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
