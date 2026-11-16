"""Read-only runtime data/state contract, RED until Day flow is installed."""
import json,os,traceback
from pathlib import Path
import unreal
R={'complete':False,'pass':False}
try:
 bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager');names=list(map(str,unreal.BlueprintEditorLibrary.list_member_variable_names(bp,False)))
 for name in ('CurrentDay','DayPhase','CustomerQueue','CurrentCustomerIndex','ActiveVisit','DayCustomersComplete','FinalStoryEventTriggered','WeekSchedule','AwaitingCustomerExit','ListeningDuration','StoreBGMRef'):assert name in names,name
 c=unreal.get_default_object(bp.generated_class())
 assert c.get_editor_property('CurrentDay')==0 and not c.get_editor_property('TutorialComplete')
 assert not c.get_editor_property('FinalStoryEventTriggered')
 assert c.get_editor_property('ListeningDuration')==10
 assert c.get_editor_property('WeekSchedule') and c.get_editor_property('EnableDaySchedule')
 events=list(map(str,unreal.BlueprintEditorLibrary.list_event_dispatchers(bp)))
 assert all(n in events for n in ('OnTutorialCompleted','OnDayStarted','OnDayEnded','OnCustomerVisitCompleted','OnFinalStoryEvent'))
 for p in ('/Game/RecordShop/Core/Flow/BP_GameFlowManager','/Game/RecordShop/Interaction/Actors/BP_Turntable'):
  assert unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(p))
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
