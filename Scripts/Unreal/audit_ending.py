"""Read-only production graph, modal, UI and defaults audit before Ending changes."""
import unreal,json,os,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import L,G
R={'complete':False,'pass':False,'read_only':True}
def graph(bp,name):
 return [{'id':n.get_name(),'class':n.get_class().get_name(),'title':str(n.get_node_title()),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in G.get_graph_editor_by_name(bp,name).list_all_nodes()]
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 R['graphs']={};R['functions']={};R['variables']={}
 for path in ('/Game/RecordShop/Core/Flow/BP_GameFlowManager','/Game/RecordShop/Interaction/Components/BPC_Interaction','/Game/RecordShop/Interaction/Actors/BP_RecordShelf','/Game/RecordShop/Interaction/Actors/BP_Turntable','/Game/RecordShop/Characters/Customers/Common/BP_Customer','/Game/RecordShop/UI/Prologue/WBP_Prologue','/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter'):
  bp=unreal.load_asset(path);names=[str(g.get_name())for g in L.list_graphs(bp)];R['functions'][path]=names;R['variables'][path]=list(map(str,L.list_member_variable_names(bp,False)))
  R['graphs'][path]={name:graph(bp,name)for name in names if path.endswith('BP_GameFlowManager')or name=='EventGraph'or 'Modal'in name or 'Interact'in name}
 flow=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager');cdo=unreal.get_default_object(flow.generated_class())
 R['defaults']={k:str(cdo.get_editor_property(k))for k in ('CurrentState','DayPhase','CurrentDay','PrologueStage','TutorialComplete','FinalStoryEventTriggered','StoreBGMVolume','StoreBGMFadeInDuration','StoreBGMFadeOutDuration')}
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
 R['widgets']=[str(a.package_name)for a in registry.get_assets_by_path('/Game',True)if str(a.asset_class_path.asset_name)=='WidgetBlueprint']
 ui=unreal.load_asset('/Game/RecordShop/UI/Prologue/WBP_Prologue');tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree)if t.get_outer()==ui)
 R['widget_tree']=[dict(name=w.get_name(),kind=w.get_class().get_name(),parent=w.get_parent().get_name()if w.get_parent()else None)for w in unreal.ObjectIterator(unreal.Widget)if w.get_outer()==tree]
 R['widget_authoring_docs']={name:getattr(unreal.EditorUtilityLibrary,name).__doc__ for name in dir(unreal.EditorUtilityLibrary)if 'source_widget'in name}
 R['game_mode_options_doc']=unreal.GameModeBase.__doc__[:200]
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
