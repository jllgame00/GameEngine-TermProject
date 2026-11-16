"""Fail-closed startup-smoke classification, including slow struct-init interleaving."""
import unittest
from mvp_validation_logs import classify_log
HEADER=['LogTemp: Error test: UE::UnifiedErrorTest::Empty: [test]',
        'LogTemp: Error with param: UE::UnifiedErrorTest::WithInt: [test]',
        'LogTemp: Error with context: UE::UnifiedErrorTest::Empty: [test]',
        'LogTemp: FError that has been invalidated: ::: []',
        'LogTemp: FError that has been moved from: ::: []']
SMOKE=['LogAutomationTest: Error: Condition failed']*15
INIT='LogEngine: Initializing Engine...'
SCRIPT='LogPython: MVP_VALIDATION_SCRIPT_BEGIN'
def log(*parts):return '\n'.join(x for part in parts for x in ([part]if isinstance(part,str)else part))
class ClassificationTests(unittest.TestCase):
 def test_original_startup_signature(self):
  r=classify_log(log(HEADER,SMOKE,INIT,SCRIPT));self.assertEqual(len(r['known_startup_engine_smoke_errors']),15);self.assertTrue(r['gameplay_log_pass']);self.assertFalse(r['globally_error_free'])
 def test_slow_struct_initialization_still_exact_startup_block(self):
  slow=['LogClass: Display: AttemptToFindUninitializedScriptStructMembers took more than 1ms to process ScriptStruct /Script/Engine.Fixture'+str(i)for i in range(12)]
  r=classify_log(log(HEADER,slow,SMOKE,INIT,SCRIPT));self.assertEqual(len(r['known_startup_engine_smoke_errors']),15);self.assertEqual(r['unexpected_errors'],[])
 def test_same_signature_after_engine_init_fails(self):
  self.assertFalse(classify_log(log(INIT,HEADER,SMOKE,SCRIPT))['gameplay_log_pass'])
 def test_same_signature_in_gameplay_fails(self):
  self.assertFalse(classify_log(log(SCRIPT,HEADER,SMOKE,INIT))['gameplay_log_pass'])
 def test_extra_condition_fails(self):
  self.assertFalse(classify_log(log(HEADER,SMOKE,[SMOKE[0]],INIT,SCRIPT))['gameplay_log_pass'])
 def test_other_error_cannot_hide_in_bridge(self):
  r=classify_log(log(HEADER,'LogTemp: Error: actual package failure',SMOKE,INIT,SCRIPT));self.assertFalse(r['gameplay_log_pass']);self.assertEqual(r['known_startup_engine_smoke_errors'],[])
 def test_other_display_does_not_qualify_bridge(self):
  self.assertFalse(classify_log(log(HEADER,'LogTemp: Display: unrelated test',SMOKE,INIT,SCRIPT))['gameplay_log_pass'])
 def test_separated_conditions_fail(self):
  self.assertFalse(classify_log(log(HEADER,SMOKE[:7],'LogTemp: Display: gap',SMOKE[7:],INIT,SCRIPT))['gameplay_log_pass'])
 def test_no_signature_or_engine_init_fails(self):
  self.assertFalse(classify_log(log(SMOKE,INIT,SCRIPT))['gameplay_log_pass']);self.assertFalse(classify_log(log(HEADER,SMOKE,SCRIPT))['gameplay_log_pass'])
 def test_runtime_error_after_known_startup_is_not_suppressed(self):
  r=classify_log(log(HEADER,SMOKE,INIT,SCRIPT,'LogScript: Warning: Accessed None'));self.assertFalse(r['gameplay_log_pass']);self.assertEqual(len(r['unexpected_errors']),1)
 def test_missing_log_fails(self):self.assertFalse(classify_log('')['gameplay_log_pass'])
if __name__=='__main__':unittest.main()
