"""Current production editor startup/quit control: no PIE, compile, or gameplay."""
import json,os
from pathlib import Path
import unreal
Path(os.environ['MVP_RESULT']).write_text(json.dumps({'complete':True,'pass':True,'control':'editor startup only; no PIE, explicit Blueprint compilation, gameplay, fixtures or input','world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()},indent=2),encoding='utf-8')
unreal.log('MVP_EDITOR_ONLY_CONTROL_BEFORE_QUIT')
unreal.SystemLibrary.quit_editor()
