"""Ending production contract; RED before UI and GFM integration exist."""
import unreal,os,json,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
R={'complete':False,'pass':False}
try:
 ending=unreal.load_asset('/Game/RecordShop/UI/Ending/WBP_Ending');title=unreal.load_asset('/Game/RecordShop/UI/Title/WBP_Title')
 assert ending and title,'Missing production Ending/Title widgets'
 L=unreal.BlueprintEditorLibrary;flow=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
 names={str(g.get_name())for g in L.list_graphs(flow)}
 assert {'BootPresentation','BeginEnding','AdvanceEnding','ReturnToTitle','StartNewGame','QuitToDesktop','FinishFrontEndTravel','IsGameplayPresentation'}<=names
 cdo=unreal.get_default_object(flow.generated_class());assert str(cdo.get_editor_property('PresentationPhase'))=='Boot'
 assert cdo.get_editor_property('EndingWidgetRef')is None and cdo.get_editor_property('TitleWidgetRef')is None
 assert cdo.get_editor_property('CurrentDay')==0 and not cdo.get_editor_property('TutorialComplete')and not cdo.get_editor_property('FinalStoryEventTriggered')
 assert not cdo.get_editor_property('RecommendationHistory')and cdo.get_editor_property('StoreBGMRef')is None
 for key,value in [('StoreBGMVolume',.18),('StoreBGMFadeInDuration',.5),('StoreBGMFadeOutDuration',.6)]:assert abs(cdo.get_editor_property(key)-value)<.0001
 for bp in (ending,title,flow,unreal.load_asset('/Game/RecordShop/Interaction/Components/BPC_Interaction')):assert L.compile_blueprint(bp)
 from ending_validation_support import assert_preservation
 R.update(preservation=assert_preservation(),**{'pass':True})
except Exception:R['fatal']=traceback.format_exc();R['pass']=False
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2),encoding='utf8')
