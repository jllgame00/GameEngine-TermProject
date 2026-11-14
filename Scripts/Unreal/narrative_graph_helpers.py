"""Supported Blueprint construction helpers for narrative foundation installers."""
from day_graph_helpers import *
def ret(g,prev,**values):
 n=g.add_return_node();link(prev,n.find_execute_pin())
 for key,value in values.items():
  if hasattr(value,'is_valid'):link(value,pin(n,key))
  else:val(pin(n,key),value)
 return n
def local_get(g,name):return pin(g.add_get_local_variable_node(name),name,True)
def local_set(g,prev,name,value):
 n=g.add_set_local_variable_node(name);link(prev,n.find_execute_pin())
 if hasattr(value,'is_valid'):link(value,pin(n,name))
 else:val(pin(n,name),value)
 return n.find_then_pin()
def each(g,prev,array):
 n=g.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop');assert n
 link(prev,pin(n,'Exec'));link(array,pin(n,'Array'));return pin(n,'LoopBody',True),pin(n,'Array Element',True),pin(n,'Completed',True)
def check(g,prev,condition):return branch(g,prev,condition)[0]
def append(g,prev,array,value):
 n=call(g,'/Script/Engine.KismetArrayLibrary.Array_Add');link(array,pin(n,'TargetArray'));link(value,pin(n,'NewItem'));link(prev,n.find_execute_pin());return n.find_then_pin()
def clear(g,prev,array):return invoke(g,prev,'/Script/Engine.KismetArrayLibrary.Array_Clear',TargetArray=array)[0]
def table_row(g,prev,source,row,prototype):
 n=action(g,'Get Data Table Row');val(pin(n,'DataTable'),prototype)
 if source is not None:link(source,pin(n,'DataTable'))
 if hasattr(row,'is_valid'):link(row,pin(n,'RowName'))
 else:val(pin(n,'RowName'),row)
 link(prev,n.find_execute_pin());return n

def struct_field(node,key):return next(p for p in node.list_output_pins() if str(p.get_pin_name()).startswith(key+'_'))
def inputs(g,items):return {k:param(g,k,t) for k,t in items}
def outputs(g,items):
 existing=[n for n in g.list_all_nodes() if n.get_class().get_name()=='K2Node_FunctionResult']
 for k,t in items:
  if not existing or not existing[0].find_input_pin(k).is_valid():g.add_graph_output_parameter(k,t)
def bool_valid(g,obj):
 n=call(g,'/Script/Engine.KismetSystemLibrary.IsValid');link(obj,pin(n,'Object'));return pin(n,'ReturnValue',True)
