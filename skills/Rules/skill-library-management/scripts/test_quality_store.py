#!/usr/bin/env python3
"""Shared-only persistence/refresh acceptance in temporary roots; no real API calls."""
import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from quality_store import Store, digest
from quality_registry import github_snapshot
from audit_library import file_manifest
from test_quality_registry import profile
from test_reference_score import reviewed

TODAY = date(2026, 10, 30)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name)/'.agents')
        self.data = self.store.load(TODAY)

    def item(self, identity='video/a', complete=True):
        p = profile(identity)
        path = self.store.root/identity/'SKILL.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\nname: '+identity.split('/')[-1]+'\ndescription: fixture\n---\n')
        p.update(entry=str(path), description='隔离文本导出', revision='package-sha256:'+digest(file_manifest(path.parent)))
        if not complete:
            p['metrics']['effect'].update(status='unverified', points=None, evidence=[])
        return p

    def add(self, *items):
        self.data, _ = self.store.merge(self.data, {'profiles': list(items)}, TODAY)

    def test_incremental_merge_does_not_replace_newer_reference_with_older_review(self):
        p=self.item(complete=False);p['review_assessment']=reviewed()['review_assessment']
        self.add(p)
        older=copy.deepcopy(p);older['review_assessment']['evaluated_at']='2026-10-29'
        with self.assertRaises(ValueError):self.store.merge(self.data,{'profiles':[older]},TODAY)

    def test_render_labels_reference_and_preserves_raw_star_and_date(self):
        p=self.item(complete=False);p['review_assessment']=reviewed()['review_assessment']
        self.add(p)
        self.data,_=self.store.merge(self.data,{'repository_snapshots':[self.snapshot(stars=99999)]},TODAY)
        self.store.directory.mkdir(parents=True)
        self.store.render(self.data,TODAY)
        view=self.store.table.read_text()
        self.assertIn('参考分／100',view)
        self.assertIn('84.5',view)
        self.assertIn('Star 99999（2026-10-30）',view)
        self.assertIn('未实测，审阅估评',view)
        self.assertEqual(self.store.query(self.data,TODAY)['summary']['complete'],0)

    def test_repository_plan_uses_reviewed_origin_instead_of_superseded_raw_attribution(self):
        p=self.item();p['review_assessment']=reviewed()['review_assessment']
        p['review_assessment']['github_review']['repository']='original/skill'
        self.add(p)
        plan=self.store.github_plan(self.data,TODAY)
        self.assertEqual([r['repository'] for r in plan],['original/skill'])

    def test_unknown_reviewed_origin_does_not_fetch_old_guessed_origin(self):
        p=self.item();p['review_assessment']=reviewed()['review_assessment']
        p['review_assessment']['github_review'].update(repository=None,attribution='unknown')
        self.add(p)
        self.assertEqual(self.store.github_plan(self.data,TODAY),[])

    @staticmethod
    def snapshot(repo='fixture/export', stars=0, observed='2026-10-30T08:00:00Z'):
        return {'requested_repository': repo, 'repository': repo, 'status': 'verified',
                'stars': stars, 'source': 'https://api.github.com/repos/'+repo, 'observed_at': observed}

    def test_offline_query_does_not_create_store_and_uses_fixed_location(self):
        with patch('quality_store.github_snapshot', side_effect=AssertionError('network forbidden')):
            result = self.store.query(self.data, TODAY)
        self.assertFalse(self.store.directory.exists())
        self.assertFalse(result['summary']['assessment_complete'])
        self.assertEqual(self.store.path, self.store.home/'skill-library-management/SKILL_QUALITY.json')

    def test_scope_rejects_other_project_and_symlink_escape(self):
        p = self.item()
        outside = Path(self.temp.name)/'other-project/SKILL.md'
        outside.parent.mkdir();outside.write_text('do not inspect')
        p['entry'] = str(outside)
        with self.assertRaises(ValueError):self.store.merge(self.data, {'profiles': [p]}, TODAY)
        alias = self.store.root/'outside'
        alias.symlink_to(outside.parent)
        p.update(id='outside', entry=str(alias/'SKILL.md'))
        with self.assertRaises(ValueError):self.store.merge(self.data, {'profiles': [p]}, TODAY)
        self.assertEqual(outside.read_text(), 'do not inspect')

    def test_identity_cannot_be_an_alias_for_another_directory(self):
        p = self.item();p['id'] = 'wrong'
        with self.assertRaises(ValueError):self.store.merge(self.data, {'profiles': [p]}, TODAY)

    def test_test_home_override_cannot_point_at_another_production_library(self):
        with self.assertRaises(ValueError):Store(Path.home()/'.another-production-library')

    def test_package_external_file_link_is_not_read_during_revision_check(self):
        p=self.item();self.add(p)
        outside=Path(self.temp.name)/'outside.txt';outside.write_text('out of scope')
        (Path(p['entry']).parent/'external.txt').symlink_to(outside)
        original=Path.read_bytes
        def guarded(path):
            if path.resolve()==outside.resolve():raise AssertionError('external contents were opened')
            return original(path)
        with patch.object(Path,'read_bytes',guarded):result=self.store.query(self.data,TODAY,check_current=True)
        self.assertIsNone(result['profiles'][0]['total'])
        self.assertEqual(result['profiles'][0]['current_revision'],'missing_or_out_of_scope')

    def test_incomplete_is_not_done_and_changed_package_invalidates_displayed_points(self):
        a, b = self.item(), self.item('video/b', complete=False)
        self.add(a, b)
        result = self.store.query(self.data, TODAY, check_current=True)
        self.assertEqual(result['summary']['complete'], 1)
        self.assertEqual(result['summary']['incomplete'], 1)
        self.assertFalse(result['summary']['assessment_complete'])
        Path(a['entry']).write_text('changed')
        changed = self.store.query(self.data, TODAY, ids=['video/a'], check_current=True)['profiles'][0]
        self.assertIsNone(changed['total'])
        self.assertTrue(all(v['points'] is None for v in changed['dimensions'].values()))

    def test_increment_preserves_other_profiles_and_history_and_is_idempotent(self):
        a, b = self.item(), self.item('video/b');self.add(a, b)
        changed = copy.deepcopy(a);changed['description'] = '更明确的用途'
        updated, count = self.store.merge(self.data, {'profiles': [changed]}, TODAY)
        self.assertEqual(count, 1)
        self.assertEqual(next(p for p in updated['profiles'] if p['id']==b['id']), b)
        self.assertEqual(updated['history'][0]['profile'], a)
        again, count = self.store.merge(updated, {'profiles': [changed]}, TODAY)
        self.assertEqual(count, 0);self.assertEqual(again, updated)

    def test_older_profile_and_silent_reset_are_rejected(self):
        p=self.item();self.add(p)
        old=copy.deepcopy(p);old['evaluated_at']='2026-10-29'
        with self.assertRaises(ValueError):self.store.merge(self.data, {'profiles':[old]}, TODAY)
        reset=copy.deepcopy(p);reset['metrics']['effect'].update(status='unverified',points=None,evidence=[])
        with self.assertRaises(ValueError):self.store.merge(self.data, {'profiles':[reset]}, TODAY)
        delta={'profiles':[reset], 'invalidations':[{'id':p['id'],'scenario':p['scenario'],'dimension':'effect','reason':'fixture dependency changed'}]}
        updated,_=self.store.merge(self.data,delta,TODAY)
        self.assertIsNone(self.store.query(updated,TODAY)['profiles'][0]['total'])

    def test_runs_cannot_be_silently_dropped(self):
        p=self.item();p['runs']=[{'id':'r1','source':'fixture.json','version':'1','scenario':'text-json','observed_at':'2026-10-30','status':'verified','outcome':'success'}];self.add(p)
        newer=copy.deepcopy(p);newer['runs']=[]
        with self.assertRaises(ValueError):self.store.merge(self.data,{'profiles':[newer]},TODAY)

    def test_run_outcome_rewrite_requires_explicit_correction_and_keeps_history(self):
        p=self.item();p['runs']=[{'id':'r1','source':'fixture.json','version':'1','scenario':'text-json','observed_at':'2026-10-30','status':'verified','outcome':'failure'}];self.add(p)
        changed=copy.deepcopy(p);changed['runs'][0]['outcome']='success'
        with self.assertRaises(ValueError):self.store.merge(self.data,{'profiles':[changed]},TODAY)
        correction={'id':p['id'],'scenario':p['scenario'],'run_id':'r1','previous_digest':digest(p['runs'][0]),'reason':'Verified the original receipt: the earlier outcome was recorded incorrectly'}
        updated,_=self.store.merge(self.data,{'profiles':[changed],'run_corrections':[correction]},TODAY)
        self.assertEqual(updated['history'][0]['profile']['runs'][0]['outcome'],'failure')
        self.assertEqual(updated['history'][0]['run_corrections'],[correction])

    def test_one_canonical_pair_and_conflicting_write_preserves_existing(self):
        self.add(self.item());expected=digest(self.store.load(TODAY))
        self.store.commit(self.data,TODAY,expected)
        files={p.name for p in self.store.directory.iterdir()}
        self.assertEqual(files,{'SKILL_QUALITY.json','SKILL_QUALITY.md'})
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):self.store.commit(self.data,TODAY,expected)
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertFalse((self.store.directory/'.quality.lock').exists())

    def test_failed_atomic_replace_keeps_old_json_and_cleans_temporary_file(self):
        self.add(self.item());self.store.commit(self.data,TODAY,digest(self.store.load(TODAY)))
        before=self.store.path.read_bytes()
        with patch('quality_store.os.replace',side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):self.store.commit(self.data,TODAY,digest(self.data))
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertEqual(len(list(self.store.directory.iterdir())),2)

    def test_view_failure_is_reported_as_committed_data_not_a_rollback(self):
        self.add(self.item())
        with patch.object(self.store,'render',side_effect=OSError('view blocked')):
            warning=self.store.commit(self.data,TODAY,digest(self.store.load(TODAY)))
        self.assertIn('JSON committed',warning)
        self.assertEqual(self.store.load(TODAY),self.data)

    def test_nested_items_are_collapsed_but_explicit_queries_can_find_them(self):
        self.add(self.item('video/pack'),self.item('video/pack/child'))
        self.assertEqual(self.store.query(self.data,TODAY)['summary']['profiles'],1)
        self.assertEqual(self.store.query(self.data,TODAY,include_children=True)['summary']['profiles'],2)
        self.assertEqual(self.store.query(self.data,TODAY,ids=['video/pack/child'])['summary']['profiles'],1)

    def test_repository_batch_deduplicates_and_reuses_real_zero(self):
        self.add(self.item(),self.item('video/b'))
        fetch=Mock(return_value=self.snapshot())
        updated,outcomes=self.store.refresh_github(self.data,TODAY,fetch=fetch)
        fetch.assert_called_once_with('fixture/export', allow_fallback=True)
        self.assertEqual(outcomes[0]['action'],'fetched')
        fetch.reset_mock()
        self.store.refresh_github(updated,TODAY,fetch=fetch)
        fetch.assert_not_called()
        self.assertEqual(updated['repository_snapshots']['fixture/export']['snapshot']['stars'],0)
        self.assertEqual(updated['profiles'],self.data['profiles'])

    def test_transient_retry_then_failure_keeps_old_snapshot_and_cools_down(self):
        self.add(self.item())
        self.data,_=self.store.merge(self.data,{'repository_snapshots':[self.snapshot(stars=123,observed='2026-10-01T00:00:00Z')]},TODAY)
        fetch=Mock(side_effect=URLError('temporary outage'))
        updated,outcomes=self.store.refresh_github(self.data,TODAY,fetch=fetch)
        self.assertEqual(fetch.call_count,2)
        self.assertEqual(updated['repository_snapshots']['fixture/export']['snapshot']['stars'],123)
        self.assertEqual(self.store.github_plan(updated,TODAY)[0]['action'],'deferred')
        self.assertEqual(outcomes[0]['action'],'failed')

    def test_404_not_retried_and_rate_limit_stops_remaining_batch(self):
        a,b=self.item(),self.item('video/b');b['upstream_repository']='other/repo';b['github']['repository']='other/repo';self.add(a,b)
        fetch=Mock(side_effect=HTTPError('url',429,'limit',None,None))
        updated,outcomes=self.store.refresh_github(self.data,TODAY,fetch=fetch)
        self.assertEqual(fetch.call_count,1)
        self.assertEqual([o['action'] for o in outcomes],['failed','deferred'])
        self.assertTrue(all(p['action']=='deferred' for p in self.store.github_plan(updated,TODAY)))
        fetch=Mock(side_effect=HTTPError('url',404,'missing',None,None))
        self.store.refresh_github(self.data,TODAY,ids=['video/a'],fetch=fetch)
        self.assertEqual(fetch.call_count,1)

    def test_gh_fallback_rate_limit_stops_batch(self):
        a,b=self.item(),self.item('video/b');b['upstream_repository']='other/repo';b['github']['repository']='other/repo';self.add(a,b)
        limited=subprocess.CompletedProcess([],1,'','gh: API rate limit exceeded (HTTP 429)')
        with patch('quality_registry.urlopen',side_effect=URLError('CA missing')),patch('quality_registry.shutil.which',return_value='gh'),patch('quality_registry.subprocess.run',return_value=limited) as gh:
            updated,outcomes=self.store.refresh_github(self.data,TODAY,fetch=github_snapshot)
        self.assertEqual([o['action'] for o in outcomes],['failed','deferred'])
        self.assertEqual(gh.call_count,1)
        self.assertTrue(all(i['action']=='deferred' for i in self.store.github_plan(updated,TODAY)))

    def test_total_transport_budget_does_not_retry_url_and_gh_twice(self):
        self.add(self.item())
        with patch('quality_registry.urlopen',side_effect=URLError('CA missing')) as url,patch('quality_registry.shutil.which',return_value='gh'),patch('quality_registry.subprocess.run',side_effect=subprocess.TimeoutExpired('gh',15)) as gh:
            _,outcomes=self.store.refresh_github(self.data,TODAY,fetch=github_snapshot)
        self.assertEqual(outcomes[0]['action'],'failed')
        self.assertEqual(url.call_count+gh.call_count,2)

    def test_second_url_attempt_cannot_add_a_third_gh_request(self):
        self.add(self.item())
        success=subprocess.CompletedProcess([],0,'{"full_name":"fixture/export","stargazers_count":1}','')
        with patch('quality_registry.urlopen',side_effect=[HTTPError('url',500,'server',None,None),URLError('reset')]) as url,patch('quality_registry.shutil.which',return_value='gh'),patch('quality_registry.subprocess.run',return_value=success) as gh:
            _,outcomes=self.store.refresh_github(self.data,TODAY,fetch=github_snapshot)
        self.assertEqual(url.call_count+gh.call_count,2)
        self.assertEqual(outcomes[0]['action'],'failed')

    def test_future_snapshot_rejected_and_older_snapshot_not_overwritten(self):
        self.data,_=self.store.merge(self.data,{'repository_snapshots':[self.snapshot(stars=1)]},TODAY)
        updated,_=self.store.merge(self.data,{'repository_snapshots':[self.snapshot(stars=999,observed='2026-10-01T00:00:00Z')]},TODAY)
        self.assertEqual(updated,self.data)
        with self.assertRaises(ValueError):self.store.merge(self.data,{'repository_snapshots':[self.snapshot(observed='2099-01-01')]},TODAY)

    def test_cli_query_is_read_only_and_incomplete_exit_is_distinct(self):
        self.add(self.item(complete=False));self.store.commit(self.data,TODAY,digest(self.store.load(TODAY)))
        before=file_manifest(self.store.home)
        cmd=[sys.executable,'-B',str(Path(__file__).with_name('quality_store.py')),'query','--agents-home',str(self.store.home),'--as-of',str(TODAY),'--require-complete']
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(json.loads(result.stdout)['summary']['assessment_complete'])
        self.assertEqual(file_manifest(self.store.home),before)

    def test_cli_incremental_update_uses_stdin_and_only_fixed_files(self):
        item=self.item()
        cmd=[sys.executable,'-B',str(Path(__file__).with_name('quality_store.py')),'update','--agents-home',str(self.store.home),'--as-of',str(TODAY),'--apply','--expected-revision',digest(self.data),'--input','-']
        result=subprocess.run(cmd,input=json.dumps({'profiles':[item]}),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['changed_profiles'],1)
        self.assertEqual(self.store.load(TODAY)['profiles'],[item])
        self.assertEqual({p.name for p in self.store.directory.iterdir()},{'SKILL_QUALITY.json','SKILL_QUALITY.md'})

    def test_query_exposes_reference_estimate_without_completing_measured_assessment(self):
        p=self.item(complete=False);p['review_assessment']=reviewed()['review_assessment'];p['review_assessment']['revision']=p['revision']
        self.add(p);self.data,_=self.store.merge(self.data,{'repository_snapshots':[self.snapshot(stars=99999)]},TODAY)
        result=self.store.query(self.data,TODAY,check_current=True)
        self.assertIn('reference_reviewed',result['summary'])
        self.assertEqual(result['summary']['reference_reviewed'],1)
        self.assertEqual(result['summary']['reference_numeric'],1)
        self.assertEqual(result['summary']['complete'],0)
        self.assertEqual(result['profiles'][0]['reference']['total'],84.5)
        self.assertIsNone(result['profiles'][0]['total'])

    def test_package_change_expires_the_reference_estimate(self):
        p=self.item(complete=False);p['review_assessment']=reviewed()['review_assessment'];p['review_assessment']['revision']=p['revision'];self.add(p)
        Path(p['entry']).write_text('Changed workflow')
        result=self.store.query(self.data,TODAY,check_current=True)
        self.assertIn('reference',result['profiles'][0])
        self.assertEqual(result['profiles'][0]['reference']['status'],'stale')
        self.assertIsNone(result['profiles'][0]['reference']['total'])
        self.assertEqual(result['summary']['reference_reviewed'],0)


if __name__=='__main__':unittest.main()
