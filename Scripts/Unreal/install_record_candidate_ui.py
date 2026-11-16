"""Keep three-card UMG, replacing authored payloads with catalogue resolution."""
import unreal,json,sys,os,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
UI='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';UC=UI+'.WBP_RecordSelect_C'
KC='/Game/RecordShop/Data/Records/BP_RecordCatalogue.BP_RecordCatalogue_C';CAT='/Game/RecordShop/Data/Records/DA_RecordCatalogue'
FC='/Game/RecordShop/Core/Flow/BP_GameFlowManager.BP_GameFlowManager_C';SHELF='/Game/RecordShop/Interaction/Actors/BP_RecordShelf'
OUT=Path(os.environ['MVP_RESULT']);R={'complete':False,'pass':False,'saved':[]}
RT=L.get_struct_type(unreal.load_asset('/Game/RecordShop/Data/Structs/ST_RecordData'));NT=L.get_basic_type_by_name('name');NA=L.get_array_type(NT);BT=L.get_basic_type_by_name('bool');TT=L.get_basic_type_by_name('text');KT=L.get_object_reference_type(unreal.load_class(None,KC))
def save(a):
 assert L.compile_blueprint(a);assert unreal.EditorAssetLibrary.save_loaded_asset(a,False);R['saved'].append(a.get_path_name())
def ui_text(g,end,name,text):
 # TextBlock Designer variable flags are protected. Use the existing button's
 # public content accessor and a standard runtime cast; keep its font/layout.
 if name=='TextBlock_0':return end
 index=name.rsplit('_',1)[1]
 n=call(g,'/Script/UMG.ContentWidget.GetContent');link(get(g,'BTN_LP0'+index),pin(n,'self'))
 obj=pin(n,'ReturnValue',True);cast=action(g,'Cast To Text Block',[obj],unreal.TextBlock)
 link(obj,pin(cast,'Object'))
 if cast.find_execute_pin().is_valid():link(end,cast.find_execute_pin());end=cast.find_then_pin()
 target=next(p for p in cast.list_output_pins() if str(p.get_pin_name()).replace(' ','').startswith('As'))
 return invoke(g,end,'/Script/UMG.TextBlock.SetText',self=target,InText=text)[0]
def strtext(g,value):
 n=call(g,'/Script/Engine.KismetTextLibrary.Conv_TextToString');link(value,pin(n,'InText'));return pin(n,'ReturnValue',True)
def astext(g,value):
 n=call(g,'/Script/Engine.KismetTextLibrary.Conv_StringToText');link(value,pin(n,'InString'));return pin(n,'ReturnValue',True)
def concat(g,*values):
 result=values[0]
 for v in values[1:]:result=calc(g,'Concat_StrStr',A=result,B=v)
 return result
try:
 bp=unreal.load_asset(UI);assert 'CandidateSetReady' not in list(map(str,L.list_member_variable_names(bp,False))),'Already migrated'
 tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree) if t.get_outer()==bp)
 for w in unreal.ObjectIterator(unreal.TextBlock):
  if w.get_outer()==tree and w.get_name() in ('TextBlock_0','TextBlock_1','TextBlock_2','TextBlock_3'):
   w.set_text('LP \uc9c4\uc5f4\uc7a5\n\uc190\ub2d8\uc758 \uc774\uc57c\uae30\uc5d0 \uc5b4\uc6b8\ub9ac\ub294 \uc74c\ubc18\uc744 \uace8\ub77c \uc8fc\uc138\uc694.\nEsc \ud0a4: \ub2eb\uae30' if w.get_name()=='TextBlock_0' else '\uc74c\ubc18 \uc815\ubcf4')
 for w in unreal.ObjectIterator(unreal.Button):
  if w.get_outer()==tree and w.get_name() in ('BTN_LP01','BTN_LP02','BTN_LP03'):assert isinstance(w.get_content(),unreal.TextBlock),w.get_name()
 for key,typ in [('RecordCatalogue',KT),('CandidateSetReady',BT),('CandidateSetInitialized',BT),('ResolvedCandidateIDs',NA),('CardRecord1',RT),('CardRecord2',RT),('CardRecord3',RT)]:assert L.add_member_variable(bp,key,typ)
 specs={'ConfigureRecordCandidates':([('Catalogue',KT),('CandidateIDs',NA)],[('Ready',BT)]),'RecordTagLabel':([('Tag',NT)],[('Label',TT)]),'FormatRecordCard':([('Record',RT)],[('Label',TT)]),'InitializeDefaultCandidates':([],[])}
 for name,(ins,outs) in specs.items():
  g=fn(bp,name);inputs(g,ins);outputs(g,outs)
  if name in ('RecordTagLabel','FormatRecordCard'):g.set_is_pure_function(True);g.set_function_is_private()
 assert L.compile_blueprint(bp);unreal.get_default_object(bp.generated_class()).set_editor_property('RecordCatalogue',unreal.load_asset(CAT))
 g=G.get_graph_editor_by_name(bp,'RecordTagLabel');tag=param(g,'Tag',NT);end=g.find_graph_entry_pin()
 for value,label in [('Quiet','조용함'),('Restless','들뜸'),('Jazz','재즈'),('Electronic','전자음악'),('Traditional','익숙한 형식'),('Sociable','함께 듣는 분위기'),('Adventurous','새로운 질감'),('Folk','포크'),('Classical','클래식'),('Reflective','생각할 여백')]:
  yes,end=branch(g,end,calc(g,'EqualEqual_NameName',A=tag,B=value));ret(g,yes,Label=label)
 ret(g,end,Label='태그 확인 필요')
 g=G.get_graph_editor_by_name(bp,'FormatRecordCard');record=param(g,'Record',RT);split=action(g,'Break ST Record Data',[record]);link(record,pin(split,'ST_RecordData'))
 labels=[]
 for key in ('Genre','Mood','Theme'):
  n=call(g,UC+':RecordTagLabel');link(struct_field(split,key),pin(n,'Tag'));labels.append(strtext(g,pin(n,'Label',True)))
 label=concat(g,strtext(g,struct_field(split,'Title')),' / ',strtext(g,struct_field(split,'Artist')),'\n',labels[0],' · ',labels[1],' · ',labels[2],'\n손님의 이야기와 어울리는 음반을 골라 주세요.')
 ret(g,g.find_graph_entry_pin(),Label=astext(g,label))
 g=G.get_graph_editor_by_name(bp,'ConfigureRecordCandidates');a=inputs(g,specs['ConfigureRecordCandidates'][0]);end=g.find_graph_entry_pin()
 end=assign(g,end,'CandidateSetReady','false');end=assign(g,end,'CandidateSetInitialized','true');end=clear(g,end,get(g,'ResolvedCandidateIDs'))
 assert g.add_local_variable('EmptyRecord',RT)
 for i in range(1,4):
  end=assign(g,end,'CardRecord'+str(i),local_get(g,'EmptyRecord'))
  end=invoke(g,end,'/Script/UMG.Widget.SetIsEnabled',self=get(g,'BTN_LP0'+str(i)),bInIsEnabled='false')[0]
  end=ui_text(g,end,'TextBlock_'+str(i),'음반 정보를 불러올 수 없습니다.')
 end=ui_text(g,end,'TextBlock_0','음반 후보를 확인해 주세요.\nEsc 키로 닫을 수 있습니다.')
 end,no=valid(g,a['Catalogue'],end);ret(g,no,Ready='false')
 end,no=branch(g,end,calc(g,'EqualEqual_IntInt',A=array_len(g,a['CandidateIDs']),B=3));ret(g,no,Ready='false')
 ids=[item(g,a['CandidateIDs'],i) for i in range(3)]
 for i,j in [(0,1),(0,2),(1,2)]:
  end,no=branch(g,end,calc(g,'NotEqual_NameName',A=ids[i],B=ids[j]));ret(g,no,Ready='false')
 records=[]
 for record_id in ids:
  n=call(g,KC+':ResolvePlayableRecord');link(a['Catalogue'],pin(n,'self'));link(record_id,pin(n,'RecordID'));end,no=branch(g,end,pin(n,'Found',True));ret(g,no,Ready='false');records.append(pin(n,'Record',True))
 end=assign(g,end,'RecordCatalogue',a['Catalogue']);end=assign(g,end,'ResolvedCandidateIDs',a['CandidateIDs'])
 for i,record in enumerate(records,1):
  end=assign(g,end,'CardRecord'+str(i),record)
  n=call(g,UC+':FormatRecordCard');link(get(g,'CardRecord'+str(i)),pin(n,'Record'));end=ui_text(g,end,'TextBlock_'+str(i),pin(n,'Label',True))
  end=invoke(g,end,'/Script/UMG.Widget.SetIsEnabled',self=get(g,'BTN_LP0'+str(i)),bInIsEnabled='true')[0]
 end=ui_text(g,end,'TextBlock_0','LP 진열장\n손님의 이야기에 어울리는 음반을 골라 주세요.\nEsc 키: 닫기');end=assign(g,end,'CandidateSetReady','true');ret(g,end,Ready='true')
 g=G.get_graph_editor_by_name(bp,'InitializeDefaultCandidates');done,end=branch(g,g.find_graph_entry_pin(),get(g,'CandidateSetInitialized'));end,_=valid(g,get(g,'RecordCatalogue'),end)
 own(g,end,UC,'ConfigureRecordCandidates',Catalogue=get(g,'RecordCatalogue'),CandidateIDs=field(g,get(g,'RecordCatalogue'),'DefaultCandidateRecordIDs',KC))
 assert L.compile_blueprint(bp)
 eg=evgraph(bp)
 # Replace three original authoring payloads while preserving every existing event.
 for old,record in [('K2Node_MakeStruct_1','CardRecord1'),('K2Node_MakeStruct_6','CardRecord2'),('K2Node_MakeStruct_0','CardRecord3')]:
  node=byname(eg,old);destinations=list(node.list_output_pins()[0].list_connected_pins())
  for p in destinations:p.break_pin_links();link(get(eg,record),p)
  eg.remove_nodes([node])
 for name in ('K2Node_ComponentBoundEvent_0','K2Node_ComponentBoundEvent_1','K2Node_ComponentBoundEvent_2'):
  prev=byname(eg,name).find_then_pin();after=list(prev.list_connected_pins());prev.break_pin_links();yes,no=branch(eg,prev,get(eg,'CandidateSetReady'))
  for p in after:link(yes,p)
 own(eg,byname(eg,'K2Node_Event_1').find_then_pin(),UC,'InitializeDefaultCandidates')
 for name in specs:layout(G.get_graph_editor_by_name(bp,name))
 save(bp)
 # Shelf chooses visit IDs; its existing OnRecordSelected/RecordSelected route stays.
 shelf=unreal.load_asset(SHELF);eg=evgraph(shelf);created=byname(eg,'K2Node_CreateWidget_0');flow=pin(byname(eg,'K2Node_CallFunction_8'),'ReturnValue',True)
 after=list(created.find_then_pin().list_connected_pins());created.find_then_pin().break_pin_links();yes,no=valid(eg,flow,created.find_then_pin())
 idsnode=call(eg,FC+':GetActiveCandidateRecordIDs');link(flow,pin(idsnode,'self'))
 yes,n1=invoke(eg,yes,UC+':ConfigureRecordCandidates',self=pin(created,'ReturnValue',True),Catalogue=field(eg,flow,'RecordCatalogue',FC),CandidateIDs=pin(idsnode,'RecordIDs',True))
 literal=eg.add_get_member_variable_node('RecordCatalogue',UC);link(pin(created,'ReturnValue',True),pin(literal,'self'));cat=pin(literal,'RecordCatalogue',True)
 no,n2=invoke(eg,no,UC+':ConfigureRecordCandidates',self=pin(created,'ReturnValue',True),Catalogue=cat,CandidateIDs=field(eg,cat,'DefaultCandidateRecordIDs',KC))
 for p in after:link(yes,p);link(no,p)
 save(shelf);R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
