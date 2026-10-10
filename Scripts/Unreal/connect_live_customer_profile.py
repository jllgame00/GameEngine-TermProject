"""Carry the existing CustomerData struct on the live actor; no authored values.

Only exact typed assignment and the existing Mood field are connected. Dialogue
selection retains root DialogueManager's existing mood filter. No ID join is added.
"""
import sys,json,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import *
FLOW='/Game/RecordShop/Core/Flow/BP_GameFlowManager';DM='/Game/DialogueManager';CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer'
R={'complete':False,'saved':[]}
try:
 customer=unreal.load_asset(CUSTOMER);flow=unreal.load_asset(FLOW);dm=unreal.load_asset(DM)
 assert 'CustomerProfile' not in [str(x) for x in L.list_member_variable_names(customer,False)],'Profile already connected'
 typ=L.get_member_variable_type(dm,'CurrentCustomer')
 assert '/Game/CustomerData.CustomerData' in typ.export_text()
 assert evgraph(customer).add_member_variable('CustomerProfile',typ)
 L.set_blueprint_variable_instance_editable(customer,'CustomerProfile',True)
 assert L.compile_blueprint(customer)
 fg=evgraph(flow)
 start=next(n for n in fg.list_all_nodes() if str(n.get_node_title())=='StartDialogue')
 upstream=start.find_execute_pin().list_connected_pins()[0];start.find_execute_pin().break_pin_links()
 profile_node=fg.add_get_member_variable_node('CustomerProfile',CUSTOMER+'.BP_Customer_C');link(get(fg,'ActiveCustomer'),pin(profile_node,'self'));profile=pin(profile_node,'CustomerProfile',True)
 assign=fg.add_set_member_variable_node('CurrentCustomer',DM+'.DialogueManager_C');link(get(fg,'DialogueManagerRef'),pin(assign,'self'));link(profile,pin(assign,'CurrentCustomer'));link(upstream,assign.find_execute_pin())
 data=action(fg,'BreakCustomerData',[profile]);mood=next(p for p in data.list_all_pins() if str(p.get_pin_name()).startswith('Mood_'))
 setmood=fg.add_set_member_variable_node('CurrentMood',DM+'.DialogueManager_C');link(get(fg,'DialogueManagerRef'),pin(setmood,'self'));link(mood,pin(setmood,'CurrentMood'));link(assign.find_then_pin(),setmood.find_execute_pin());link(setmood.find_then_pin(),start.find_execute_pin())
 R['profile_default']=unreal.get_default_object(customer.generated_class()).get_editor_property('CustomerProfile').export_text()
 R['compiles']={a.get_path_name():L.compile_blueprint(a) for a in [customer,flow,dm]};assert all(R['compiles'].values())
 for a in [customer,flow]:
  assert unreal.EditorAssetLibrary.save_loaded_asset(a);R['saved'].append(a.get_path_name())
 R['complete']=True
except Exception:R['fatal']=traceback.format_exc()
finally:
 (ROOT/'Saved/MVPCompletion/live-profile.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
 unreal.SystemLibrary.quit_editor()
