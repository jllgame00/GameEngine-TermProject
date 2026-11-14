"""Read-only Editor audit and RED-first Customer A production contract."""
import os,json,traceback,sys,hashlib
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,text_literal
from record_expansion_support import RECORD_IDS,candidates,assert_protected_assets
from narrative_graph_helpers import L,G
R={'complete':False,'pass':False}
try:
 R['reference_integrity']=assert_reference_integrity()
 legacy=unreal.load_asset('/Game/CustomerDialogue')
 R['a1_original_rows']=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(legacy))
 flow=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
 R['routing_graph']=[{'title':str(n.get_node_title()),'class':n.get_class().get_name()} for n in G.get_graph_editor_by_name(flow,'ConfigureActiveNarrative').list_all_nodes()]
 R['result_graphs']=[str(g.get_name())for g in L.list_graphs(flow)if any(k in str(g.get_name())for k in ('Result','Score','History','Revisit'))]
 R['active_profile_default']=unreal.get_default_object(unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C')).get_editor_property('CustomerProfile').export_text()
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 R['visits']=[{'id':str(v.get_editor_property('CustomerID')),'visit':v.get_editor_property('VisitNumber'),'day':v.get_editor_property('Day'),'narrative':v.get_editor_property('Narrative').get_path_name() if v.get_editor_property('Narrative') else None}for d in week.get_editor_property('Days')for v in d.get_editor_property('Visits')]
 for num in (2,3):
  a=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_A'+str(num)+'_Narrative');assert a,'Missing A'+str(num)+' Production Narrative'
  v=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_A_'+str(num));assert v.get_editor_property('Narrative')==a
  assert str(a.get_editor_property('SequenceID'))=='A_Visit'+str(num)
  assert a.get_editor_property('SourceTable')!=legacy
  assert str(a.get_editor_property('ReviewStatus'))=='READY'
 baseline=json.loads((ROOT/'Scripts/Unreal/customer_a_reference_baseline.json').read_text(encoding='utf-8'))
 assert_protected_assets(baseline)
 authored=json.loads((ROOT/'Scripts/Unreal/customer_a_dialogue.json').read_text(encoding='utf-8-sig'))
 table=unreal.load_asset(authored['source']);exported=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
 assert len(exported)==20 and {r['Name']:text_literal(r['Text'])for r in exported}==authored['rows']
 assert all(text_literal(r['Speaker'])==authored['speaker']and r['Mood']=='Quiet'and r['MusicPreference']=='Jazz' for r in exported)
 for num in (2,3):
  definition=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_A'+str(num)+'_Narrative')
  assert list(definition.get_editor_property('MemoryVisitNumbers'))==list(range(1,num))
  assert bool(definition.get_editor_property('RequireAllMemories'))==(num==3)
  assert definition.get_editor_property('EarlierMemoryVisitNumber')==(1 if num==3 else 0)
  assert list(map(str,definition.get_editor_property('CandidateRecordIDs')))==candidates('A',num)
  assert all(str(definition.get_editor_property(k))=='None'for k in ('TargetMoodOverride','TargetGenreOverride','TargetThemeOverride'))
 R['new_rows']=len(exported);R['protected_packages']=len(baseline['asset_sha256']);R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
