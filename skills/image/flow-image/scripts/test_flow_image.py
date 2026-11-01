import importlib.util,unittest,tempfile,contextlib,io,sys
from unittest.mock import patch
from pathlib import Path
class DriverTests(unittest.TestCase):
 def load(self):
  p=Path(__file__).with_name('flow_image.py');self.assertTrue(p.exists(),'Flow CLI driver is not implemented yet')
  s=importlib.util.spec_from_file_location('flow_image',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_model_is_verified_before_submit(self):
  m=self.load()
  with self.assertRaises(ValueError):m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana Pro x1','draft':''})
  with self.assertRaises(ValueError):m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana 2.1 x1','draft':'unfinished user prompt'})
  m.validate_state({'url':m.PROJECT_URL,'account_ok':True,'model_text':'Nano Banana 2.1 x1','draft':''})
 def test_does_not_mistake_old_or_unready_images_for_results(self):
  m=self.load();baseline={'old'}
  rows=[{'id':'new','position':0,'width':1024,'height':1024},{'id':'old','position':1,'width':1024,'height':1024},{'id':'late-old','position':2,'width':1024,'height':1024}]
  self.assertEqual(m.new_images(rows,baseline)[0]['id'],'new')
  self.assertEqual(m.new_images([dict(rows[0],width=0),rows[1]],baseline),[])
  self.assertEqual(m.new_images([rows[1],rows[2]],baseline),[])
 def test_accepts_cli_serialized_auto_connect_flag_without_restart(self):
  m=self.load();calls=[]
  def fake(*args,**kwargs):
   calls.append(args)
   return 'daemon is running.\npid=44561 version=1.12.0\nargs=["--auto-connect"]'
  m.run_cli=fake
  self.assertIn('44561',m.ensure_daemon())
  self.assertEqual(calls,[('status',)])
 def test_bad_reference_is_rejected_before_browser_or_submission(self):
  m=self.load()
  with self.assertRaisesRegex(ValueError,'Reference'):
   m.validate_reference(Path('/missing-reference.jpg'))
 def test_uploaded_reference_is_not_treated_as_a_generated_result(self):
  m=self.load()
  rows=[{'id':'result','position':0,'width':1024,'height':1024},{'id':'upload','position':1,'width':1024,'height':1024},{'id':'old','position':2,'width':1024,'height':1024}]
  self.assertEqual([r['id'] for r in m.new_images(rows,{'upload','old'})],['result'])
 def test_ready_reference_requires_a_loaded_nonbusy_chip(self):
  m=self.load()
  self.assertFalse(m.references_ready([]))
  self.assertFalse(m.references_ready([{'busy':True,'width':1024,'height':1024}]))
  self.assertFalse(m.references_ready([{'busy':False,'width':0,'height':0}]))
  self.assertTrue(m.references_ready([{'busy':False,'width':1024,'height':1024}]))
 def test_old_failure_does_not_fail_a_new_request(self):
  m=self.load()
  self.assertFalse(m.has_new_failure(1,1))
  self.assertTrue(m.has_new_failure(2,1))
 def test_every_reference_must_be_ready_before_submission(self):
  m=self.load();ready={'busy':False,'width':1024,'height':1024}
  self.assertTrue(m.references_ready([ready,ready],expected=2))
  self.assertFalse(m.references_ready([ready],expected=2))
  self.assertFalse(m.references_ready([ready,dict(ready,busy=True)],expected=2))
  self.assertFalse(m.references_ready([ready,dict(ready,width=0)],expected=2))
  self.assertFalse(m.references_ready([ready,ready,ready],expected=2))
 def test_repeated_ref_arguments_reach_generation_in_order(self):
  m=self.load();seen=[]
  with tempfile.TemporaryDirectory() as d:
   m.ROOT=Path(d);m.CONFIG={'account':'test','project':'test'}
   m.generate=lambda *args:seen.append(args) or {'ok':True}
   with patch.object(sys,'argv',['flow-image','image','combine','--ref','/a.jpg','--ref','/b.png','--output','/out.jpg']),contextlib.redirect_stdout(io.StringIO()):
    self.assertEqual(m.main(),0)
  self.assertEqual(seen[0][3],[Path('/a.jpg'),Path('/b.png')])
 def test_invalid_second_reference_stops_before_browser_activity(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);first=root/'a.jpg';first.write_bytes(b'\xff\xd8\xff'+b'0'*16)
   m.PENDING=root/'pending.json'
   m.ensure_daemon=lambda:self.fail('Browser must not be touched for an invalid second reference')
   with self.assertRaisesRegex(ValueError,'Reference'):
    m.generate('combine',root/'output.jpg','1:1',[first,root/'missing.png'])
if __name__=='__main__' :unittest.main()
