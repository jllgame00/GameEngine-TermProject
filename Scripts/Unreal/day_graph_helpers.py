"""Small supported Blueprint graph construction helpers for the day installer."""
import unreal
from mvp_graph_helpers import *

def own(g,prev,path,name,**args):return invoke(g,prev,path+':'+name,**args)[0]
def invoke(g,prev,path,**args):
 n=call(g,path)
 for k,v in args.items():
  if hasattr(v,'is_valid'):link(v,pin(n,k))
  else:val(pin(n,k),v)
 link(prev,n.find_execute_pin());return n.find_then_pin(),n

def calc(g,name,**args):
 library='KismetStringLibrary' if ('StrStr' in name or name in ('Concat_StrStr','Conv_IntToString','Conv_NameToString')) else 'KismetMathLibrary'
 n=call(g,'/Script/Engine.'+library+'.'+name)
 for k,v in args.items():
  if hasattr(v,'is_valid'):link(v,pin(n,k))
  else:val(pin(n,k),v)
 return pin(n,'ReturnValue',True)

def assign(g,prev,name,v):
 n=setv(g,name)
 if hasattr(v,'is_valid'):link(v,pin(n,name))
 else:val(pin(n,name),v)
 link(prev,n.find_execute_pin());return n.find_then_pin()

def branch(g,prev,c):
 n=g.add_branch_node();link(prev,n.find_execute_pin());link(c,pin(n,'Condition'));return pin(n,'then',True),pin(n,'else',True)

def field(g,target,name,declaring):
 n=g.add_get_member_variable_node(name,declaring);assert n,name
 link(target,pin(n,'self'));return pin(n,name,True)

def fn(bp,name):
 if name not in [g.get_name() for g in L.list_graphs(bp)]:return function(bp,name)
 g=G.get_graph_editor_by_name(bp,name)
 g.remove_nodes([n for n in g.list_all_nodes() if n.get_class().get_name() not in ('K2Node_FunctionEntry','K2Node_FunctionResult')]);return g

def param(g,name,typ):
 n=g.find_graph_entry_pin().get_owning_node();p=n.find_output_pin(name)
 return p if p.is_valid() else g.add_graph_input_parameter(name,typ)

def selfref(g):return pin(action(g,'Get a reference to self'),'self',True)

def timer(g,prev,name,time,loop=False):
 return invoke(g,prev,'/Script/Engine.KismetSystemLibrary.K2_SetTimer',Object=selfref(g),FunctionName=name,Time=time,bLooping=str(loop).lower())[0]

def clear_timer(g,prev,name):
 return invoke(g,prev,'/Script/Engine.KismetSystemLibrary.K2_ClearTimer',Object=selfref(g),FunctionName=name)[0]

def array_len(g,a):
 n=call(g,'/Script/Engine.KismetArrayLibrary.Array_Length');link(a,pin(n,'TargetArray'));return pin(n,'ReturnValue',True)

def item(g,a,index):
 n=call(g,'/Script/Engine.KismetArrayLibrary.Array_Get');link(a,pin(n,'TargetArray'))
 if hasattr(index,'is_valid'):link(index,pin(n,'Index'))
 else:val(pin(n,'Index'),index)
 return pin(n,'Item',True)

def splice(prev,n):
 after=list(prev.list_connected_pins());prev.break_pin_links();link(prev,n.find_execute_pin())
 for p in after:link(n.find_then_pin(),p)

def byname(g,name):return next(n for n in g.list_all_nodes() if n.get_name()==name)

def visibility(g,prev,obj,value):return invoke(g,prev,'/Script/UMG.Widget.SetVisibility',self=obj,InVisibility=value)[0]

def dispatch(g,prev,name,**args):
 n=action(g,'Call '+name)
 for k,v in args.items():
  if hasattr(v,'is_valid'):link(v,pin(n,k))
  else:val(pin(n,k),v)
 link(prev,n.find_execute_pin());return n.find_then_pin()
