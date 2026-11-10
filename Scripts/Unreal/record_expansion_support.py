"""Authoring expectations and narrow hash migrations, never runtime record authority."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'Scripts/Unreal/record_expansion.json').read_text(encoding='utf8'))
RECORD_IDS=['RS00'+str(i)for i in range(1,7)]
DEFAULT_IDS=['RS001','RS002','RS003']
PROFILES={'A':('Quiet','Jazz','Traditional'),'B1':('Restless','Electronic','Adventurous'),'B':('Quiet','Electronic','Adventurous'),'C':('Quiet','Folk','Sociable'),'D':('Quiet','Classical','Reflective'),'E':('Quiet','Jazz','Sociable')}
SCORES={'A':(3,2,0,1,1,1),'B1':(0,0,3,2,0,0),'B':(1,1,2,3,1,1),'C':(1,2,0,1,3,1),'D':(1,1,0,1,1,3),'E':(2,3,0,1,2,1)}

def candidates(identity,visit=1):return DATA['candidates'].get(identity+'_'+str(visit),DEFAULT_IDS)

def narrative_fields(asset):
 result={}
 for key in ('SequenceID','ReviewStatus','ContentVersion','TargetMoodOverride','TargetGenreOverride','TargetThemeOverride','RequireAllMemories','EarlierMemoryVisitNumber'):
  result[key]=str(asset.get_editor_property(key))
 source=asset.get_editor_property('SourceTable');result['SourceTable']=source.get_path_name()if source else None
 for key in ('OrderedRows','MemoryVisitNumbers','BestIntroRows','GoodIntroRows','PoorIntroRows','NoMemoryIntroRows','AllPositiveOutroRows','OtherMemoryOutroRows','EarlierBestRows','EarlierGoodRows','EarlierPoorRows'):
  result[key]=list(map(str,asset.get_editor_property(key)))
 return result

def assert_protected_assets(baseline):
 migration=json.loads((ROOT/'Scripts/Unreal/record_expansion_reference.json').read_text(encoding='utf8'))
 for path,sha in baseline['asset_sha256'].items():
  expected=migration['updated_asset_sha256'].get(path,sha)
  from audio_handoff_validation_support import assert_asset_hash
  assert_asset_hash(path,expected)
