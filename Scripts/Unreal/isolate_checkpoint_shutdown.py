"""Run checkpoint assertions in separate rendered Unreal processes.

Host Python (not Unreal Python): python Scripts/Unreal/isolate_checkpoint_shutdown.py all
Selected scopes retain their original assertions; selection supplies records for
turntable checks, and each non-natural PIE scope verifies natural Ready/Next.
editor-startup and preflight are editor-only controls; they never start PIE.
Artifacts stay in Saved/CheckpointCrashRepair. Never run render processes in parallel.
The optional staged shutdown is an experiment, not a claimed crash repair.
"""
import argparse, hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CheckpointCrashRepair'
ENGINE = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
def source(name, group):
    s = (ROOT/'Scripts/Unreal/validate_integration_round.py').read_text(encoding='utf-8')
    s = s.replace("OUT = ROOT / 'Saved/OvernightIntegration/Round1/worker-runtime.json'", f"OUT = ROOT / 'Saved/CheckpointCrashRepair/{name}.json'")
    s = s.replace("'natural': [], 'isolated': {},", f"'selected_group': {group!r}, 'natural': [], 'isolated': {{}},")
    if group in ('editor-startup', 'preflight'):
        if group == 'preflight':
            s = s.split('assert level.load_level(')[0]
            s += "\nRESULT['scope'] = 'Editor preflight only; no PIE'\n"
        else:
            s = ("import unreal, json\nfrom pathlib import Path\n"
                 f"OUT = Path({str(OUT / (name + '.json'))!r})\n"
                 "RESULT = {'complete': False, 'selected_group': 'editor-startup', 'compiles': {}, 'isolated': {}}\n"
                 "def save(): OUT.write_text(json.dumps(RESULT, indent=2), encoding='utf-8')\n"
                 "save()\n"
                 "assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()\n"
                 "RESULT['startup_world'] = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()\n"
                 "RESULT['scope'] = 'Editor startup only; no PIE or project assertions'\n")
        s += ("RESULT['complete'] = True\n"
              "RESULT['teardown'] = ['quit_editor_without_pie']\n"
              "save()\nunreal.SystemLibrary.quit_editor()\n")
        compile(s, name, 'exec')
        path = OUT / f'{name}.py'
        path.write_text(s, encoding='utf-8')
        return path
    s = s.replace('worker-dialogue.png', f'{name}-dialogue.png')
    s = s.replace('def check(name, action):\n    try:', "def check(name, action):\n    RESULT['last_assertion'] = name\n    save()\n    try:")
    s = s.replace('    OUT.parent.mkdir', "    RESULT['teardown'] = globals().get('teardown', [])\n    OUT.parent.mkdir")
    s = s.replace('level.editor_request_end_play()', "teardown.append('request_end_play'); save(); level.editor_request_end_play(); teardown.append('end_play_request_returned'); save()")
    s = s.replace('unreal.unregister_slate_post_tick_callback(handle)', "teardown.append('unregister_callback'); save(); unreal.unregister_slate_post_tick_callback(handle)")
    s = s.replace('unreal.SystemLibrary.quit_editor()', "teardown.append('quit_editor'); save(); unreal.SystemLibrary.quit_editor(); teardown.append('quit_editor_returned'); save()")
    s = s.replace('def tick(delta):', 'teardown = []\n\ndef tick(delta):')
    s = s.replace("            RESULT['isolated']['exit_after'] =", "            RESULT['last_assertion'] = 'exit_after'\n            RESULT['isolated']['exit_after'] =")
    s = s.replace('        yield from physical_input_checks', "        RESULT['last_assertion'] = 'physical_input_sphere_trace_interface'; save()\n        yield from physical_input_checks")
    s = s.replace('        yield from keyboard_closes()', "        RESULT['last_assertion'] = 'slate_escape_close_reopen_and_unrelated_key'; save()\n        yield from keyboard_closes()")
    if group != 'all':
        dialogue = (ROOT/'Scripts/Unreal/dialogue_handoff_checks.py').read_text(encoding='utf-8')
        if group == 'natural': dialogue = dialogue.split('    def natural_next():')[0]
        elif group != 'dialogue': dialogue = dialogue.split('    # Unsaved diagnostic actor:')[0]
        s = s.replace('from dialogue_handoff_checks import dialogue_checks', dialogue)
        if group in ('natural', 'close', 'dialogue', 'exit'):
            s = s.replace('    pc = unreal.GameplayStatics.get_player_controller(world, 0)\n    pawn =', '    return\n    pc = unreal.GameplayStatics.get_player_controller(world, 0)\n    pawn =', 1)
        else:
            if group != 'turntable':
                for line in ("    check('no_record_rejects_playback', no_record_playback)", "    check('turntable_reentry_cross_modal', turntable_reentry)", "    check('turntable_invalid_valid_order_and_repeat', turntable_order)", "    rpm_ui_checks(world, pawn, cls(TURNTABLE), cls(TURNTABLE_UI), tt.get_editor_property('CurrentRecord'), check)"):
                    s = s.replace(line, '')
            if group not in ('selection', 'turntable'): s = s.replace("    check('selection_reentry_cross_modal_and_all_records', selection)", '')
            if group != 'physical': s = s.replace("        RESULT['last_assertion'] = 'physical_input_sphere_trace_interface'; save()\n        yield from physical_input_checks(world, flow, pawn,\n                                        [(shelves[0], cls(SELECT_UI)), (tt, cls(TURNTABLE_UI))], RESULT, save)", '')
            if group != 'keyboard': s = s.replace("        RESULT['last_assertion'] = 'slate_escape_close_reopen_and_unrelated_key'; save()\n        yield from keyboard_closes()", '        yield from ()')
        if group != 'exit':
            a = s.index("        if state['tested'] and state['keyboard'] is None and not state['exit_requested']:")
            b = s.index("            RESULT['assertions_pass']", a)
            s = s[:a] + "        if elapsed >= 25 and state['tested'] and state['keyboard'] is None and not state['ended']:\n            state['ended'] = True\n" + s[b:]
    compile(s, name, 'exec')
    p = OUT/f'{name}.py'; p.write_text(s, encoding='utf-8'); return p

def run(name, script, null=False, project=None, extra=(), editor=True):
    log = OUT/f'{name}.log'
    args = [str(ENGINE), str(project or ROOT/'RecordShop.uproject'), '-EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities', '-unattended', '-nosound', '-nop4', '-nosplash', f'-ddc=(Local=(Type=FileSystem,Path={ROOT / "DerivedDataCache"}))', '-DDC-ForceMemoryCache', f'-UserDir={OUT / "User"}', f'-abslog={log}']
    if null: args += ['-nullrhi']
    if editor: args += ['-RenderOffscreen', '-NoLoadStartupPackages', f'-ExecutePythonScript={script}']
    else: args += ['-run=pythonscript', f'-script={script}']
    args += list(extra)
    if (OUT/f'{name}-command.json').exists():
        raise FileExistsError(f'Refusing to overwrite evidence for {name}')
    start = time.time()
    (OUT/f'{name}-command.json').write_text(json.dumps(args, indent=2))
    with (OUT/f'{name}-stdout.txt').open('w', encoding='utf-8') as stream:
        p = subprocess.Popen(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        timed_out = False
        try: code = p.wait(timeout=900)
        except subprocess.TimeoutExpired:
            timed_out = True
            p.kill(); code = p.wait()
    result_file = OUT/f'{name}.json'
    result = json.loads(result_file.read_text(encoding='utf-8')) if result_file.exists() else {}
    txt = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
    summary = {'name':name, 'exit_code':code, 'exit_hex':hex(code & 0xffffffff), 'seconds':round(time.time()-start,2), 'complete':result.get('complete',False), 'fatal':result.get('fatal'), 'assertions_pass':result.get('assertions_pass'), 'last_assertion':result.get('last_assertion'), 'teardown':result.get('teardown',[]), 'conditions':txt.count('LogAutomationTest: Error: Condition failed'), 'diagnostics':[line for line in txt.splitlines() if re.search(r'0xC0000005|EXCEPTION_ACCESS_VIOLATION|Fatal error|Callstack:|ensure condition failed|Accessed None',line,re.I)]}
    summary['signed_exit_code'] = code if code < 0x80000000 else code - 0x100000000
    summary['native_access_violation'] = (code & 0xffffffff) == 0xc0000005
    summary['engine_shutdown_log_reached'] = 'LogExit: Exiting.' in txt
    group = result.get('selected_group')
    expected = {'all':16, 'natural':1, 'close':2, 'dialogue':6, 'selection':3,
                'turntable':8, 'physical':3, 'keyboard':3, 'exit':4,
                'editor-startup':0, 'preflight':0}.get(group)
    expected_compiles = 0 if group == 'editor-startup' else 12
    assertions = [item['pass'] for item in result.get('isolated',{}).values() if 'pass' in item]
    summary.update({'group':group, 'timed_out':timed_out,
                    'assertion_count':len(assertions), 'expected_assertions':expected,
                    'compile_count':len(result.get('compiles',{})),
                    'script_sha256':hashlib.sha256(Path(script).read_bytes()).hexdigest()})
    summary['pass'] = (code == 0 and not timed_out and summary['complete'] and not summary['fatal']
                       and not summary['diagnostics'] and expected is not None
                       and len(assertions) == expected and all(assertions)
                       and len(result.get('compiles',{})) == expected_compiles and all(result['compiles'].values()))
    (OUT/f'{name}-process.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary), flush=True)
    return summary

def staged(name,group):
    p=source(name,group);s=p.read_text(encoding='utf-8')
    old="""            teardown.append('request_end_play'); save(); level.editor_request_end_play(); teardown.append('end_play_request_returned'); save()
            teardown.append('unregister_callback'); save(); unreal.unregister_slate_post_tick_callback(handle)
            teardown.append('quit_editor'); save(); unreal.SystemLibrary.quit_editor(); teardown.append('quit_editor_returned'); save()"""
    assert old in s
    s=s.replace(old,"""            teardown.append('request_end_play'); save()
            level.editor_request_end_play()
            state['shutdown_requested'] = time.monotonic()
            teardown.append('end_play_request_returned'); save()""")
    s=s.replace("def tick(delta):\n    try:\n", """def tick(delta):
    try:
        if state.get('shutdown_requested'):
            if level.is_in_play_in_editor() or editor.get_game_world():
                assert time.monotonic() - state['shutdown_requested'] < 30, 'PIE did not stop'
                return
            if 'pie_stopped' not in state:
                state['pie_stopped'] = time.monotonic()
                teardown.append('pie_stopped_observed'); save()
                return
            if time.monotonic() - state['pie_stopped'] < 2:
                return
            teardown.append('unregister_callback'); save()
            unreal.unregister_slate_post_tick_callback(handle)
            teardown.append('quit_editor_after_pie'); save()
            unreal.SystemLibrary.quit_editor()
            return
""")
    compile(s,name,'exec');p.write_text(s,encoding='utf-8');return p

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('groups', nargs='+', choices=['all','natural','close','dialogue','selection','turntable','physical','keyboard','exit','editor-startup','preflight'])
    parser.add_argument('--nullrhi', action='store_true')
    parser.add_argument('--staged-shutdown', action='store_true')
    opts = parser.parse_args()
    if opts.staged_shutdown and any(group in ('editor-startup', 'preflight') for group in opts.groups):
        parser.error('--staged-shutdown requires PIE scopes')
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    results = []
    for index, group in enumerate(opts.groups):
        name = f'{stamp}-{index}-{group}'
        script = (staged if opts.staged_shutdown else source)(name, group)
        results.append(run(name, script, null=opts.nullrhi))
    raise SystemExit(0 if all(result['pass'] for result in results) else 1)
