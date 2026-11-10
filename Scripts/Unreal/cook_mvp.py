"""Host-side production-map loose cook, with exit/log/artifact evidence. No package claim."""
import datetime,json,pathlib,subprocess,sys
from mvp_validation_logs import classify_log
from record_expansion_support import DATA
root=pathlib.Path(__file__).resolve().parents[2];folder=root/'Saved/MVPCompletion'
folder.mkdir(parents=True,exist_ok=True)
name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-cook-final'
log=folder/(name+'.log');output=folder/(name+'-Cooked')
args=['C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(root/'RecordShop.uproject'),'-run=cook','-SkipZenStore','-targetplatform=Windows','-Map=/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox','-unattended','-nop4','-nosound','-nullrhi','-ddc=(Local=(Type=FileSystem,Path='+str(root/'DerivedDataCache')+'))','-DDC-ForceMemoryCache','-UserDir='+str(folder/'CookUser'),'-abslog='+str(log),'-OutputDir='+str(output)]
# Bounded dependency/cook smoke: avoid generating nonignored CookerOpenOrder in
# Build. This does not validate a packaged asset registry, staging, or an archive.
args+=['-SkipSaveAssetRegistry']
(folder/(name+'-command.json')).write_text(json.dumps(args,indent=2),encoding='utf-8');print('START',name,flush=True)
with (folder/(name+'-stdout.txt')).open('w',encoding='utf-8') as stream:
 process=subprocess.Popen(args,stdout=stream,stderr=subprocess.STDOUT)
 try:code=process.wait(timeout=1800)
 except subprocess.TimeoutExpired:process.terminate();code=process.wait();print('COOK TIMEOUT',flush=True)
text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
maps=[str(x.relative_to(output)) for x in output.rglob('L_RecordShop_Greybox.umap')]
results=[str(x.relative_to(output)) for x in output.rglob('WBP_Result_IntegrationFallback.uasset')]
prologues=[str(x.relative_to(output)) for x in output.rglob('WBP_Prologue.uasset')]
histories=[str(x.relative_to(output)) for x in output.rglob('BP_RecommendationHistoryEntry.uasset')]
foundation={name:[str(x.relative_to(output)) for x in output.rglob(name+'.uasset')] for name in ('DT_RecordCatalogue','DA_RecordCatalogue','DA_A1_Narrative','DA_TutorialNarrative','DT_TutorialDialogue','DT_A_RevisitDialogue','DA_A2_Narrative','DA_A3_Narrative','DT_B_Dialogue','DA_B1_Narrative','DA_B2_Narrative','DA_B3_Narrative','DT_C_Dialogue','DA_C1_Narrative','DA_C2_Narrative','DT_D_Dialogue','DA_D1_Narrative','DA_D2_Narrative','DT_E_Dialogue','DA_E1_Narrative','DT_F_Dialogue','DA_F1_Narrative','DT_G_Dialogue','DA_G1_Narrative','DT_H_Dialogue','DA_H1_Narrative')}
expansion={data[key]:[str(x.relative_to(output))for x in output.rglob(data[key]+'.uasset')]for data in DATA['records'].values()for key in ('Audio','Cover')}
weeks=[str(x.relative_to(output)) for x in output.rglob('DA_TemporaryWeek.uasset')]
days=[str(x.relative_to(output)) for x in output.rglob('DA_Day*.uasset') if x.parent.name=='Schedule']
visits=[str(x.relative_to(output)) for x in output.rglob('DA_Visit_*.uasset') if x.parent.name=='Schedule']
errors=[line for line in text.splitlines() if ': Error:' in line]
log_gate=classify_log(text)
report={'exit_code':code,'exit_hex':hex(code & 0xffffffff),'log':str(log),'cooked_maps':maps,'cooked_result_widgets':results,'cooked_prologue_widgets':prologues,'cooked_record_expansion':expansion,'cooked_narrative_foundation':foundation,'cooked_history_contract':histories,'cooked_week_schedule':weeks,'cooked_days':days,'cooked_visits':visits,'errors':errors,'log_gate':log_gate,'pass':code==0 and bool(maps) and bool(results) and bool(prologues) and bool(weeks) and bool(histories) and all(foundation.values()) and len(expansion)==6 and all(expansion.values()) and len(days)==7 and len(visits)==16 and not errors and log_gate['gameplay_log_pass'],'package':'NOT RUN','scope':'bounded cook smoke with SkipSaveAssetRegistry'}
(folder/(name+'-process.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True);sys.exit(0 if report['pass'] else 1)
