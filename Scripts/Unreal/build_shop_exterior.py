"""Build the shop storefront + street exterior for L_RecordShop_Greybox. Editor only, re-runnable.
- Exterior actors live in the streaming sublevel L_RecordShop_Greybox_Exterior (label prefix EXT_).
- Replaces the solid GB_Wall_Front_L/R with a storefront (two windows + glass double door).
"""
import unreal, json, os, random, traceback
random.seed(7)
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); unreal.log('[EXT] ' + s)

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MAT_DIR = '/Game/RecordShop/Art/Environment/Exterior/Materials'
PERSIST = None  
SUB = '/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox_Exterior'
CUBE = unreal.load_asset('/Engine/BasicShapes/Cube')
CYL = unreal.load_asset('/Engine/BasicShapes/Cylinder')
SPH = unreal.load_asset('/Engine/BasicShapes/Sphere')
CHAR = unreal.load_asset('/Game/RecordShop/Art/Environment/ListeningBar/Materials/M_Shop_Charcoal')
BRASS = unreal.load_asset('/Game/RecordShop/Art/Environment/ListeningBar/Materials/M_Shop_Brass')

# ---------- materials ----------
def master():
    p = MAT_DIR + '/M_Ext_Base'
    if EAL.does_asset_exist(p): return unreal.load_asset(p)
    m = AT.create_asset('M_Ext_Base', MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    bc = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -100)
    bc.set_editor_property('parameter_name', 'BaseColor'); bc.set_editor_property('default_value', unreal.LinearColor(0.5,0.5,0.5,1))
    MEL.connect_material_property(bc, '', unreal.MaterialProperty.MP_BASE_COLOR)
    r = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 100)
    r.set_editor_property('parameter_name', 'Roughness'); r.set_editor_property('default_value', 0.8)
    MEL.connect_material_property(r, '', unreal.MaterialProperty.MP_ROUGHNESS)
    mt = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 200)
    mt.set_editor_property('parameter_name', 'Metallic'); mt.set_editor_property('default_value', 0.0)
    MEL.connect_material_property(mt, '', unreal.MaterialProperty.MP_METALLIC)
    ec = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -700, 300)
    ec.set_editor_property('parameter_name', 'EmissiveColor'); ec.set_editor_property('default_value', unreal.LinearColor(1,0.7,0.4,1))
    es = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -700, 450)
    es.set_editor_property('parameter_name', 'EmissiveStrength'); es.set_editor_property('default_value', 0.0)
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 350)
    MEL.connect_material_expressions(ec, '', mul, 'A'); MEL.connect_material_expressions(es, '', mul, 'B')
    MEL.connect_material_property(mul, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m)
    return m

def glass_mat():
    p = MAT_DIR + '/M_Ext_WindowGlass'
    if EAL.does_asset_exist(p):
        m = unreal.load_asset(p); MEL.delete_all_material_expressions(m)
    else:
        m = AT.create_asset('M_Ext_WindowGlass', MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property('two_sided', True)
    m.set_editor_property('translucency_lighting_mode', unreal.TranslucencyLightingMode.TLM_SURFACE)
    def const(cls, x, y, prop, **kv):
        e = MEL.create_material_expression(m, cls, x, y)
        for k, v in kv.items(): e.set_editor_property(k, v)
        MEL.connect_material_property(e, '', prop); return e
    const(unreal.MaterialExpressionConstant3Vector, -400, -100, unreal.MaterialProperty.MP_BASE_COLOR, constant=unreal.LinearColor(0.85, 0.92, 0.9, 1))
    const(unreal.MaterialExpressionConstant, -400, 0, unreal.MaterialProperty.MP_ROUGHNESS, r=0.05)
    const(unreal.MaterialExpressionConstant, -400, 80, unreal.MaterialProperty.MP_SPECULAR, r=0.25)
    const(unreal.MaterialExpressionConstant, -400, 160, unreal.MaterialProperty.MP_OPACITY, r=0.07)
    MEL.recompile_material(m); EAL.save_loaded_asset(m)
    return m

def mi(name, color, rough=0.8, metal=0.0, emis=None, es=0.0):
    p = MAT_DIR + '/' + name
    inst = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(name, MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    inst.set_editor_property('parent', master())
    MEL.set_material_instance_vector_parameter_value(inst, 'BaseColor', unreal.LinearColor(*color, 1))
    MEL.set_material_instance_scalar_parameter_value(inst, 'Roughness', rough)
    MEL.set_material_instance_scalar_parameter_value(inst, 'Metallic', metal)
    if emis: MEL.set_material_instance_vector_parameter_value(inst, 'EmissiveColor', unreal.LinearColor(*emis, 1))
    MEL.set_material_instance_scalar_parameter_value(inst, 'EmissiveStrength', es)
    MEL.update_material_instance(inst); EAL.save_loaded_asset(inst)
    return inst

# ---------- level ----------
def ensure_sublevel():
    world = unreal.EditorLevelLibrary.get_editor_world()
    names = [l.get_path_name().split('.')[0] for l in unreal.EditorLevelUtils.get_levels(world)]
    log('levels', names)
    if SUB not in names:
        if EAL.does_asset_exist(SUB):
            unreal.EditorLevelUtils.add_level_to_world(world, SUB, unreal.LevelStreamingAlwaysLoaded)
            log('added existing sublevel')
        else:
            unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingAlwaysLoaded, SUB, False)
            log('created sublevel')
    ok = LES.set_current_level_by_name('L_RecordShop_Greybox_Exterior')
    log('current level set', ok)
    return ok

def clear_ext():
    n = 0
    for a in ACT.get_all_level_actors():
        if a.get_actor_label().startswith('EXT_'):
            ACT.destroy_actor(a); n += 1
    log('cleared', n)

def box(name, x0, x1, y0, y1, z0, z1, mat, folder, coll=True, rot=None):
    c = unreal.Vector((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
    a = ACT.spawn_actor_from_class(unreal.StaticMeshActor, c, rot or unreal.Rotator(0,0,0))
    smc = a.static_mesh_component; smc.set_static_mesh(CUBE)
    a.set_actor_scale3d(unreal.Vector(abs(x1-x0)/100, abs(y1-y0)/100, abs(z1-z0)/100))
    smc.set_material(0, mat)
    if not coll:
        a.set_actor_enable_collision(False)
    a.set_actor_label('EXT_' + name); a.set_folder_path('Exterior/' + folder)
    return a

def mesh(name, m, loc, scale, mat, folder, coll=True):
    a = ACT.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator(0,0,0))
    a.static_mesh_component.set_static_mesh(m); a.set_actor_scale3d(unreal.Vector(*scale))
    a.static_mesh_component.set_material(0, mat)
    if not coll: a.set_actor_enable_collision(False)
    a.set_actor_label('EXT_' + name); a.set_folder_path('Exterior/' + folder)
    return a

def text(name, s, loc, yaw, size, color, folder):
    a = ACT.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    t = a.text_render
    t.set_text(s); t.set_world_size(size)
    t.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    t.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    t.set_text_render_color(unreal.Color(*color))
    a.set_actor_label('EXT_' + name); a.set_folder_path('Exterior/' + folder)
    return a

def point(name, loc, intensity, color, radius, folder):
    a = ACT.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator(0,0,0))
    lc = a.point_light_component
    lc.set_intensity(intensity); lc.set_light_color(unreal.LinearColor(*color, 1)); lc.set_attenuation_radius(radius)
    lc.set_editor_property('source_radius', 8.0)
    a.set_actor_label('EXT_' + name); a.set_folder_path('Exterior/' + folder)
    return a

def build():
    M = dict(
        green=mi('MI_Ext_StorefrontGreen', (0.025, 0.07, 0.05), 0.45),
        brick=mi('MI_Ext_Brick', (0.22, 0.075, 0.05), 0.9),
        beige=mi('MI_Ext_Beige', (0.45, 0.38, 0.28), 0.85),
        grey=mi('MI_Ext_Concrete', (0.28, 0.28, 0.27), 0.95),
        asphalt=mi('MI_Ext_Asphalt', (0.04, 0.04, 0.045), 0.7),
        line=mi('MI_Ext_RoadLine', (0.6, 0.5, 0.15), 0.8),
        awning=mi('MI_Ext_Awning', (0.22, 0.03, 0.035), 0.75),
        darkwin=mi('MI_Ext_WindowDark', (0.02, 0.025, 0.035), 0.08, 0.3),
        litwin=mi('MI_Ext_WindowLit', (0.3, 0.22, 0.12), 0.3, 0, (1.0, 0.62, 0.3), 1.2),
        signbox=mi('MI_Ext_SignLight', (0.9, 0.85, 0.7), 0.5, 0, (1.0, 0.85, 0.6), 2.5),
        lamp=mi('MI_Ext_LampGlow', (0.9, 0.8, 0.6), 0.4, 0, (1.0, 0.75, 0.45), 20.0),
        metal=mi('MI_Ext_DarkMetal', (0.05, 0.05, 0.05), 0.4, 1.0),
        leaf=mi('MI_Ext_Foliage', (0.05, 0.16, 0.04), 0.9),
        slate=mi('MI_Ext_Slate', (0.12, 0.13, 0.15), 0.85),
    )
    global GLASS
    GLASS = glass_mat()
    INNER = None
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == 'GB_Wall_Left':
            INNER = a.static_mesh_component.get_material(0)
    INNER = INNER or M['beige']
    log('inner wall material', INNER.get_path_name())
    F = 'Storefront'
    # front wall: y -620..-600, x -450..450, z 0..320; door x -80..80 z 0..250 (lintel exists)
    for side, sx in (('L', -1), ('R', 1)):
        def X(a, b):  # mirror helper
            return (a, b) if sx < 0 else (-b, -a)
        box('Front_%s_Sill' % side, *X(-450, -80), -620, -610, 0, 75, M['green'], F)
        box('Front_%s_Sill_In' % side, *X(-450, -80), -610, -600, 0, 75, INNER, F)
        box('Front_%s_Head' % side, *X(-450, -80), -620, -610, 255, 320, M['green'], F)
        box('Front_%s_Head_In' % side, *X(-450, -80), -610, -600, 255, 320, INNER, F)
        box('Front_%s_PillarOut' % side, *X(-450, -405), -620, -610, 75, 255, M['green'], F)
        box('Front_%s_PillarOut_In' % side, *X(-450, -405), -610, -600, 75, 255, INNER, F)
        box('Front_%s_PillarIn' % side, *X(-125, -80), -620, -610, 75, 255, M['green'], F)
        box('Front_%s_PillarIn_In' % side, *X(-125, -80), -610, -600, 75, 255, INNER, F)
        box('Front_%s_Mullion' % side, *X(-268, -262), -614, -606, 75, 255, CHAR, F)
        box('Front_%s_Transom' % side, *X(-405, -125), -614, -606, 212, 216, CHAR, F)
        box('Front_%s_Glass' % side, *X(-405, -125), -611, -609, 75, 255, GLASS, F)
        box('Front_%s_SillLedge' % side, *X(-410, -120), -630, -598, 72, 78, CHAR, F)
        # awning (slanted)
        aw = box('Awning_%s' % side, *X(-415, -115), -700, -620, 0, 4, M['awning'], 'Awning', coll=False)
        aw.set_actor_location(unreal.Vector(sx * 265, -660, 280), False, False)
        aw.set_actor_rotation(unreal.Rotator(roll=-22, pitch=0, yaw=0), False)
        box('AwningValance_%s' % side, *X(-415, -115), -702, -698, 236, 262, M['awning'], 'Awning', coll=False)
    # glass double door (closed, blocks pawns)
    box('Door_Glass_L', -78, -2, -611, -609, 2, 246, GLASS, 'Door')
    box('Door_Glass_R', 2, 78, -611, -609, 2, 246, GLASS, 'Door')
    for nm, a0, a1 in (('L', -80, -76), ('ML', -4, 0), ('MR', 0, 4), ('R', 76, 80)):
        box('Door_Stile_' + nm, a0, a1, -614, -606, 0, 250, CHAR, 'Door')
    box('Door_Rail_Top', -80, 80, -614, -606, 244, 250, CHAR, 'Door')
    box('Door_Rail_Bottom', -80, 80, -614, -606, 0, 14, CHAR, 'Door')
    for nm, x in (('L', -12), ('R', 12)):
        box('Door_Handle_Out_' + nm, x - 1.5, x + 1.5, -622, -618, 95, 145, BRASS, 'Door', coll=False)
        box('Door_Handle_In_' + nm, x - 1.5, x + 1.5, -602, -598, 95, 145, BRASS, 'Door', coll=False)
    # hanging OPEN sign on the door (faces street)
    box('Door_SignBoard', -30, 30, -616, -614, 170, 196, M['slate'], 'Door', coll=False)
    # sign text (OPEN / CLOSED) lives in the lighting presets so it flips with the time of day
    # upper facade + shop sign
    box('Upper_Facade', -470, 470, -632, -600, 320, 760, M['brick'], 'Upper')
    box('Upper_Cap', -470, 470, -640, -600, 760, 775, M['beige'], 'Upper')
    box('Upper_Block', -460, 460, -600, 620, 342, 760, M['brick'], 'Upper', coll=False)
    for i, x in enumerate((-300, 0, 300)):
        lit = M['litwin'] if i == 1 else M['darkwin']
        box('Upper_Win%d' % i, x - 70, x + 70, -634, -630, 470, 680, lit, 'Upper', coll=False)
        box('Upper_WinSill%d' % i, x - 80, x + 80, -645, -630, 462, 470, M['beige'], 'Upper', coll=False)
    box('Sign_Board', -230, 230, -650, -632, 330, 400, M['green'], 'Sign', coll=False)
    box('Sign_Lightbox', -215, 215, -652, -650, 340, 390, M['signbox'], 'Sign', coll=False)
    text('Sign_Text', 'RECORD SHOP', (0, -653, 368), -90, 34, (30, 40, 34, 255), 'Sign')
    text('Sign_Sub', 'LP  .  CD  .  COFFEE', (0, -653, 347), -90, 11, (60, 50, 40, 255), 'Sign')
    # neighbours
    box('Neighbour_L', -1700, -470, -620, 800, 0, 980, M['beige'], 'Neighbours')
    box('Neighbour_R', 470, 1700, -620, 800, 0, 820, M['slate'], 'Neighbours')
    box('Neighbour_L_Shutter', -1300, -700, -624, -620, 0, 260, M['metal'], 'Neighbours', coll=False)
    box('Neighbour_R_Shop', 700, 1300, -624, -620, 40, 250, M['darkwin'], 'Neighbours', coll=False)
    for k, (x0, x1, top) in enumerate(((-1700, -470, 980), (470, 1700, 820))):
        for fz in range(380, top - 150, 280):
            for wx in range(int(x0) + 120, int(x1) - 100, 220):
                lit = random.random() < 0.3
                box('Neighbour%d_Win_%d_%d' % (k, wx, fz), wx, wx + 110, -624, -620, fz, fz + 160, M['litwin'] if lit else M['darkwin'], 'Neighbours', coll=False)
    # street
    S = 'Street'
    box('Sidewalk_Near', -3500, 3500, -1000, -620, -10, 0, M['grey'], S)
    box('Curb_Near', -3500, 3500, -1015, -1000, -22, 2, M['grey'], S)
    box('Road', -3500, 3500, -1700, -1015, -22, -12, M['asphalt'], S)
    for x in range(-3400, 3500, 400):
        box('RoadLine_%d' % x, x, x + 200, -1362, -1352, -12, -11.5, M['line'], S, coll=False)
    box('Curb_Far', -3500, 3500, -1715, -1700, -22, 2, M['grey'], S)
    box('Sidewalk_Far', -3500, 3500, -2000, -1715, -10, 0, M['grey'], S)
    # opposite block
    x = -3400; b = 0
    while x < 3400:
        w = random.choice((500, 650, 800, 900)); h = random.choice((700, 950, 1200, 1450))
        mat = random.choice((M['brick'], M['beige'], M['slate'], M['grey']))
        box('Opp_Bldg%d' % b, x, x + w - 10, -2500, -2000, 0, h, mat, 'Opposite', coll=False)
        box('Opp_Bldg%d_Shop' % b, x + 60, x + w - 70, -2004, -2000, 30, 250, M['litwin'] if random.random() < 0.5 else M['darkwin'], 'Opposite', coll=False)
        for fz in range(340, h - 120, 260):
            for wx in range(x + 70, x + w - 120, 170):
                lit = random.random() < 0.35
                box('Opp_Bldg%d_W_%d_%d' % (b, wx, fz), wx, wx + 90, -2004, -2000, fz, fz + 150, M['litwin'] if lit else M['darkwin'], 'Opposite', coll=False)
        x += w; b += 1
    # street lamps on near sidewalk
    for i, lx in enumerate((-700, 700)):
        mesh('Lamp%d_Pole' % i, CYL, (lx, -940, 220), (0.12, 0.12, 4.4), M['metal'], 'Lamps')
        box('Lamp%d_Arm' % i, lx - 3, lx + 3, -940, -880, 430, 436, M['metal'], 'Lamps', coll=False)
        mesh('Lamp%d_Head' % i, SPH, (lx, -880, 420), (0.32, 0.32, 0.32), M['lamp'], 'Lamps', coll=False)
        # lamp light itself lives in the day-lighting presets (on for rain/sunset only)
    # bench + planters
    box('Bench_Seat', 200, 380, -740, -700, 42, 48, M['green'], 'Props')
    box('Bench_Back', 200, 380, -705, -700, 48, 90, M['green'], 'Props')
    for x0 in (210, 362):
        box('Bench_Leg_%d' % x0, x0, x0 + 8, -738, -702, 0, 42, M['metal'], 'Props')
    for i, px in enumerate((-430, -110)):
        box('Planter%d' % i, px - 25, px + 25, -690, -640, 0, 50, M['slate'], 'Props')
        mesh('Planter%d_Bush' % i, SPH, (px, -665, 75), (0.6, 0.55, 0.55), M['leaf'], 'Props', coll=False)
    # warm wash on facade from the sign
    point('Sign_Wash', (0, -720, 360), 8.0, (1.0, 0.8, 0.55), 600, 'Sign')

def replace_front_walls():
    gone = []
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() in ('GB_Wall_Front_L', 'GB_Wall_Front_R', 'Shop_Vestibule'):
            gone.append(a.get_actor_label()); ACT.destroy_actor(a)
    log('removed from persistent', gone)

def persistent_name():
    w = unreal.EditorLevelLibrary.get_editor_world()
    return w.get_name()

R = {'ok': False}
try:
    if not EAL.does_directory_exist(MAT_DIR): EAL.make_directory(MAT_DIR)
    LES.set_current_level_by_name(persistent_name())
    replace_front_walls()
    ensure_sublevel()
    clear_ext()
    build()
    LES.save_all_dirty_levels()
    R['ok'] = True
except Exception:
    R['error'] = traceback.format_exc(); log(R['error'])
R['log'] = LOG
d = os.path.join(unreal.Paths.project_saved_dir(), 'EnvBuild'); os.makedirs(d, exist_ok=True)
p = os.path.join(d, 'exterior_result.json')
json.dump(R, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
