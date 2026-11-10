"""Shared read-only golden value checks for narrative foundation tests."""
import hashlib,json,re
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')).hexdigest()
def text_literal(value):
 if value.startswith(('NSLOCTEXT(','INVTEXT(','LOCTEXT(')):return json.loads('['+value[value.index('(')+1:-1]+']')[-1]
 return value

def struct_value(value,key):
 name=re.search(r'\b'+re.escape(key)+r'_[A-Za-z0-9_]+(?==)',value.export_text()).group(0)
 return value.get_editor_property(name)
def canonical_record(value):
 result={}
 for key in ('RecordID','Title','Artist','Genre','Mood','Energy','Theme','Cover','Audio'):
  field=struct_value(value,key)
  result[key]=field.get_path_name() if key in ('Cover','Audio') and field else (None if field is None else str(field))
 return result

def assert_reference_integrity():
 baseline=json.loads((ROOT/'Scripts/Unreal/narrative_reference_baseline.json').read_text(encoding='utf8'))
 for path,sha in baseline['asset_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/CustomerDialogue')))
 assert digest(rows)==baseline['a1_rows_sha256']
 catalogue=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue');assert catalogue
 exported=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(catalogue.get_editor_property('Table')))
 for row in exported:
  if row['RecordID']not in baseline['record_ftext_identity_sha256']:continue
  assert digest({key:row[key] for key in ('Title','Artist')})==baseline['record_ftext_identity_sha256'][row['RecordID']],row['RecordID']
 found={}
 for record_id,sha in baseline['record_semantic_sha256'].items():
  ok,record=catalogue.call_method('ResolveRecord',args=(record_id,));assert ok,record_id
  semantics=canonical_record(record);assert digest(semantics)==sha,(record_id,semantics,digest(semantics),sha)
  found[record_id]=semantics
 return {'unchanged_packages':len(baseline['asset_sha256']),'unchanged_a1_rows':5,'canonical_records':found}


def returned_flag(value):
 """Blueprint array inputs are reflected as in/out arrays by Editor Python."""
 if isinstance(value,bool):return value
 flags=[x for x in value if isinstance(x,bool)] if isinstance(value,tuple) else []
 assert len(flags)==1,(type(value),value)
 return flags[0]
