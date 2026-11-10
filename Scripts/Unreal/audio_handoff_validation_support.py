"""Narrow intentional package migration; previous gate baselines remain immutable."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def assert_asset_hash(path,expected):
 reference=json.loads((ROOT/'Scripts/Unreal/audio_handoff_reference.json').read_text(encoding='utf8'))
 changed=reference['packages']
 assert set(changed)=={'Content/RecordShop/Core/Flow/BP_GameFlowManager.uasset','Content/RecordShop/Interaction/Actors/BP_Turntable.uasset'}
 if path in changed:
  assert expected==changed[path]['before'],path+' unknown baseline'
  expected=changed[path]['after']
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
