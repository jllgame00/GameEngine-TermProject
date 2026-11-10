"""Read-only B production audit; RED before B data exists."""
import os,json,hashlib,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,text_literal
from narrative_graph_helpers import L,G
R={'complete':False,'pass':False}
try:
 R['legacy']=assert_reference_integrity()
 base=json.loads((ROOT/'Scripts/Unreal/customer_b_reference_baseline.json').read_text(encoding='utf-8'))
 for path,sha in base['asset_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 flow=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
 R['graphs']={key:[str(n.get_node_title())for n in G.get_graph_editor_by_name(flow,key).list_all_nodes()]for key in ('ConfigureActiveNarrative','ApplyVisitProfileOverrides','EvaluateRecordScore','CommitRecommendationHistory')}
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 R['visits']=[{'id':str(v.get_editor_property('CustomerID')),'visit':v.get_editor_property('VisitNumber'),'day':v.get_editor_property('Day'),'source':v.get_editor_property('Narrative').get_path_name()if v.get_editor_property('Narrative')else None}for day in week.get_editor_property('Days')for v in day.get_editor_property('Visits')]
 R['profile']=unreal.get_default_object(unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')).get_editor_property('CustomerProfile').export_text()
 for num in (1,2,3):
  asset=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_B'+str(num)+'_Narrative');assert asset,'Missing B'+str(num)+' production narrative'
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_B_'+str(num));assert visit.get_editor_property('Narrative')==asset
  assert str(asset.get_editor_property('SequenceID'))=='B_V'+str(num)
  assert str(asset.get_editor_property('TargetMoodOverride'))==('Restless'if num==1 else 'Quiet')
  assert str(asset.get_editor_property('TargetGenreOverride'))=='Electronic'and str(asset.get_editor_property('TargetThemeOverride'))=='Adventurous'
 authored=json.loads((ROOT/'Scripts/Unreal/customer_b_dialogue.json').read_text(encoding='utf-8-sig'))
 table=unreal.load_asset(authored['source']);rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
 assert len(rows)==26 and {r['Name']:text_literal(r['Text'])for r in rows}==authored['rows']
 assert all(text_literal(r['Speaker'])==authored['speaker']and r['Mood']==('Restless'if r['Name'].startswith('B1_')else 'Quiet')and r['MusicPreference']=='Electronic'for r in rows)
 for num in (1,2,3):
  visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_B_'+str(num));asset=visit.get_editor_property('Narrative')
  assert (str(visit.get_editor_property('CustomerID')),visit.get_editor_property('VisitNumber'),visit.get_editor_property('Day'))==('B',num,{1:2,2:4,3:6}[num])
  assert list(asset.get_editor_property('MemoryVisitNumbers'))==list(range(1,num))
  assert bool(asset.get_editor_property('RequireAllMemories'))==(num==3)
  assert asset.get_editor_property('EarlierMemoryVisitNumber')==(1 if num==3 else 0)
  assert list(map(str,asset.get_editor_property('CandidateRecordIDs')))==(['RS001','RS002','RS003']if num==1 else [])
  assert str(asset.get_editor_property('ReviewStatus'))=='READY'and asset.get_editor_property('SourceTable')==table
 for d in week.get_editor_property('Days'):
  for v in d.get_editor_property('Visits'):
   if str(v.get_editor_property('CustomerID'))not in ('A','B','C','D','E','F','G','H'):assert v.get_editor_property('Narrative')is None
 catalogue=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue')
 assert list(map(str,unreal.DataTableFunctionLibrary.get_data_table_row_names(catalogue.get_editor_property('Table'))))==['RS001','RS002','RS003']
 assert not catalogue.call_method('ResolveRecord',args=('RS004',))[0]
 result_ui=unreal.load_asset('/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback')
 assert all(name in [g.get_name()for g in L.list_graphs(result_ui)]for name in ('UsesVisitProfileOverrides','PreferenceAwareFeedback'))
 R['new_rows']=26;R['protected_assets']=len(base['asset_sha256']);R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
