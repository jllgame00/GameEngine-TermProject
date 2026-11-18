"""Create editable Blueprint PrimaryDataAsset visit/day/week definitions and instances.
Run in Editor; no raw binary serialization, and no runtime Python dependency.
"""
import json,os,traceback,sys
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
L=unreal.BlueprintEditorLibrary
BASE='/Game/RecordShop/Data/Schedule'
CUSTOMER='/Game/RecordShop/Characters/Customers/Common/BP_Customer.BP_Customer_C'
PLACEHOLDER='/Game/RecordShop/Characters/Customers/Customer01/Blueprints/BP_Customer01.BP_Customer01_C'
R={'complete':False,'pass':False,'saved':[]};OUT=Path(os.environ['MVP_RESULT'])
def report():OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
def save(asset):
 if isinstance(asset,unreal.Blueprint):assert L.compile_blueprint(asset),asset.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False)
 R['saved'].append(asset.get_path_name());report()
def definition(name,fields):
 asset=unreal.load_asset(BASE+'/'+name)
 if asset is None:
  factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.PrimaryDataAsset)
  asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,BASE,unreal.Blueprint,factory)
 assert asset
 names=list(map(str,L.list_member_variable_names(asset,False)))
 for field,typ in fields:
  if field not in names:assert L.add_member_variable(asset,field,typ)
  L.set_blueprint_variable_instance_editable(asset,field,True)
 save(asset);return asset.generated_class()
def instance(name,kind,properties):
 asset=unreal.load_asset(BASE+'/'+name)
 if asset is None:
  factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',kind)
  asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,BASE,kind,factory)
 assert asset,name
 for key,value in properties.items():asset.set_editor_property(key,value)
 save(asset);return asset
try:
 n=lambda kind:L.get_basic_type_by_name(kind)
 # CustomerData row handle is reserved for later content; CustomerClass is the
 # current authoritative profile/content reference for all temporary entries.
 visit=definition('BP_CustomerVisitDefinition',[('CustomerID',n('name')),('VisitNumber',n('int')),('Day',n('int')),('OrderInDay',n('int')),('CustomerClass',L.get_class_reference_type(unreal.load_class(None,CUSTOMER))),('CustomerData',L.get_struct_type(unreal.DataTableRowHandle.static_struct())),('StoryEventID',n('name')),('IsPlaceholderContent',n('bool'))])
 day=definition('BP_DayScheduleDefinition',[('Day',n('int')),('Visits',L.get_array_type(L.get_object_reference_type(visit)))])
 week=definition('BP_WeekScheduleDefinition',[('Days',L.get_array_type(L.get_object_reference_type(day))),('FinalStoryEventID',n('name'))])
 schedule=[ [('A',1),('E',1)], [('B',1),('C',1)], [('A',2),('F',1),('D',1)], [('B',2),('C',2)], [('A',3),('G',1)], [('B',3),('D',2),('H',1)], [('TEMP_D7_01',1),('TEMP_D7_02',1)] ]
 days=[]
 for number,entries in enumerate(schedule,1):
  visits=[]
  for order,(identity,count) in enumerate(entries,1):
   visits.append(instance('DA_Visit_'+identity+'_'+str(count),visit,dict(CustomerID=identity,VisitNumber=count,Day=number,OrderInDay=order,CustomerClass=unreal.load_class(None,PLACEHOLDER),StoryEventID='None',IsPlaceholderContent=True)))
  days.append(instance('DA_Day%02d'%number,day,dict(Day=number,Visits=visits)))
 instance('DA_TemporaryWeek',week,dict(Days=days,FinalStoryEventID='FinalStoryEvent'))
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;report()
