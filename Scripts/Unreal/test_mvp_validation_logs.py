"""Host-side regression tests for the runtime-error safety gate."""
import unittest
from mvp_validation_logs import classify_log


def smoke_block(count=15):
    return ('LogTemp: Error test: UE::UnifiedErrorTest::Empty: [localized engine test]\n'
            + 'LogAutomationTest: Error: Condition failed\n' * count
            + 'LogEngine: Initializing Engine...\n')


class LogGateTests(unittest.TestCase):
    def test_exact_startup_block_is_reported_separately(self):
        report = classify_log(smoke_block() + 'MVP_VALIDATION_SCRIPT_BEGIN\n')
        self.assertTrue(report['gameplay_log_pass'])
        self.assertFalse(report['globally_error_free'])
        self.assertEqual(len(report['known_startup_engine_smoke_errors']), 15)

    def test_audited_player_controller_error_fails(self):
        report = classify_log(smoke_block() + 'MVP_VALIDATION_SCRIPT_BEGIN\n'
                              + 'LogPlayerController: Error: InputMode:UIOnly - Attempting to focus Non-Focusable widget SObjectWidget\n')
        self.assertFalse(report['gameplay_log_pass'])
        self.assertEqual(len(report['unexpected_errors']), 1)

    def test_additional_or_gameplay_automation_errors_fail(self):
        for text in [smoke_block(16), smoke_block() + 'LogAutomationTest: Error: Condition failed\n',
                     'MVP_VALIDATION_SCRIPT_BEGIN\n' + smoke_block(),
                     'LogAutomationTest: Error: Something else\n']:
            with self.subTest(text=text):
                self.assertFalse(classify_log(text)['gameplay_log_pass'])

    def test_blueprint_ensure_fatal_and_missing_logs_fail(self):
        for text in ['', 'LogScript: Warning: Accessed None reading Foo',
                     'LogOutputDevice: Warning: Blueprint Runtime Error: bad reference',
                     'Ensure condition failed: false', 'Assertion failed: false',
                     'Unhandled Exception: EXCEPTION_ACCESS_VIOLATION', 'LogPython: Error: failed']:
            with self.subTest(text=text):
                self.assertFalse(classify_log(text)['gameplay_log_pass'])

    def test_clean_commandlet_passes(self):
        self.assertTrue(classify_log('LogExit: Exiting')['globally_error_free'])


if __name__ == '__main__':
    unittest.main()
