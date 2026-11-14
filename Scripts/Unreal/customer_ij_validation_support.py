"""I/J test expectations and exact three-package migration; never runtime authority."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'Scripts/Unreal/customer_ij_dialogue.json').read_text(encoding='utf8'))
PROFILES={k:tuple(v['profile'])for k,v in DATA.items()}
def migrated_hash(path,expected):
 ref=json.loads((ROOT/'Scripts/Unreal/customer_ij_reference.json').read_text(encoding='utf8'))
 assert set(ref['packages'])=={'Content/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition.uasset','Content/RecordShop/UI/Result/WBP_Result_IntegrationFallback.uasset','Content/RecordShop/Data/Schedule/DA_Day07.uasset'}
 if path in ref['packages']:
  entry=ref['packages'][path];assert expected==entry['before'],path+' unknown I/J baseline';return entry['after']
 return expected
def expected_rows(identity):return list(DATA[identity]['rows'])
def expected_feedback(identity,score):
 from customer_b_validation_support import expected_result
 neutral=json.loads((ROOT/'Scripts/Unreal/preference_result_feedback.json').read_text(encoding='utf-8-sig'))
 grade=expected_result(score);source=DATA[identity]['reactions']
 return neutral[grade].split('\n')[0]+'\n'+source['Result'+grade.title()+'Text']+'\n\n'+source['ExitText']
