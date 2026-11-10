# Selected LP Store BGM plan

Goal: complete audio ownership and transitions on current branch. No staging/commit/push/new branch/story work.

Architecture: reuse GFM StoreBGMRef/StoreBGMRequested and Turntable.CurrentRecord. Resolve canonical RecordID through Shared Catalogue at accepted Result. Same-track restart with .5s fade-in/.18 volume, since TT destroys listening component. Selection initiates .6s BGM fade; preplay finishes any remaining stop before new audio starts. Day begin clears BGM and completed TT selection.

Ruling: user explicitly authorizes production-safe restart and execution. Proceed inline; preserve old baseline JSON and declare only two Blueprint hash migrations.

Tasks:
- [x] READ-ONLY branch/HEAD/status, 778-file snapshot, graph/catalogue/component audit PASS052836.
- [x] RED real-audio canonical RS003 handoff:053315 fixed-RS001 mismatch. First property-edit fixture error053224 retained; unsaved Blueprint fixture function corrected access.
- [x] Minimal Editor installer053502 PASS, GFM/TT only. 74 other function graphs frozen; no new manager.
- [x] Runtime six records/replacement/duplicate/natural loop/empty-selection/lifetime:053622 and fresh053853 PASS. Contract053837 PASS.
- [x] Natural week same-LP/Dialogue/Tutorial/day/History16 assertions: corrected062749 complete17cycles PASS, resets8/dialogue9/history16.
- [x] Current-state26-group evidence consolidated: 25 passing processes plus corrected full week, all package hashes unchanged. Native3 first-pass, compile/dependency/map/cook PASS; host11/Python10/diff checks PASS. Initial failed aggregate explicitly retained.
- [x] Final18-sectionreport and exact15incremental files;734 start files unchanged and0new production assets. Branch/HEAD/index unchanged.

Review focus: rapid play during fading old BGM; natural/late callbacks; invalid audio no fallback; duplicate Result/history; Tutorial/day state.

Audit: fixed RS001 GFM.StoreBGMSound default drives separate CreateSound2D. BeginDay and CloseResult start it. TT BeginTonearmReturn fades .45 then CompletePlayback stops/clears after1.2s return motion. EndCurrentDay already fades then .75s day timer. Dialogue voice/ducking not added.

Independent read-only feature review: no Critical/Important finding. Invalid selection runtime case is specifically empty completed selection; shared resolver separately tests unknown ID/missing Audio. Full frozen regression started054007: expansion contract and3 fresh ordered16visit/96score/18click sessions PASS with matching digest. Human hearing/hardware/package remain pending.

Natural week055751 failed after6cycles in test harness only: an auto-destroyed old BGM Python wrapper becomes null, so calling is_playing after later gestures raises Internal Error. Fix observes actual live components by retained path (same no-overlap assertion), not a dead wrapper. Production assets are unchanged. Preserve failed report and rerun entire17cycleweek. The existing core runner continues its remaining independent native/audio/startup/cook groups; final evidence will explicitly select successful same-state groups and replacement full-week report, never mark failed aggregate as passed.

Second week061330 reached11cycles then test incorrectly required identical BGM component across Dialogue, although natural EOF loop recreates it. No production edits. Added unsaved OnAudioFinished observer: same ID/sound and one live component required; replacement allowed only after observed natural completion. Continue uses same distinction and avoids dead wrappers. Both failed reports retained. One obsolete attempt062426 was cancelled after PID/path/exact UTC start verification because a host patch assertion had prevented harness update; user Editor untouched.

Final: audio-handoff-final-evidence.json complete/pass true,26groups,17sameLPcycles,History16,8resets,9Dialogue observations,74protectedgraphs,3equalcandidate digests. Two production packages match installed after hashes; all other assets unchanged. Independent final report review PASS:26groups,18sections,15files,all evidence links and hashes verified; no remaining Critical/Important findings. Stop at Audio ownership; no Day7/ending content.
