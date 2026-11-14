"""Read-only exact Ending migration and preservation assertions; no runtime authority."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACKAGES={'Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset','Content/RecordShop/Interaction/Components/BPC_Interaction.uasset'}
def reference():
 ref=json.loads((ROOT/'Scripts/Unreal/ending_reference.json').read_text(encoding='utf8'));assert set(ref['packages'])==PACKAGES;return ref
def migrated_hash(path,expected):
 ref=reference()
 if path in ref['packages']:
  item=ref['packages'][path];assert expected==item['before'],path+' unknown Ending baseline';return item['after']
 return expected
def graph_hash(path,name,expected):
 ref=reference();item=ref['changed_graphs'].get(path,{}).get(name)
 if item:assert expected==item['before'],(path,name,'unknown graph baseline');return item['after']
 return expected
def assert_preservation():
 ref=reference()
 for path,expected in ref['unchanged_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
 for path,item in ref['packages'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==item['after'],path
 return {'unchanged_content':len(ref['unchanged_sha256']),'modified_packages':sorted(PACKAGES)}
