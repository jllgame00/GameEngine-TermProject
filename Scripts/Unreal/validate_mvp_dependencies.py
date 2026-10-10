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
 pending=[R['root']];seen=set()
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
