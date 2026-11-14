"""Host checks for immutable approved copy and exact production migration boundaries."""
import ast,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class EndingSource(unittest.TestCase):
 def test_locked_copy(self):
  data=json.loads((ROOT/'Scripts/Unreal/ending_content.json').read_text(encoding='utf8'));p=data['pages']
  self.assertEqual(p[0]['body'],'마지막 손님이 가게를 나섰다.\n부모님에게서 짧은 연락이 왔다.')
  self.assertEqual(p[1]['body'],'오늘이 마지막 날이네.\n일주일 동안 가게 맡아줘서 고마워.\n마감하면 편히 쉬렴.')
  self.assertEqual(p[2]['body'],'오늘 손님도 다 다녀가셨어요.\n이제 마감할게요.')
  self.assertEqual((p[3]['title'],p[3]['action']),('일주일의 운영을 마쳤습니다.','크레딧 보기'))
  self.assertEqual((p[-1]['title'],p[-1]['action']),('함께해 주셔서 고맙습니다.','타이틀로'))
  self.assertEqual(len(p),9)
 def test_unknown_credits_do_not_invent_rights(self):
  data=json.loads((ROOT/'Scripts/Unreal/ending_content.json').read_text(encoding='utf8'))
  unknown=[x for x in data['credits_sources']if x['status']=='CREDIT_VERIFICATION_REQUIRED'];self.assertEqual(len(unknown),3)
  for entry in unknown:self.assertNotIn('license',entry);self.assertNotIn('author',entry)
  self.assertIn('정우빈 — Integration / Core Flow / Camera',data['pages'][4]['body'])
 def test_exact_hash_migration(self):
  from ending_validation_support import reference,migrated_hash
  for path,item in reference()['packages'].items():
   self.assertEqual(migrated_hash(path,item['before']),item['after'])
   with self.assertRaises(AssertionError):migrated_hash(path,'unknown')
  self.assertEqual(migrated_hash('unrelated','same'),'same')
 def test_runner_fails_closed_on_fatal(self):
  tree=ast.parse((ROOT/'Scripts/Unreal/run_mvp_validation.py').read_text(encoding='utf8'))
  node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Subscript)and isinstance(t.slice,ast.Constant)and t.slice.value=='process_pass'for t in n.targets))
  scope={'code':0,'summary':dict(complete=True,assertions_pass=True,gameplay_log_pass=True,fatal='late assertion')}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'runner-pass-guard','exec'),scope);self.assertFalse(scope['summary']['process_pass'])
  scope['summary']['fatal']=None;exec(compile(ast.Module(body=[node],type_ignores=[]),'runner-pass-guard','exec'),scope);self.assertTrue(scope['summary']['process_pass'])
if __name__=='__main__':unittest.main()
