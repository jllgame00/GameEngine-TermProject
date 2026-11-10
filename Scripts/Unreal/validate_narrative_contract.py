"""RED-first foundation API/data contract; fresh Editor, no asset saves."""
import os,json,traceback,hashlib
from pathlib import Path
import unreal,sys
sys.path.insert(0,str(Path(unreal.Paths.project_dir())/"Scripts/Unreal"))
from narrative_validation_support import assert_reference_integrity
R={'complete':False,'pass':False}
try:
 dm=unreal.load_asset('/Game/DialogueManager')
 names=[g.get_name() for g in unreal.BlueprintEditorLibrary.list_graphs(dm)]
 for n in ('SetPendingDialogueSequence','ClearPendingDialogueSequence','CancelDialogueSequence'):assert n in names,'Missing sequence API: '+n
 catalogue=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue');assert catalogue
 assert catalogue.call_method('ResolveRecord',args=('RS001',))[0]
 for n in ('RS001','RS002','RS003'):
  result=catalogue.call_method('ResolveRecord',args=(n,));assert result[0],n
 table=catalogue.get_editor_property('Table');assert list(map(str,unreal.DataTableFunctionLibrary.get_data_table_row_names(table)))==['RS001','RS002','RS003']
 rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/CustomerDialogue')))
 assert [r['Name'] for r in rows]==['C01_Quiet_%02d'%i for i in range(1,6)]
 assert unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_A1_Narrative')
 R['reference_integrity']=assert_reference_integrity()
 visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_A_1');definition=visit.get_editor_property('Narrative')
 assert definition.get_editor_property('SourceTable')==unreal.load_asset('/Game/CustomerDialogue')
 assert list(map(str,definition.get_editor_property('OrderedRows')))==['C01_Quiet_%02d'%i for i in range(1,6)]
 assert list(map(str,definition.get_editor_property('CandidateRecordIDs')))==['RS001','RS002','RS003']
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 for day in week.get_editor_property('Days'):
  for v in day.get_editor_property('Visits'):
   if str(v.get_editor_property('CustomerID'))=='A' and v.get_editor_property('VisitNumber')in (2,3):
    assert v.get_editor_property('Narrative')==unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_A'+str(v.get_editor_property('VisitNumber'))+'_Narrative')
   elif str(v.get_editor_property('CustomerID'))in ('B','C','D','E','F','G','H'):
    assert v.get_editor_property('Narrative')==unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_'+str(v.get_editor_property('CustomerID'))+str(v.get_editor_property('VisitNumber'))+'_Narrative')
   elif v!=visit:assert v.get_editor_property('Narrative') is None, v.get_name()
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
