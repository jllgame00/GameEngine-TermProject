"""Editor-only I/J authoring and optional Result leaves; no flow/audio mutation."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
NAR='/Game/RecordShop/Data/Narrative';SCH='/Game/RecordShop/Data/Schedule'
NC=NAR+'/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C'
UI='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback';UC=UI+'.WBP_Result_IntegrationFallback_C'
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
ALLOWED={'Content/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.uasset','Content/RecordShop/Data/Schedule/DA_Day07.uasset','Content/RecordShop/UI/Result/WBP_Result_IntegrationFallback.uasset'}
def save(asset):
 assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);R['saved'].append(asset.get_path_name())
 OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def instance(path,kind,values):
 asset=unreal.load_asset(path)
 if asset is None:
  factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',kind)
  asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],kind,factory)
 for key,value in values.items():asset.set_editor_property(key,value)
 save(asset);return asset
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 baseline=json.loads((ROOT/'Saved/MVPCompletion/day7-customer-start-state.json').read_text(encoding='utf8'))
 data=json.loads((ROOT/'Scripts/Unreal/customer_ij_dialogue.json').read_text(encoding='utf8'))
 schema=unreal.load_asset(NAR+'/BP_VisitNarrativeDefinition');old=list(map(str,L.list_member_variable_names(schema,False)))
 for key in data['I']['reactions']:
  if key not in old:assert L.add_member_variable(schema,key,L.get_basic_type_by_name('text'))
  L.set_blueprint_variable_instance_editable(schema,key,True)
 assert L.compile_blueprint(schema);save(schema)
 # Wrap existing grade-selected description leaves; all previous fallbacks remain intact.
 bp=unreal.load_asset(UI);ST=L.get_basic_type_by_name('string');NT=L.get_basic_type_by_name('name')
 g=fn(bp,'VisitResultFeedback');a=inputs(g,[('Fallback',ST),('Grade',NT),('Heading',ST)]);outputs(g,[('Text',ST)]);g.set_is_pure_function(True)
 end,n=invoke(g,g.find_graph_entry_pin(),'/Script/Engine.GameplayStatics.GetActorOfClass',ActorClass=FC)
 actor=pin(n,'ReturnValue',True);end,no=valid(g,actor,end);ret(g,no,Text=a['Fallback'])
 n=call(g,FC+':GetActiveNarrativeDefinition');link(actor,pin(n,'self'));ref=pin(n,'Narrative',True)
 end,no=valid(g,ref,end);ret(g,no,Text=a['Fallback'])
 def to_string(value):
  n=call(g,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(value,pin(n,'InText'));return pin(n,'ReturnValue',True)
 def select(x,y,condition):
  n=call(g,'/Script/Engine.KismetMathLibrary.SelectString');link(x,pin(n,'A'));link(y,pin(n,'B'));link(condition,pin(n,'bPickA'));return pin(n,'ReturnValue',True)
 reaction=select(to_string(field(g,ref,'ResultBestText',NC)),select(to_string(field(g,ref,'ResultGoodText',NC)),to_string(field(g,ref,'ResultPoorText',NC)),calc(g,'EqualEqual_NameName',A=a['Grade'],B='GOOD')),calc(g,'EqualEqual_NameName',A=a['Grade'],B='BEST'))
 end,no=branch(g,end,calc(g,'NotEqual_StrStr',A=reaction,B=''));ret(g,no,Text=a['Fallback'])
 body=calc(g,'Concat_StrStr',A=calc(g,'Concat_StrStr',A=a['Heading'],B='\n'),B=reaction)
 exit_text=to_string(field(g,ref,'ExitText',NC));end,no=branch(g,end,calc(g,'NotEqual_StrStr',A=exit_text,B=''));ret(g,no,Text=body)
 ret(g,end,Text=calc(g,'Concat_StrStr',A=calc(g,'Concat_StrStr',A=body,B='\n\n'),B=exit_text));layout(g)
 assert L.compile_blueprint(bp)
 g=G.get_graph_editor_by_name(bp,'SetRawScoreDisplay')
 for grade,name,input_name in [('BEST','K2Node_CallFunction_5','A'),('GOOD','K2Node_CallFunction_4','A'),('POOR','K2Node_CallFunction_4','B')]:
  leaf=pin(byname(g,name),input_name);oldpin=list(leaf.list_connected_pins());assert len(oldpin)==1
  if str(oldpin[0].get_owning_node().get_node_title()).replace(' ','')=='VisitResultFeedback':continue
  previous=oldpin[0];assert str(previous.get_owning_node().get_node_title()).replace(' ','')=='PreferenceAwareFeedback'
  heading=pin(previous.get_owning_node(),'NeutralText').get_pin_value().split('\n')[0]
  leaf.break_pin_links();node=call(g,UC+':VisitResultFeedback');link(previous,pin(node,'Fallback'));val(pin(node,'Grade'),grade);val(pin(node,'Heading'),heading);link(pin(node,'Text',True),leaf)
 assert L.compile_blueprint(bp);save(bp)
 visits=[];struct=unreal.load_asset('/Game/DialogueData')
 for order,(identity,source)in enumerate(data.items(),1):
  table=unreal.load_asset(source['source'])
  if table is None:
   factory=unreal.DataTableFactory();factory.set_editor_property('struct',struct);table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_'+identity+'_Dialogue',NAR,unreal.DataTable,factory)
  def loc(row,key,value):return 'NSLOCTEXT("Customer'+identity+'", '+json.dumps(row+'_'+key)+', '+json.dumps(value,ensure_ascii=False)+')'
  rows=[dict(Name=k,DialogueID=k,Speaker=loc(k,'Speaker',source['speaker']),Text=loc(k,'Text',v),Mood=source['profile'][0],MusicPreference=source['profile'][1],IsEndNode=k==identity+'1_Current_04')for k,v in source['rows'].items()]
  assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),struct);save(table)
  values=dict(SequenceID=identity+'_V1',SourceTable=table,OrderedRows=list(source['rows']),MemoryVisitNumbers=[],CandidateRecordIDs=source['candidates'],TargetMoodOverride=source['profile'][0],TargetGenreOverride=source['profile'][1],TargetThemeOverride=source['profile'][2],ReviewStatus='READY',ContentVersion=1,RequireAllMemories=False,EarlierMemoryVisitNumber=0,**source['reactions'])
  for key in ('BestIntroRows','GoodIntroRows','PoorIntroRows','NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):values[key]=[]
  narrative=instance(NAR+'/DA_'+identity+'1_Narrative',unreal.load_class(None,NC),values)
  visit=instance(SCH+'/DA_Visit_'+identity+'_1',unreal.load_class(None,SCH+'/BP_CustomerVisitDefinition.BP_CustomerVisitDefinition_C'),dict(CustomerID=identity,VisitNumber=1,Day=7,OrderInDay=order,CustomerClass=unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'),StoryEventID='None',IsPlaceholderContent=True,Narrative=narrative))
  visits.append(visit)
 day=unreal.load_asset(SCH+'/DA_Day07');day.set_editor_property('Visits',visits);save(day)
 unchanged={p:h for p,h in baseline['asset_sha256'].items()if p not in ALLOWED}
 for p,h in unchanged.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 ref={'packages':{p:dict(before=baseline['asset_sha256'][p],after=hashlib.sha256((ROOT/p).read_bytes()).hexdigest())for p in sorted(ALLOWED)},'unchanged_sha256':unchanged}
 (ROOT/'Scripts/Unreal/customer_ij_reference.json').write_text(json.dumps(ref,indent=2),encoding='utf8')
 R.update(protected=len(unchanged),**{'pass':True})
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
