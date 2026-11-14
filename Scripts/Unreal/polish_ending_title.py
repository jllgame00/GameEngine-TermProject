"""Editor-only correction of inherited new RichText/Button defaults on Title Quit."""
import unreal,os,json
from pathlib import Path
bp=unreal.load_asset('/Game/RecordShop/UI/Title/WBP_Title')
tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree)if t.get_outer()==bp)
ws={w.get_name():w for w in unreal.ObjectIterator(unreal.Widget)if w.get_outer()==tree}
ws['QuitLabel'].set_default_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(.92,.91,.87,1)))
ws['Quit'].set_background_color(ws['Continue'].get_editor_property('background_color'))
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
Path(os.environ['MVP_RESULT']).write_text(json.dumps(dict(complete=True,**{'pass':True},saved=bp.get_path_name())),encoding='utf8')
