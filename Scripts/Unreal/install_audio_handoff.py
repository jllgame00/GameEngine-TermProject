"""Editor-only selected-LP BGM migration; exactly GFM and Turntable packages."""
import unreal,os,json,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';FC=FLOW+'.BP_GameFlowManager_C'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable';TC=TT+'.BP_Turntable_C'
KC='/Game/RecordShop/Data/Records/BP_RecordCatalogue.BP_RecordCatalogue_C'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
def owncall(g,end,name,**args):return own(g,end,FC,name,**args)
def join(g,ends,name,value):
 n=setv(g,name,value)
 for end in ends:link(end,n.find_execute_pin())
 return n.find_then_pin()
def split_record(g,record):
 n=action(g,'Break ST Record Data',[record]);link(record,pin(n,'ST_RecordData'));return n
def normalized_graph(bp,name):
 g=G.get_graph_editor_by_name(bp,name)
 return [{'id':n.get_name(),'title':str(n.get_node_title()),'class':n.get_class().get_name(),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in g.list_all_nodes()]
def graph_digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 start=json.loads((ROOT/'Saved/MVPCompletion/audio-handoff-start-state.json').read_text(encoding='utf8'))
 paths=['Content'+p[len('/Game'):]+'.uasset'for p in (FLOW,TT)]
 before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in paths}
 assert all(before[p]==start['sha256'][p]for p in paths),'Packages differ from read-only audit; refuse migration'
 bp=unreal.load_asset(FLOW);tt=unreal.load_asset(TT);eg=evgraph(bp)
 excluded={FLOW:{'EventGraph','StopStoreBGM','BeginDay'},TT:{'EventGraph'}}
 protected={p:{g.get_name():graph_digest(normalized_graph(asset,g.get_name()))for g in L.list_graphs(asset)if g.get_name()not in excluded[p]}for p,asset in ((FLOW,bp),(TT,tt))}
 assert 'CurrentStoreBGMRecordID'not in list(map(str,L.list_member_variable_names(bp,False))),'Already installed'
 ft=L.get_member_variable_type(tt,'TonearmMotionAlpha')
 for key,kind in [('CurrentStoreBGMRecordID',L.get_basic_type_by_name('name')),('StoreBGMVolume',ft),('StoreBGMFadeInDuration',ft),('StoreBGMFadeOutDuration',ft)]:assert L.add_member_variable(bp,key,kind)
 for key in ('StoreBGMVolume','StoreBGMFadeInDuration','StoreBGMFadeOutDuration'):L.set_blueprint_variable_instance_editable(bp,key,True)
 L.set_blueprint_variable_instance_editable(bp,'StoreBGMSound',False)
 for key in ('BeginCompletedStoreBGM','FinishStoreBGMStop','ResetDayAudio'):fn(bp,key)
 play=eg.add_custom_event_node('PlayCurrentStoreBGM')
 start_event=byname(eg,'K2Node_CustomEvent_11');finished=byname(eg,'K2Node_CustomEvent_12')
 # The old BGM cluster is isolated: remove its dead hardcoded implementation, keep public events.
 nodes={n.get_name():n for n in eg.list_all_nodes()};seen=set();todo=[start_event.get_name(),finished.get_name()]
 while todo:
  key=todo.pop()
  if key in seen:continue
  seen.add(key);todo.extend(q.get_owning_node().get_name()for p in nodes[key].list_all_pins()for q in p.list_connected_pins())
 assert len(seen)==20 and 'K2Node_CallFunction_50'in seen,seen
 eg.remove_nodes([nodes[k]for k in seen if k not in (start_event.get_name(),finished.get_name())])
 assert L.compile_blueprint(bp)
 # Clearing demand precedes unbinding/fading; no late completion can restart old audio.
 g=fn(bp,'StopStoreBGM');end=assign(g,g.find_graph_entry_pin(),'StoreBGMRequested','false');end=assign(g,end,'CurrentStoreBGMRecordID','None');end=assign(g,end,'StoreBGMSound','None')
 end,no=valid(g,get(g,'StoreBGMRef'),end)
 unbind=action(g,'Unbind all Events from On Audio Finished',[get(g,'StoreBGMRef')],unreal.AudioComponent);link(end,unbind.find_execute_pin())
 end,_=invoke(g,unbind.find_then_pin(),'/Script/Engine.AudioComponent.FadeOut',self=get(g,'StoreBGMRef'),FadeOutDuration=get(g,'StoreBGMFadeOutDuration'),FadeVolumeLevel=0)
 timer(g,end,'FinishStoreBGMStop',get(g,'StoreBGMFadeOutDuration'));assign(g,no,'StoreBGMRef','None')
 g=fn(bp,'FinishStoreBGMStop');end=clear_timer(g,g.find_graph_entry_pin(),'FinishStoreBGMStop');end,no=valid(g,get(g,'StoreBGMRef'),end)
 unbind=action(g,'Unbind all Events from On Audio Finished',[get(g,'StoreBGMRef')],unreal.AudioComponent);link(end,unbind.find_execute_pin())
 end,_=invoke(g,unbind.find_then_pin(),'/Script/Engine.AudioComponent.Stop',self=get(g,'StoreBGMRef'));join(g,[end,no],'StoreBGMRef','None')
 g=fn(bp,'BeginCompletedStoreBGM');end=check(g,g.find_graph_entry_pin(),calc(g,'Not_PreBool',A=get(g,'StoreBGMRequested')))
 end=check(g,end,get(g,'ResultStartedForCustomer'));end=check(g,end,calc(g,'EqualEqual_ByteByte',A=get(g,'CurrentState'),B=5))
 end,_=valid(g,get(g,'TurntableRef'),end);end,_=valid(g,get(g,'RecordCatalogue'),end)
 end=check(g,end,field(g,get(g,'TurntableRef'),'HasRecord',TC));record=field(g,get(g,'TurntableRef'),'CurrentRecord',TC);split=split_record(g,record)
 resolved=call(g,KC+':ResolvePlayableRecord');link(get(g,'RecordCatalogue'),pin(resolved,'self'));link(struct_field(split,'RecordID'),pin(resolved,'RecordID'))
 end=check(g,end,pin(resolved,'Found',True));split=split_record(g,pin(resolved,'Record',True))
 end=owncall(g,end,'FinishStoreBGMStop');end=assign(g,end,'CurrentStoreBGMRecordID',struct_field(split,'RecordID'));end=assign(g,end,'StoreBGMSound',struct_field(split,'Audio'));end=assign(g,end,'StoreBGMRequested','true');owncall(g,end,'PlayCurrentStoreBGM')
 owncall(eg,start_event.find_then_pin(),'BeginCompletedStoreBGM')
 end=check(eg,play.find_then_pin(),get(eg,'StoreBGMRequested'));end,_=valid(eg,get(eg,'StoreBGMSound'),end)
 valid_ref,missing=valid(eg,get(eg,'StoreBGMRef'),end);playing=call(eg,'/Script/Engine.AudioComponent.IsPlaying');link(get(eg,'StoreBGMRef'),pin(playing,'self'));already,stopped=branch(eg,valid_ref,pin(playing,'ReturnValue',True))
 create=call(eg,'/Script/Engine.GameplayStatics.CreateSound2D');link(missing,create.find_execute_pin());link(stopped,create.find_execute_pin());link(get(eg,'StoreBGMSound'),pin(create,'Sound'));val(pin(create,'bAutoDestroy'),'true');val(pin(create,'bPersistAcrossLevelTransition'),'false')
 end=assign(eg,create.find_then_pin(),'StoreBGMRef',pin(create,'ReturnValue',True));end,_=valid(eg,get(eg,'StoreBGMRef'),end)
 bind=action(eg,'Bind Event to On Audio Finished',[get(eg,'StoreBGMRef')],unreal.AudioComponent);link(pin(finished,'OutputDelegate',True),pin(bind,'Delegate'));link(end,bind.find_execute_pin())
 invoke(eg,bind.find_then_pin(),'/Script/Engine.AudioComponent.FadeIn',self=get(eg,'StoreBGMRef'),FadeInDuration=get(eg,'StoreBGMFadeInDuration'),FadeVolumeLevel=get(eg,'StoreBGMVolume'))
 end=check(eg,finished.find_then_pin(),get(eg,'StoreBGMRequested'));valid_ref,missing=valid(eg,get(eg,'StoreBGMRef'),end)
 playing=call(eg,'/Script/Engine.AudioComponent.IsPlaying');link(get(eg,'StoreBGMRef'),pin(playing,'self'));already,stopped=branch(eg,valid_ref,pin(playing,'ReturnValue',True));end=join(eg,[stopped,missing],'StoreBGMRef','None');owncall(eg,end,'PlayCurrentStoreBGM')
 # Result acceptance occurs only after original TT Stop/clear. Keep Continue call as guarded no-op.
 hook=call(eg,FC+':StartStoreBGM');splice(byname(eg,'K2Node_CallFunction_62').find_then_pin(),hook)
 # Selection starts a fade well before the needle; preplay guarantees zero residual overlap.
 hook=call(eg,FC+':StopStoreBGM');splice(byname(eg,'K2Node_CustomEvent_0').find_then_pin(),hook)
 # Declare the TT API before linking it.
 g=fn(tt,'ClearCompletedRecord');end,active=valid(g,get(g,'PlaybackAudio'),g.find_graph_entry_pin())
 # Refuse clearing live selection; normal completed playback has already cleared its component.
 end=active;end=own(g,end,TC,'SetRecord');assign(g,end,'HasRecord','false')
 assert L.compile_blueprint(tt)
 g=fn(bp,'ResetDayAudio');end=owncall(g,g.find_graph_entry_pin(),'StopStoreBGM');end,_=valid(g,get(g,'TurntableRef'),end);own(g,end,TC,'ClearCompletedRecord',self=get(g,'TurntableRef'))
 g=G.get_graph_editor_by_name(bp,'BeginDay');old=next(n for n in g.list_all_nodes()if str(n.get_node_title()).replace(' ','')=='StartStoreBGM');parents=list(old.find_execute_pin().list_connected_pins());children=list(old.find_then_pin().list_connected_pins());g.remove_nodes([old])
 new=call(g,FC+':ResetDayAudio')
 for p in parents:link(p,new.find_execute_pin())
 for p in children:link(new.find_then_pin(),p)
 # Lookup sole existing GFM, stop old BGM synchronously before CreateSound2D.
 g=evgraph(tt);start_audio=byname(g,'K2Node_CustomEvent_1');old_next=list(start_audio.find_then_pin().list_connected_pins());start_audio.find_then_pin().break_pin_links()
 end,lookup=invoke(g,start_audio.find_then_pin(),'/Script/Engine.GameplayStatics.GetActorOfClass',ActorClass=FC);ref=pin(lookup,'ReturnValue',True);end,missing=valid(g,ref,end);end=own(g,end,FC,'FinishStoreBGMStop',self=ref)
 for p in old_next:link(end,p);link(missing,p)
 assert L.compile_blueprint(tt);assert L.compile_blueprint(bp)
 cdo=unreal.get_default_object(bp.generated_class())
 for k,v in dict(StoreBGMSound=None,CurrentStoreBGMRecordID='None',StoreBGMVolume=.18,StoreBGMFadeInDuration=.5,StoreBGMFadeOutDuration=.6).items():cdo.set_editor_property(k,v)
 for p,asset in ((FLOW,bp),(TT,tt)):
  for name,sha in protected[p].items():assert graph_digest(normalized_graph(asset,name))==sha,(p,name)
 for asset in (tt,bp):
  assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);R['saved'].append(asset.get_path_name())
 reference={'packages':{p:{'before':before[p],'after':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}for p in paths},'protected_graphs':protected,'transition':'same-track restart after original Turntable completion','audit':'20261110T052836Z-audio-handoff-audit.json'}
 (ROOT/'Scripts/Unreal/audio_handoff_reference.json').write_text(json.dumps(reference,indent=2),encoding='utf8');R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
