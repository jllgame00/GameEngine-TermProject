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
    header = ('LogTemp: Error test: UE::UnifiedErrorTest::Empty:',
              'LogTemp: Error with param: UE::UnifiedErrorTest::WithInt:',
              'LogTemp: Error with context: UE::UnifiedErrorTest::Empty:',
              'LogTemp: FError that has been invalidated: ::: []',
              'LogTemp: FError that has been moved from: ::: []')
    allowed = header + ('LogClass: Display: AttemptToFindUninitializedScriptStructMembers '
                        'took more than 1ms to process ScriptStruct ',)
    marker = max((i for i, line in enumerate(lines[:smoke[0] if smoke else 0])
                  if header[0] in line), default=-1)
    bridge = lines[marker:smoke[0]] if marker >= 0 and smoke else []
    # Slow engine initialization can insert any number of these exact struct
    # timing diagnostics. Recognize structure, not an arbitrary line-distance;
    # unrelated lines/errors cannot make a different test inherit the exception.
    bridge_valid = (bool(bridge)
                    and all(any(token in line for line in bridge) for token in header)
                    and all(any(token in line for token in allowed) for line in bridge))
    known = (len(smoke) == 15 and smoke == list(range(smoke[0], smoke[0] + 15))
             and smoke[-1] < initialized and bridge_valid
             and not any('MVP_VALIDATION_SCRIPT_BEGIN' in line or 'MVP_STAGE ' in line
                         for line in lines[:smoke[-1] + 1]))
    for i, line in enumerate(lines):
        if known and i in smoke:
            startup.append({'line': i + 1, 'text': line})
        elif (re.search(r'\b(?:Error|Fatal):', line)
              # Unreal emits this as a Warning, but a persisted production node
              # without identity is not ready for deterministic cooking.
              or re.search(r"\bNode '/Game/[^']+' missing NodeGuid\b", line)
              or re.search(r'Accessed None|Blueprint Runtime Error|Ensure condition failed|Assertion failed|Unhandled Exception', line, re.I)):
            errors.append({'line': i + 1, 'text': line})
    return {'log_present': bool(text), 'unexpected_errors': errors,
            'known_startup_engine_smoke_errors': startup,
            'gameplay_log_pass': bool(text) and not errors,
            'globally_error_free': bool(text) and not errors and not startup}
