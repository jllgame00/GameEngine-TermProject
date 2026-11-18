"""Editor preview: show exactly one lighting preset (Morning / Rain / Sunset / Closing).
Usage (Cmd): py ".../preview_day_lighting.py" Closing
Closing also dims the shop's Shop_AreaLight* in the editor (restored by any other preset). Preview Morning before saving.
"""
import unreal, sys
want = sys.argv[1] if len(sys.argv) > 1 else 'Morning'
world = unreal.EditorLevelLibrary.get_editor_world()
for l in unreal.EditorLevelUtils.get_levels(world):
    n = l.get_path_name().split('.')[0].split('/')[-1]
    if n.startswith('L_RecordShop_Light_'):
        unreal.EditorLevelUtils.set_level_visibility(l, n.endswith('_' + want), False)
area = 200.0 if want == 'Closing' else 950.0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label().startswith('Shop_AreaLight'):
        a.light_component.set_intensity(area)
unreal.log('[DAYLIGHT] preview ' + want)
