"""Editor-only lifecycle guards; recompile and save the final checkpoint normally."""
import json,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable'
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager'
TU='/Game/RecordShop/UI/Turntable/WBP_Turntable'
SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect'
RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
R={'complete':False,'saved':[]}
try:
 tt=unreal.load_asset(TT);reset=G.get_graph_editor_by_name(tt,'SetRecord')
 assert not any(str(n.get_node_title())=='Is Valid' for n in reset.list_all_nodes()),'Already hardened'
 # Do not replace the owned record while its actual AudioComponent is playing.
 entry=reset.find_graph_entry_pin();down=entry.list_connected_pins()[0];entry.break_pin_links()
 _,bad=valid(reset,get(reset,'PlaybackAudio'),entry);link(bad,down)
 assets=[tt]
 for path in [TU,SU,RU]:
  bp=unreal.load_asset(path);g=evgraph(bp);event=action(g,'Destruct')
  if path==TU:
   node=setv(g,'TurntableRef')
  else:
   node=action(g,'UnbindAllEventsfrom'+('OnRecordSelected' if path==SU else 'OnContinue'))
  link(event.find_then_pin(),node.find_execute_pin());assets.append(bp)
 # Persist compiler GUID fixups with normal diagnostics for all changed assets.
 for path in [FLOW,'/Game/DialogueManager','/Game/RecordShop/Interaction/Actors/BP_RecordShelf']:
  assets.append(unreal.load_asset(path))
 R['compiles']={a.get_path_name():L.compile_blueprint(a) for a in assets}
 assert all(R['compiles'].values())
 for a in assets:
  assert unreal.EditorAssetLibrary.save_loaded_asset(a);R['saved'].append(a.get_path_name())
 R['complete']=True
except Exception:R['fatal']=traceback.format_exc()
finally:
 (ROOT/'Saved/MVPCompletion/harden.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
 unreal.SystemLibrary.quit_editor()
