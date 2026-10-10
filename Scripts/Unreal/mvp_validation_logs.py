"""Fail closed on runtime errors; identify the exact retained startup smoke failure."""
import re


def classify_log(text):
    lines = text.splitlines()
    errors = []
    startup = []
    initialized = next((i for i, line in enumerate(lines) if 'LogEngine: Initializing Engine...' in line), -1)
    smoke = [i for i, line in enumerate(lines) if re.search(r'LogAutomationTest: Error: Condition failed\s*$', line)]
    # This exact 15-line contiguous engine startup block was reproduced without
    # project Python or PIE. Never allow the same message in gameplay, additional
    # messages, or a different automation failure to inherit this classification.
    known = (len(smoke) == 15 and smoke == list(range(smoke[0], smoke[0] + 15))
             and smoke[-1] < initialized
             and any('LogTemp: Error test: UE::UnifiedErrorTest::Empty:' in line
                     for line in lines[max(0, smoke[0] - 8):smoke[0]])
             and not any('MVP_VALIDATION_SCRIPT_BEGIN' in line or 'MVP_STAGE ' in line
                         for line in lines[:smoke[-1] + 1]))
    for i, line in enumerate(lines):
        if known and i in smoke:
            startup.append({'line': i + 1, 'text': line})
        elif (re.search(r'\b(?:Error|Fatal):', line)
              or re.search(r'Accessed None|Blueprint Runtime Error|Ensure condition failed|Assertion failed|Unhandled Exception', line, re.I)):
            errors.append({'line': i + 1, 'text': line})
    return {'log_present': bool(text), 'unexpected_errors': errors,
            'known_startup_engine_smoke_errors': startup,
            'gameplay_log_pass': bool(text) and not errors,
            'globally_error_free': bool(text) and not errors and not startup}
