"""Editor leaf patch: GetCommandLine is impure in this engine; execute it before its use."""
import unreal,os,sys,json,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from ending_validation_support import assert_preservation
assert_preservation();reference=ROOT/'Scripts/Unreal/ending_reference.json';data=json.loads(reference.read_text(encoding='utf8'))
path='Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset';bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager');g=G.get_graph_editor_by_name(bp,'BootPresentation')
cmd=next(n for n in g.list_all_nodes()if str(n.get_node_title())=='GetCommandLine');consumer=pin(cmd,'ReturnValue',True).list_connected_pins()[0].get_owning_node();boolean=pin(consumer,'ReturnValue',True).list_connected_pins()[0].get_owning_node();decision=pin(boolean,'ReturnValue',True).list_connected_pins()[0].get_owning_node()
incoming=list(decision.find_execute_pin().list_connected_pins());assert len(incoming)==1 and not cmd.find_execute_pin().list_connected_pins();decision.find_execute_pin().break_pin_links();link(incoming[0],cmd.find_execute_pin());link(cmd.find_then_pin(),decision.find_execute_pin())
assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False);data['packages'][path]['after']=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();reference.write_text(json.dumps(data,indent=2),encoding='utf8')
Path(os.environ['MVP_RESULT']).write_text(json.dumps(dict(complete=True,**{'pass':True},saved=path,preservation=assert_preservation())),encoding='utf8')
