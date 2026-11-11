"""Editor entry guard invalidates a late day callback once front-end travel starts."""
import unreal,os,sys,json,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from ending_validation_support import assert_preservation
assert_preservation();reference=ROOT/'Scripts/Unreal/ending_reference.json';data=json.loads(reference.read_text(encoding='utf8'))
asset='/Game/RecordShop/Core/Flow/BP_GameFlowManager';path='Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset';bp=unreal.load_asset(asset)
g=G.get_graph_editor_by_name(bp,'FinishDayTransition');assert not any(str(n.get_node_title())=='Get PresentationPhase'for n in g.list_all_nodes()),'One-shot fix already applied';entry=g.find_graph_entry_pin();after=list(entry.list_connected_pins());entry.break_pin_links()
allowed=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=get(g,'PresentationPhase'),B='Playing'),B=calc(g,'EqualEqual_NameName',A=get(g,'PresentationPhase'),B='EndingPending'))
yes=check(g,entry,allowed)
for child in after:link(yes,child)
assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
def graph():return [{'id':n.get_name(),'title':str(n.get_node_title()),'class':n.get_class().get_name(),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in g.list_all_nodes()]
data['packages'][path]['after']=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();data['changed_graphs'][asset]['FinishDayTransition']['after']=hashlib.sha256(json.dumps(graph(),sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
reference.write_text(json.dumps(data,indent=2),encoding='utf8');Path(os.environ['MVP_RESULT']).write_text(json.dumps(dict(complete=True,**{'pass':True},saved=path,preservation=assert_preservation())),encoding='utf8')
