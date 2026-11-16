"""Natural Day7 cycles after an explicitly isolated, unsaved day-entry fixture."""
import os
from pathlib import Path
import unreal
os.environ['MVP_DAY7_ONLY']='1'
source=Path(unreal.Paths.project_dir())/'Scripts/Unreal/validate_day_week.py'
exec(compile(source.read_text(encoding='utf8'),str(source),'exec'))
