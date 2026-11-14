"""Input-driven front-end acceptance helpers; no production mutations on import."""
import json,time
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());DATA=json.loads((ROOT/'Scripts/Unreal/ending_content.json').read_text(encoding='utf8'))
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C'
EC='/Game/RecordShop/UI/Ending/WBP_Ending.WBP_Ending_C';TC='/Game/RecordShop/UI/Title/WBP_Title.WBP_Title_C'
CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C'
def frames(n=3):
 for _ in range(n):yield
def viewport_size(pc,width,height):
 import ctypes,os
 from ctypes import wintypes
 user=ctypes.WinDLL('user32',use_last_error=True);windows=[]
 callback=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
 user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
 user.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
 @callback
 def visit(hwnd,param):
  pid=wintypes.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid));title=ctypes.create_unicode_buffer(512);user.GetWindowTextW(hwnd,title,512)
  if pid.value==os.getpid()and title.value.startswith('RecordShop - '):windows.append(hwnd)
  return True
 user.EnumWindows.argtypes=[callback,wintypes.LPARAM];user.EnumWindows(visit,0);assert len(windows)==1,windows
 hwnd=windows[0];user.ShowWindow.argtypes=[wintypes.HWND,ctypes.c_int];user.ShowWindow(hwnd,9)
 user.GetWindowRect.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.RECT)]
 user.SetWindowPos.argtypes=[wintypes.HWND,wintypes.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.UINT]
 yield from frames(15)
 for _ in range(8):
  actual=pc.get_viewport_size()
  if actual==(width,height):return actual
  rect=wintypes.RECT();assert user.GetWindowRect(hwnd,ctypes.byref(rect))
  assert user.SetWindowPos(hwnd,None,0,0,rect.right-rect.left+width-actual[0],rect.bottom-rect.top+height-actual[1],0x0016)
  yield from frames(15)
 assert pc.get_viewport_size()==(width,height),pc.get_viewport_size()
 return pc.get_viewport_size()
def wait(predicate,seconds=15):
 deadline=time.monotonic()+seconds
 while not predicate():assert time.monotonic()<deadline,'Front-end timeout';yield
def context(editor):
 world=editor.get_game_world()
 if not world:return None
 flows=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,FC))
 return (world,flows[0],unreal.GameplayStatics.get_player_controller(world,0),unreal.GameplayStatics.get_player_pawn(world,0))if flows else None
def alive(actor):
 try:return unreal.SystemLibrary.is_valid(actor)
 except TypeError as error:
  # UE Python cannot marshal an Actor proxy after its World was destroyed.
  assert isinstance(actor,unreal.Actor)and "Cannot nativize 'Actor' as 'Object'"in str(error),str(error)
  return False
def interaction(pawn):
 comp=pawn.call_method('AddComponentByClass',args=(unreal.WidgetInteractionComponent.static_class(),False,unreal.Transform(),False));comp.set_component_tick_enabled(False);comp.activate(True);return comp
def click(panel,component,after=None):
 button=panel.get_editor_property('Continue');assert button.get_is_enabled()and button.has_keyboard_focus(),'Missing production front-end focus'
 component.set_focus(button);yield from frames(2);key=unreal.Key();key.import_text('Enter');assert component.press_and_release_key(key)
 if after:after()
 yield from frames(3)
def no_audio(world,flow):
 assert flow.get_editor_property('StoreBGMRef')is None and not flow.get_editor_property('StoreBGMRequested')
 assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))=='None'
 assert not [a for a in unreal.ObjectIterator(unreal.AudioComponent)if a.get_world()==world and a.is_playing()]
def fresh_title(world,flow,pc,pawn):
 assert str(flow.get_editor_property('PresentationPhase'))=='Title'
 assert flow.get_editor_property('CurrentDay')==0 and str(flow.get_editor_property('DayPhase'))=='AwaitingTutorial'
 assert flow.get_editor_property('ActiveCustomer')is None and flow.get_editor_property('ActiveVisit')is None and not flow.get_editor_property('CustomerQueue')
 assert not flow.get_editor_property('RecommendationHistory')and not flow.get_editor_property('TutorialComplete')and not flow.get_editor_property('FinalStoryEventTriggered')
 assert not flow.get_editor_property('TurntableRef').get_editor_property('HasRecord')
 assert flow.get_editor_property('TurntableRef').is_actor_tick_enabled()
 assert flow.get_editor_property('PrologueStage')==0 and flow.get_editor_property('PrologueWidgetRef')is None and flow.get_editor_property('EndingWidgetRef')is None
 assert pc.get_editor_property('show_mouse_cursor')and pc.get_view_target()==pawn
 assert not unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,CUSTOMER));no_audio(world,flow)
 panel=flow.get_editor_property('TitleWidgetRef');assert panel and panel.is_in_viewport()
 assert str(panel.get_editor_property('RecordTitle').get_text())==DATA['title']and str(panel.get_editor_property('RecordID').get_text())==DATA['new_game']
 assert panel.get_editor_property('Quit').get_is_enabled()
 return panel
def new_game(editor,flow):
 yield from wait(lambda:flow.get_editor_property('FrontEndInputReady'))
 world=flow.get_world();pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 panel=fresh_title(world,flow,pc,pawn);component=interaction(pawn);yield from click(panel,component)
 # The old manager must be destroyed, not reset in-place.
 yield from wait(lambda:not alive(flow),20)
 yield from wait(lambda:context(editor)is not None,20);fresh=context(editor)
 yield from wait(lambda:fresh[1].get_editor_property('PrologueWidgetRef')is not None,10)
 new_flow=fresh[1];assert str(new_flow.get_editor_property('PresentationPhase'))=='Playing'and new_flow.get_editor_property('CurrentDay')==0
 assert not new_flow.get_editor_property('RecommendationHistory')and not new_flow.get_editor_property('TutorialComplete')and not new_flow.get_editor_property('FinalStoryEventTriggered')
 assert not new_flow.get_editor_property('TurntableRef').get_editor_property('HasRecord');no_audio(fresh[0],new_flow)
 assert new_flow.get_editor_property('TurntableRef').is_actor_tick_enabled()
 yield from frames(12);return fresh
def finish_ending(editor,flow,component,report,out,captures=True):
 yield from wait(lambda:str(flow.get_editor_property('PresentationPhase'))=='EndingDialogue')
 world=flow.get_world();panel=flow.get_editor_property('EndingWidgetRef');assert panel
 selected=str(flow.get_editor_property('CurrentStoreBGMRecordID'));sound=flow.get_editor_property('StoreBGMSound')
 from history_validation_support import payload
 history=[payload(e)for e in flow.get_editor_property('RecommendationHistory')]
 pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 assert flow.get_editor_property('ActiveCustomer')is None and flow.get_editor_property('ActiveVisit')is None
 assert not unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,CUSTOMER))
 for _ in range(3):flow.call_method('BeginEnding',args=('FinalStoryEvent',));flow.call_method('FinishDayTransition');flow.call_method('SpawnQueuedCustomer')
 assert flow.get_editor_property('EndingWidgetRef')==panel and flow.get_editor_property('EndingStep')==0
 pages=[]
 for index,page in enumerate(DATA['pages']):
  yield from wait(lambda:flow.get_editor_property('FrontEndInputReady'))
  assert flow.get_editor_property('EndingStep')==index and str(flow.get_editor_property('PresentationPhase'))==page['phase']
  assert str(panel.get_editor_property('RecordTitle').get_text())==page['title']
  assert str(panel.get_editor_property('ScoreStatus').get_text())==page['body']
  assert str(panel.get_editor_property('RecordID').get_text())==page['action']
  assert panel.get_editor_property('Continue').has_keyboard_focus()
  assert pc.get_view_target()==pawn and pc.get_editor_property('show_mouse_cursor')
  assert [payload(e)for e in flow.get_editor_property('RecommendationHistory')]==history
  assert len(unreal.WidgetLibrary.get_all_widgets_of_class(world,unreal.load_class(None,EC),True))==1
  if sound:
   ref=flow.get_editor_property('StoreBGMRef');assert ref and ref.is_playing()and ref.get_editor_property('sound')==sound
   assert str(flow.get_editor_property('CurrentStoreBGMRecordID'))==selected
   assert len([a for a in unreal.ObjectIterator(unreal.AudioComponent)if a.get_world()==world and a.is_playing()])==1
  pages.append(dict(index=index,phase=page['phase'],title=page['title'],audio=selected))
  if captures:
   path=out.with_name(out.stem+'-ending-'+str(index)+'.png');unreal.SystemLibrary.execute_console_command(world,'Shot showui filename="'+str(path)+'" -nosuffix');yield from frames(4);pages[-1]['capture']=str(path)
  # A forged origin cannot consume the one available action.
  flow.call_method('AdvanceEnding',args=(None,));assert flow.get_editor_property('EndingStep')==index
  def duplicate():
   if index<len(DATA['pages'])-1:
    after=flow.get_editor_property('EndingStep');assert after==index+1
    flow.call_method('AdvanceEnding',args=(panel,));assert flow.get_editor_property('EndingStep')==after,'Repeated callback skipped a page'
  yield from click(panel,component,duplicate)
 report.setdefault('ending_runs',[]).append(dict(pages=pages,record=selected,single_widget=True,duplicate_safe=True,history_count=len(history),history_unchanged=True))
 if alive(flow):
  assert str(flow.get_editor_property('PresentationPhase'))in ('Leaving','Traveling')
  for _ in range(3):flow.call_method('ReturnToTitle');flow.call_method('BeginEnding',args=('FinalStoryEvent',));flow.call_method('FinishDayTransition')
 yield from wait(lambda:not alive(flow),20)
 yield from wait(lambda:context(editor)is not None,20);fresh=context(editor)
 yield from wait(lambda:fresh[1].get_editor_property('FrontEndInputReady'))
 fresh_title(*fresh);return fresh
