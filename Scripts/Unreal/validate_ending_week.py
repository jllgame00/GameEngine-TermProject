"""Actual cold Title -> New Game -> 17 cycles -> Ending/Credits -> Title/New Game."""
import os
from pathlib import Path
import unreal
os.environ['MVP_COLD_TITLE']='1';os.environ['MVP_HISTORY_VALIDATION']='1'
source=Path(unreal.Paths.project_dir())/'Scripts/Unreal/validate_day_week.py'
exec(compile(source.read_text(encoding='utf8'),str(source),'exec'))
