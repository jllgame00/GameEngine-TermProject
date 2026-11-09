"""Execute the existing contiguous week with history/memory assertions enabled."""
import os
from pathlib import Path
import unreal
os.environ['MVP_HISTORY_VALIDATION']='1'
source=Path(unreal.Paths.project_dir())/'Scripts/Unreal/validate_day_week.py'
exec(compile(source.read_text(encoding='utf-8-sig'),str(source),'exec'))
