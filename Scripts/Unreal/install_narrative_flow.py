"""Connect visit narrative/memory/runtime profile and tutorial identity to sole GFM."""
import unreal,sys,os,json,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
CC='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C';MC='/Game/DialogueManager.DialogueManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'
NC='/Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C'
CAT='/Game/RecordShop/Data/Records/DA_RecordCatalogue';KC='/Game/RecordShop/Data/Records/BP_RecordCatalogue.BP_RecordCatalogue_C'
EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
NT=L.get_basic_type_by_name('name');NA=L.get_array_type(NT);BT=L.get_basic_type_by_name('bool');ST=L.get_basic_type_by_name('string')
def owncall(g,end,name,**args):return own(g,end,FC,name,**args)
def def_field(g,obj,key):return field(g,obj,key,NC)
def addlocal(g,name,typ):
 if name not in list(map(str,g.list_local_variable_names())):assert g.add_local_variable(name,typ)
def make_profile(g,end,values):
 make=action(g,'Make Customer Data')
 for p in make.list_input_pins():
  key=str(p.get_pin_name()).split('_')[0]
  if key in values:
   value=values[key]
   if hasattr(value,'is_valid'):link(value,p)
   else:val(p,value)
 setter=g.add_set_member_variable_node('CustomerProfile',CC);link(get(g,'ActiveCustomer'),pin(setter,'self'));link(make.list_output_pins()[0],pin(setter,'CustomerProfile'));link(end,setter.find_execute_pin());return setter.find_then_pin()
def break_profile(g):
 profile=field(g,get(g,'ActiveCustomer'),'CustomerProfile',CC);split=action(g,'Break Customer Data',[profile]);link(profile,pin(split,'CustomerData'))
 return {str(p.get_pin_name()).split('_')[0]:p for p in split.list_output_pins()}
try:
 bp=unreal.load_asset(FLOW);old=list(map(str,L.list_member_variable_names(bp,False)))
 for name,typ in [('RecordCatalogue',L.get_object_reference_type(unreal.load_class(None,KC))),('TutorialNarrative',L.get_object_reference_type(unreal.load_class(None,NC))),('EnableNarrativeRouting',BT),('NarrativeMemoryIntroKey',NT),('NarrativeMemoryVisits',L.get_array_type(L.get_object_reference_type(unreal.load_class(None,EC))))]:
  if name not in old:assert L.add_member_variable(bp,name,typ)
 for n in ('RecordCatalogue','TutorialNarrative','EnableNarrativeRouting'):L.set_blueprint_variable_instance_editable(bp,n,True)
 specs={'GetActiveNarrativeDefinition':([],[('Narrative',L.get_object_reference_type(unreal.load_class(None,NC)))]),'GetActiveCandidateRecordIDs':([],[('RecordIDs',NA)]),'ApplyVisitContext':([],[]),'ApplyVisitProfileOverrides':([],[]),'ConfigureActiveNarrative':([],[]),'ClearNarrativeVisitContext':([],[]),'CancelActiveNarrativeDialogue':([],[])}
 for name,(ins,outs) in specs.items():
  g=fn(bp,name);inputs(g,ins);outputs(g,outs)
  if name.startswith('GetActive'):g.set_is_pure_function(True)
 assert L.compile_blueprint(bp)
 cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('RecordCatalogue',unreal.load_asset(CAT));cdo.set_editor_property('TutorialNarrative',unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_TutorialNarrative'));cdo.set_editor_property('EnableNarrativeRouting',True)
 g=G.get_graph_editor_by_name(bp,'GetActiveNarrativeDefinition');end,no=branch(g,g.find_graph_entry_pin(),get(g,'EnableNarrativeRouting'));ret(g,no,Narrative='None')
 queued,tutorial=valid(g,get(g,'ActiveVisit'),end)
 ref=field(g,get(g,'ActiveVisit'),'Narrative',VC);end,no=valid(g,ref,queued);ret(g,no,Narrative='None')
 end,no=branch(g,end,calc(g,'EqualEqual_NameName',A=def_field(g,ref,'ReviewStatus'),B='READY'));ret(g,no,Narrative='None');ret(g,end,Narrative=ref)
 end,no=valid(g,get(g,'ActiveCustomer'),tutorial);ret(g,no,Narrative='None')
 for cond in [calc(g,'EqualEqual_IntInt',A=get(g,'CurrentDay'),B=0),calc(g,'Not_PreBool',A=get(g,'TutorialComplete'))]:
  end,no=branch(g,end,cond);ret(g,no,Narrative='None')
 end,no=valid(g,get(g,'TutorialNarrative'),end);ret(g,no,Narrative='None')
 end,no=branch(g,end,calc(g,'EqualEqual_NameName',A=def_field(g,get(g,'TutorialNarrative'),'ReviewStatus'),B='READY'));ret(g,no,Narrative='None');ret(g,end,Narrative=get(g,'TutorialNarrative'))
 g=G.get_graph_editor_by_name(bp,'GetActiveCandidateRecordIDs');ref=call(g,FC+':GetActiveNarrativeDefinition');ref=pin(ref,'Narrative',True)
 use,default=valid(g,ref,g.find_graph_entry_pin());ids=def_field(g,ref,'CandidateRecordIDs');use,empty=branch(g,use,calc(g,'Greater_IntInt',A=array_len(g,ids),B=0));ret(g,use,RecordIDs=ids)
 fallback=call(g,'/Script/Engine.KismetSystemLibrary.IsValid');link(get(g,'RecordCatalogue'),pin(fallback,'Object'))
 gate=g.add_branch_node();link(default,gate.find_execute_pin());link(empty,gate.find_execute_pin());link(pin(fallback,'ReturnValue',True),pin(gate,'Condition'));ret(g,pin(gate,'else',True))
 ret(g,pin(gate,'then',True),RecordIDs=field(g,get(g,'RecordCatalogue'),'DefaultCandidateRecordIDs',KC))
 g=G.get_graph_editor_by_name(bp,'ApplyVisitContext');end,_=valid(g,get(g,'ActiveCustomer'),g.find_graph_entry_pin())
 addlocal(g,'RuntimeIdentity',ST);addlocal(g,'TutorialIdentity',BT)
 queue,tutorial=valid(g,get(g,'ActiveVisit'),end)
 queue=local_set(g,queue,'RuntimeIdentity',calc(g,'Conv_NameToString',InName=field(g,get(g,'ActiveVisit'),'CustomerID',VC)));queue=local_set(g,queue,'TutorialIdentity','false')
 tutorial=check(g,tutorial,calc(g,'EqualEqual_IntInt',A=get(g,'CurrentDay'),B=0));tutorial=check(g,tutorial,calc(g,'Not_PreBool',A=get(g,'TutorialComplete')))
 tutorial=local_set(g,tutorial,'RuntimeIdentity','TUTORIAL');tutorial=local_set(g,tutorial,'TutorialIdentity','true')
 # Both accepted identities join one profile copy, preserving every other field.
 values=break_profile(g);values['CustomerID']=local_get(g,'RuntimeIdentity')
 choose=call(g,'/Script/Engine.KismetMathLibrary.SelectText');val(pin(choose,'A'),'연습 손님');link(values['Name'],pin(choose,'B'));link(local_get(g,'TutorialIdentity'),pin(choose,'bPickA'));values['Name']=pin(choose,'ReturnValue',True)
 # One setter chain receives both exec inputs; no instance/class default mutation.
 make=action(g,'Make Customer Data')
 for p in make.list_input_pins():
  key=str(p.get_pin_name()).split('_')[0]
  if key in values:link(values[key],p)
 setter=g.add_set_member_variable_node('CustomerProfile',CC);link(get(g,'ActiveCustomer'),pin(setter,'self'));link(make.list_output_pins()[0],pin(setter,'CustomerProfile'));link(queue,setter.find_execute_pin());link(tutorial,setter.find_execute_pin());owncall(g,setter.find_then_pin(),'ApplyVisitProfileOverrides')
 g=G.get_graph_editor_by_name(bp,'ApplyVisitProfileOverrides');end,_=valid(g,get(g,'ActiveCustomer'),g.find_graph_entry_pin());ref=call(g,FC+':GetActiveNarrativeDefinition');ref=pin(ref,'Narrative',True);end,_=valid(g,ref,end)
 values=break_profile(g)
 for key,override in [('Mood','TargetMoodOverride'),('MusicPreference','TargetGenreOverride'),('Personality','TargetThemeOverride')]:
  target=def_field(g,ref,override);select=call(g,'/Script/Engine.KismetMathLibrary.SelectString');link(calc(g,'Conv_NameToString',InName=target),pin(select,'A'));link(values[key],pin(select,'B'));link(calc(g,'NotEqual_NameName',A=target,B='None'),pin(select,'bPickA'));values[key]=pin(select,'ReturnValue',True)
 make_profile(g,end,values)
 g=G.get_graph_editor_by_name(bp,'CancelActiveNarrativeDialogue');end,_=valid(g,get(g,'DialogueManagerRef'),g.find_graph_entry_pin());own(g,end,MC,'CancelDialogueSequence',self=get(g,'DialogueManagerRef'))
 g=G.get_graph_editor_by_name(bp,'ClearNarrativeVisitContext');end=assign(g,g.find_graph_entry_pin(),'NarrativeMemoryIntroKey','NO_MEMORY');end=clear(g,end,get(g,'NarrativeMemoryVisits'));owncall(g,end,'CancelActiveNarrativeDialogue')
 g=G.get_graph_editor_by_name(bp,'ConfigureActiveNarrative');end=assign(g,g.find_graph_entry_pin(),'NarrativeMemoryIntroKey','NO_MEMORY');end=clear(g,end,get(g,'NarrativeMemoryVisits'));end,_=valid(g,get(g,'DialogueManagerRef'),end)
 end=own(g,end,MC,'ClearPendingDialogueSequence',self=get(g,'DialogueManagerRef'));end=owncall(g,end,'ApplyVisitProfileOverrides')
 # Mirror the runtime profile into the same existing score authority.
 profile=field(g,get(g,'ActiveCustomer'),'CustomerProfile',CC);split=action(g,'Break Customer Data',[profile]);link(profile,pin(split,'CustomerData'))
 for key,value in [('CurrentCustomer',profile),('CurrentMood',struct_field(split,'Mood'))]:
  n=g.add_set_member_variable_node(key,MC);link(get(g,'DialogueManagerRef'),pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
 refnode=call(g,FC+':GetActiveNarrativeDefinition');ref=pin(refnode,'Narrative',True);end,_=valid(g,ref,end)
 addlocal(g,'ComposedRows',NA);addlocal(g,'NarrativeDefinition',L.get_object_reference_type(unreal.load_class(None,NC)))
 end=local_set(g,end,'NarrativeDefinition',ref);ref=local_get(g,'NarrativeDefinition')
 with_memory,without=valid(g,get(g,'ActiveVisit'),end)
 body,num,done=each(g,with_memory,def_field(g,ref,'MemoryVisitNumbers'))
 permitted,bad=branch(g,body,calc(g,'BooleanAND',A=calc(g,'Greater_IntInt',A=num,B=0),B=calc(g,'Less_IntInt',A=num,B=field(g,get(g,'ActiveVisit'),'VisitNumber',VC))))
 assign(g,bad,'NarrativeMemoryIntroKey','NO_MEMORY')
 end,n=invoke(g,permitted,FC+':GetRecommendationForVisit',CustomerID=field(g,get(g,'ActiveVisit'),'CustomerID',VC),VisitNumber=num)
 entry=pin(n,'Entry',True);end,missing=valid(g,entry,end);assign(g,missing,'NarrativeMemoryIntroKey','NO_MEMORY')
 end=append(g,end,get(g,'NarrativeMemoryVisits'),entry);result=field(g,entry,'RecommendationResult',EC)
 known=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=result,B='BEST'),B=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=result,B='GOOD'),B=calc(g,'EqualEqual_NameName',A=result,B='POOR')))
 end,unknown=branch(g,end,known);assign(g,end,'NarrativeMemoryIntroKey',result);assign(g,unknown,'NarrativeMemoryIntroKey','NO_MEMORY')
 # Gathered memories precede row composition and the external memory-ready event.
 compose=g.add_branch_node();link(done,compose.find_execute_pin());link(without,compose.find_execute_pin());link(calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='BEST'),pin(compose,'Condition'))
 best=pin(compose,'then',True);other=pin(compose,'else',True);best=local_set(g,best,'ComposedRows',def_field(g,ref,'BestIntroRows'))
 good,other=branch(g,other,calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='GOOD'));good=local_set(g,good,'ComposedRows',def_field(g,ref,'GoodIntroRows'))
 poor,neutral=branch(g,other,calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='POOR'));poor=local_set(g,poor,'ComposedRows',def_field(g,ref,'PoorIntroRows'));neutral=local_set(g,neutral,'ComposedRows',def_field(g,ref,'NoMemoryIntroRows'))
 join=call(g,'/Script/Engine.KismetArrayLibrary.Array_Append');link(local_get(g,'ComposedRows'),pin(join,'TargetArray'));link(def_field(g,ref,'OrderedRows'),pin(join,'SourceArray'))
 for p in (best,good,poor,neutral):link(p,join.find_execute_pin())
 own(g,join.find_then_pin(),MC,'SetPendingDialogueSequence',self=get(g,'DialogueManagerRef'),SourceTable=def_field(g,ref,'SourceTable'),OrderedRowNames=local_get(g,'ComposedRows'),SequenceID=def_field(g,ref,'SequenceID'))
 assert L.compile_blueprint(bp)
 # Existing PrepareRevisitMemory remains the one public hook, after context setup.
 g=G.get_graph_editor_by_name(bp,'PrepareRevisitMemory');node=call(g,FC+':ConfigureActiveNarrative');splice(g.find_graph_entry_pin(),node)
 g=G.get_graph_editor_by_name(bp,'CloseDialogue');node=call(g,FC+':CancelActiveNarrativeDialogue');splice(g.find_graph_entry_pin(),node)
 eg=evgraph(bp);node=call(eg,FC+':ClearNarrativeVisitContext');splice(byname(eg,'K2Node_CallFunction_3').find_then_pin(),node)
 for name in specs:layout(G.get_graph_editor_by_name(bp,name))
 assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False);R['saved'].append(bp.get_path_name());R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
