"""Day lighting presets for L_RecordShop_Greybox. Editor only, re-runnable.
Creates three Blueprint-streamed sublevels (Morning / Rain / Sunset), each holding its own sun, sky light,
height fog, colour-grade volume and street-lamp lights. Removes the TEST_ sun/sky light from the persistent level.
Morning is initially loaded so the game looks right even before any day hook exists.
Day -> preset mapping (for the GameFlowManager hook): 1 Morning, 2 Morning, 3 Rain, 4 Sunset, 5 Rain, 6 Morning, 7 Sunset
Closing: ending only (after the last customer). Night outside, one warm light on the turntable, door sign CLOSED.
  The hook should also dim Shop_AreaLight00/01/10/11 (persistent) to ~CLOSING_AREA_LIGHT.
"""
import unreal, json, os, traceback
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); unreal.log('[DAYLIGHT] ' + s)
EAL = unreal.EditorAssetLibrary
ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
DIR = '/Game/RecordShop/Maps/Greybox/'
MOV = unreal.ComponentMobility.MOVABLE

PRESETS = {
  'Morning': dict(sun_rot=(-45, -60), sun_lux=15.0, sun_col=(1.0, 0.93, 0.82), sky=2.0, fog=0.006, fog_col=(0.55, 0.62, 0.72),
                  lamps=0.0, temp=6200, sat=1.0, initially=True),
  'Rain':    dict(sun_rot=(-60, 20), sun_lux=1.5, sun_col=(0.75, 0.82, 0.95), sky=1.6, fog=0.03, fog_col=(0.30, 0.35, 0.42),
                  lamps=18.0, temp=7600, sat=0.8, initially=False),
  'Sunset':  dict(sun_rot=(-14, -155), sun_lux=10.0, sun_col=(1.0, 0.55, 0.28), sky=1.2, fog=0.012, fog_col=(0.9, 0.55, 0.35),
                  lamps=30.0, temp=5000, sat=1.1, initially=False),
  'Closing': dict(sun_rot=(-40, -60), sun_lux=0.25, sun_col=(0.55, 0.65, 1.0), sky=0.5, fog=0.02, fog_col=(0.08, 0.10, 0.18),
                  lamps=150.0, temp=6000, sat=0.95, initially=False, closed=True, exposure_bias=-0.5, exposure_min=1.5, vignette=0.55),
}
CLOSING_AREA_LIGHT = 200.0   # Shop_AreaLight* default 950
SIGN_OUT = (255, 214, 150, 255)

def label(a, name, folder):
    a.set_actor_label('LGT_' + name); a.set_folder_path('Lighting/DayPresets/' + folder)

def safe(obj, prop, val):
    try: obj.set_editor_property(prop, val); return True
    except Exception as e: log('skip', prop, e); return False

def build_preset(name, P):
    world = unreal.EditorLevelLibrary.get_editor_world()
    path = DIR + 'L_RecordShop_Light_' + name
    loaded = [l.get_path_name().split('.')[0] for l in unreal.EditorLevelUtils.get_levels(world)]
    if path not in loaded:
        if EAL.does_asset_exist(path):
            unreal.EditorLevelUtils.add_level_to_world(world, path, unreal.LevelStreamingDynamic)
        else:
            unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingDynamic, path, False)
    lvname = 'L_RecordShop_Light_' + name
    assert LES.set_current_level_by_name(lvname), lvname
    # clear previous preset actors in this sublevel
    for a in ACT.get_all_level_actors():
        if a.get_actor_label().startswith('LGT_') and lvname in a.get_path_name():
            ACT.destroy_actor(a)
    pitch, yaw = P['sun_rot']
    sun = ACT.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 600), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw))
    sun.root_component.set_mobility(MOV)
    lc = sun.light_component
    lc.set_intensity(P['sun_lux']); lc.set_light_color(unreal.LinearColor(*P['sun_col'], 1))
    safe(lc, 'atmosphere_sun_light', True)
    label(sun, name + '_Sun', name)
    sky = ACT.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 400), unreal.Rotator(0, 0, 0))
    sky.root_component.set_mobility(MOV)
    sc = sky.light_component
    safe(sc, 'real_time_capture', True)
    sc.set_intensity(P['sky'])
    label(sky, name + '_SkyLight', name)
    fog = ACT.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, -50), unreal.Rotator(0, 0, 0))
    fc = fog.component
    safe(fc, 'fog_density', P['fog'])
    if not safe(fc, 'fog_inscattering_luminance', unreal.LinearColor(*P['fog_col'], 1)):
        safe(fc, 'fog_inscattering_color', unreal.LinearColor(*P['fog_col'], 1))
    label(fog, name + '_Fog', name)
    ppv = ACT.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    ppv.set_editor_property('unbound', True); ppv.set_editor_property('priority', 1.0)
    st = ppv.settings
    st.set_editor_property('override_white_temp', True); st.set_editor_property('white_temp', float(P['temp']))
    st.set_editor_property('override_color_saturation', True)
    st.set_editor_property('color_saturation', unreal.Vector4(P['sat'], P['sat'], P['sat'], 1.0))
    if 'exposure_bias' in P:
        safe(st, 'override_auto_exposure_bias', True); safe(st, 'auto_exposure_bias', P['exposure_bias'])
    if 'exposure_min' in P:   # stop auto-exposure from brightening the night back to day
        safe(st, 'override_auto_exposure_min_brightness', True); safe(st, 'auto_exposure_min_brightness', P['exposure_min'])
    if 'vignette' in P:
        safe(st, 'override_vignette_intensity', True); safe(st, 'vignette_intensity', P['vignette'])
    ppv.set_editor_property('settings', st)
    label(ppv, name + '_Grade', name)
    if P['lamps'] > 0:
        for i, lx in enumerate((-700, 700)):
            pl = ACT.spawn_actor_from_class(unreal.PointLight, unreal.Vector(lx, -880, 400), unreal.Rotator(0, 0, 0))
            pl.root_component.set_mobility(MOV)
            c = pl.point_light_component
            c.set_intensity(P['lamps']); c.set_light_color(unreal.LinearColor(1.0, 0.72, 0.42, 1)); c.set_attenuation_radius(1400)
            label(pl, '%s_StreetLamp%d' % (name, i), name)
    # door sign (board itself is EXT_Door_SignBoard in the exterior level)
    closed = P.get('closed', False)
    for nm, txt, y, yaw, size in (('SignOut', 'CLOSED' if closed else 'OPEN', -617.2, -90, 14 if closed else 16),
                                  ('SignIn', 'SEE YOU<br>TOMORROW' if closed else 'THANK YOU', -612.8, 90, 7 if closed else 9)):
        t = ACT.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(0, y, 183), unreal.Rotator(0, 0, yaw))
        tc = t.text_render
        tc.set_text(txt); tc.set_world_size(size)
        tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        tc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        tc.set_text_render_color(unreal.Color(*SIGN_OUT))
        label(t, '%s_Door%s' % (name, nm), name)
    if closed:
        # one warm work light left on over the turntable / bar
        sp = ACT.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(80, 395, 290), unreal.Rotator(roll=0, pitch=-90, yaw=0))
        sp.root_component.set_mobility(MOV)
        c = sp.spot_light_component
        c.set_intensity(900.0); c.set_light_color(unreal.LinearColor(1.0, 0.72, 0.45, 1)); c.set_attenuation_radius(700)
        c.set_inner_cone_angle(14.0); c.set_outer_cone_angle(34.0)
        safe(c, 'source_radius', 6.0)
        label(sp, name + '_TurntableLight', name)
        # faint sign glow for the facade
        gl = ACT.spawn_actor_from_class(unreal.PointLight, unreal.Vector(0, -720, 360), unreal.Rotator(0, 0, 0))
        gl.root_component.set_mobility(MOV)
        g = gl.point_light_component; g.set_intensity(4.0); g.set_light_color(unreal.LinearColor(1.0, 0.8, 0.55, 1)); g.set_attenuation_radius(500)
        label(gl, name + '_SignGlow', name)
    # streaming flags
    sl = unreal.GameplayStatics.get_streaming_level(world, lvname)
    if sl:
        safe(sl, 'initially_loaded', P['initially']); safe(sl, 'initially_visible', P['initially'])
    log('built', name)

def persistent_name():
    w = unreal.EditorLevelLibrary.get_editor_world()
    return w.get_name()

R = {'ok': False}
try:
    LES.set_current_level_by_name(persistent_name())
    removed = []
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() in ('TEST_DirectionalLight', 'TEST_SkyLight'):
            removed.append(a.get_actor_label()); ACT.destroy_actor(a)
        elif a.get_actor_label() == 'TEST_SkyAtmosphere':
            a.set_actor_label('Shop_SkyAtmosphere'); a.set_folder_path('Lighting')
    log('persistent cleanup', removed)
    world = unreal.EditorLevelLibrary.get_editor_world()
    for l in unreal.EditorLevelUtils.get_levels(world):
        if 'L_RecordShop_Light_' in l.get_path_name():
            unreal.EditorLevelUtils.set_level_visibility(l, True, False)
    for n, P in PRESETS.items():
        build_preset(n, P)
    LES.set_current_level_by_name(persistent_name())
    LES.save_all_dirty_levels()
    R['ok'] = True
except Exception:
    R['error'] = traceback.format_exc(); log(R['error'])
R['log'] = LOG
d = os.path.join(unreal.Paths.project_saved_dir(), 'EnvBuild'); os.makedirs(d, exist_ok=True)
json.dump(R, open(os.path.join(d, 'daylight_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
