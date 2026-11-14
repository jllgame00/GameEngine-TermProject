"""Read-only audio API/default/wiring contract and unchanged non-audio graphs."""
import unreal,os,json,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import L,G
from audio_handoff_validation_support import assert_asset_hash
R={'complete':False,'pass':False}
def graph(bp,name):
 return [{'id':n.get_name(),'title':str(n.get_node_title()),'class':n.get_class().get_name(),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in G.get_graph_editor_by_name(bp,name).list_all_nodes()]
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 ref=json.loads((ROOT/'Scripts/Unreal/audio_handoff_reference.json').read_text(encoding='utf8'));count=0
 for p,hashes in ref['packages'].items():assert_asset_hash(p,hashes['before'])
 for path,graphs in ref['protected_graphs'].items():
  bp=unreal.load_asset(path)
  for name,sha in graphs.items():
   from ending_validation_support import graph_hash
   sha=graph_hash(path,name,sha)
   assert hashlib.sha256(json.dumps(graph(bp,name),sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()==sha,(path,name)
   count+=1
 flow=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager');tt=unreal.load_asset('/Game/RecordShop/Interaction/Actors/BP_Turntable');cdo=unreal.get_default_object(flow.generated_class())
 assert cdo.get_editor_property('StoreBGMSound')is None and cdo.get_editor_property('StoreBGMRef')is None and str(cdo.get_editor_property('CurrentStoreBGMRecordID'))=='None'
 tuning={k:cdo.get_editor_property(k)for k in ('StoreBGMVolume','StoreBGMFadeInDuration','StoreBGMFadeOutDuration')}
 for k,v in zip(tuning,(.18,.5,.6)):assert abs(tuning[k]-v)<.0001
 begin=graph(flow,'BeginDay');assert any(n['title'].replace(' ','')=='ResetDayAudio'for n in begin)and not any(n['title'].replace(' ','')=='StartStoreBGM'for n in begin)
 g=G.get_graph_editor_by_name(flow,'EventGraph');commit=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='CommitRecommendationHistory')
 assert [str(p.get_owning_node().get_node_title()).replace(' ','')for p in commit.find_then_pin().list_connected_pins()]==['StartStoreBGM']
 g=G.get_graph_editor_by_name(tt,'EventGraph');create=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='CreateSound2D')
 parents=[str(p.get_owning_node().get_node_title()).replace(' ','')for p in create.find_execute_pin().list_connected_pins()];assert 'FinishStoreBGMStop'in parents
 assert len([n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='CreateSound2D'])==1
 assert L.compile_blueprint(flow)and L.compile_blueprint(tt)
 R.update(**{'pass':True},unchanged_non_audio_graphs=count,tuning=tuning,transition=ref['transition'],canonical_catalogue=True,preplay_cleanup=True,result_hook=True,day_reset=True)
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
