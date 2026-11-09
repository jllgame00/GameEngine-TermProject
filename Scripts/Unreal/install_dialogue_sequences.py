"""Add one-shot pending/active sources to existing DialogueManager; scoring untouched."""
import unreal,json,os,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
PATH='/Game/DialogueManager';MC=PATH+'.DialogueManager_C';LEGACY='/Game/CustomerDialogue';DSTRUCT='/Game/DialogueData'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
NT=L.get_basic_type_by_name('name');NA=L.get_array_type(NT);BT=L.get_basic_type_by_name('bool');DT=L.get_object_reference_type(unreal.DataTable)
def owncall(g,end,name,**args):return own(g,end,MC,name,**args)
def finish(g,end):return owncall(g,end,'FinishDialogueSequence')
try:
 bp=unreal.load_asset(PATH)
 assert 'ActiveDialogueSource' not in list(map(str,L.list_member_variable_names(bp,False))),'Already installed'
 for name,typ in [('PendingDialogueSource',DT),('PendingDialogueRows',NA),('PendingSequenceID',NT),('HasPendingDialogueSequence',BT),('ActiveDialogueSource',DT),('ActiveSequenceID',NT),('DialogueSequenceActive',BT),('LastSequenceRouteStatus',NT)]:assert L.add_member_variable(bp,name,typ)
 specs={
  'SetPendingDialogueSequence':([('SourceTable',DT),('OrderedRowNames',NA),('SequenceID',NT)],[('Accepted',BT)]),
  'IsDialogueSequenceValid':([('SourceTable',DT),('OrderedRowNames',NA),('SequenceID',NT)],[('Valid',BT)]),
  'BuildLegacyDialogueRows':([],[('Rows',NA)]),
  'ClearPendingDialogueSequence':([],[]),'ClearDialogueContext':([],[]),'CancelDialogueSequence':([],[]),
  'BeginDialogueSequence':([],[]),'AdvanceDialogueSequence':([],[]),'FinishDialogueSequence':([],[])}
 for name,(ins,outs) in specs.items():
  g=fn(bp,name);inputs(g,ins);outputs(g,outs)
  if name in ('IsDialogueSequenceValid','BuildLegacyDialogueRows'):g.set_is_pure_function(True)
  if name in ('BeginDialogueSequence','AdvanceDialogueSequence','FinishDialogueSequence','IsDialogueSequenceValid','BuildLegacyDialogueRows'):g.set_function_is_private()
 assert L.compile_blueprint(bp)
 g=G.get_graph_editor_by_name(bp,'ClearPendingDialogueSequence');end=g.find_graph_entry_pin()
 for key,value in [('HasPendingDialogueSequence','false'),('PendingDialogueSource','None'),('PendingSequenceID','None')]:end=assign(g,end,key,value)
 clear(g,end,get(g,'PendingDialogueRows'))
 g=G.get_graph_editor_by_name(bp,'ClearDialogueContext');end=owncall(g,g.find_graph_entry_pin(),'ClearPendingDialogueSequence')
 for key,value in [('DialogueSequenceActive','false'),('ActiveDialogueSource','None'),('ActiveSequenceID','None'),('CurrentLineIndex',0)]:end=assign(g,end,key,value)
 clear(g,end,get(g,'DialogueList'))
 g=G.get_graph_editor_by_name(bp,'CancelDialogueSequence');owncall(g,g.find_graph_entry_pin(),'ClearDialogueContext')
 g=G.get_graph_editor_by_name(bp,'IsDialogueSequenceValid');a=inputs(g,specs['IsDialogueSequenceValid'][0]);end,no=valid(g,a['SourceTable'],g.find_graph_entry_pin());ret(g,no,Valid='false')
 typ=call(g,'/Script/Engine.DataTableFunctionLibrary.GetDataTableRowStruct');link(a['SourceTable'],pin(typ,'Table'))
 for c in [calc(g,'EqualEqual_ObjectObject',A=pin(typ,'ReturnValue',True),B=DSTRUCT+'.DialogueData'),calc(g,'NotEqual_NameName',A=a['SequenceID'],B='None'),calc(g,'Greater_IntInt',A=array_len(g,a['OrderedRowNames']),B=0)]:
  end,no=branch(g,end,c);ret(g,no,Valid='false')
 body,row,done=each(g,end,a['OrderedRowNames'])
 end,n=invoke(g,body,'/Script/Engine.DataTableFunctionLibrary.DoesDataTableRowExist',Table=a['SourceTable'],RowName=row)
 yes,no=branch(g,end,pin(n,'ReturnValue',True));ret(g,no,Valid='false');ret(g,done,Valid='true')
 g=G.get_graph_editor_by_name(bp,'SetPendingDialogueSequence');a=inputs(g,specs['SetPendingDialogueSequence'][0])
 occupied,end=branch(g,g.find_graph_entry_pin(),get(g,'DialogueSequenceActive'));ret(g,occupied,Accepted='false')
 end=owncall(g,end,'ClearPendingDialogueSequence')
 checknode=call(g,MC+':IsDialogueSequenceValid')
 for k,v in a.items():link(v,pin(checknode,k))
 end,bad=branch(g,end,pin(checknode,'Valid',True));bad=assign(g,bad,'LastSequenceRouteStatus','INVALID_PENDING');ret(g,bad,Accepted='false')
 for k,v in [('PendingDialogueSource',a['SourceTable']),('PendingDialogueRows',a['OrderedRowNames']),('PendingSequenceID',a['SequenceID']),('HasPendingDialogueSequence','true')]:end=assign(g,end,k,v)
 ret(g,end,Accepted='true')
 g=G.get_graph_editor_by_name(bp,'BuildLegacyDialogueRows');assert g.add_local_variable('LegacyRows',NA)
 end,n=invoke(g,g.find_graph_entry_pin(),'/Script/Engine.DataTableFunctionLibrary.GetDataTableRowNames',Table=LEGACY)
 body,key,done=each(g,end,pin(n,'OutRowNames',True));row=table_row(g,body,None,key,LEGACY);data=pin(row,'ReturnValue',True)
 split=action(g,'Break Dialogue Data',[data]);link(data,pin(split,'DialogueData'))
 end=check(g,row.find_then_pin(),calc(g,'EqualEqual_StrStr',A=struct_field(split,'Mood'),B=get(g,'CurrentMood')))
 append(g,end,local_get(g,'LegacyRows'),key)
 end,_=invoke(g,done,'/Script/Engine.KismetArrayLibrary.SortNameArray',TargetArray=local_get(g,'LegacyRows'),bStableSort='true',bLexicalSort='true',SortOrder='Ascending')
 ret(g,end,Rows=local_get(g,'LegacyRows'))
 g=G.get_graph_editor_by_name(bp,'BeginDialogueSequence');occupied,end=branch(g,g.find_graph_entry_pin(),get(g,'DialogueSequenceActive'))
 # Keep pending until its valid source/rows/identity have been copied to active.
 use_pending,legacy=branch(g,end,get(g,'HasPendingDialogueSequence'))
 n=call(g,MC+':IsDialogueSequenceValid');link(get(g,'PendingDialogueSource'),pin(n,'SourceTable'));link(get(g,'PendingDialogueRows'),pin(n,'OrderedRowNames'));link(get(g,'PendingSequenceID'),pin(n,'SequenceID'))
 explicit,invalid=branch(g,use_pending,pin(n,'Valid',True))
 for k,v in [('ActiveDialogueSource',get(g,'PendingDialogueSource')),('DialogueList',get(g,'PendingDialogueRows')),('ActiveSequenceID',get(g,'PendingSequenceID')),('LastSequenceRouteStatus','EXPLICIT')]:explicit=assign(g,explicit,k,v)
 # Invalid pending shares the same harmless legacy source fallback.
 fallback=call(g,MC+':ClearPendingDialogueSequence');link(legacy,fallback.find_execute_pin());link(invalid,fallback.find_execute_pin())
 legacy=fallback.find_then_pin();legacy=assign(g,legacy,'ActiveDialogueSource',LEGACY)
 rows=call(g,MC+':BuildLegacyDialogueRows');legacy=assign(g,legacy,'DialogueList',pin(rows,'Rows',True));legacy=assign(g,legacy,'ActiveSequenceID','LEGACY_MOOD');legacy=assign(g,legacy,'LastSequenceRouteStatus','LEGACY')
 start=call(g,MC+':ClearPendingDialogueSequence');link(explicit,start.find_execute_pin());link(legacy,start.find_execute_pin());end=start.find_then_pin()
 end=assign(g,end,'CurrentLineIndex',0);end=assign(g,end,'DialogueSequenceActive','true');owncall(g,end,'AdvanceDialogueSequence')
 g=G.get_graph_editor_by_name(bp,'AdvanceDialogueSequence');end=check(g,g.find_graph_entry_pin(),get(g,'DialogueSequenceActive'))
 show,done=branch(g,end,calc(g,'Less_IntInt',A=get(g,'CurrentLineIndex'),B=array_len(g,get(g,'DialogueList'))));finish(g,done)
 key=item(g,get(g,'DialogueList'),get(g,'CurrentLineIndex'))
 end,n=invoke(g,show,'/Script/Engine.DataTableFunctionLibrary.DoesDataTableRowExist',Table=get(g,'ActiveDialogueSource'),RowName=key)
 end,bad=branch(g,end,pin(n,'ReturnValue',True));finish(g,bad)
 row=table_row(g,end,get(g,'ActiveDialogueSource'),key,LEGACY);data=pin(row,'ReturnValue',True);split=action(g,'Break Dialogue Data',[data]);link(data,pin(split,'DialogueData'))
 # Snapshot row data before the index advances; a local avoids re-evaluation of key.
 ST=L.get_struct_type(unreal.load_asset(DSTRUCT));assert g.add_local_variable('DisplayedRow',ST)
 end=local_set(g,row.find_then_pin(),'DisplayedRow',data);end=assign(g,end,'CurrentLineIndex',calc(g,'Add_IntInt',A=get(g,'CurrentLineIndex'),B=1))
 split2=action(g,'Break Dialogue Data',[local_get(g,'DisplayedRow')]);link(local_get(g,'DisplayedRow'),pin(split2,'DialogueData'))
 dispatch(g,end,'On Update Dialogue UI',Speaker=struct_field(split2,'Speaker'),DialogueText=struct_field(split2,'Text'));finish(g,pin(row,'RowNotFound',True))
 g=G.get_graph_editor_by_name(bp,'FinishDialogueSequence');end=check(g,g.find_graph_entry_pin(),get(g,'DialogueSequenceActive'));end=owncall(g,end,'ClearDialogueContext');dispatch(g,end,'On Dialogue Finished')
 # Preserve the connected EvaluateLP component exactly; replace only dialogue code.
 eg=evgraph(bp);start=byname(eg,'K2Node_CustomEvent_0');nextline=byname(eg,'K2Node_CustomEvent_2');evaluate=byname(eg,'K2Node_CustomEvent_1')
 keep={evaluate.get_name()};pending=[evaluate]
 while pending:
  node=pending.pop()
  for p in node.list_all_pins():
   for q in p.list_connected_pins():
    other=q.get_owning_node()
    if other.get_name() not in keep:keep.add(other.get_name());pending.append(other)
 keep.update([start.get_name(),nextline.get_name()])
 eg.remove_nodes([n for n in eg.list_all_nodes() if n.get_name() not in keep and n.get_class().get_name()!='K2Node_Event'])
 start.find_then_pin().break_pin_links();nextline.find_then_pin().break_pin_links()
 owncall(eg,start.find_then_pin(),'BeginDialogueSequence');owncall(eg,nextline.find_then_pin(),'AdvanceDialogueSequence')
 assert L.compile_blueprint(bp)
 for name in specs:layout(G.get_graph_editor_by_name(bp,name))
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False);R['saved'].append(bp.get_path_name());R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
