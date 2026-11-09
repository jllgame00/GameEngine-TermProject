"""Install session history on the existing production authority via Editor APIs only."""
import json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from day_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
ENTRY='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry';EC=ENTRY+'.BP_RecommendationHistoryEntry_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'
TC='/Game/RecordShop/Interaction/Actors/BP_Turntable.BP_Turntable_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
FIELDS=[('CustomerID','name'),('VisitNumber','int'),('Day','int'),('RecordID','name'),('RecommendationScore','int'),('RecommendationResult','name'),('Sequence','int')]
def report():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def save(bp):
 assert L.compile_blueprint(bp),bp.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 R['saved'].append(bp.get_path_name());report()
def output(g,name,typ):return g.add_graph_output_parameter(name,typ)
def ret(g,prev,**values):
 n=g.add_return_node();link(prev,n.find_execute_pin())
 for key,value in values.items():
  if hasattr(value,'is_valid'):link(value,pin(n,key))
  else:val(pin(n,key),value)
 return n
def lget(g,name):return pin(g.add_get_local_variable_node(name),name,True)
def lset(g,prev,name,value):
 n=g.add_set_local_variable_node(name);link(prev,n.find_execute_pin())
 if hasattr(value,'is_valid'):link(value,pin(n,name))
 else:val(pin(n,name),value)
 return n.find_then_pin()
def check(g,prev,cond):return branch(g,prev,cond)[0]
def boolvalid(g,obj):
 n=call(g,'/Script/Engine.KismetSystemLibrary.IsValid');link(obj,pin(n,'Object'));return pin(n,'ReturnValue',True)
def foreach(g,prev,array):
 n=g.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop');assert n
 link(prev,pin(n,'Exec'));link(array,pin(n,'Array'));return pin(n,'LoopBody',True),pin(n,'Array Element',True),pin(n,'Completed',True)
def construct(g,prev,values):
 n=action(g,'Construct Object from Class');val(pin(n,'Class'),EC);link(selfref(g),pin(n,'self'));link(prev,n.find_execute_pin());end=n.find_then_pin();obj=pin(n,'ReturnValue',True)
 for key,value in values.items():
  s=g.add_set_member_variable_node(key,EC);link(obj,pin(s,'self'));link(end,s.find_execute_pin())
  if hasattr(value,'is_valid'):link(value,pin(s,key))
  else:val(pin(s,key),value)
  end=s.find_then_pin()
 return end,obj
def stored(g,identity,number=0):
 n=call(g,FC+':FindStoredRecommendation');link(identity,pin(n,'CustomerID'))
 if hasattr(number,'is_valid'):link(number,pin(n,'VisitNumber'))
 else:val(pin(n,'VisitNumber'),number)
 return pin(n,'Entry',True)
def append(g,prev,array,value):
 n=call(g,'/Script/Engine.KismetArrayLibrary.Array_Add');link(array,pin(n,'TargetArray'));link(value,pin(n,'NewItem'));link(prev,n.find_execute_pin());return n.find_then_pin()
def efield(g,obj,key):return field(g,obj,key,EC)
def run(g,prev,name,**args):return own(g,prev,FC,name,**args)
try:
 bp=unreal.load_asset(FLOW);assert bp
 assert 'RecommendationHistory' not in list(map(str,L.list_member_variable_names(bp,False))),'History already installed'
 entry=unreal.load_asset(ENTRY)
 if not entry:
  factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Object)
  entry=unreal.AssetToolsHelpers.get_asset_tools().create_asset(ENTRY.rsplit('/',1)[1],ENTRY.rsplit('/',1)[0],unreal.Blueprint,factory)
 assert entry
 for key,kind in FIELDS:
  assert L.add_member_variable(entry,key,L.get_basic_type_by_name(kind))
  L.set_blueprint_variable_instance_editable(entry,key,True)
 assert L.compile_blueprint(entry)
 ET=L.get_object_reference_type(entry.generated_class());AT=L.get_array_type(ET);NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');BT=L.get_basic_type_by_name('bool')
 assert L.add_member_variable(bp,'RecommendationHistory',AT)
 specs={
  'FindStoredRecommendation':([('CustomerID',NT),('VisitNumber',IT)],[('Entry',ET)]),
  'CloneRecommendationEntry':([('Source',ET)],[('Entry',ET)]),
  'HasPreviousVisit':([('CustomerID',NT)],[('Found',BT)]),
  'GetLatestRecommendation':([('CustomerID',NT)],[('Entry',ET)]),
  'GetRecommendationForVisit':([('CustomerID',NT),('VisitNumber',IT)],[('Entry',ET)]),
  'GetRecommendationHistory':([('CustomerID',NT)],[('Entries',AT)]),
  'GetActiveVisitMemory':([],[('CustomerID',NT),('VisitNumber',IT),('Day',IT),('HasPrevious',BT),('Latest',ET)]),
  'ClassifyRecommendationScore':([('Score',IT)],[('Result',NT)]),
  'CommitRecommendationHistory':([],[]),'PrepareRevisitMemory':([],[]),'ResetRecommendationHistory':([],[])}
 for name,(inputs,outputs) in specs.items():
  g=fn(bp,name)
  for key,typ in inputs:param(g,key,typ)
  for key,typ in outputs:output(g,key,typ)
  if name in ('FindStoredRecommendation','HasPreviousVisit','ClassifyRecommendationScore'):g.set_is_pure_function(True)
  if name in ('FindStoredRecommendation','CloneRecommendationEntry','ClassifyRecommendationScore','CommitRecommendationHistory','PrepareRevisitMemory','ResetRecommendationHistory'):g.set_function_is_private()
 assert L.add_event_dispatcher(bp,'OnRevisitMemoryReady')
 for key,typ in [('CustomerID',NT),('VisitNumber',IT),('HasPrevious',BT)]:assert L.add_event_dispatcher_parameter(bp,'OnRevisitMemoryReady',key,typ)
 assert L.compile_blueprint(bp)
 # Pure internal lookup returns the stored object only within this authority.
 g=G.get_graph_editor_by_name(bp,'FindStoredRecommendation');identity=param(g,'CustomerID',NT);number=param(g,'VisitNumber',IT)
 assert g.add_local_variable('FoundEntry',ET)
 body,obj,done=foreach(g,g.find_graph_entry_pin(),get(g,'RecommendationHistory'))
 cond=calc(g,'BooleanAND',A=calc(g,'EqualEqual_NameName',A=efield(g,obj,'CustomerID'),B=identity),B=calc(g,'BooleanOR',A=calc(g,'EqualEqual_IntInt',A=number,B=0),B=calc(g,'EqualEqual_IntInt',A=efield(g,obj,'VisitNumber'),B=number)))
 yes,no=branch(g,body,cond);lset(g,yes,'FoundEntry',obj);ret(g,done,Entry=lget(g,'FoundEntry'))
 g=G.get_graph_editor_by_name(bp,'CloneRecommendationEntry');source=param(g,'Source',ET);end,no=valid(g,source,g.find_graph_entry_pin())
 end,obj=construct(g,end,{key:efield(g,source,key) for key,_ in FIELDS});ret(g,end,Entry=obj);ret(g,no,Entry='None')
 g=G.get_graph_editor_by_name(bp,'HasPreviousVisit');ret(g,g.find_graph_entry_pin(),Found=boolvalid(g,stored(g,param(g,'CustomerID',NT))))
 for name in ('GetLatestRecommendation','GetRecommendationForVisit'):
  g=G.get_graph_editor_by_name(bp,name);identity=param(g,'CustomerID',NT);end=g.find_graph_entry_pin();number=0
  if name=='GetRecommendationForVisit':
   number=param(g,'VisitNumber',IT);end,no=branch(g,end,calc(g,'Greater_IntInt',A=number,B=0));ret(g,no,Entry='None')
  end,n=invoke(g,end,FC+':CloneRecommendationEntry',Source=stored(g,identity,number));ret(g,end,Entry=pin(n,'Entry',True))
 g=G.get_graph_editor_by_name(bp,'GetRecommendationHistory');identity=param(g,'CustomerID',NT);assert g.add_local_variable('Copies',AT)
 body,obj,done=foreach(g,g.find_graph_entry_pin(),get(g,'RecommendationHistory'))
 end=check(g,body,calc(g,'EqualEqual_NameName',A=efield(g,obj,'CustomerID'),B=identity));end,n=invoke(g,end,FC+':CloneRecommendationEntry',Source=obj)
 append(g,end,lget(g,'Copies'),pin(n,'Entry',True));ret(g,done,Entries=lget(g,'Copies'))
 g=G.get_graph_editor_by_name(bp,'GetActiveVisitMemory');end,no=valid(g,get(g,'ActiveVisit'),g.find_graph_entry_pin());ret(g,no,CustomerID='None',VisitNumber=0,Day=0,HasPrevious='false',Latest='None')
 assert g.add_local_variable('PreviousEntry',ET)
 identity=field(g,get(g,'ActiveVisit'),'CustomerID',VC);number=field(g,get(g,'ActiveVisit'),'VisitNumber',VC);day=field(g,get(g,'ActiveVisit'),'Day',VC)
 body,obj,done=foreach(g,end,get(g,'RecommendationHistory'))
 end=check(g,body,calc(g,'BooleanAND',A=calc(g,'EqualEqual_NameName',A=efield(g,obj,'CustomerID'),B=identity),B=calc(g,'Less_IntInt',A=efield(g,obj,'VisitNumber'),B=number)))
 lset(g,end,'PreviousEntry',obj)
 end,n=invoke(g,done,FC+':CloneRecommendationEntry',Source=lget(g,'PreviousEntry'))
 ret(g,end,CustomerID=identity,VisitNumber=number,Day=day,HasPrevious=boolvalid(g,lget(g,'PreviousEntry')),Latest=pin(n,'Entry',True))
 g=G.get_graph_editor_by_name(bp,'ClassifyRecommendationScore');score=param(g,'Score',IT)
 best,other=branch(g,g.find_graph_entry_pin(),calc(g,'GreaterEqual_IntInt',A=score,B=3));ret(g,best,Result='BEST')
 good,poor=branch(g,other,calc(g,'GreaterEqual_IntInt',A=score,B=2));ret(g,good,Result='GOOD');ret(g,poor,Result='POOR')
 g=G.get_graph_editor_by_name(bp,'CommitRecommendationHistory');end=g.find_graph_entry_pin()
 for name in ('ActiveVisit','ActiveCustomer','ResultWidgetRef','TurntableRef'):end,_=valid(g,get(g,name),end)
 for name in ('ResultStartedForCustomer','RawScoreAvailable'):end=check(g,end,get(g,name))
 end=check(g,end,calc(g,'EqualEqual_ByteByte',A=get(g,'CurrentState'),B=5))
 identity=field(g,get(g,'ActiveVisit'),'CustomerID',VC);number=field(g,get(g,'ActiveVisit'),'VisitNumber',VC);day=field(g,get(g,'ActiveVisit'),'Day',VC)
 score=get(g,'RawRecommendationScore')
 for cond in [calc(g,'EqualEqual_IntInt',A=day,B=get(g,'CurrentDay')),calc(g,'NotEqual_NameName',A=identity,B='None'),calc(g,'Greater_IntInt',A=number,B=0),calc(g,'GreaterEqual_IntInt',A=score,B=0),calc(g,'LessEqual_IntInt',A=score,B=3)]:end=check(g,end,cond)
 duplicate,end=valid(g,stored(g,identity,number),end)
 record=field(g,get(g,'TurntableRef'),'CurrentRecord',TC);split=action(g,'Break ST Record Data',[record]);link(record,pin(split,'ST_RecordData'))
 recordid=next(p for p in split.list_output_pins() if str(p.get_pin_name()).startswith('RecordID_'))
 end=check(g,end,calc(g,'NotEqual_NameName',A=recordid,B='None'))
 category=call(g,FC+':ClassifyRecommendationScore');link(score,pin(category,'Score'))
 end,obj=construct(g,end,dict(CustomerID=identity,VisitNumber=number,Day=day,RecordID=recordid,RecommendationScore=score,RecommendationResult=pin(category,'Result',True),Sequence=calc(g,'Add_IntInt',A=array_len(g,get(g,'RecommendationHistory')),B=1)))
 append(g,end,get(g,'RecommendationHistory'),obj)
 g=G.get_graph_editor_by_name(bp,'PrepareRevisitMemory');end,_=valid(g,get(g,'ActiveVisit'),g.find_graph_entry_pin());end,n=invoke(g,end,FC+':GetActiveVisitMemory')
 dispatch(g,end,'On Revisit Memory Ready',CustomerID=pin(n,'CustomerID',True),VisitNumber=pin(n,'VisitNumber',True),HasPrevious=pin(n,'HasPrevious',True))
 g=G.get_graph_editor_by_name(bp,'ResetRecommendationHistory');end=check(g,g.find_graph_entry_pin(),calc(g,'EqualEqual_IntInt',A=get(g,'CurrentDay'),B=0))
 yes,end=branch(g,end,get(g,'TutorialComplete'));yes,end=valid(g,get(g,'ActiveCustomer'),end)
 clear=call(g,'/Script/Engine.KismetArrayLibrary.Array_Clear');link(get(g,'RecommendationHistory'),pin(clear,'TargetArray'));link(end,clear.find_execute_pin())
 # Extend accepted production chains, never replace their existing guards.
 g=evgraph(bp);n=call(g,FC+':CommitRecommendationHistory');splice(byname(g,'K2Node_CallFunction_38').find_then_pin(),n)
 dialogue=byname(g,'K2Node_CallFunction_20');incoming=list(dialogue.find_execute_pin().list_connected_pins());dialogue.find_execute_pin().break_pin_links()
 prep=call(g,FC+':PrepareRevisitMemory')
 for p in incoming:link(p,prep.find_execute_pin())
 link(prep.find_then_pin(),dialogue.find_execute_pin())
 reset=call(g,FC+':ResetRecommendationHistory');splice(byname(g,'K2Node_Event_0').find_then_pin(),reset)
 assert L.compile_blueprint(bp)
 for name in specs:layout(G.get_graph_editor_by_name(bp,name))
 save(entry);save(bp);R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;report()
