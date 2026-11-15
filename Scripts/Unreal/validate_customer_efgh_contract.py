"""Read-only single-visit production contract; RED until E/F/G/H data exists."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,text_literal
from record_expansion_support import RECORD_IDS,candidates,assert_protected_assets
from customer_efgh_validation_support import PROFILES,DAYS,ORDERS,expected_efgh_rows
R={'complete':False,'pass':False,'visits':[]}
try:
 R['legacy']=assert_reference_integrity()
 base=json.loads((ROOT/'Scripts/Unreal/customer_efgh_reference_baseline.json').read_text(encoding='utf8'))
 assert_protected_assets(base)
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 visits=[v for day in week.get_editor_property('Days')for v in day.get_editor_property('Visits')]
 for identity in PROFILES:
  asset=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_'+identity+'1_Narrative');assert asset,'Missing '+identity+'1 production narrative'
  data=json.loads((ROOT/'Scripts/Unreal/customer_efgh_dialogue.json').read_text(encoding='utf8'))[identity]
  matching=[v for v in visits if str(v.get_editor_property('CustomerID'))==identity];assert len(matching)==1
  visit=matching[0];assert visit.get_editor_property('Narrative')==asset
  assert (visit.get_editor_property('VisitNumber'),visit.get_editor_property('Day'),visit.get_editor_property('OrderInDay'))==(1,DAYS[identity],ORDERS[identity])
  assert str(asset.get_editor_property('SequenceID'))==identity+'_V1'
  table=unreal.load_asset(data['source']);assert table and asset.get_editor_property('SourceTable')==table
  rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
  assert len(rows)==4 and {r['Name']:text_literal(r['Text'])for r in rows}==data['rows']
  assert all(text_literal(r['Speaker'])==data['speaker']and (r['Mood'],r['MusicPreference'])==PROFILES[identity][:2]for r in rows)
  assert {r['Name']for r in rows if r['IsEndNode']}=={identity+'1_Current_04'}
  assert list(map(str,asset.get_editor_property('OrderedRows')))==expected_efgh_rows(identity)
  assert [str(asset.get_editor_property(k))for k in ('TargetMoodOverride','TargetGenreOverride','TargetThemeOverride')]==list(PROFILES[identity])
  for key in ('MemoryVisitNumbers','BestIntroRows','GoodIntroRows','PoorIntroRows','NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):assert not asset.get_editor_property(key),(identity,key)
  assert list(map(str,asset.get_editor_property('CandidateRecordIDs')))==candidates(identity,1)
  assert not asset.get_editor_property('RequireAllMemories')and asset.get_editor_property('EarlierMemoryVisitNumber')==0
  assert str(asset.get_editor_property('ReviewStatus'))=='READY'and asset.get_editor_property('ContentVersion')==1
  assert visit.get_editor_property('IsPlaceholderContent')
  assert visit.get_editor_property('CustomerClass')==unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')
  R['visits'].append(dict(id=identity,visit=1,day=DAYS[identity],order=ORDERS[identity],sequence=identity+'_V1',profile=PROFILES[identity],appearance='PLACEHOLDER'))
 for v in visits:
  if str(v.get_editor_property('CustomerID')).startswith('TEMP_D7_'):assert v.get_editor_property('Narrative')is None
 cat=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue')
 assert list(map(str,unreal.DataTableFunctionLibrary.get_data_table_row_names(cat.get_editor_property('Table'))))==RECORD_IDS
 for identity in RECORD_IDS:assert cat.call_method('ResolvePlayableRecord',args=(identity,))[0]
 R.update(protected_assets=len(base['asset_sha256']),new_rows=16,**{'pass':True})
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
