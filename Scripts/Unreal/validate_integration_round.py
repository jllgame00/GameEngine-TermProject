"""Compatibility entry point for the maintained isolated regression suite.

Run with run_mvp_validation.py, or Invoke-IntegrationPython.ps1 -Editor.
These diagnostics include direct calls and are not natural E2E evidence;
use validate_mvp_cycle.py for the contiguous input-driven customer cycle.
No production asset or map is saved.
"""
import os
from pathlib import Path
import sys

import unreal

root = Path(unreal.Paths.project_dir())
scripts = root / 'Scripts/Unreal'
sys.path.insert(0, str(scripts))
if 'MVP_RESULT' not in os.environ:
    output = root / 'Saved/MVPCompletion/integration-regressions.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    os.environ['MVP_RESULT'] = str(output)

# Execute in this script's globals so Slate callbacks retain the same lifetime
# as a direct -ExecutePythonScript invocation of the maintained suite.
suite = scripts / 'validate_mvp_regressions.py'
exec(compile(suite.read_text(encoding='utf-8-sig'), str(suite), 'exec'))
