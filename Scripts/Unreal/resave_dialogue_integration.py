"""Recompile and resave only the dialogue integration assets after Editor GUID fixup."""
import json,traceback
from pathlib import Path
import unreal
out={'complete':False,'compiles':{},'saved':[]}
try:
    for path in ['/Game/RecordShop/UI/Dialogue/WBP_Dialogue','/Game/RecordShop/Core/Flow/BP_GameFlowManager','/Game/RecordShop/Interaction/Actors/BP_RecordShelf','/Game/RecordShop/Interaction/Actors/BP_Turntable']:
        bp=unreal.load_asset(path)
        out['compiles'][path]=unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        assert out['compiles'][path]
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
        out['saved'].append(path)
    out['complete']=True
except Exception:out['error']=traceback.format_exc()
Path(unreal.Paths.project_dir(),'Saved/OvernightIntegration/Round1/worker-resave.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
unreal.SystemLibrary.quit_editor()
