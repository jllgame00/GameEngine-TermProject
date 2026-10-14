"""Read-only final production-map dependency closure and Blueprint compile gate."""
import unreal,json,traceback,os
from pathlib import Path
OUT=Path(os.environ['MVP_RESULT'])
R={'complete':False,'root':'/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox','packages':{},'missing':[],'redirectors':[],'compile_failures':[]}
def save():OUT.write_text(json.dumps(R,indent=2),encoding='utf-8')
save()
try:
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
 options=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
 # The configured GameMode is a cook root outside the map's hard references.
 # Include it so the player Blueprint, mesh, skeleton and materials are compiled/loaded too.
 import configparser
 config=configparser.ConfigParser(strict=False,interpolation=None);config.read(str(Path(unreal.Paths.project_dir())/'Config/DefaultEngine.ini'),encoding='utf-8-sig')
 game_mode=config['/Script/EngineSettings.GameMapsSettings']['GlobalDefaultGameMode'].split('.')[0]
 R['roots']=[R['root'],game_mode]
 pending=list(R['roots']);seen=set()
 while pending:
  package=pending.pop()
  if package in seen or package.startswith('/Script/'):continue
  seen.add(package)
  assets=registry.get_assets_by_package_name(package)
  deps=[str(x) for x in registry.get_dependencies(package,options)]
  item={'dependencies':deps,'assets':[]};R['packages'][package]=item
  if not assets:R['missing'].append(package)
  for data in assets:
   kind=str(data.asset_class_path.asset_name)
   item['assets'].append({'name':str(data.asset_name),'class':kind})
   if kind=='ObjectRedirector':R['redirectors'].append(package)
   if package.startswith('/Game/'):
    asset=data.get_asset()
    if asset is None:R['missing'].append(package+': load failed')
    if kind in ('Blueprint','WidgetBlueprint','AnimBlueprint'):
     compiled=unreal.BlueprintEditorLibrary.compile_blueprint(asset)
     item['assets'][-1]['compile']=compiled
     if not compiled:R['compile_failures'].append(package)
  pending.extend(deps)
 R['customer_profile_default']=unreal.get_default_object(unreal.load_class(None,'/Game/DialogueManager.DialogueManager_C')).get_editor_property('CurrentCustomer').export_text()
 # Validate authored production data, without generating fixtures or saving assets.
 rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/CustomerDialogue')))
 assert [row['Name'] for row in rows]==['C01_Quiet_%02d'%i for i in range(1,6)]
 assert all(row['DialogueID']==row['Name'] and row['Mood']=='Quiet' and row['MusicPreference']=='Jazz' and row['Speaker'] and row['Text'] for row in rows)
 customer=unreal.get_default_object(unreal.load_class(None,'/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'))
 profile_value=customer.get_editor_property('CustomerProfile')
 profile=profile_value.export_text()
 import re
 fields={key:str(profile_value.get_editor_property(re.search(key+r'_[A-Za-z0-9_]+(?==)',profile).group(0))) for key in ('CustomerID','Name','VisitReason','Personality','Mood','MusicPreference')}
 assert fields['CustomerID']=='C01' and fields['Personality']=='Traditional' and fields['MusicPreference']=='Jazz' and fields['Mood']=='Quiet'
 assert fields['Name']=='중년 손님'
 assert [row['IsEndNode'] for row in rows]==[False,False,False,False,True]
 bp=unreal.load_asset('/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect')
 records=[]
 for node in unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph').list_all_nodes():
  if node.get_class().get_name()!='K2Node_MakeStruct':continue
  record={str(pin.get_pin_name()).split('_')[0]:pin.get_pin_value() for pin in node.list_input_pins()}
  if 'RecordID' not in record:continue
  assert all(record.get(key) not in (None,'','None') for key in ('RecordID','Title','Artist','Genre','Mood','Energy','Theme'))
  record['expected_score']=sum((record['Mood']==fields['Mood'],record['Genre']==fields['MusicPreference'],record['Theme']==fields['Personality']))
  records.append(record)
 assert {record['RecordID']:record['expected_score'] for record in records}=={'RS001':3,'RS002':2,'RS003':0}
 R['authored_content']={'profile':fields,'dialogue':rows,'catalogue':records,'rule':'Existing CalculateLPScore: Mood / Genre / Theme map to Mood / MusicPreference / Personality; one point each. Energy is descriptive.'}
 # Fonts must be cooked project dependencies, rather than the editor-only Korean fallback.
 font_path='/Game/RecordShop/UI/Fonts/NanumGothic_Font'
 assert font_path in R['packages'] and '/Game/RecordShop/UI/Fonts/NanumGothic' in R['packages']
 ui_text=[]
 for suffix in ('Dialogue/WBP_Dialogue','RecordSelection/WBP_RecordSelect','Turntable/WBP_Turntable','Result/WBP_Result_IntegrationFallback'):
  widget_bp=unreal.load_asset('/Game/RecordShop/UI/'+suffix)
  tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree) if t.get_outer()==widget_bp)
  for widget in unreal.ObjectIterator(unreal.Widget):
   if widget.get_outer()!=tree or not isinstance(widget,(unreal.TextBlock,unreal.RichTextBlock)):continue
   font=(widget.get_editor_property('font') if isinstance(widget,unreal.TextBlock) else widget.get_editor_property('default_text_style_override').get_editor_property('font'))
   assert font.get_editor_property('font_object').get_path_name().startswith(font_path),widget.get_name()
   text=str(widget.get_text())
   if not text:continue
   latin=re.findall(r'[A-Za-z]+',text)
   assert all(word in ('LP','Esc','RPM') for word in latin),(widget.get_name(),text)
   ui_text.append({'widget':suffix,'name':widget.get_name(),'text':text})
 assert not any('Mina' in str(row) for row in rows)
 R['korean_ui']={'texts':ui_text,'allowed_latin':['LP (record format)','Esc (keyboard key)','RPM (rotation speed)'],'cooked_font':font_path}
 # Physical presentation must survive a fresh asset load and cook, not just PIE overrides.
 movement=customer.get_component_by_class(unreal.CharacterMovementComponent)
 assert movement.max_walk_speed == 180
 blend=unreal.load_asset('/Game/RecordShop/Animation/Customers/Customer01/A_C01_BS_Idle_Walk_Run')
 walks=[sample for sample in blend.get_editor_property('sample_data') if '_Walk_' in sample.get_editor_property('animation').get_name()]
 R['walk_samples']=[sample.export_text() for sample in walks]
 assert len(walks)==9 and all(abs(sample.get_editor_property('sample_value').y-180)<0.01 and abs(sample.get_editor_property('rate_scale')-0.6)<0.001 for sample in walks), R['walk_samples']
 player=unreal.get_default_object(unreal.load_class(None,'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C'))
 player_component=player.get_component_by_class(unreal.SkeletalMeshComponent)
 player_mesh=player_component.get_editor_property('skeletal_mesh_asset')
 assert player_mesh.get_name()=='SKM_ShopOwner'
 assert player_mesh.get_editor_property('skeleton')==unreal.load_asset('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
 assert player_component.get_editor_property('anim_class').get_name()=='ABP_Unarmed_C'
 materials=player_mesh.get_editor_property('materials')
 assert len(materials)==7 and all(slot.get_editor_property('material_interface') and slot.get_editor_property('material_interface').get_editor_property('used_with_skeletal_mesh') for slot in materials)
 turntable=unreal.load_asset('/Game/RecordShop/Interaction/Actors/BP_Turntable')
 for variable in ('SilentPlaybackRemaining','TonearmReturnAlpha'):
  schema=unreal.BlueprintEditorLibrary.pin_type_to_json_schema(unreal.BlueprintEditorLibrary.get_member_variable_type(turntable,variable),turntable.generated_class())
  assert 'number' in schema, (variable,schema)
 R['physical_presentation']={'customer_walk_speed':180,'walk_rate':0.6,'walk_samples':len(walks),'player_mesh':player_mesh.get_path_name(),'player_skeleton':player_mesh.get_editor_property('skeleton').get_path_name(),'player_materials':[slot.get_editor_property('material_interface').get_path_name() for slot in materials]}
 R['complete']=True
 R['pass']=not (R['missing'] or R['redirectors'] or R['compile_failures'])
 R['engine_audio_candidates']=[str(a.package_name) for a in registry.get_assets_by_path('/Engine/EditorSounds',True) if str(a.asset_class_path.asset_name) in ('SoundWave','SoundCue')]
 R['project_audio']=[str(a.package_name) for a in registry.get_assets_by_path('/Game',True) if str(a.asset_class_path.asset_name) in ('SoundWave','SoundCue','MetaSoundSource')]
 R['struct_fields']={}
 for path in ['/Game/CustomerData','/Game/DialogueData','/Game/RecordShop/Data/Structs/ST_RecordData']:
  struct=unreal.load_asset(path)
  R['struct_fields'][path]=struct.export_text() if hasattr(struct,'export_text') else str(struct)
except Exception:R['fatal']=traceback.format_exc()
save()
