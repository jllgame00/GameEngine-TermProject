"""Data-only C/D install through Editor APIs; shared graphs/assets untouched."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity
PROFILES={'C':('Quiet','Folk','Sociable'),'D':('Quiet','Classical','Reflective')}
DAYS={'C':(2,4),'D':(3,6)}
NAR='/Game/RecordShop/Data/Narrative';R={'complete':False,'pass':False,'saved':[]}
def protected():
 baseline=json.loads((ROOT/'Scripts/Unreal/customer_cd_reference_baseline.json').read_text(encoding='utf8'))
 for path,sha in baseline['asset_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 return len(baseline['asset_sha256'])
def save(asset):
 assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);R['saved'].append(asset.get_path_name())
try:
 R['protected_before']=protected();data=json.loads((ROOT/'Scripts/Unreal/customer_cd_dialogue.json').read_text(encoding='utf-8-sig'));assert set(data)=={'C','D'}
 struct=unreal.load_asset('/Game/DialogueData');kind=unreal.load_class(None,NAR+'/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C')
 for identity in ('C','D'):
  authored=data[identity];assert authored['source']==NAR+'/DT_'+identity+'_Dialogue'and len(authored['rows'])==12
  table=unreal.load_asset(authored['source'])
  if table is None:
   factory=unreal.DataTableFactory();factory.set_editor_property('struct',struct);table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_'+identity+'_Dialogue',NAR,unreal.DataTable,factory)
  def loc(row,key,value):return 'NSLOCTEXT("Customer'+identity+'", '+json.dumps(row+'_'+key)+', '+json.dumps(value,ensure_ascii=False)+')'
  rows=[dict(Name=k,DialogueID=k,Speaker=loc(k,'Speaker',authored['speaker']),Text=loc(k,'Text',v),Mood='Quiet',MusicPreference=PROFILES[identity][1],IsEndNode=k in (identity+'1_Current_05',identity+'2_Current_04'))for k,v in authored['rows'].items()]
  assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),struct);save(table)
  for number in (1,2):
   visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_'+str(number))
   assert (str(visit.get_editor_property('CustomerID')),visit.get_editor_property('VisitNumber'),visit.get_editor_property('Day'))==(identity,number,DAYS[identity][number-1])
   name='DA_'+identity+str(number)+'_Narrative';asset=unreal.load_asset(NAR+'/'+name)
   if asset is None:
    factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',kind);asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,NAR,kind,factory)
   values=dict(SequenceID=identity+'_V'+str(number),SourceTable=table,OrderedRows=[identity+str(number)+'_Current_%02d'%i for i in range(1,6 if number==1 else 5)],MemoryVisitNumbers=[1]if number==2 else [],CandidateRecordIDs=[],TargetMoodOverride=PROFILES[identity][0],TargetGenreOverride=PROFILES[identity][1],TargetThemeOverride=PROFILES[identity][2],ReviewStatus='READY',ContentVersion=1,RequireAllMemories=False,EarlierMemoryVisitNumber=0)
   for field in ('NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):values[field]=[]
   for result in ('Best','Good','Poor'):values[result+'IntroRows']=[identity+'2_Memory_'+result.upper()]if number==2 else []
   for field,value in values.items():asset.set_editor_property(field,value)
   save(asset);visit.set_editor_property('Narrative',asset);save(visit)
 R['protected_after']=protected();R['legacy']=assert_reference_integrity();R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
