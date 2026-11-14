"""Host checks for approved wording and narrow migration boundaries."""
import ast,json,subprocess,unittest,time,traceback
from types import SimpleNamespace
from pathlib import Path
from customer_ij_validation_support import DATA,migrated_hash,expected_feedback
ROOT=Path(__file__).resolve().parents[2]
class SourceContract(unittest.TestCase):
 def test_late_day7_assertion_fails_closed(self):
  source=ROOT/'Scripts/Unreal/validate_day_week.py'
  handler=next(n for n in ast.parse(source.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef)and n.name=='tick')
  def late_failure():
   if False:yield
   raise AssertionError('late final History check')
  result={'pass':True,'complete':False};writes=[]
  scope={'phase':{'gen':late_failure(),'end':None,'busy':False},'R':result,'time':time,'started':time.monotonic(),'traceback':traceback,'save':lambda:writes.append(dict(result)),'level':SimpleNamespace(editor_request_end_play=lambda:None)}
  exec(compile(ast.Module(body=[handler],type_ignores=[]),str(source),'exec'),scope);scope['tick'](0.1)
  self.assertFalse(result['pass']);self.assertTrue(result['complete']);self.assertIn('late final History check',result['fatal']);self.assertEqual(writes[-1],result)
 def test_content_lock_matches_document(self):
  doc=(ROOT/'Docs/Architecture/Day7EndingContentPlan.md').read_text(encoding='utf8')
  for identity,source in DATA.items():
   for row,text in source['rows'].items():
    lines=[line for line in doc.splitlines()if line.startswith('| '+row+' |')]
    self.assertEqual(len(lines),1);self.assertEqual(lines[0].split('|')[3].strip(),text)
   for text in source['reactions'].values():self.assertIn(text,doc)
 def test_no_existing_record_or_candidate_change(self):
  before=json.loads(subprocess.check_output(['git','show','HEAD:Scripts/Unreal/record_expansion.json'],cwd=ROOT))
  after=json.loads((ROOT/'Scripts/Unreal/record_expansion.json').read_text(encoding='utf8'))
  self.assertEqual(before['records'],after['records'])
  for key,value in before['candidates'].items():self.assertEqual(after['candidates'][key],value)
 def test_migration_rejects_unknown_baseline(self):
  ref=json.loads((ROOT/'Scripts/Unreal/customer_ij_reference.json').read_text())
  for path,item in ref['packages'].items():
   self.assertEqual(migrated_hash(path,item['before']),item['after'])
   with self.assertRaises(AssertionError):migrated_hash(path,'unknown')
  self.assertEqual(migrated_hash('unrelated','unchanged'),'unchanged')
 def test_each_result_keeps_heading_and_exit(self):
  for identity,source in DATA.items():
   for score in range(4):
    text=expected_feedback(identity,score);self.assertTrue(text.endswith('\n\n'+source['reactions']['ExitText']))
    self.assertIn('/ 3',text.split('\n')[0])
if __name__=='__main__':unittest.main()
