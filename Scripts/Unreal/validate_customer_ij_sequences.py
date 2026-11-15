"""Reuse the single-visit runtime harness with approved I/J expectations."""
import os
from pathlib import Path
import unreal
os.environ['MVP_SINGLE_VISIT_SET']='IJ'
source=Path(unreal.Paths.project_dir())/'Scripts/Unreal/validate_customer_efgh_sequences.py'
exec(compile(source.read_text(encoding='utf8'),str(source),'exec'))
