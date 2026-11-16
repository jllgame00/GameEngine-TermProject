"""Day7 I/J production data and preservation contract; read-only Editor check."""
import os,json,sys,traceback,hashlib
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,text_literal
from record_expansion_support import candidates
R={'complete':False,'pass':False,'visits':[]}
try:
 data=json.loads((ROOT/'Scripts/Unreal/customer_ij_dialogue.json').read_text(encoding='utf8'))
 day=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Day07');visits=list(day.get_editor_property('Visits'))
 assert [str(v.get_editor_property('CustomerID'))for v in visits]==['I','J'],'Day7 still TEMP or wrong authored order'
 for order,(identity,source)in enumerate(data.items(),1):
  visit=visits[order-1];asset=visit.get_editor_property('Narrative');assert asset
  assert (visit.get_editor_property('Day'),visit.get_editor_property('VisitNumber'),visit.get_editor_property('OrderInDay'))==(7,1,order)
  assert asset.get_path_name()=='/Game/RecordShop/Data/Narrative/DA_'+identity+'1_Narrative.DA_'+identity+'1_Narrative'
  assert str(asset.get_editor_property('SequenceID'))==identity+'_V1'
  assert list(map(str,asset.get_editor_property('OrderedRows')))==list(source['rows'])
  assert [str(asset.get_editor_property(k))for k in ('TargetMoodOverride','TargetGenreOverride','TargetThemeOverride')]==source['profile']
  assert str(asset.get_editor_property('ReviewStatus'))=='READY'
  for key in ('MemoryVisitNumbers','BestIntroRows','GoodIntroRows','PoorIntroRows','NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):assert not asset.get_editor_property(key),(identity,key)
  assert not asset.get_editor_property('RequireAllMemories')and asset.get_editor_property('EarlierMemoryVisitNumber')==0
  assert list(map(str,asset.get_editor_property('CandidateRecordIDs')))==source['candidates']==candidates(identity,1)
  assert asset.get_editor_property('SourceTable')==unreal.load_asset(source['source'])
  rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(asset.get_editor_property('SourceTable')))
  assert len(rows)==4 and {r['Name']:text_literal(r['Text'])for r in rows}==source['rows']
  assert all(text_literal(r['Speaker'])==source['speaker']and [r['Mood'],r['MusicPreference']]==source['profile'][:2]for r in rows)
  assert [r['Name']for r in rows if r['IsEndNode']]==[identity+'1_Current_04']
  for key,value in source['reactions'].items():assert str(asset.get_editor_property(key))==value
  assert visit.get_editor_property('IsPlaceholderContent')and str(visit.get_editor_property('StoryEventID'))=='None'
  assert visit.get_editor_property('CustomerClass')==unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')
  handle=visit.get_editor_property('CustomerData');assert handle.get_editor_property('data_table')is None and str(handle.get_editor_property('row_name'))in ('','None')
  R['visits'].append(dict(id=identity,day=7,visit=1,order=order,sequence=identity+'_V1',candidates=source['candidates'],profile=source['profile'],appearance='PLACEHOLDER'))
 ref=json.loads((ROOT/'Scripts/Unreal/customer_ij_reference.json').read_text(encoding='utf8'))
 from ending_validation_support import migrated_hash
 for path,sha in ref['unchanged_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==migrated_hash(path,sha),path
 for path,entry in ref['packages'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['after'],path
 # Empty defaults must preserve every previously authored narrative instance.
 for assetdata in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/RecordShop/Data/Narrative',False):
  if str(assetdata.asset_name).startswith('DA_')and str(assetdata.asset_name)not in ('DA_I1_Narrative','DA_J1_Narrative'):
   old=assetdata.get_asset()
   for key in data['I']['reactions']:assert not str(old.get_editor_property(key)),(old.get_name(),key)
 R.update(legacy=assert_reference_integrity(),protected=len(ref['unchanged_sha256']),**{'pass':True})
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
