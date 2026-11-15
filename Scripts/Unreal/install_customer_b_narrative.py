"""Data-only Customer B install. Never modifies shared GFM/schema/profile defaults."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity
NAR='/Game/RecordShop/Data/Narrative';OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
def protected():
 base=json.loads((ROOT/'Scripts/Unreal/customer_b_reference_baseline.json').read_text(encoding='utf-8'))
 for path,sha in base['asset_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 return len(base['asset_sha256'])
def save(a):
 assert unreal.EditorAssetLibrary.save_loaded_asset(a,False);R['saved'].append(a.get_path_name())
try:
 R['protected_before']=protected();data=json.loads((ROOT/'Scripts/Unreal/customer_b_dialogue.json').read_text(encoding='utf-8-sig'));struct=unreal.load_asset('/Game/DialogueData')
 table=unreal.load_asset(data['source'])
 if table is None:
  f=unreal.DataTableFactory();f.set_editor_property('struct',struct);table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_B_Dialogue',NAR,unreal.DataTable,f)
 def loc(row,key,value):return 'NSLOCTEXT("CustomerB", '+json.dumps(row+'_'+key)+', '+json.dumps(value,ensure_ascii=False)+')'
 rows=[dict(Name=k,DialogueID=k,Speaker=loc(k,'Speaker',data['speaker']),Text=loc(k,'Text',v),Mood='Restless'if k.startswith('B1_')else 'Quiet',MusicPreference='Electronic',IsEndNode=k in ('B1_Current_06','B2_Current_05','B3_Payoff_Aligned','B3_Payoff_Clarify'))for k,v in data['rows'].items()]
 assert len(rows)==26
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),struct);save(table)
 kind=unreal.load_class(None,NAR+'/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C')
 for num in (1,2,3):
  path=NAR+'/DA_B'+str(num)+'_Narrative';asset=unreal.load_asset(path)
  if asset is None:
   f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',kind);asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],NAR,kind,f)
  values=dict(SequenceID='B_V'+str(num),SourceTable=table,MemoryVisitNumbers=list(range(1,num)),OrderedRows=['B'+str(num)+'_Current_%02d'%i for i in range(1,{1:7,2:6,3:4}[num])],ReviewStatus='READY',ContentVersion=1,RequireAllMemories=num==3,EarlierMemoryVisitNumber=1 if num==3 else 0,NoMemoryIntroRows=['B3_Memory_NEUTRAL']if num==3 else [],AllPositiveOutroRows=['B3_Payoff_Aligned']if num==3 else [],OtherMemoryOutroRows=['B3_Payoff_Clarify']if num==3 else [],CandidateRecordIDs=['RS001','RS002','RS003']if num==1 else [],TargetMoodOverride='Restless'if num==1 else 'Quiet',TargetGenreOverride='Electronic',TargetThemeOverride='Adventurous')
  for result in ('Best','Good','Poor'):
   values[result+'IntroRows']=['B'+str(num)+'_Memory_'+result.upper()]if num>1 else []
   values['Earlier'+result+'Rows']=['B3_Earlier_'+result.upper()]if num==3 else []
  for key,value in values.items():asset.set_editor_property(key,value)
  save(asset);visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_B_'+str(num));visit.set_editor_property('Narrative',asset);save(visit)
 R['protected_after']=protected();R['legacy']=assert_reference_integrity();R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
