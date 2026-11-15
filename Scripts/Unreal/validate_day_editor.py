"""Compile/dependency/data gates in one fresh Editor session; never save assets."""
import json,os,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir());OUT=Path(os.environ['MVP_RESULT'])
R={'complete':False,'pass':False,'checks':{}}
try:
 for name in ('validate_prologue_contract','validate_day_contract','validate_day_schedule','validate_mvp_dependencies'):
  target=OUT.with_name(OUT.stem+'-'+name+'.json');os.environ['MVP_RESULT']=str(target)
  source=ROOT/'Scripts/Unreal'/(name+'.py');exec(compile(source.read_text(encoding='utf-8-sig'),str(source),'exec'),{'__name__':'__main__'})
  value=json.loads(target.read_text(encoding='utf8'));R['checks'][name]={'pass':value.get('pass',False),'result':str(target),'fatal':value.get('fatal')}
 R['pass']=all(c['pass'] for c in R['checks'].values())
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True
OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
