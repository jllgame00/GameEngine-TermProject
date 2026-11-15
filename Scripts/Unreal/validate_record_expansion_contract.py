"""Read-only expansion data/audio/candidate contract; RED before content import."""
import unreal,os,json,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_validation_support import assert_reference_integrity,struct_value,text_literal
from record_expansion_support import DATA,RECORD_IDS,DEFAULT_IDS,candidates,narrative_fields
R={'complete':False,'pass':False,'records':[],'visits':[]}
try:
 cat=unreal.load_asset('/Game/RecordShop/Data/Records/DA_RecordCatalogue')
 for identity,source in DATA['records'].items():
  ok,record=cat.call_method('ResolvePlayableRecord',args=(identity,));assert ok,'Missing playable '+identity
  assert str(struct_value(record,'RecordID'))==identity
  for key in ('Title','Artist','Mood','Genre','Theme','Energy'):assert str(struct_value(record,key))==source[key],(identity,key)
  sound=struct_value(record,'Audio');cover=struct_value(record,'Cover');assert sound and cover
  assert sound.get_path_name()=='/Game/RecordShop/Audio/Music/'+source['Audio']+'.'+source['Audio']
  assert cover.get_path_name()=='/Game/RecordShop/Art/Records/Covers/'+source['Cover']+'.'+source['Cover']
  assert 25<=sound.get_editor_property('duration')<=35 and sound.get_editor_property('num_channels')==2
  assert sound.get_editor_property('sample_rate')==48000 and not sound.get_editor_property('looping')
  assert abs(sound.get_editor_property('volume')-.8)<.0001 and sound.get_editor_property('compression_quality')==80
  assert cover.blueprint_get_size_x()==cover.blueprint_get_size_y()==1024
  R['records'].append(dict(id=identity,audio=sound.get_path_name(),cover=cover.get_path_name(),duration=sound.get_editor_property('duration'),recommended_rpm=source['RecommendedRPM']))
 assert list(map(str,unreal.DataTableFunctionLibrary.get_data_table_row_names(cat.get_editor_property('Table'))))==RECORD_IDS
 assert list(map(str,cat.get_editor_property('DefaultCandidateRecordIDs')))==DEFAULT_IDS
 assert not cat.call_method('ResolveRecord',args=('MISSING',))[0]
 ui=unreal.load_asset('/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect');tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree)if t.get_outer()==ui)
 images=[w for w in unreal.ObjectIterator(unreal.Image)if w.get_outer()==tree and w.get_name().startswith('RecordCover')];assert len(images)==3
 R['original_records']=assert_reference_integrity()
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 for day in week.get_editor_property('Days'):
  for visit in day.get_editor_property('Visits'):
   identity=str(visit.get_editor_property('CustomerID'));number=visit.get_editor_property('VisitNumber');definition=visit.get_editor_property('Narrative');ids=candidates(identity,number)
   assert len(ids)==len(set(ids))==3 and all(cat.call_method('ResolvePlayableRecord',args=(i,))[0]for i in ids)
   if identity.startswith('TEMP_D7_'):assert definition is None and ids==DEFAULT_IDS
   else:assert list(map(str,definition.get_editor_property('CandidateRecordIDs')))==ids
   R['visits'].append(dict(id=identity,visit=number,day=visit.get_editor_property('Day'),candidates=ids))
 assert len(R['visits'])==16
 # Narrative body/memory/profile/reaction content must remain unchanged.
 baseline=json.loads((ROOT/'Scripts/Unreal/record_expansion_reference.json').read_text(encoding='utf8'))
 for path,fields in baseline['narrative_fields'].items():
  assert narrative_fields(unreal.load_asset(path))==fields,path
 from audio_handoff_validation_support import assert_asset_hash
 for path,sha in baseline['unchanged_sha256'].items():assert_asset_hash(path,sha)
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
