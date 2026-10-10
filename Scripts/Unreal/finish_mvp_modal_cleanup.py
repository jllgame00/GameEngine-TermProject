"""Synchronously clear removed-modal references; Destruct may be delayed by Slate."""
import sys,json,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager'
TU='/Game/RecordShop/UI/Turntable/WBP_Turntable'
SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect'
RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
R={'complete':False,'saved':[]}
def insert(previous,node):
 down=list(previous.list_connected_pins());previous.break_pin_links();link(previous,node.find_execute_pin())
 for p in down:link(node.find_then_pin(),p)
try:
 turnui=unreal.load_asset(TU);selection=unreal.load_asset(SU);flow=unreal.load_asset(FLOW)
 for bp in [turnui,selection]:
  for graph in L.list_graphs(bp):
   g=G.get_graph_editor(graph)
   removes=[n for n in g.list_all_nodes() if str(n.get_node_title())=='RemoveFromParent']
   for remove in removes:
    n=setv(g,'TurntableRef') if bp==turnui else action(g,'UnbindAllEventsfromOnRecordSelected')
    insert(remove.find_then_pin(),n)
 cleanup=G.get_graph_editor_by_name(flow,'CloseRecordShopInteractionModals')
 for node_name,path,suffix in [('K2Node_CallFunction_1',SU,'CastToWBP_RecordSelect'),('K2Node_CallFunction_3',TU,'CastToWBP_Turntable')]:
  remove=next(n for n in cleanup.list_all_nodes() if n.get_name()==node_name)
  widget=pin(remove,'self').list_connected_pins()[0]
  cast=action(cleanup,suffix,[widget]);link(remove.find_then_pin(),cast.find_execute_pin())
  obj=next(p for p in cast.list_all_pins() if str(p.get_pin_name()).startswith('As'))
  if path==TU:
   n=cleanup.add_set_member_variable_node('TurntableRef',TU+'.WBP_Turntable_C');link(obj,pin(n,'self'))
  else:n=action(cleanup,'UnbindAllEventsfromOnRecordSelected',[obj],cls(SU))
  link(cast.find_then_pin(),n.find_execute_pin())
 close=G.get_graph_editor_by_name(flow,'CloseResult')
 remove=next(n for n in close.list_all_nodes() if str(n.get_node_title())=='RemoveFromParent')
 unbind=action(close,'UnbindAllEventsfromOnContinue',[get(close,'ResultWidgetRef')],cls(RU));insert(remove.find_then_pin(),unbind)
 assets=[turnui,selection,flow]
 R['compiles']={a.get_path_name():L.compile_blueprint(a) for a in assets};assert all(R['compiles'].values())
 for a in assets:
  assert unreal.EditorAssetLibrary.save_loaded_asset(a);R['saved'].append(a.get_path_name())
 R['complete']=True
except Exception:R['fatal']=traceback.format_exc()
finally:
 (ROOT/'Saved/MVPCompletion/modal-cleanup.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
 unreal.SystemLibrary.quit_editor()
