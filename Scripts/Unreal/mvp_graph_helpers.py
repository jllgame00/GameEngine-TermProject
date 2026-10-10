"""Shared supported Editor graph helpers; no asset mutations on import."""
import unreal
L=unreal.BlueprintEditorLibrary
G=unreal.BlueprintGraphEditor
def pin(n,name,out=False):
 p=n.find_output_pin(name) if out else n.find_input_pin(name)
 assert p.is_valid(),str(n.get_node_title())+':'+name+' available='+str([str(x.get_pin_name()) for x in n.list_all_pins()])
 return p

def link(a,b):
 assert a.try_create_connection(b),str(a.get_pin_name())+' -> '+str(b.get_pin_name())

def val(p,s): assert p.set_pin_value(str(s)),str(s)
def call(g,path):
 n=g.add_call_function_node(path)
 assert n,path
 return n

def action(g,suffix,context=(),declaring=None):
 unreal.log('INSTALL_ACTION '+suffix)
 normalize=lambda s: ''.join(c for c in s.lower() if c.isalnum())
 names=[str(n) for n in g.list_available_nodes(list(context)) if normalize(str(n).rsplit('|',1)[-1]).endswith(normalize(suffix))]
 assert names, suffix+' candidates='+str([str(n) for n in g.list_available_nodes(list(context)) if 'break' in str(n).lower()])
 for name in names:
  unreal.log('INSTALL_CREATE '+name)
  node=g.create_node_from_name(name,unreal.Vector2D(0,0),list(context),declaring)
  if node:return node
 raise RuntimeError('No matching action '+suffix)

def cls(path):return unreal.load_class(None,path+'.'+path.rsplit('/',1)[1]+'_C')
def get(g,name):return pin(g.add_get_member_variable_node(name),name,True)
def setv(g,name,value=None):
 n=g.add_set_member_variable_node(name)
 if value is not None:val(pin(n,name),value)
 return n

def function(bp,name):return G.create_and_edit_function_graph(bp,name)
def evgraph(bp):return G.get_graph_editor_by_name(bp,'EventGraph')
def valid(g,obj,previous):
 n=g.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:IsValid')
 assert n
 link(obj,pin(n,'InputObject'));link(previous,pin(n,'exec'))
 return pin(n,'Is Valid',True),pin(n,'Is Not Valid',True)

def signature_event(bp,name,params):
 assert L.add_event_dispatcher(bp,name+'Signature')
 for key,typ in params: assert L.add_event_dispatcher_parameter(bp,name+'Signature',key,typ)
 assert L.compile_blueprint(bp)
 node=evgraph(bp).add_dispatcher_event_node(name+'Signature')
 assert node
 assert L.remove_event_dispatcher(bp,name+'Signature')
 return node

def restore(g,previous):
 pc=call(g,'/Script/Engine.GameplayStatics.GetPlayerController')
 cursor=g.add_set_member_variable_node('bShowMouseCursor','/Script/Engine.PlayerController')
 val(pin(cursor,'bShowMouseCursor'),'false');link(pin(pc,'ReturnValue',True),pin(cursor,'self'))
 mode=call(g,'/Script/UMG.WidgetBlueprintLibrary.SetInputMode_GameOnly')
 val(pin(mode,'bFlushInput'),'true');link(pin(pc,'ReturnValue',True),pin(mode,'PlayerController'))
 focus=call(g,'/Script/UMG.WidgetBlueprintLibrary.SetFocusToGameViewport')
 link(previous,cursor.find_execute_pin());link(cursor.find_then_pin(),mode.find_execute_pin());link(mode.find_then_pin(),focus.find_execute_pin())
 return focus.find_then_pin()

def layout(g):
 for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%6)*360,(i//6)*310))
