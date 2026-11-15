"""Install A2/A3 production data and optional categorical memory modules. Editor only."""
import unreal,os,sys,json,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
from narrative_validation_support import assert_reference_integrity
unreal.InternationalizationLibrary.set_current_language('en',False)
NAR='/Game/RecordShop/Data/Narrative';NC=NAR+'/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C'
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C';MC='/Game/DialogueManager.DialogueManager_C'
VC='/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C';CC='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C';EC='/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
NT=L.get_basic_type_by_name('name');NA=L.get_array_type(NT);BT=L.get_basic_type_by_name('bool');IT=L.get_basic_type_by_name('int')
def save(a):
 if isinstance(a,unreal.Blueprint):assert L.compile_blueprint(a)
 assert unreal.EditorAssetLibrary.save_loaded_asset(a,False);R['saved'].append(a.get_path_name())
def addlocal(g,key,typ):
 if key not in list(map(str,g.list_local_variable_names())):assert g.add_local_variable(key,typ)
def append_rows(g,end,target,source):return invoke(g,end,'/Script/Engine.KismetArrayLibrary.Array_Append',TargetArray=target,SourceArray=source)[0]
def set_false(g,end):
 end=local_set(g,end,'AllMemoriesFound','false');return local_set(g,end,'AllMemoriesPositive','false')
def pick_rows(g,end,key,ref,prefix,local,default):
 paths=[]
 for result in ('BEST','GOOD','POOR'):
  yes,end=branch(g,end,calc(g,'EqualEqual_NameName',A=key,B=result));paths.append(local_set(g,yes,local,field(g,ref,prefix+result.title()+'Rows',NC)))
 paths.append(local_set(g,end,local,field(g,ref,default,NC))if default else clear(g,end,local_get(g,local)))
 return paths
try:
 R['before']=assert_reference_integrity()
 definition=unreal.load_asset(NAR+'/BP_VisitNarrativeDefinition');names=list(map(str,L.list_member_variable_names(definition,False)))
 fields=[('RequireAllMemories',BT),('EarlierMemoryVisitNumber',IT),('EarlierBestRows',NA),('EarlierGoodRows',NA),('EarlierPoorRows',NA),('AllPositiveOutroRows',NA),('OtherMemoryOutroRows',NA)]
 for name,typ in fields:
  if name not in names:assert L.add_member_variable(definition,name,typ)
  L.set_blueprint_variable_instance_editable(definition,name,True)
 save(definition)
 bp=unreal.load_asset(FLOW);g=fn(bp,'ConfigureActiveNarrative')
 for key,typ in [('ComposedRows',NA),('EarlierRows',NA),('EarlierResult',NT),('AllMemoriesFound',BT),('AllMemoriesPositive',BT),('NarrativeDefinition',L.get_object_reference_type(unreal.load_class(None,NC)))]:addlocal(g,key,typ)
 end=assign(g,g.find_graph_entry_pin(),'NarrativeMemoryIntroKey','NO_MEMORY');end=clear(g,end,get(g,'NarrativeMemoryVisits'));end,_=valid(g,get(g,'DialogueManagerRef'),end)
 end=own(g,end,MC,'ClearPendingDialogueSequence',self=get(g,'DialogueManagerRef'));end=own(g,end,FC,'ApplyVisitProfileOverrides')
 profile=field(g,get(g,'ActiveCustomer'),'CustomerProfile',CC);split=action(g,'Break Customer Data',[profile]);link(profile,pin(split,'CustomerData'))
 for key,value in [('CurrentCustomer',profile),('CurrentMood',struct_field(split,'Mood'))]:
  n=g.add_set_member_variable_node(key,MC);link(get(g,'DialogueManagerRef'),pin(n,'self'));link(value,pin(n,key));link(end,n.find_execute_pin());end=n.find_then_pin()
 n=call(g,FC+':GetActiveNarrativeDefinition');ref=pin(n,'Narrative',True);end,_=valid(g,ref,end);end=local_set(g,end,'NarrativeDefinition',ref);ref=local_get(g,'NarrativeDefinition')
 end=local_set(g,end,'EarlierResult','NO_MEMORY')
 anymem=calc(g,'Greater_IntInt',A=array_len(g,field(g,ref,'MemoryVisitNumbers',NC)),B=0)
 for key in ('AllMemoriesFound','AllMemoriesPositive'):end=local_set(g,end,key,anymem)
 with_memory,without=valid(g,get(g,'ActiveVisit'),end)
 # A tutorial/preview without ActiveVisit can never claim known memories.
 without=set_false(g,without)
 body,num,done=each(g,with_memory,field(g,ref,'MemoryVisitNumbers',NC))
 permitted,bad=branch(g,body,calc(g,'BooleanAND',A=calc(g,'Greater_IntInt',A=num,B=0),B=calc(g,'Less_IntInt',A=num,B=field(g,get(g,'ActiveVisit'),'VisitNumber',VC))))
 bad=assign(g,bad,'NarrativeMemoryIntroKey','NO_MEMORY');set_false(g,bad)
 end,n=invoke(g,permitted,FC+':GetRecommendationForVisit',CustomerID=field(g,get(g,'ActiveVisit'),'CustomerID',VC),VisitNumber=num)
 entry=pin(n,'Entry',True);end,missing=valid(g,entry,end);missing=assign(g,missing,'NarrativeMemoryIntroKey','NO_MEMORY');set_false(g,missing)
 end=append(g,end,get(g,'NarrativeMemoryVisits'),entry);result=field(g,entry,'RecommendationResult',EC)
 known=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=result,B='BEST'),B=calc(g,'BooleanOR',A=calc(g,'EqualEqual_NameName',A=result,B='GOOD'),B=calc(g,'EqualEqual_NameName',A=result,B='POOR')))
 end,unknown=branch(g,end,known);unknown=assign(g,unknown,'NarrativeMemoryIntroKey','NO_MEMORY');set_false(g,unknown)
 end=assign(g,end,'NarrativeMemoryIntroKey',result)
 # Categorical predicates consume confirmed Result; no score formula is added.
 positive,poor=branch(g,end,calc(g,'NotEqual_NameName',A=result,B='POOR'));poor=local_set(g,poor,'AllMemoriesPositive','false')
 earlier=g.add_branch_node();link(positive,earlier.find_execute_pin());link(poor,earlier.find_execute_pin());link(calc(g,'EqualEqual_IntInt',A=num,B=field(g,ref,'EarlierMemoryVisitNumber',NC)),pin(earlier,'Condition'));local_set(g,pin(earlier,'then',True),'EarlierResult',result)
 gate=g.add_branch_node();link(done,gate.find_execute_pin());link(without,gate.find_execute_pin());link(calc(g,'BooleanAND',A=field(g,ref,'RequireAllMemories',NC),B=calc(g,'Not_PreBool',A=local_get(g,'AllMemoriesFound'))),pin(gate,'Condition'))
 reset=assign(g,pin(gate,'then',True),'NarrativeMemoryIntroKey','NO_MEMORY');reset=local_set(g,reset,'EarlierResult','NO_MEMORY')
 choose=g.add_branch_node();link(reset,choose.find_execute_pin());link(pin(gate,'else',True),choose.find_execute_pin());link(calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='BEST'),pin(choose,'Condition'))
 best=local_set(g,pin(choose,'then',True),'ComposedRows',field(g,ref,'BestIntroRows',NC));other=pin(choose,'else',True)
 good,other=branch(g,other,calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='GOOD'));good=local_set(g,good,'ComposedRows',field(g,ref,'GoodIntroRows',NC))
 poor,neutral=branch(g,other,calc(g,'EqualEqual_NameName',A=get(g,'NarrativeMemoryIntroKey'),B='POOR'));poor=local_set(g,poor,'ComposedRows',field(g,ref,'PoorIntroRows',NC));neutral=local_set(g,neutral,'ComposedRows',field(g,ref,'NoMemoryIntroRows',NC))
 earlier_gate=g.add_branch_node()
 for end in (best,good,poor,neutral):link(end,earlier_gate.find_execute_pin())
 link(calc(g,'EqualEqual_NameName',A=local_get(g,'EarlierResult'),B='BEST'),pin(earlier_gate,'Condition'))
 e_best=local_set(g,pin(earlier_gate,'then',True),'EarlierRows',field(g,ref,'EarlierBestRows',NC));other=pin(earlier_gate,'else',True)
 e_good,other=branch(g,other,calc(g,'EqualEqual_NameName',A=local_get(g,'EarlierResult'),B='GOOD'));e_good=local_set(g,e_good,'EarlierRows',field(g,ref,'EarlierGoodRows',NC))
 e_poor,e_none=branch(g,other,calc(g,'EqualEqual_NameName',A=local_get(g,'EarlierResult'),B='POOR'));e_poor=local_set(g,e_poor,'EarlierRows',field(g,ref,'EarlierPoorRows',NC));e_none=clear(g,e_none,local_get(g,'EarlierRows'))
 join=call(g,'/Script/Engine.KismetArrayLibrary.Array_Append');link(local_get(g,'ComposedRows'),pin(join,'TargetArray'));link(local_get(g,'EarlierRows'),pin(join,'SourceArray'))
 for end in (e_best,e_good,e_poor,e_none):link(end,join.find_execute_pin())
 end=append_rows(g,join.find_then_pin(),local_get(g,'ComposedRows'),field(g,ref,'OrderedRows',NC))
 positive,other=branch(g,end,calc(g,'BooleanAND',A=local_get(g,'AllMemoriesFound'),B=local_get(g,'AllMemoriesPositive')))
 positive=append_rows(g,positive,local_get(g,'ComposedRows'),field(g,ref,'AllPositiveOutroRows',NC));other=append_rows(g,other,local_get(g,'ComposedRows'),field(g,ref,'OtherMemoryOutroRows',NC))
 n=call(g,MC+':SetPendingDialogueSequence');link(positive,n.find_execute_pin());link(other,n.find_execute_pin());link(get(g,'DialogueManagerRef'),pin(n,'self'));link(field(g,ref,'SourceTable',NC),pin(n,'SourceTable'));link(local_get(g,'ComposedRows'),pin(n,'OrderedRowNames'));link(field(g,ref,'SequenceID',NC),pin(n,'SequenceID'))
 layout(g);save(bp)
 data=json.loads((ROOT/'Scripts/Unreal/customer_a_dialogue.json').read_text(encoding='utf-8-sig'));struct=unreal.load_asset('/Game/DialogueData');table=unreal.load_asset(data['source'])
 if table is None:
  f=unreal.DataTableFactory();f.set_editor_property('struct',struct);table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_A_RevisitDialogue',NAR,unreal.DataTable,f)
 # Stable localization namespace/key for all newly authored text.
 def text_literal(row,key,value):return 'NSLOCTEXT("CustomerARevisit", '+json.dumps(row+'_'+key)+', '+json.dumps(value,ensure_ascii=False)+')'
 rows=[dict(Name=k,DialogueID=k,Speaker=text_literal(k,'Speaker',data['speaker']),Text=text_literal(k,'Text',v),Mood='Quiet',MusicPreference='Jazz',IsEndNode=k in ('A2_Current_05','A3_Payoff_Aligned','A3_Payoff_Clarify'))for k,v in data['rows'].items()]
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),struct);save(table)
 for num in (2,3):
  path=NAR+'/DA_A'+str(num)+'_Narrative';asset=unreal.load_asset(path)
  if asset is None:
   f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',definition.generated_class());asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],NAR,definition.generated_class(),f)
  values=dict(SequenceID='A_Visit'+str(num),SourceTable=table,MemoryVisitNumbers=list(range(1,num)),OrderedRows=['A'+str(num)+'_Current_%02d'%i for i in range(1,6 if num==2 else 4)],ReviewStatus='READY',ContentVersion=1,RequireAllMemories=num==3,EarlierMemoryVisitNumber=1 if num==3 else 0)
  for result in ('Best','Good','Poor'):values[result+'IntroRows']=['A'+str(num)+'_Memory_'+result.upper()];values['Earlier'+result+'Rows']=['A3_Earlier_'+result.upper()]if num==3 else []
  values.update(NoMemoryIntroRows=['A3_Memory_NEUTRAL']if num==3 else [],AllPositiveOutroRows=['A3_Payoff_Aligned']if num==3 else [],OtherMemoryOutroRows=['A3_Payoff_Clarify']if num==3 else [],CandidateRecordIDs=[],TargetMoodOverride='None',TargetGenreOverride='None',TargetThemeOverride='None')
  for key,value in values.items():asset.set_editor_property(key,value)
  save(asset);visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_A_'+str(num));visit.set_editor_property('Narrative',asset);save(visit)
 R['after']=assert_reference_integrity();R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
