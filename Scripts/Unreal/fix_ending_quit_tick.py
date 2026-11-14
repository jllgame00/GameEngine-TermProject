"""Editor leaf patch: stop Turntable tick before controller destruction on world exit."""
import unreal,os,sys,json,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from ending_validation_support import assert_preservation
assert_preservation()
reference=ROOT/'Scripts/Unreal/ending_reference.json';data=json.loads(reference.read_text(encoding='utf8'))
path='Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset';bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
g=G.get_graph_editor_by_name(bp,'FinishFrontEndTravel');assert not any(str(n.get_node_title()).replace(' ','')=='SetActorTickEnabled'for n in g.list_all_nodes()),'One-shot fix already applied';anchor=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='ClearPresentationTimers')
children=list(anchor.find_then_pin().list_connected_pins());anchor.find_then_pin().break_pin_links()
yes,no=valid(g,get(g,'TurntableRef'),anchor.find_then_pin());yes=invoke(g,yes,'/Script/Engine.Actor.SetActorTickEnabled',self=get(g,'TurntableRef'),bEnabled='false')[0]
for child in children:link(yes,child);link(no,child)
assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
data['packages'][path]['after']=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();reference.write_text(json.dumps(data,indent=2),encoding='utf8')
Path(os.environ['MVP_RESULT']).write_text(json.dumps(dict(complete=True,**{'pass':True},saved=path,preservation=assert_preservation())),encoding='utf8')
