"""Keep original buttons/cached records; add noninteractive cover images beside captions."""
import unreal,os,json,sys,traceback,hashlib
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from narrative_graph_helpers import *
UI='/Game/RecordShop/UI/RecordSelection/WBP_RecordSelect';UC=UI+'.WBP_RecordSelect_C'
R={'complete':False,'pass':False};OUT=Path(os.environ['MVP_RESULT'])
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 bp=unreal.load_asset(UI);tree=next(t for t in unreal.ObjectIterator(unreal.WidgetTree)if t.get_outer()==bp)
 widgets={w.get_name():w for w in unreal.ObjectIterator(unreal.Widget)if w.get_outer()==tree}
 installed='SetCandidateCover'in [g.get_name()for g in L.list_graphs(bp)]
 for i in ([]if installed else range(1,4)):
  button=widgets['BTN_LP0'+str(i)];caption=button.get_content();assert isinstance(caption,unreal.TextBlock)
  box=unreal.EditorUtilityLibrary.add_source_widget(bp,unreal.HorizontalBox,'RecordCard'+str(i),'PresentationContent');image=unreal.EditorUtilityLibrary.add_source_widget(bp,unreal.Image,'RecordCover'+str(i),box.get_name());image.set_visibility(unreal.SlateVisibility.COLLAPSED)
  slot=image.get_editor_property('slot');slot.set_padding(unreal.Margin(0,0,16,0));slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
  slot=box.add_child_to_horizontal_box(caption);slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER);slot.set_size(unreal.SlateChildSize(1,unreal.SlateSizeRule.FILL));button.add_child(box)
 # MakeBrush requires a texture; clear it after preserving the serialized dimensions.
 prototype=unreal.load_asset('/Game/RecordShop/Art/Records/Covers/T_RS004_Cover');assert prototype,'Import expansion media before cover UI'
 for image in [w for w in unreal.ObjectIterator(unreal.Image)if w.get_outer()==tree and w.get_name().startswith('RecordCover')]:
  image.set_brush(unreal.WidgetLibrary.make_brush_from_texture(prototype,96,96));image.set_brush_from_texture(None,False)
 assert L.compile_blueprint(bp)
 g=G.get_graph_editor_by_name(bp,'ConfigureRecordCandidates')
 # Existing caption writes still target the same TextBlock, now child1 of a row.
 adapters=0
 for old in list(g.list_all_nodes()):
  if old.get_class().get_name()!='K2Node_DynamicCast' or not ''.join(str(old.get_node_title()).split()).endswith('CastToTextBlock'):continue
  adapters+=1
  existing=list(pin(old,'Object').list_connected_pins())
  if existing and 'GetChildAt'in str(existing[0].get_owning_node().get_node_title()).replace(' ',''):continue
  obj=pin(old,'Object');up=list(obj.list_connected_pins());assert len(up)==1
  previous=list(old.find_execute_pin().list_connected_pins());obj.break_pin_links();old.find_execute_pin().break_pin_links()
  cast=action(g,'Cast To Horizontal Box',[up[0]],unreal.HorizontalBox);link(up[0],pin(cast,'Object'))
  for p in previous:link(p,cast.find_execute_pin())
  link(cast.find_then_pin(),old.find_execute_pin());target=next(p for p in cast.list_output_pins()if str(p.get_pin_name()).replace(' ','').startswith('As'))
  child=call(g,'/Script/UMG.PanelWidget.GetChildAt');link(target,pin(child,'self'));val(pin(child,'Index'),1);link(pin(child,'ReturnValue',True),obj)
 assert adapters==6,('Expected six caption paths',adapters)
 R['caption_adapters']=adapters
 if not installed:
  g=fn(bp,'SetCandidateCover');a=inputs(g,[('Button',L.get_object_reference_type(unreal.Button)),('Texture',L.get_object_reference_type(unreal.Texture2D))])
  content=call(g,'/Script/UMG.ContentWidget.GetContent');link(a['Button'],pin(content,'self'));obj=pin(content,'ReturnValue',True)
  cast=action(g,'Cast To Horizontal Box',[obj],unreal.HorizontalBox);link(obj,pin(cast,'Object'));link(g.find_graph_entry_pin(),cast.find_execute_pin());target=next(p for p in cast.list_output_pins()if str(p.get_pin_name()).replace(' ','').startswith('As'))
  child=call(g,'/Script/UMG.PanelWidget.GetChildAt');link(target,pin(child,'self'));val(pin(child,'Index'),0)
  cast_image=action(g,'Cast To Image',[pin(child,'ReturnValue',True)],unreal.Image);link(pin(child,'ReturnValue',True),pin(cast_image,'Object'));link(cast.find_then_pin(),cast_image.find_execute_pin());target=next(p for p in cast_image.list_output_pins()if str(p.get_pin_name()).replace(' ','').startswith('As'))
  end,_=invoke(g,cast_image.find_then_pin(),'/Script/UMG.Image.SetBrushFromTexture',self=target,Texture=a['Texture'],bMatchSize='false')
  yes,no=valid(g,a['Texture'],end)
  invoke(g,yes,'/Script/UMG.Widget.SetVisibility',self=target,InVisibility='HitTestInvisible');invoke(g,no,'/Script/UMG.Widget.SetVisibility',self=target,InVisibility='Collapsed')
 assert L.compile_blueprint(bp)
 g=G.get_graph_editor_by_name(bp,'ConfigureRecordCandidates')
 for node in list(g.list_all_nodes()):
  title=str(node.get_node_title()).replace(' ','')
  if title not in ('SetCardRecord1','SetCardRecord2','SetCardRecord3'):continue
  if any('SetCandidateCover'in str(p.get_owning_node().get_node_title()).replace(' ','')for p in node.find_then_pin().list_connected_pins()):continue
  i=title[-1];record=get(g,'CardRecord'+i);split=action(g,'Break ST Record Data',[record]);link(record,pin(split,'ST_RecordData'))
  n=call(g,UC+':SetCandidateCover');link(get(g,'BTN_LP0'+i),pin(n,'Button'));link(struct_field(split,'Cover'),pin(n,'Texture'));splice(node.find_then_pin(),n)
 assert L.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 p=ROOT/'Scripts/Unreal/record_expansion_reference.json';baseline=json.loads(p.read_text(encoding='utf8'));path='Content/RecordShop/UI/RecordSelection/WBP_RecordSelect.uasset';baseline['updated_asset_sha256'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest();p.write_text(json.dumps(baseline,indent=2,ensure_ascii=False),encoding='utf8');R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;OUT.write_text(json.dumps(R,indent=2),encoding='utf8')
