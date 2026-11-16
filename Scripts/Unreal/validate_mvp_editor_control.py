"""Current production editor startup/quit control: no PIE, compile, or gameplay."""
import json,os
from pathlib import Path
import unreal
Path(os.environ['MVP_RESULT']).write_text(json.dumps({'complete':True,'pass':True,'control':'editor startup only; no PIE, explicit Blueprint compilation, gameplay, fixtures or input','world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()},indent=2),encoding='utf-8')
unreal.log('MVP_EDITOR_ONLY_CONTROL_BEFORE_EXECUTOR_EXIT')
# Let -ExecutePythonScript finish its notification before queuing QUIT_EDITOR.
# Direct quit_editor() leaves that notification for plugin shutdown, after the
# core ticker reset; its deferred Slate text destruction can outlive ICU.
unreal.EditorPythonScripting.set_keep_python_script_alive(False)
