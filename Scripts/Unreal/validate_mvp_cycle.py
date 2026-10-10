"""Observe one contiguous production cycle; no downstream function/event injection.

Existing blank authored row is used unchanged. Enhanced Input IA_Interact,
Slate navigation/Enter and native Windows Enter messages are synthetic.
Use --rendered --windowed for native Result Enter or --result-navigation for
NullRHI virtual-user Tab/Enter. Both assert production focus without setting it.
Pawn teleport supplies interaction geometry only;
customer navigation, gameplay state, completion and exit are never manipulated.
"""
import os,json,time,traceback,sys
from pathlib import Path
from datetime import datetime,timezone
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
OUT=Path(os.environ['MVP_RESULT'])
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager'
TT='/Game/RecordShop/Interaction/Actors/BP_Turntable'
SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
DU='/Game/RecordShop/UI/Dialogue/WBP_Dialogue'
SU='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect'
TU='/Game/RecordShop/UI/Turntable/WBP_Turntable'
RU='/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback'
CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer'
R={'complete':False,'pass':False,'started_utc':datetime.now(timezone.utc).isoformat(),'stages':[],'compiles':{},'fixture':'unchanged existing blank CustomerDialogue/NewRow; no generated or saved fixture','input':'synthetic Enhanced Input IA_Interact + synthetic Slate Enter; Result uses native Windows Enter or virtual Slate Tab/Enter with production focus asserted; pawn positioned for collision; customer route untouched'}
def save():OUT.write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf-8')
def cls(path):return unreal.load_class(None,path+'.'+path.rsplit('/',1)[1]+'_C')
def widgets(path):return list(unreal.WidgetLibrary.get_all_widgets_of_class(world,cls(path),True))
def mark(stage,**extra):
 R['stages'].append({'stage':stage,'utc':datetime.now(timezone.utc).isoformat(),'state':str(flow.get_editor_property('CurrentState')),'customer':str(flow.get_editor_property('ActiveCustomer')),**extra});save();unreal.log('MVP_STAGE '+stage)
def state(value):assert int(flow.get_editor_property('CurrentState').value)==value,str(flow.get_editor_property('CurrentState'))
def no_modals():assert not any(widgets(x) for x in [DU,SU,TU,RU])
def wait_frames(count=4):
 for _ in range(count):yield
def click(widget,name):
 button=widget.get_editor_property(name)
 interaction.set_focus(button)
 button.set_keyboard_focus()
 yield from wait_frames()
 key=unreal.Key();key.import_text('Enter')
 assert interaction.press_and_release_key(key),'Slate Enter not handled for '+name
 yield from wait_frames()
 R.setdefault('ui_inputs',[]).append({'button':name,'pathway':'Slate Enter -> focused SButton -> OnClicked'});save()

def continue_with_default_focus(result):
 # WidgetInteraction uses a separate Slate virtual user. To exercise the actual
 # PlayerController keyboard focus, post Windows key messages to this editor's
 # window. Do not set focus, activate windows, or call any button/gameplay handler.
 import ctypes
 from ctypes import wintypes
 button=result.get_editor_property('Continue')
 assert button.has_keyboard_focus(), 'Production did not focus Result Continue'
 assert button.has_user_focus(pc), 'Continue lacks owning player focus'
 if os.environ.get('MVP_RESULT_NAVIGATION')=='1':
  # NullRHI has no native Windows input window. Exercise ordinary navigation for
  # the separate virtual Slate user, after asserting the real player's focus.
  # There is deliberately no set_focus/set_keyboard_focus call for Result.
  R['result_default_focus']={'keyboard_focus':True,'owning_player_focus':True,'test_focus_correction':False,'input':'virtual Slate Tab then Enter; not native keyboard delivery'}
  key=unreal.Key();key.import_text('Tab');interaction.press_and_release_key(key)
  yield from wait_frames()
  key.import_text('Enter');interaction.press_and_release_key(key)
  yield from wait_frames()
  R.setdefault('ui_inputs',[]).append({'button':'Continue','pathway':'synthetic Slate virtual-user Tab/Enter -> navigation -> OnClicked; native player default focus separately asserted'})
  save();return
 user32=ctypes.WinDLL('user32',use_last_error=True)
 callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 user32.EnumWindows.argtypes=[callback_type,wintypes.LPARAM]
 user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
 user32.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
 user32.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
 user32.PostMessageW.restype=wintypes.BOOL
 windows=[]
 @callback_type
 def visit(hwnd,param):
  pid=wintypes.DWORD();user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
  if pid.value==os.getpid():
   title=ctypes.create_unicode_buffer(512);user32.GetWindowTextW(hwnd,title,512)
   if title.value:windows.append((hwnd,title.value))
  return True
 user32.EnumWindows(visit,0)
 candidates=[(hwnd,title) for hwnd,title in windows if title.startswith('RecordShop - ')]
 assert len(candidates)==1,windows
 hwnd,title=candidates[0]
 R['result_default_focus']={'keyboard_focus':True,'owning_player_focus':True,'test_focus_correction':False,'window':title}
 save()
 assert user32.PostMessageW(hwnd,0x0100,0x0D,1 | (0x1C << 16)),ctypes.get_last_error()
 yield from wait_frames(2)
 assert user32.PostMessageW(hwnd,0x0101,0x0D,1 | (0x1C << 16) | (3 << 30)),ctypes.get_last_error()
 yield from wait_frames()
 R.setdefault('ui_inputs',[]).append({'button':'Continue','pathway':'synthetic Windows Enter messages -> Slate keyboard user -> production-focused SButton -> OnClicked; no test-side focus assignment'})
 save()
def interact(actor,path):
 origin,extent=actor.get_actor_bounds(False);component=pawn.get_editor_property('BPC_Interaction')
 movement=pawn.get_component_by_class(unreal.CharacterMovementComponent);movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);movement.stop_movement_immediately()
 found=False
 for yaw,offset in [(0,unreal.Vector(-1,0,0)),(180,unreal.Vector(1,0,0)),(90,unreal.Vector(0,-1,0)),(-90,unreal.Vector(0,1,0))]:
  pos=origin+offset*((extent.x if offset.x else extent.y)+100);pos.z=max(origin.z,100)
  pawn.set_actor_location_and_rotation(pos,unreal.Rotator(0,yaw,0),False,True)
  hit=unreal.SystemLibrary.sphere_trace_single(component,pos,pos+pawn.get_actor_forward_vector()*180,60,unreal.TraceTypeQuery.ECC_INTERACTABLE,False,[],unreal.DrawDebugTrace.NONE,True)
  if hit and actor.get_name() in hit.export_text():found=True;break
 assert found,'No interaction geometry '+actor.get_name()
 yield from wait_frames()
 lib=unreal.get_default_object(unreal.load_class(None,'/Script/Engine.SubsystemBlueprintLibrary'))
 subsystem=lib.call_method('GetLocalPlayerSubSystemFromPlayerController',args=(pc,unreal.EnhancedInputLocalPlayerSubsystem.static_class()))
 action=unreal.load_asset('/Game/RecordShop/Input/IA_Interact');keys=[k.export_text() for k in subsystem.query_keys_mapped_to_action(action)];assert 'E' in keys
 subsystem.inject_input_vector_for_action(action,unreal.Vector(1,0,0),[],[])
 yield from wait_frames()
 assert len(widgets(path))==1,(path,len(widgets(path)))
 R.setdefault('interaction_inputs',[]).append({'target':actor.get_name(),'keys':keys,'trace':hit.export_text(),'pathway':'synthetic Enhanced Input -> IA_Interact -> sphere trace -> interface -> UI'});save()

level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
save()
for path in [FLOW,TT,SHELF,'/Game/DialogueManager',DU,SU,TU,RU,CUSTOMER,'/Game/RecordShop/Interaction/Components/BPC_Interaction','/Game/RecordShop/Interaction/Interfaces/BPI_Interactable','/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter','/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController']:
 R['compiles'][path]=unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(path))
assert all(R['compiles'].values())
R['dialogue_rows']=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/CustomerDialogue')));save()
assert level.load_level('/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox')
unreal.EditorPythonScripting.set_keep_python_script_alive(True);level.editor_request_begin_play()
start=time.monotonic();phase={'generator':None,'end':None}

def run():
 global world,flow,pc,pawn,interaction
 while not editor.get_game_world():yield
 world=editor.get_game_world();flow=unreal.GameplayStatics.get_all_actors_of_class(world,cls(FLOW))[0]
 pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 mark('Greybox startup')
 while not widgets(DU):
  assert time.monotonic()-start<70,'Customer did not naturally reach dialogue'
  yield
 state(1);customer=flow.get_editor_property('ActiveCustomer');assert customer
 manager=flow.get_editor_property('DialogueManagerRef');assert manager.get_editor_property('CurrentLineIndex')==1
 assert manager.get_editor_property('CurrentCustomer').export_text()==customer.get_editor_property('CustomerProfile').export_text()
 assert manager.get_editor_property('CurrentMood')==''
 assert len(widgets(DU))==1;mark('Spawn -> entry -> Ready -> StartDialogue -> UI',line_index=1)
 interaction=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False))
 interaction.set_component_tick_enabled(False);interaction.activate(True)
 yield from click(widgets(DU)[0],'Next')
 assert not widgets(DU);state(2);assert not pc.get_editor_property('show_mouse_cursor');mark('Next -> finished -> RecordSelection')
 shelf=unreal.GameplayStatics.get_all_actors_of_class(world,cls(SHELF))[0]
 yield from interact(shelf,SU);mark('Shelf interaction -> record selection UI')
 yield from click(widgets(SU)[0],'BTN_LP01')
 tt=unreal.GameplayStatics.get_all_actors_of_class(world,cls(TT))[0]
 assert tt.get_editor_property('HasRecord');assert 'Test_record_01' in tt.get_editor_property('CurrentRecord').export_text();assert not widgets(SU);state(3)
 mark('Record selected -> shelf -> GameFlow -> Turntable.SetRecord',record=tt.get_editor_property('CurrentRecord').export_text())
 yield from interact(tt,TU);mark('Turntable interaction -> UI')
 widget=widgets(TU)[0]
 for name,step in [('BTN_OpenLid',1),('BTN_PlaceRecord',2),('BTN_SelectRPM',2),('BTN_RPM33',3),('BTN_MoveTonearm',4)]:
  yield from click(widget,name);assert tt.get_editor_property('TurntableStep')==step,(name,tt.get_editor_property('TurntableStep'))
 mark('Ordered turntable setup',rpm=tt.get_editor_property('SelectedRPM'))
 yield from click(widget,'BTN_Play')
 assert tt.get_editor_property('TurntableStep')==5;assert tt.get_editor_property('CompletionSent');assert len(widgets(RU))==1;assert not widgets(TU);state(5)
 assert widget.get_editor_property('TurntableRef') is None
 result=widgets(RU)[0];assert str(result.get_editor_property('RecordID').get_text())=='Test_record_01'
 assert str(result.get_editor_property('ScoreStatus').get_text())=='Score: unavailable'
 mark('Audio=None deterministic completion -> Result',score_available=False,audible_playback=False)
 unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(OUT.with_suffix('.png'))+'" -nosuffix')
 yield from wait_frames(30)
 before=customer.get_actor_location();yield from continue_with_default_focus(result)
 assert not widgets(RU);assert flow.get_editor_property('ResultSubmitted');assert not pc.get_editor_property('show_mouse_cursor')
 mark('Result Continue -> FinishResult -> customer exit route',before_exit=str(before))
 while flow.get_editor_property('ActiveCustomer'):
  assert time.monotonic()-start<150,'Exit route did not finish'
  yield
 state(0);no_modals();assert not pc.get_editor_property('show_mouse_cursor');assert flow.get_editor_property('DialogueWidgetRef') is None;assert flow.get_editor_property('ResultWidgetRef') is None
 mark('CustomerExited -> ActiveCustomer cleared -> Explore',after_exit=str(customer.get_actor_location()))
 interaction.destroy_component(pawn)
 R['pass']=True;R['complete']=True;save()

def tick(delta):
 if phase.get('busy'):return
 phase['busy']=True
 try:
  if phase['end'] is not None:
   if time.monotonic()-phase['end']>3:
    unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
   return
  if phase['generator'] is None:phase['generator']=run()
  assert time.monotonic()-start<180,'Cycle timeout'
  next(phase['generator'])
 except StopIteration:
  level.editor_request_end_play();phase['end']=time.monotonic()
 except Exception:
  R['fatal']=traceback.format_exc();R['complete']=True;save();level.editor_request_end_play();phase['end']=time.monotonic()
 finally:phase['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
