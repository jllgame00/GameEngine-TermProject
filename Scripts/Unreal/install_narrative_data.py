"""Migrate existing record payloads and create minimal visit/tutorial data. Editor only."""
import unreal,os,json,sys,hashlib,traceback,re
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
unreal.InternationalizationLibrary.set_current_language('en',False)
REC='/Game/RecordShop/Data/Records';NAR='/Game/RecordShop/Data/Narrative'
TABLE=REC+'/DT_RecordCatalogue';CAT=REC+'/BP_RecordCatalogue';CC=CAT+'.BP_RecordCatalogue_C'
DEF=NAR+'/BP_VisitNarrativeDefinition';NC=DEF+'.BP_VisitNarrativeDefinition_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
NT=L.get_basic_type_by_name('name');IT=L.get_basic_type_by_name('int');BT=L.get_basic_type_by_name('bool');DT=L.get_object_reference_type(unreal.DataTable);NA=L.get_array_type(NT)
def report():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def save(a):
 if isinstance(a,unreal.Blueprint):assert L.compile_blueprint(a),a.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(a,False)
 R['saved'].append(a.get_path_name());report()
def definition(path,fields):
 a=unreal.load_asset(path)
 if not a:
  f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.PrimaryDataAsset);a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.Blueprint,f)
 names=list(map(str,L.list_member_variable_names(a,False)))
 for key,typ in fields:
  if key not in names:assert L.add_member_variable(a,key,typ)
  L.set_blueprint_variable_instance_editable(a,key,True)
 assert L.compile_blueprint(a);return a

def instance(path,kind,values):
 a=unreal.load_asset(path)
 if not a:
  f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',kind);a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],kind,f)
 for k,v in values.items():a.set_editor_property(k,v)
 save(a);return a

def data_table(path,struct,rows):
 a=unreal.load_asset(path)
 if not a:
  f=unreal.DataTableFactory();f.set_editor_property('struct',struct);a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.DataTable,f)
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(a,json.dumps(rows,ensure_ascii=False),struct)
 save(a);return a
try:
 # Extract the original authoring site before UI migration. No values are invented.
 ui=unreal.load_asset('/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect');rows=[]
 for node in evgraph(ui).list_all_nodes():
  if node.get_class().get_name()=='K2Node_MakeStruct':
   row={str(p.get_pin_name()).split('_')[0]:p.get_pin_value() for p in node.list_input_pins()}
   if 'RecordID' in row:
    row['Name']=row['RecordID'];row['Cover']=row.get('Cover') or 'None';rows.append(row)
 assert len(rows)==3,'Run migration before removing the old UI payloads'
 rows.sort(key=lambda r:r['RecordID']);assert [r['RecordID'] for r in rows]==['RS001','RS002','RS003']
 struct=unreal.load_asset('/Game/RecordShop/Data/Structs/ST_RecordData');RT=L.get_struct_type(struct)
 table=data_table(TABLE,struct,rows)
 cat=definition(CAT,[('Table',DT),('DefaultCandidateRecordIDs',NA)])
 g=fn(cat,'ResolveRecord');a=inputs(g,[('RecordID',NT)]);outputs(g,[('Found',BT),('Record',RT)]);g.set_is_pure_function(True)
 end,no=valid(g,get(g,'Table'),g.find_graph_entry_pin());ret(g,no,Found='false')
 kind=call(g,'/Script/Engine.DataTableFunctionLibrary.GetDataTableRowStruct');link(get(g,'Table'),pin(kind,'Table'))
 end,no=branch(g,end,calc(g,'EqualEqual_ObjectObject',A=pin(kind,'ReturnValue',True),B=struct.get_path_name()));ret(g,no,Found='false')
 end,n=invoke(g,end,'/Script/Engine.DataTableFunctionLibrary.DoesDataTableRowExist',Table=get(g,'Table'),RowName=a['RecordID'])
 end,no=branch(g,end,pin(n,'ReturnValue',True));ret(g,no,Found='false')
 row=table_row(g,end,get(g,'Table'),a['RecordID'],TABLE)
 ret(g,row.find_then_pin(),Found='true',Record=pin(row,'ReturnValue',True));ret(g,pin(row,'RowNotFound',True),Found='false')
 assert L.compile_blueprint(cat)
 g=fn(cat,'ResolvePlayableRecord');a=inputs(g,[('RecordID',NT)]);outputs(g,[('Found',BT),('Record',RT)]);g.set_is_pure_function(True)
 resolve=call(g,CC+':ResolveRecord');link(a['RecordID'],pin(resolve,'RecordID'))
 end,no=branch(g,g.find_graph_entry_pin(),pin(resolve,'Found',True));ret(g,no,Found='false')
 data=pin(resolve,'Record',True);split=action(g,'Break ST Record Data',[data]);link(data,pin(split,'ST_RecordData'))
 end,no=branch(g,end,calc(g,'EqualEqual_NameName',A=struct_field(split,'RecordID'),B=a['RecordID']));ret(g,no,Found='false')
 end,no=valid(g,struct_field(split,'Audio'),end);ret(g,no,Found='false');ret(g,end,Found='true',Record=data)
 save(cat)
 instance(REC+'/DA_RecordCatalogue',cat.generated_class(),dict(Table=table,DefaultCandidateRecordIDs=['RS001','RS002','RS003']))
 fields=[('SequenceID',NT),('SourceTable',DT),('OrderedRows',NA),('MemoryVisitNumbers',L.get_array_type(IT)),('BestIntroRows',NA),('GoodIntroRows',NA),('PoorIntroRows',NA),('NoMemoryIntroRows',NA),('TargetMoodOverride',NT),('TargetGenreOverride',NT),('TargetThemeOverride',NT),('CandidateRecordIDs',NA),('ReviewStatus',NT),('ContentVersion',IT)]
 definition_asset=definition(DEF,fields);save(definition_asset)
 tutorial_lines=[
  '가게를 처음 맡으셨군요. 잠깐 음악을 함께 골라 볼까요?',
  '오늘은 조용한 음악을 듣고 싶어요.',
  '작은 재즈 합주처럼 익숙한 소리가 좋아요.',
  '새로운 해석보다는 전통적인 분위기로 부탁드릴게요.',
  '이야기를 다 들으셨다면 진열장에서 음반을 골라 주세요.']
 tutorial_rows=[dict(Name='TUTORIAL_%02d'%i,DialogueID='TUTORIAL_%02d'%i,Speaker='연습 손님',Text=text,Mood='Quiet',MusicPreference='Jazz',IsEndNode=i==5) for i,text in enumerate(tutorial_lines,1)]
 tutorial=data_table(NAR+'/DT_TutorialDialogue',unreal.load_asset('/Game/DialogueData'),tutorial_rows)
 instance(NAR+'/DA_TutorialNarrative',definition_asset.generated_class(),dict(SequenceID='TUTORIAL_Training',SourceTable=tutorial,OrderedRows=[r['Name'] for r in tutorial_rows],ReviewStatus='READY',ContentVersion=1))
 a1=instance(NAR+'/DA_A1_Narrative',definition_asset.generated_class(),dict(SequenceID='A_Visit1',SourceTable=unreal.load_asset('/Game/CustomerDialogue'),OrderedRows=['C01_Quiet_%02d'%i for i in range(1,6)],CandidateRecordIDs=['RS001','RS002','RS003'],ReviewStatus='READY',ContentVersion=1))
 visit=unreal.load_asset('/Game/RecordShop/Data/Schedule/BP_CustomerVisitDefinition')
 if 'Narrative' not in list(map(str,L.list_member_variable_names(visit,False))):assert L.add_member_variable(visit,'Narrative',L.get_object_reference_type(definition_asset.generated_class()))
 L.set_blueprint_variable_instance_editable(visit,'Narrative',True);save(visit)
 v=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_Visit_A_1');v.set_editor_property('Narrative',a1);save(v)
 tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree) if t.get_outer()==ui)
 R['widget_texts']=[{'name':w.get_name(),'text':str(w.get_text())} for w in unreal.ObjectIterator(unreal.TextBlock) if w.get_outer()==tree]
 R['catalogue_rows']=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table));R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;report()
