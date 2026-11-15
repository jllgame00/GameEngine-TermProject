# RS004 / RS005 / RS006 Production Plan

Goal: playable original records, six-row shared catalogue, deterministic authored three-card visits and complete narrative/core regression. User gate2026-11-10 is the binding spec.

Start: feature/customer-narrative-content / 7e94f0cfdafc949bdddd209326da593f1062ff7e, clean. No staging/commit/push/new branch/raw package editing. Stop before Day7/ending/events/mesh/world expansion.

Architecture: existing catalogue resolver, ST_RecordData, visit CandidateRecordIDs, WBP three-card caches and Shelf -> GFM -> Turntable authority. Existing formula and dialogue/history/profile/reaction semantics unchanged. Original three record payloads and WAV/packages frozen. Existing Store BGM is the fixed RS001 sound at0.18 after Continue, not selected LP looping; preserve and report.

Audit: Saved/MVPCompletion/20261110T034533Z-records456-audit.json PASS. Initial audit serialization of Unreal Array failed read-only; corrected to list and retained raw error. Existing three Stereo48kHz32.879/31.3/29.535s, sound volume0.8/nonloop/compression80. Existing Cover=None. ST_RecordData fields RecordID/Title/Artist/Genre/Mood/Energy/Theme/Cover/Audio; no RPM field.33/45/78 are player turntable settings, proposed recommended33RPM for new quiet tracks is authoring metadata only, no schema change.

Tasks:
- [x] Read-only branch/content hashes, graph/data/audio pipeline audit.
- [x] RED contract for six records/new covers/audio and ordered visits.
- [x] Original seeded audio and vector covers with source/provenance/technical self-checks (independent owned folders).
- [x] Editor-only import/append existing table and authored CandidateRecordIDs; preserve original FText and payloads. Show new covers using existing card UI, without duplicated record authority.
- [x] Runtime score matrix six profiles x six records, all sixteen visit candidate resolve/render/index mapping in at least3 fresh processes, invalid-set fail closed; canonical new playback via natural week.
- [x] Update old three-row/candidate-only fixtures and intentional hash guards using declared narrow changes and semantic before/after checks; preserve historical baseline files.
- [x] Fresh full EFGH/CD/B/A/Core gate, exact week/history16, original3native cases, audio/focus/dependency compile/map/cook. Retain every failure; no first-fail/rerun laundering.
- [x] Read-only independent review, cover/UI inspection, report19 user sections, final hashes/status and stop.

Ordering finding: previous RS002 failure is validate_mvp_cycle.py owner_alignment21.54cm versus15cm threshold, not candidate order. Widget ConfigureRecordCandidates already directly resolves ordered indices0/1/2. Investigate player timing separately; no alphabetical/frame sorting. Prove candidate order repeatedly in fresh sessions.

Ruling: user supplies detailed design/authorization, execute inline without extra approval/worktree/commit workflow. Parallel agents own audio and cover sources only; all Unreal work remains serial under root. Keep existing original generator and WAVs untouched.

Progress: RED20261110T035102Z Missing playable RS004; reference snapshot035148PASS (577 original protected files,15 allowed original packages). UI installer initial attempts failed on UMG GUID/temporary detached-caption compilation; no asset saved, owned failed editor processes stopped. Corrected to EditorUtilityLibrary.add_source_widget with all widgets attached during each structural compile. UI040103PASS; media/table/candidates040207PASS. Full serial expansion gate040408running (contract +3 fresh order sessions +all EFGH/CD/B/A/Core). Original3 FText/semantic/audio unchanged in installer before/after.

UI runtime RED040438: Configure Ready=false. Graph inspection040642 showed six Cast To TextBlock paths skipped by literal Text Block matcher. Root + reviewer diagnosed; normalized matcher +assert6 installed040743PASS. Old integration final catalogue count3 changed to6 afterindependentreview. Gate040839 then passedcontract andthree fresh96score/16visit/18click sessions with identicaldigests. Visualreview caught brushonly32px: SetDesiredSizeOverride is transient Slate-only perlocalUE Image.cpp; serializedBrush.ImageSize mustbe96. Addedbrush-sizecontract, intentionally stopped onlyownedvalidationprocess tree42244 toreplaceUIbeforefinalrun. Oldpartialaggregatepreserved, notfinalaccepted. RootnowrunningbrushRED041720thenpersistedBrushfixandfullfreshgate.

Size diagnostic follow-up: deprecated SlateVector2D Python wrapper lacks x/y; SlateLibrary cached geometry is zero in this PIE path (as existing validation notes). These failed diagnostic probes are retained, not counted as behavior passes. Removed brittle geometry assertion; texture identity/order remains automated and actual cover legibility is checked in rendered screenshots. UI fix uses WidgetLibrary.make_brush_from_texture with96x96 then clears resource throughpublicSetBrushFromTexture(None,false), serializing proper dimensions without a default selected cover. This is a static visual content fix; finalfresh3 +Core willrunafterit.

Final frozen gate042505: contractPASS; order sessions042535/042636/042731PASS with identical dc2a90c9bb8bc07fd0764430f6325b4c52b10c1434d60d2a7c6ff3c1419f683b,288scores/54permutationclicks. Actual96px cover/source16candidate screenshots visuallyreviewed and savedUIreviewJSON/contact sheets. EFGH042824contract+matrixPASS, CD043052contract+matrixPASS, B043223contract+matrixPASS, A043340contract+matrixPASS. Core043500editor/sequence/integration/guardsPASS; naturalweek/native/audio/cookpending. Do not mutate production assets during verification.

Final: records456-final-evidence.json independently flattened24passing groups from full042505aggregate, verified3equal digests/288scores/54clicks, all577protected hashes +15declared updated hashes, new WAV andSVG/PNG hashes,63changed files/6newuassets. Source installer added fail-closed roster guard before writing table; no further asset changes. Full Git status blocked byMSYS LFS signalpipepermission: inventory usesstartSHA+scopedtracked diff+gitlsothers; index/HEADcomparison staged0. Oneempty source-generationtempdirACL warning preserved. Branch/HEADunchanged. Final read-only report review PASS: no remaining Critical/Important findings; 24 atomic groups, 3 digests, week17/History16, protected hashes, 19 report sections, 63-file inventory and links independently verified. Stop before Day7/ending.
