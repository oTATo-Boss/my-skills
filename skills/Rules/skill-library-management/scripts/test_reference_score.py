"""Reference estimates stay separate from verified task results."""
import copy
from datetime import date
import unittest

import quality_registry as quality
from test_quality_registry import profile

TODAY=date(2026,10,30)


def reviewed():
    p=profile()
    p['metrics']['effect'].update(status='unverified',points=None,evidence=[])
    p['review_assessment']={
        'evaluated_at':'2026-10-30','version':'1','revision':'fixture-revision-1',
        'basis':'content_review','confidence':'medium',
        'task':{'input':'UTF-8 text','output':'JSON string','acceptance':['Valid JSON','Preserves text']},
        'dimensions':{k:{'points':v,'reason':'Read workflow and checked its declared limits; not runtime certification.'} for k,v in [('effect',20),('reliability',16),('capability',13),('maintenance',8)]},
        'reviewed_files':['fixture/SKILL.md','fixture/SOURCE.md'],
        'runtime_evidence':[],
        'github_review':{'repository':'fixture/export','scope':'dedicated','attribution':'confirmed','reason':'Original source confirmed.'},
        'ownership_review':{'kind':'original','contribution':None,'reason':'Original workflow and implementation confirmed.'}}
    return p


def snapshots(stars=99999):
    return {'fixture/export':{'snapshot':{'status':'verified','stars':stars,'observed_at':'2026-10-30T08:00:00Z'}}}


class ReferenceTests(unittest.TestCase):
    def evaluate(self,p=None,facts=None,today=TODAY):
        fn=getattr(quality,'reference_score',None)
        self.assertTrue(callable(fn),'Missing reference assessment calculator')
        return fn(p or reviewed(),snapshots() if facts is None else facts,today)

    def test_reference_total_does_not_certify_actual_effect_or_replace_verified_score(self):
        p=reviewed();before=copy.deepcopy(p);r=self.evaluate(p)
        self.assertEqual(r['total'],84.5)
        self.assertEqual(r['quality_points'],57)
        self.assertEqual(r['basis'],'content_review')
        self.assertEqual(r['raw_stars'],99999)
        self.assertEqual(r['github_observed_at'],'2026-10-30T08:00:00Z')
        self.assertIsNone(quality.score(p,TODAY)['total'])
        self.assertEqual(p,before)

    def test_unknown_star_gives_explicit_range_not_an_actual_zero(self):
        r=self.evaluate(facts={})
        self.assertIsNone(r['total']);self.assertIsNone(r['github_points'])
        self.assertEqual((r['minimum'],r['maximum']),(72,87))

    def test_collection_and_personal_preference_are_distinct_from_quality(self):
        p=reviewed();p['review_assessment']['github_review']['scope']='collection'
        p['review_assessment']['ownership_review']['kind']='collected'
        r=self.evaluate(p)
        self.assertEqual(r['quality_points'],57);self.assertEqual(r['github_points'],6.25)
        self.assertEqual(r['ownership_points'],0);self.assertEqual(r['total'],63.25)

    def test_real_zero_and_unknown_scope_are_not_confused(self):
        self.assertEqual(self.evaluate(facts=snapshots(0))['github_points'],0)
        p=reviewed();p['review_assessment']['github_review']['scope']='unknown'
        self.assertIsNone(self.evaluate(p)['github_points'])

    def test_deep_adaptation_requires_supported_fraction_not_full_authorship(self):
        p=reviewed();p['review_assessment']['ownership_review'].update(kind='deep_adapted',contribution=None)
        self.assertIsNone(self.evaluate(p)['ownership_points'])
        p['review_assessment']['ownership_review']['contribution']=0.6
        self.assertEqual(self.evaluate(p)['ownership_points'],9)
        p['review_assessment']['ownership_review']['contribution']=1
        with self.assertRaises(ValueError):self.evaluate(p)

    def test_bad_or_future_review_is_rejected(self):
        for value in [True,26,float('nan')]:
            p=reviewed();p['review_assessment']['dimensions']['effect']['points']=value
            with self.assertRaises(ValueError):self.evaluate(p)
        p=reviewed();p['review_assessment']['evaluated_at']='2099-01-01'
        with self.assertRaises(ValueError):self.evaluate(p)
        p=reviewed();p['review_assessment']['dimensions']['effect']['reason']=''
        with self.assertRaises(ValueError):self.evaluate(p)

    def test_old_repository_fact_keeps_uncertainty(self):
        facts=snapshots();facts['fixture/export']['snapshot']['observed_at']='2026-10-01T00:00:00Z'
        self.assertIsNone(self.evaluate(facts=facts)['github_points'])

    def test_missing_review_is_not_a_default_score(self):
        p=reviewed();del p['review_assessment']
        self.assertIsNone(self.evaluate(p))

    def test_invalid_review_lists_are_rejected_before_persistence(self):
        for key,value in [('limitations',None),('strengths','good'),('runtime_evidence',[None])]:
            p=reviewed();p['review_assessment'][key]=value
            with self.assertRaises(ValueError):self.evaluate(p)

    def test_query_reference_includes_its_actual_rationale_and_evidence(self):
        p=reviewed();r=self.evaluate(p)
        self.assertEqual(r['assessment']['dimensions'],p['review_assessment']['dimensions'])
        self.assertEqual(r['assessment']['reviewed_files'],p['review_assessment']['reviewed_files'])
        r['assessment']['dimensions']['effect']['points']=0
        self.assertEqual(p['review_assessment']['dimensions']['effect']['points'],20)


if __name__=='__main__':unittest.main()
