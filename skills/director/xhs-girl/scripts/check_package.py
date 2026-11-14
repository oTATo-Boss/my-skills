"""Check portable links, reference assets and standalone photography examples."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    failures = []
    links = 0
    for page in ROOT.rglob('*.md'):
        for href in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', page.read_text()):
            if re.match(r'\w+://|#', href):
                continue
            path = href.split('#')[0].strip('<>')
            if not path:
                continue
            links += 1
            if not (page.parent / path).exists():
                failures.append(f'Broken link: {page.relative_to(ROOT)} -> {href}')
    manifest = json.loads((ROOT / 'assets/reference-covers/manifest.json').read_text())
    if len(manifest) != 30 or len({r['id'] for r in manifest}) != 30:
        failures.append('Reference manifest must contain 30 unique cases')
    for row in manifest:
        if not (ROOT / row['file']).is_file():
            failures.append(f'Missing asset: {row["file"]}')
        if not (ROOT / f'references/photography-cases/{row["id"].lower()}.md').is_file():
            failures.append(f'Missing case: {row["id"]}')
        x1, y1, x2, y2 = row['crop']
        w, h = row['source_size']
        if not (0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h):
            failures.append(f'Invalid crop: {row["id"]}')
    examples = list((ROOT / 'examples').glob('*.json'))
    for path in examples:
        card = json.loads(path.read_text())
        mode = card['摄影设计']['相机']['拍摄关系']
        if mode not in {'third-person', 'front-camera-selfie', 'mirror-selfie', 'ecommerce-editorial'}:
            failures.append(f'Unknown relationship in standalone example: {path.name}')
    for failure in failures:
        print(failure, file=sys.stderr)
    print(json.dumps({'links_checked': links, 'cases': len(manifest),
                      'examples': len(examples), 'failures': len(failures)}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
