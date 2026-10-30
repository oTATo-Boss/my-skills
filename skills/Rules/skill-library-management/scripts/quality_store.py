#!/usr/bin/env python3
"""One shared-library quality store; query offline, apply reviewed deltas explicitly."""
import argparse
import copy
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError

from audit_library import file_manifest
from quality_registry import catalog, day, github_snapshot, require, score


def digest(data):
    # Retain the package fingerprint convention used by existing quality files.
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class Store:
    def __init__(self, agents_home=None):
        self.home = Path(agents_home or Path.home() / '.agents').expanduser().resolve()
        require(self.home == (Path.home()/'.agents').resolve() or self.home.is_relative_to(Path(tempfile.gettempdir()).resolve()),
                'Alternate agents-home is allowed only in system temporary fixtures')
        self.root = self.home / 'skills'
        self.directory = self.home / 'skill-library-management'
        self.path = self.directory / 'SKILL_QUALITY.json'
        self.table = self.directory / 'SKILL_QUALITY.md'

    def entry(self, profile):
        path = Path(profile['entry']).expanduser()
        require(path.is_absolute() and path.is_relative_to(self.root), 'Entry must be inside the shared library')
        require(path.resolve().is_relative_to(self.root.resolve()), 'External symlink target is outside shared scope')
        require(path.name in {'SKILL.md', 'SKILLS_INDEX.md'} and path.is_file(), 'Missing shared Skill/package entry')
        require(profile['id'] == path.resolve().parent.relative_to(self.root.resolve()).as_posix(), 'ID must be the canonical shared relative directory')
        return path

    def load(self, today):
        require(not self.directory.is_symlink(), 'Quality directory must not redirect outside the fixed location')
        require(not self.path.is_symlink() and not self.table.is_symlink(), 'Quality files must not be symlinks')
        if not self.path.exists():
            return {'schema_version': 1, 'library_root': str(self.root), 'profiles': [],
                    'repository_snapshots': {}, 'history': []}
        data = json.loads(self.path.read_text(encoding='utf-8'))
        require(data.get('library_root') == str(self.root), 'Store belongs to another library')
        catalog(data, today)
        for p in data['profiles']:
            # Removed entries remain recorded, never silently resurrected or deleted.
            path = Path(p['entry']).expanduser()
            require(path.is_absolute() and path.is_relative_to(self.root), 'Out-of-scope stored entry')
        return data

    def query(self, data, today, ids=(), scenario=None, include_children=False, check_current=False):
        profiles = data['profiles']
        if ids:
            profiles = [p for p in profiles if p['id'] in ids or p['name'] in ids]
        if scenario:
            profiles = [p for p in profiles if p['scenario'] == scenario]
        if not include_children and not ids:
            parents = {p['id'] for p in profiles}
            profiles = [p for p in profiles if not any(a.as_posix() in parents for a in Path(p['id']).parents if a.as_posix() != '.')]
        rows = []
        for p in profiles:
            result = score(p, today)
            try:
                path = self.entry(p)
                current = 'not_checked'
                if check_current:
                    revision = 'package-sha256:' + digest(file_manifest(path.parent, allowed_root=self.root))
                    current = 'matched' if revision == p['revision'] else 'changed'
            except ValueError as exc:
                current = 'missing_or_out_of_scope'
                result['entry_problem'] = str(exc)
            pending = [k for k, v in result['dimensions'].items() if v['points'] is None]
            if current in {'changed', 'missing_or_out_of_scope'}:
                result.update(total=None, known_points=0, possible_max=100, verified_weight=0)
                pending = list(result['dimensions'])
                result['dimensions'] = {k: dict(v, status='stale', points=None) for k, v in result['dimensions'].items()}
            # Ordinary reads reuse scores but do not claim disk revision validation.
            result.update(name=p['name'], entry=p['entry'], description=p.get('description', ''),
                          github_observed_at=next((e['observed_at'] for e in reversed(p['github']['evidence']) if e['source'].startswith('https://api.github.com/repos/')), None),
                          current_revision=current, pending_dimensions=pending,
                          pending_reasons={k: (p[k] if k in {'github', 'ownership'} else p['metrics'][k]).get('reason', 'Evidence needs review') for k in pending},
                          assessment_status='complete' if result['total'] is not None else 'incomplete')
            rows.append(result)
        complete = sum(r['assessment_status'] == 'complete' for r in rows)
        return {'store': str(self.path), 'store_revision': digest(data), 'as_of': str(today),
                'summary': {'profiles': len(rows), 'complete': complete, 'incomplete': len(rows)-complete,
                            'assessment_complete': bool(rows) and complete == len(rows)}, 'profiles': rows}

    def merge(self, data, delta, today):
        require(isinstance(delta, dict), 'Expected update object')
        updated = copy.deepcopy(data)
        existing = {(p['id'], p['scenario']): p for p in updated['profiles']}
        changed = 0
        seen = set()
        for p in delta.get('profiles', []):
            self.entry(p)
            score(p, today)
            key = (p['id'], p['scenario'])
            require(key not in seen, 'Duplicate incoming ID/scenario')
            seen.add(key)
            old = existing.get(key)
            require(not old or p['evaluated_at'] >= old['evaluated_at'], 'Older profile cannot replace newer evidence')
            if old == p:
                continue
            if old:
                old_score, new_score = score(old, today), score(p, today)
                reset = {k for k, v in old_score['dimensions'].items()
                         if v['points'] is not None and new_score['dimensions'][k]['points'] is None}
                declared = {i['dimension'] for i in delta.get('invalidations', [])
                            if i.get('id') == p['id'] and i.get('scenario') == p['scenario'] and i.get('reason')}
                require(reset <= declared, 'Invalidating verified dimensions requires explicit reasons')
                require({r['id'] for r in old.get('runs', [])} <= {r['id'] for r in p.get('runs', [])}, 'Incremental updates must retain recorded runs')
                old_runs = {r['id']: r for r in old.get('runs', [])}
                corrections = [c for c in delta.get('run_corrections', []) if c.get('id')==p['id'] and c.get('scenario')==p['scenario']]
                for run in p.get('runs', []):
                    previous = old_runs.get(run['id'])
                    if previous and previous != run:
                        require(any(c.get('run_id')==run['id'] and c.get('reason') and c.get('previous_digest')==digest(previous) for c in corrections),
                                'Changing an existing run requires an explicit correction tied to its previous digest')
                updated['history'].append({'replaced_at': str(today), 'profile': old, 'run_corrections': copy.deepcopy(corrections)})
            existing[key] = copy.deepcopy(p)
            changed += 1
        updated['profiles'] = sorted(existing.values(), key=lambda p: (p['id'], p['scenario']))
        for snapshot in delta.get('repository_snapshots', []):
            repo = snapshot.get('requested_repository') or snapshot.get('repository')
            require(isinstance(repo, str) and re.fullmatch(r'[\w.-]+/[\w.-]+', repo), 'Invalid snapshot repository')
            require(not any(x in {'.', '..'} for x in repo.split('/')), 'Invalid repository segments')
            require(snapshot.get('status') == 'verified' and type(snapshot.get('stars')) is int and snapshot['stars'] >= 0, 'Expected verified real Star count')
            observed = day(snapshot['observed_at'][:10])
            require(observed <= today, 'Future repository snapshot')
            previous = updated['repository_snapshots'].get(repo.lower())
            if previous and previous.get('snapshot') and previous['snapshot']['observed_at'] > snapshot['observed_at']:
                continue
            updated['repository_snapshots'][repo.lower()] = {'snapshot': copy.deepcopy(snapshot)}
        catalog(updated, today)
        return updated, changed

    def github_plan(self, data, today, max_age=7, ids=()):
        require(max_age >= 0, 'max-age-days must be nonnegative')
        repos = {}
        for p in data['profiles']:
            if ids and p['id'] not in ids and p['name'] not in ids:
                continue
            gh = p['github']
            try:
                self.entry(p)
            except ValueError:
                continue
            repo = p.get('upstream_repository')
            if repo and gh.get('attribution') == 'confirmed' and repo.lower() == str(gh.get('repository', '')).lower():
                require(re.fullmatch(r'[\w.-]+/[\w.-]+', repo) and not any(s in {'.', '..'} for s in repo.split('/')), 'Invalid original repository')
                repos.setdefault(repo.lower(), set()).add(p['id'])
        plan = []
        for repo, identities in sorted(repos.items()):
            cached = data['repository_snapshots'].get(repo, {})
            snapshot = cached.get('snapshot')
            if cached.get('retry_after') and today < day(cached['retry_after']):
                action = 'deferred'
            elif snapshot and day(snapshot['observed_at'][:10]) + timedelta(days=max_age) >= today:
                action = 'reuse'
            else:
                action = 'fetch'
            plan.append({'repository': repo, 'ids': sorted(identities), 'action': action})
        return plan

    def refresh_github(self, data, today, max_age=7, ids=(), fetch=github_snapshot):
        updated = copy.deepcopy(data)
        results = []
        limited = False
        for item in self.github_plan(data, today, max_age, ids):
            repo = item['repository']
            if limited and item['action'] == 'fetch':
                updated['repository_snapshots'].setdefault(repo, {})['retry_after'] = str(today + timedelta(days=1))
            if item['action'] != 'fetch' or limited:
                results.append(dict(item, action='deferred' if limited else item['action']))
                continue
            cache = updated['repository_snapshots'].setdefault(repo, {})
            try:
                # The caller/connector may supply a batch. CLI fallback retries one
                # transient transport/server failure; never retry 404 or rate limits.
                for attempt in range(2):
                    try:
                        snapshot = fetch(repo, allow_fallback=attempt == 0)
                        break
                    except HTTPError as exc:
                        if exc.code >= 500 and attempt == 0 and getattr(exc, 'transport_attempts', 1) < 2:
                            continue
                        limited = exc.code in {403, 429}
                        raise
                    except (URLError, TimeoutError, subprocess.TimeoutExpired):
                        if attempt:
                            raise
                updated, _ = self.merge(updated, {'repository_snapshots': [snapshot]}, today)
                results.append(dict(item, action='fetched'))
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                # Keep the last good snapshot, do not turn failure into 0 Stars.
                cache['last_error'] = {'observed_at': str(today), 'type': type(exc).__name__}
                cache['retry_after'] = str(today + timedelta(days=1))
                results.append(dict(item, action='failed', error_type=type(exc).__name__))
        # Refreshing a repository fact does not certify per-Skill attribution or
        # silently extend metric review dates. Agent merges reviewed metric deltas.
        return updated, results

    def commit(self, data, today, expected):
        self.directory.mkdir(parents=True, exist_ok=True)
        lock = self.directory / '.quality.lock'
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.close(fd)
            require(digest(self.load(today)) == expected, 'Store changed; read and merge again')
            self.atomic_write(self.path, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
            try:
                self.render(data, today)
            except OSError:
                # JSON is already committed; a failed derived view must never be
                # reported as a rolled-back data update or used as a second truth.
                return 'JSON committed; Markdown view failed. Run render again.'
        finally:
            lock.unlink()

    @staticmethod
    def atomic_write(path, content):
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
                temp = Path(stream.name)
                os.chmod(temp, 0o600)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if temp and temp.exists():
                temp.unlink()

    def render(self, data, today):
        result = self.query(data, today)
        lines = ['# 共享库质量表', '', f'唯一数据源：{self.path}', f'数据修订：{digest(data)}；展示日期：{today}',
                 '', '这是派生视图；查询与更新以 JSON 为准。按 ID + 场景在 JSON 查询各维度证据、版本、原因与下一步。总分待评不能称评分完成；查询未重新核对全部包内容。',
                 '', f"已完整评分 {result['summary']['complete']}／{result['summary']['profiles']}；待完成 {result['summary']['incomplete']}。", '',
                 '| Skill／ID／场景 | 用途 | 效果25 | 可靠20 | 完整15 | 维护10 | Star15 | 本人15 | 总分100 | 原始Star | Star查询日期 | 未完成项 |',
                 '|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---|']
        def cell(value):
            return str(value).replace('|', '／').replace('\n', ' ')
        for row in result['profiles']:
            values = [f"{row['name']} [{row['id']}]／{row['scenario']}", row['description']]
            values += [v['points'] if v['points'] is not None else '待评' for v in row['dimensions'].values()]
            values += [row['total'] if row['total'] is not None else '待评', row['github']['stars'] if row['github']['stars'] is not None else '未知', row['github_observed_at'] or '未核实', ', '.join(row['pending_dimensions'])]
            lines.append('| '+' | '.join(cell(v) for v in values)+' |')
        self.atomic_write(self.table, '\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['query', 'update', 'plan-github', 'refresh-github', 'render'])
    parser.add_argument('--agents-home', type=Path, help='Isolated test home; normally omit (defaults to ~/.agents)')
    parser.add_argument('--as-of', type=day, default=date.today())
    parser.add_argument('--id', action='append', default=[])
    parser.add_argument('--scenario')
    parser.add_argument('--include-children', action='store_true')
    parser.add_argument('--check-current', action='store_true')
    parser.add_argument('--require-complete', action='store_true', help='query exits 2 while any requested assessment is incomplete')
    parser.add_argument('--input', help='Reviewed update JSON; - reads stdin')
    parser.add_argument('--max-age-days', type=int, default=7)
    parser.add_argument('--expected-revision')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        store = Store(args.agents_home)
        data = store.load(args.as_of)
        if args.command == 'query':
            result = store.query(data, args.as_of, args.id, args.scenario, args.include_children, args.check_current)
        elif args.command == 'plan-github':
            result = {'repositories': store.github_plan(data, args.as_of, args.max_age_days, args.id)}
        else:
            require(args.apply and args.expected_revision, 'Writes require --apply and --expected-revision from query')
            require(digest(data) == args.expected_revision, 'Store changed; read again')
            if args.command == 'update':
                require(bool(args.input), 'update requires --input (use - for stdin)')
                delta = json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8'))
                data, count = store.merge(data, delta, args.as_of)
                result = {'changed_profiles': count}
            elif args.command == 'refresh-github':
                data, outcomes = store.refresh_github(data, args.as_of, args.max_age_days, args.id)
                result = {'repositories': outcomes}
            else:
                result = {'rendered': str(store.table)}
            warning = store.commit(data, args.as_of, args.expected_revision)
            result.update(store=str(store.path), store_revision=digest(data), summary=store.query(data, args.as_of)['summary'])
            if warning:
                result['warning'] = warning
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if args.command == 'query' and args.require_complete and not result['summary']['assessment_complete']:
            return 2
        return 0
    except (OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
