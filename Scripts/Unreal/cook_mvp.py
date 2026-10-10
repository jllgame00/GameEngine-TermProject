"""Host-side production-map loose cook, with exit/log/artifact evidence. No package claim."""
import datetime,json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[2];folder=root/'Saved/MVPCompletion'
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
errors=[line for line in text.splitlines() if ': Error:' in line]
report={'exit_code':code,'exit_hex':hex(code & 0xffffffff),'log':str(log),'cooked_maps':maps,'cooked_result_widgets':results,'errors':errors,'pass':code==0 and bool(maps) and bool(results) and not errors,'package':'NOT RUN','scope':'bounded cook smoke with SkipSaveAssetRegistry'}
(folder/(name+'-process.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True);sys.exit(0 if report['pass'] else 1)
