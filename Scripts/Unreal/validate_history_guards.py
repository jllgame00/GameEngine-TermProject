"""Isolated value/API diagnostics with explicitly seeded unsaved primitive entries."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from history_validation_support import payload
from day_graph_helpers import *
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'scope':'isolated unsaved history fixtures; no natural customer-cycle claim'}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
# Runtime Blueprint setters in an unsaved diagnostic class keep the production
# backing array non-editable in the Editor property panel.
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C'
EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
probe=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_HistoryFixture','/Game/RecordShop/Dev/HistoryValidation',unreal.Blueprint,factory)
g=function(probe,'SetFixtureHistoryAndDay')
flow_pin=param(g,'Flow',L.get_object_reference_type(unreal.load_class(None,FC)))
entries_pin=param(g,'Entries',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC))))
day_pin=param(g,'Day',L.get_basic_type_by_name('int'))
a=g.add_set_member_variable_node('RecommendationHistory',FC);link(flow_pin,pin(a,'self'));link(entries_pin,pin(a,'RecommendationHistory'));link(g.find_graph_entry_pin(),a.find_execute_pin())
b=g.add_set_member_variable_node('CurrentDay',FC);link(flow_pin,pin(b,'self'));link(day_pin,pin(b,'CurrentDay'));link(a.find_then_pin(),b.find_execute_pin())
assert L.compile_blueprint(probe);fixture_setter=unreal.get_default_object(probe.generated_class())
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play();started=time.monotonic();phase={'gen':None,'end':None,'busy':False}
def run():
 while not editor.get_game_world():yield
 world=editor.get_game_world();kind=unreal.load_class(None,'/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C');flow=unreal.GameplayStatics.get_all_actors_of_class(world,kind)[0]
 assert not flow.get_editor_property('RecommendationHistory')
 flow.call_method('CommitRecommendationHistory');assert not flow.get_editor_property('RecommendationHistory')
 entrykind=unreal.load_class(None,'/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C')
 expected=[];fixtures=[]
 for identity,visit,day,record,score,result in [('A',1,1,'RS002',2,'GOOD'),('B',1,2,'RS003',0,'POOR'),('A',2,3,'RS001',3,'BEST')]:
  fields=dict(CustomerID=identity,VisitNumber=visit,Day=day,RecordID=record,RecommendationScore=score,RecommendationResult=result,Sequence=len(fixtures)+1)
  obj=unreal.new_object(entrykind,outer=flow)
  for key,value in fields.items():obj.set_editor_property(key,value)
  fixtures.append(obj);expected.append(fields)
 fixture_setter.call_method('SetFixtureHistoryAndDay',args=(flow,fixtures,0))
 for identity in ('A','B','UNKNOWN'):
  entries=flow.call_method('GetRecommendationHistory',args=(identity,));model=[x for x in expected if x['CustomerID']==identity]
  assert [payload(x) for x in entries]==model
  assert bool(flow.call_method('HasPreviousVisit',args=(identity,)))==bool(model)
  latest=flow.call_method('GetLatestRecommendation',args=(identity,));assert payload(latest)==(model[-1] if model else None)
  for number in (-1,0,1,2,999):
   obj=flow.call_method('GetRecommendationForVisit',args=(identity,number));match=next((x for x in model if x['VisitNumber']==number),None)
   assert payload(obj)==match
   if obj:obj.set_editor_property('RecommendationScore',99)
  for obj in entries:obj.set_editor_property('RecordID','MUTATED_COPY')
  assert [payload(x) for x in flow.call_method('GetRecommendationHistory',args=(identity,))]==model
  if latest:latest.set_editor_property('CustomerID','MUTATED_COPY')
 assert [payload(x) for x in flow.get_editor_property('RecommendationHistory')]==expected
 R['queries_and_copy_isolation']=True
 # Explicit isolated bad-timing fixture: a day change cannot authorize reset.
 fixture_setter.call_method('SetFixtureHistoryAndDay',args=(flow,fixtures,1));flow.call_method('ResetRecommendationHistory');assert len(flow.get_editor_property('RecommendationHistory'))==3
 fixture_setter.call_method('SetFixtureHistoryAndDay',args=(flow,fixtures,0));flow.call_method('ResetRecommendationHistory');assert not flow.get_editor_property('RecommendationHistory')
 for identity in ('A','B'):
  assert not flow.call_method('HasPreviousVisit',args=(identity,)) and flow.call_method('GetLatestRecommendation',args=(identity,)) is None
 R['guarded_opening_reset']=True
 R.update(complete=True,**{'pass':True});save()
def tick(delta):
 if phase['busy']:return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle);unreal.EditorPythonScripting.set_keep_python_script_alive(False)
   return
  if phase['gen'] is None:phase['gen']=run()
  assert time.monotonic()-started<65
  next(phase['gen'])
 except StopIteration:level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
