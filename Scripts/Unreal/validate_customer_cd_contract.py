"""Read-only C/D production contract; expected RED until data is installed."""
import unreal,os,json,hashlib,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,text_literal
from record_expansion_support import RECORD_IDS,candidates,assert_protected_assets
from customer_cd_validation_support import PROFILES,DAYS,expected_cd_rows
R={'complete':False,'pass':False,'visits':[]}
try:
 R['legacy']=assert_reference_integrity()
 base=json.loads((ROOT/'Scripts/Unreal/customer_cd_reference_baseline.json').read_text(encoding='utf8'))
 assert_protected_assets(base)
 data=json.loads((ROOT/'Scripts/Unreal/customer_cd_dialogue.json').read_text(encoding='utf-8-sig'))
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 R['schedule']=[(str(v.get_editor_property('CustomerID')),v.get_editor_property('VisitNumber'),v.get_editor_property('Day'),v.get_editor_property('OrderInDay'))for day in week.get_editor_property('Days')for v in day.get_editor_property('Visits')]
 for identity in ('C','D'):
  for number in (1,2):
   asset=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_'+identity+str(number)+'_Narrative');assert asset,'Missing '+identity+str(number)+' production narrative'
   visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_'+identity+'_'+str(number))
   assert visit.get_editor_property('Narrative')==asset
   assert (str(visit.get_editor_property('CustomerID')),visit.get_editor_property('VisitNumber'),visit.get_editor_property('Day'))==(identity,number,DAYS[identity][number-1])
   assert str(asset.get_editor_property('SequenceID'))==identity+'_V'+str(number)
   table=unreal.load_asset(data[identity]['source']);assert table and asset.get_editor_property('SourceTable')==table
   rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
   assert len(rows)==12 and {r['Name']:text_literal(r['Text'])for r in rows}==data[identity]['rows']
   assert all(text_literal(r['Speaker'])==data[identity]['speaker']and r['Mood']=='Quiet'and r['MusicPreference']==PROFILES[identity][1]for r in rows)
   assert {r['Name']for r in rows if r['IsEndNode']}=={identity+'1_Current_05',identity+'2_Current_04'}
   assert list(map(str,asset.get_editor_property('OrderedRows')))==expected_cd_rows(identity,number)
   assert list(asset.get_editor_property('MemoryVisitNumbers'))==([1]if number==2 else [])
   assert [str(asset.get_editor_property(k))for k in ('TargetMoodOverride','TargetGenreOverride','TargetThemeOverride')]==list(PROFILES[identity])
   assert list(map(str,asset.get_editor_property('CandidateRecordIDs')))==candidates(identity,number)
   assert not asset.get_editor_property('RequireAllMemories')and asset.get_editor_property('EarlierMemoryVisitNumber')==0
   for name in ('NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):assert not asset.get_editor_property(name)
   for result in ('Best','Good','Poor'):assert list(map(str,asset.get_editor_property(result+'IntroRows')))==([identity+'2_Memory_'+result.upper()]if number==2 else [])
   assert str(asset.get_editor_property('ReviewStatus'))=='READY'and asset.get_editor_property('ContentVersion')==1
   assert visit.get_editor_property('IsPlaceholderContent'),'Appearance must remain explicitly placeholder'
   R['visits'].append({'id':identity,'visit':number,'day':DAYS[identity][number-1],'sequence':str(asset.get_editor_property('SequenceID')),'profile':list(PROFILES[identity]),'appearance':'PLACEHOLDER'})
 for day in week.get_editor_property('Days'):
  for v in day.get_editor_property('Visits'):
   if str(v.get_editor_property('CustomerID'))not in ('A','B','C','D','E','F','G','H','I','J'):assert v.get_editor_property('Narrative')is None
 cat=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue')
 assert list(map(str,unreal.DataTableFunctionLibrary.get_data_table_row_names(cat.get_editor_property('Table'))))==RECORD_IDS
 for identity in RECORD_IDS:assert cat.call_method('ResolvePlayableRecord',args=(identity,))[0]
 R.update(protected_assets=len(base['asset_sha256']),new_rows=24,**{'pass':True})
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
