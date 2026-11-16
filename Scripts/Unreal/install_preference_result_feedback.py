"""Replace only Result description leaves for overridden visit profiles; preserve score logic."""
import unreal,json,os,sys,hashlib,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
UI='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback';UC=UI+'.WBP_Result_IntegrationFallback_C'
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C';NC='/Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.BP_VisitNarrativeDefinition_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
try:
 bp=unreal.load_asset(UI);reference=json.loads((ROOT/'Scripts/Unreal/result_feedback_reference.json').read_text(encoding='utf-8'));neutral=json.loads((ROOT/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
 names=[g.get_name()for g in L.list_graphs(bp)]
 if 'UsesVisitProfileOverrides'not in names:assert hashlib.sha256((ROOT/'Content/RecordShop/UI/Result/WBP_Result_IntegrationFallback.uasset').read_bytes()).hexdigest()==reference['widget_sha256']
 BT=L.get_basic_type_by_name('bool');ST=L.get_basic_type_by_name('string')
 g=fn(bp,'UsesVisitProfileOverrides');outputs(g,[('UseNeutral',BT)]);g.set_is_pure_function(True)
 end,n=invoke(g,g.find_graph_entry_pin(),'/Script/Engine.GameplayStatics.GetActorOfClass',ActorClass=FC)
 actor=pin(n,'ReturnValue',True);end,no=valid(g,actor,end);ret(g,no,UseNeutral='false')
 refnode=call(g,FC+':GetActiveNarrativeDefinition');link(actor,pin(refnode,'self'));ref=pin(refnode,'Narrative',True);end,no=valid(g,ref,end);ret(g,no,UseNeutral='false')
 terms=[calc(g,'NotEqual_NameName',A=field(g,ref,k,NC),B='None')for k in ('TargetMoodOverride','TargetGenreOverride','TargetThemeOverride')]
 ret(g,end,UseNeutral=calc(g,'BooleanOR',A=terms[0],B=calc(g,'BooleanOR',A=terms[1],B=terms[2])));layout(g)
 assert L.compile_blueprint(bp)
 g=fn(bp,'PreferenceAwareFeedback');a=inputs(g,[('LegacyText',ST),('NeutralText',ST)]);outputs(g,[('Text',ST)]);g.set_is_pure_function(True)
 use=call(g,UC+':UsesVisitProfileOverrides');n=call(g,'/Script/Engine.KismetMathLibrary.SelectString');link(a['NeutralText'],pin(n,'A'));link(a['LegacyText'],pin(n,'B'));link(pin(use,'UseNeutral',True),pin(n,'bPickA'));ret(g,g.find_graph_entry_pin(),Text=pin(n,'ReturnValue',True));layout(g)
 assert L.compile_blueprint(bp)
 g=G.get_graph_editor_by_name(bp,'SetRawScoreDisplay')
 for category,name,input_name in [('BEST','K2Node_CallFunction_5','A'),('GOOD','K2Node_CallFunction_4','A'),('POOR','K2Node_CallFunction_4','B')]:
  leaf=pin(byname(g,name),input_name)
  old=list(leaf.list_connected_pins())
  if old:
   assert len(old)==1 and 'PreferenceAwareFeedback'in str(old[0].get_owning_node().get_node_title()).replace(' ',''),category
   node=old[0].get_owning_node()
  else:
   assert leaf.get_pin_value()==reference['legacy_pin_defaults'][category],category
   node=call(g,UC+':PreferenceAwareFeedback');val(pin(node,'LegacyText'),leaf.get_pin_value());link(pin(node,'Text',True),leaf)
  val(pin(node,'NeutralText'),neutral[category])
 assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False);R['saved']=[bp.get_path_name()];R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
