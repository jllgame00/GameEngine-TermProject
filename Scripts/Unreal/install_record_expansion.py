"""Import only new original media; append catalogue and author ordered visit IDs."""
import unreal,os,json,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from record_expansion_support import DATA,narrative_fields
from narrative_validation_support import assert_reference_integrity
R={'complete':False,'pass':False,'saved':[]}

def save(asset):
 assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);R['saved'].append(asset.get_path_name())

def import_new(source,folder,name):
 asset=unreal.load_asset(folder+'/'+name)
 if asset is None:
  task=unreal.AssetImportTask();task.set_editor_property('filename',str(source));task.set_editor_property('destination_path',folder);task.set_editor_property('destination_name',name);task.set_editor_property('automated',True);task.set_editor_property('save',False)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);asset=unreal.load_asset(folder+'/'+name)
 assert asset,name
 return asset

try:
 R['original_before']=assert_reference_integrity()
 baseline_path=ROOT/'Scripts/Unreal/record_expansion_reference.json';baseline=json.loads(baseline_path.read_text(encoding='utf8'))
 for path,sha in baseline['unchanged_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
 table=unreal.load_asset('/Game/RecordShop/Data/Records/DT_RecordCatalogue');rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
 assert len(rows)in (3,6)and {r['RecordID']for r in rows}=={'RS00'+str(i)for i in range(1,len(rows)+1)},'Unexpected records: refusing to replace catalogue rows'
 original=[r for r in rows if r['RecordID']in ('RS001','RS002','RS003')];assert len(original)==3
 rows=original.copy();prototype=unreal.load_asset('/Game/RecordShop/Audio/Music/RS002_Good')
 for identity,data in DATA['records'].items():
  sound=import_new(ROOT/'ArtSource/Audio/Music'/(data['Audio']+'.wav'),'/Game/RecordShop/Audio/Music',data['Audio'])
  for key in ('volume','compression_quality','loading_behavior','sample_rate_quality','sound_group','looping'):sound.set_editor_property(key,prototype.get_editor_property(key))
  save(sound)
  cover=import_new(ROOT/'ArtSource/Records/Covers'/(data['Cover']+'.png'),'/Game/RecordShop/Art/Records/Covers',data['Cover']);cover.set_editor_property('srgb',True);save(cover)
  row=dict(Name=identity,RecordID=identity)
  for key in ('Title','Artist'):row[key]='NSLOCTEXT("RecordExpansion", "'+identity+'_'+key+'", '+json.dumps(data[key],ensure_ascii=False)+')'
  for key in ('Mood','Genre','Theme','Energy'):row[key]=data[key]
  row.update(Audio="/Script/Engine.SoundWave'"+sound.get_path_name()+"'",Cover="/Script/Engine.Texture2D'"+cover.get_path_name()+"'");rows.append(row)
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(rows,ensure_ascii=False),unreal.load_asset('/Game/RecordShop/Data/Structs/ST_RecordData'));save(table)
 for key,ids in DATA['candidates'].items():
  identity,number=key.split('_');asset=unreal.load_asset('/Game/RecordShop/Data/Narrative/DA_'+identity+number+'_Narrative');assert asset,key
  assert narrative_fields(asset)==baseline['narrative_fields'][asset.get_path_name()]
  if list(map(str,asset.get_editor_property('CandidateRecordIDs')))!=ids:asset.set_editor_property('CandidateRecordIDs',ids);save(asset)
 baseline['updated_asset_sha256']={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest()for path in baseline['allowed_changed']}
 baseline_path.write_text(json.dumps(baseline,indent=2,ensure_ascii=False),encoding='utf8')
 R['original_after']=assert_reference_integrity();R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
