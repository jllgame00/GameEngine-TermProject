"""RED-first production history contract; no saves or mutations."""
import json,os,traceback
from pathlib import Path
import unreal
R={'complete':False,'pass':False}
try:
 bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
 names=[g.get_name() for g in unreal.BlueprintEditorLibrary.list_graphs(bp)]
 for name in ('HasPreviousVisit','GetLatestRecommendation','GetRecommendationHistory','GetRecommendationForVisit','GetActiveVisitMemory','ResetRecommendationHistory'):
  assert name in names,'Missing history API: '+name
 cdo=unreal.get_default_object(bp.generated_class())
 assert not cdo.get_editor_property('RecommendationHistory')
 assert not cdo.call_method('HasPreviousVisit',args=('A',))
 assert cdo.call_method('GetLatestRecommendation',args=('A',)) is None
 assert cdo.call_method('GetRecommendationForVisit',args=('A',1)) is None
 assert not cdo.call_method('GetRecommendationHistory',args=('A',))
 entry=unreal.load_class(None,'/Game/RecordShop/Data/History/BP_RecommendationHistoryEntry.BP_RecommendationHistoryEntry_C');assert entry
 obj=unreal.get_default_object(entry)
 for name in ('CustomerID','VisitNumber','Day','RecordID','RecommendationScore','RecommendationResult','Sequence'):obj.get_editor_property(name)
 assert 'OnRevisitMemoryReady' in list(map(str,unreal.BlueprintEditorLibrary.list_event_dispatchers(bp)))
 assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
