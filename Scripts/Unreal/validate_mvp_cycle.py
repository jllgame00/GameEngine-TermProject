"""Observe one contiguous production cycle; no downstream function/event injection.

Existing blank authored row is used unchanged. Enhanced Input IA_Interact,
Slate navigation/Enter and native Windows Enter messages are synthetic.
Use --rendered --windowed for native Result Enter or --result-navigation for
NullRHI virtual-user Tab/Enter. Both assert production focus without setting it.
Pawn teleport supplies interaction geometry; the settled pre-interaction player
viewpoint is restored after Result Continue for exit evidence.
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

def request_capture(label):
 # Observe the actual viewport only in rendered runs. Requests are evidence,
 # not visual approval; the reviewer must inspect the resulting images.
 if '-nullrhi' in unreal.SystemLibrary.get_command_line().lower():return
 target=OUT.with_name(OUT.stem+'-'+label+'.png')
 unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(target)+'" -nosuffix')
 R.setdefault('screenshots_requested',[]).append({'stage':label,'path':str(target)});save()

def capture(label):
 if '-nullrhi' in unreal.SystemLibrary.get_command_line().lower():return
 request_capture(label)
 yield from wait_frames(4)

def observe_customer(route,force=False):
 customer=flow.get_editor_property('ActiveCustomer')
 if not customer:return
 velocity=customer.get_velocity()
 location=customer.get_actor_location()
 acceleration=customer.get_component_by_class(unreal.CharacterMovementComponent).get_current_acceleration()
 sample={'seconds':round(time.monotonic()-start,3),'route':route,
         'location':str(location),'location_xyz':[location.x,location.y,location.z],'velocity':str(velocity),
         'speed_xy':(velocity.x**2+velocity.y**2)**0.5,
         'acceleration_xy':(acceleration.x**2+acceleration.y**2)**0.5,
         'forward':str(customer.get_actor_forward_vector()),
         'state':str(flow.get_editor_property('CurrentState'))}
 mesh=customer.get_component_by_class(unreal.SkeletalMeshComponent)
 if mesh:
  anim=mesh.get_anim_instance()
  sample['presentation']={'mesh':str(mesh.get_editor_property('skeletal_mesh_asset')),
                          'relative_rotation':mesh.get_editor_property('relative_rotation').export_text(),
                          'relative_scale':mesh.get_editor_property('relative_scale3d').export_text(),
                          'anim_class':anim.get_class().get_path_name() if anim else None}
  if anim:
   montage=anim.get_current_active_montage()
   sample['presentation']['montage']=montage.get_path_name() if montage else None
   sample['presentation']['montage_position']=anim.montage_get_position(montage) if montage else None
   sample['presentation']['montage_playing']=anim.montage_is_playing(montage) if montage else False
   for key in ('GroundSpeed','ShouldMove','IsFalling'):
    sample['presentation'][key]=anim.get_editor_property(key)
 samples=R.setdefault('customer_observations',[])
 if force or not samples or samples[-1]['route']!=route or sample['seconds']-samples[-1]['seconds']>=0.1:
  samples.append(sample)
 return sample
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
 entry_captured=False
 while not widgets(DU):
  assert time.monotonic()-start<70,'Customer did not naturally reach dialogue'
  sample=observe_customer('entry_to_ready')
  active=flow.get_editor_property('ActiveCustomer')
  if not entry_captured and sample and sample['speed_xy']>1 and active.get_distance_to(active.get_editor_property('SeatTarget'))<170:
   entry_captured=True
   request_capture('customer-entering')
  yield
 state(1);customer=flow.get_editor_property('ActiveCustomer');assert customer
 manager=flow.get_editor_property('DialogueManagerRef');assert manager.get_editor_property('CurrentLineIndex')==1
 assert manager.get_editor_property('CurrentCustomer').export_text()==customer.get_editor_property('CustomerProfile').export_text()
 assert manager.get_editor_property('CurrentMood')==''
 assert len(widgets(DU))==1;mark('Spawn -> entry -> Ready -> StartDialogue -> UI',line_index=1)
 ready=observe_customer('ready_dialogue',True)
 mesh=customer.get_component_by_class(unreal.SkeletalMeshComponent)
 assert mesh.get_editor_property('skeletal_mesh_asset').get_name()=='SKM_C01'
 assert mesh.get_anim_instance().get_class().get_name()=='ABP_C01_C'
 talk=mesh.get_anim_instance().get_current_active_montage()
 assert talk and talk.get_name()=='AM_C01_Talk_01', 'Authored talk montage did not start at dialogue handoff'
 assert any(s['route']=='entry_to_ready' and s['speed_xy']>1 and s.get('presentation',{}).get('ShouldMove') for s in R['customer_observations']), 'No natural entry locomotion observed'
 # Ready is connected to AI MoveTo success. The preserved CharacterMovement
 # brakes from its current speed; navigation acceleration must end immediately.
 # Observe every tick so the 0.5 s pose settling budget cannot hide continued
 # movement. Residual travel is bounded by the existing MoveTo acceptance (50 cm).
 previous_speed=ready['speed_xy'];initial_position=mesh.get_anim_instance().montage_get_position(talk)
 settled_at=time.monotonic();stopped_at=None;max_displacement=0
 def check_braking(sample):
  nonlocal previous_speed,stopped_at,max_displacement
  assert sample['acceleration_xy']<=1, 'Navigation acceleration continued after Ready'
  assert not sample['presentation']['ShouldMove'], 'Locomotion input continued after Ready'
  assert sample['speed_xy']<=previous_speed+1, 'Customer gained speed after Ready'
  displacement=sum((a-b)**2 for a,b in zip(sample['location_xyz'],ready['location_xyz']))**0.5
  max_displacement=max(max_displacement,displacement)
  assert displacement<=50, 'Customer braking exceeded the existing MoveTo acceptance radius'
  if stopped_at is not None:assert sample['speed_xy']<=1, 'Customer resumed moving during dialogue'
  if stopped_at is None and sample['speed_xy']<=1:stopped_at=sample['seconds']-ready['seconds']
  previous_speed=sample['speed_xy']
 for _ in range(2):
  yield
  stopped=observe_customer('ready_stopping',True)
  check_braking(stopped)
 anim=mesh.get_anim_instance()
 while time.monotonic()-settled_at<0.5:
  sample=observe_customer('dialogue_observation',True)
  check_braking(sample)
  assert anim.montage_is_playing(talk), 'Talk montage stopped before passive dialogue observation finished'
  yield
 settled=observe_customer('dialogue_settled',True);check_braking(settled)
 assert settled['speed_xy']<=1 and settled['presentation']['GroundSpeed']<=1, 'Customer did not stop within the 0.5 s braking budget'
 R['customer_braking']={'stopped_after_seconds':stopped_at,'max_displacement_cm':max_displacement,'displacement_budget_cm':50,'time_budget_seconds':0.5,'monotonic_decay':True,'no_renewed_acceleration':True}
 assert anim.montage_get_position(talk)>initial_position+0.1, 'Talk montage time did not advance'
 yield from capture('dialogue')
 # Save after the player's initial gravity settling, before interaction geometry
 # changes its movement mode or location. The spawn-frame Z is not a floor pose.
 startup_location=pawn.get_actor_location();startup_rotation=pawn.get_actor_rotation();startup_control_rotation=pc.get_control_rotation()
 interaction=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False))
 interaction.set_component_tick_enabled(False);interaction.activate(True)
 yield from click(widgets(DU)[0],'Next')
 assert not widgets(DU);state(2);assert not pc.get_editor_property('show_mouse_cursor');mark('Next -> finished -> RecordSelection')
 waiting=observe_customer('waiting_after_dialogue',True)
 assert waiting['speed_xy']<=1 and not waiting['presentation']['ShouldMove'], 'Customer did not wait idle after dialogue'
 assert not mesh.get_anim_instance().montage_is_playing(talk), 'Talk montage continued after dialogue close'
 idle_at=time.monotonic()
 while time.monotonic()-idle_at<0.5:
  waiting=observe_customer('waiting_idle_observation')
  assert waiting['speed_xy']<=1 and not waiting['presentation']['ShouldMove'], 'Customer moved while waiting for a record'
  assert not anim.montage_is_playing(talk), 'Talk montage restarted after dialogue close'
  yield
 observe_customer('waiting_idle_settled',True)
 yield from capture('customer-waiting')
 shelf=unreal.GameplayStatics.get_all_actors_of_class(world,cls(SHELF))[0]
 yield from interact(shelf,SU);mark('Shelf interaction -> record selection UI')
 yield from capture('record-selection')
 yield from click(widgets(SU)[0],'BTN_LP01')
 tt=unreal.GameplayStatics.get_all_actors_of_class(world,cls(TT))[0]
 assert tt.get_editor_property('HasRecord');assert 'Test_record_01' in tt.get_editor_property('CurrentRecord').export_text();assert not widgets(SU);state(3)
 mark('Record selected -> shelf -> GameFlow -> Turntable.SetRecord',record=tt.get_editor_property('CurrentRecord').export_text())
 yield from interact(tt,TU);mark('Turntable interaction -> UI')
 yield from capture('turntable-open')
 widget=widgets(TU)[0]
 for name,step in [('BTN_OpenLid',1),('BTN_PlaceRecord',2),('BTN_SelectRPM',2),('BTN_RPM33',3),('BTN_MoveTonearm',4)]:
  yield from click(widget,name);assert tt.get_editor_property('TurntableStep')==step,(name,tt.get_editor_property('TurntableStep'))
 mark('Ordered turntable setup',rpm=tt.get_editor_property('SelectedRPM'))
 yield from capture('turntable-ready')
 yield from click(widget,'BTN_Play')
 assert tt.get_editor_property('TurntableStep')==5;assert tt.get_editor_property('CompletionSent');assert len(widgets(RU))==1;assert not widgets(TU);state(5)
 assert widget.get_editor_property('TurntableRef') is None
 result=widgets(RU)[0];assert str(result.get_editor_property('RecordID').get_text())=='Test_record_01'
 assert str(result.get_editor_property('ScoreStatus').get_text())=='Score: unavailable'
 mark('Audio=None deterministic completion -> Result',score_available=False,audible_playback=False)
 yield from capture('result')
 yield from wait_frames(30)
 before=customer.get_actor_location();yield from continue_with_default_focus(result)
 assert not widgets(RU);assert flow.get_editor_property('ResultSubmitted');assert not pc.get_editor_property('show_mouse_cursor')
 mark('Result Continue -> FinishResult -> customer exit route',before_exit=str(before))
 # The interaction fixture moved the player to the turntable. Restore only the
 # player's settled pre-interaction viewpoint after the real Continue handler; customer and
 # gameplay state are untouched, and exit is sampled during camera settling.
 pawn.set_actor_location_and_rotation(startup_location,startup_rotation,False,True)
 pc.set_control_rotation(startup_control_rotation)
 R.setdefault('viewpoint_observations',[]).append({'stage':'exit','provenance':'Test restores settled pre-interaction player transform/control rotation after actual Result Continue; no customer/state mutation','location':str(startup_location),'rotation':str(startup_rotation),'control_rotation':str(startup_control_rotation)})
 exit_captured=False
 exit_view_frames=0
 while flow.get_editor_property('ActiveCustomer'):
  assert time.monotonic()-start<150,'Exit route did not finish'
  sample=observe_customer('exit',exit_view_frames<4)
  exit_view_frames+=1
  if not exit_captured and exit_view_frames>4 and sample and sample['speed_xy']>300:
   exit_captured=True
   request_capture('customer-exiting')
  yield
 assert any(s['route']=='exit' and s['speed_xy']>1 and s.get('presentation',{}).get('ShouldMove') for s in R['customer_observations']), 'No natural exit locomotion observed'
 state(0);no_modals();assert not pc.get_editor_property('show_mouse_cursor');assert flow.get_editor_property('DialogueWidgetRef') is None;assert flow.get_editor_property('ResultWidgetRef') is None
 mark('CustomerExited -> ActiveCustomer cleared -> Explore',after_exit=str(customer.get_actor_location()))
 yield from capture('explore')
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
