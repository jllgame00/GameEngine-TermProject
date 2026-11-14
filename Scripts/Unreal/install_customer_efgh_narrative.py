"""Data-only E/F/G/H authoring through Editor APIs; shared production assets protected."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity
NAR='/Game/RecordShop/Data/Narrative';R={'complete':False,'pass':False,'saved':[]}
PROFILES={'E':('Quiet','Jazz','Sociable'),'F':('Restless','Electronic','Adventurous'),'G':('Quiet','Folk','Sociable'),'H':('Quiet','Classical','Reflective')}
DAYS={'E':1,'F':3,'G':5,'H':6}

def protected():
 baseline=json.loads((ROOT/'Scripts/Unreal/customer_efgh_reference_baseline.json').read_text(encoding='utf8'))
 for path,sha in baseline['asset_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 return len(baseline['asset_sha256'])

def save(asset):
 assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);R['saved'].append(asset.get_path_name())

try:
 R['protected_before']=protected();data=json.loads((ROOT/'Scripts/Unreal/customer_efgh_dialogue.json').read_text(encoding='utf8'));assert set(data)==set(PROFILES)
 struct=unreal.load_asset('/Game/DialogueData');kind=unreal.load_class(None,NAR+'/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C')
 for identity,tags in PROFILES.items():
  authored=data[identity];assert authored['source']==NAR+'/DT_'+identity+'_Dialogue'and list(authored['rows'])==[identity+'1_Current_%02d'%i for i in range(1,5)]
  table=unreal.load_asset(authored['source'])
  if table is None:
   factory=unreal.DataTableFactory();factory.set_editor_property('struct',struct);table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_'+identity+'_Dialogue',NAR,unreal.DataTable,factory)
  def loc(row,key,value):return 'NSLOCTEXT("Customer'+identity+'", '+json.dumps(row+'_'+key)+', '+json.dumps(value,ensure_ascii=False)+')'
  rows=[dict(Name=k,DialogueID=k,Speaker=loc(k,'Speaker',authored['speaker']),Text=loc(k,'Text',v),Mood=tags[0],MusicPreference=tags[1],IsEndNode=k==identity+'1_Current_04')for k,v in authored['rows'].items()]
  assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),struct);save(table)
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_1')
  assert (str(visit.get_editor_property('CustomerID')),visit.get_editor_property('VisitNumber'),visit.get_editor_property('Day'))==(identity,1,DAYS[identity])
  name='DA_'+identity+'1_Narrative';asset=unreal.load_asset(NAR+'/'+name)
  if asset is None:
   factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',kind);asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,NAR,kind,factory)
  values=dict(SequenceID=identity+'_V1',SourceTable=table,OrderedRows=list(authored['rows']),MemoryVisitNumbers=[],CandidateRecordIDs=[],TargetMoodOverride=tags[0],TargetGenreOverride=tags[1],TargetThemeOverride=tags[2],ReviewStatus='READY',ContentVersion=1,RequireAllMemories=False,EarlierMemoryVisitNumber=0)
  for field in ('BestIntroRows','GoodIntroRows','PoorIntroRows','NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):values[field]=[]
  for field,value in values.items():asset.set_editor_property(field,value)
  save(asset);visit.set_editor_property('Narrative',asset);save(visit)
 R['protected_after']=protected();R['legacy']=assert_reference_integrity();R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
