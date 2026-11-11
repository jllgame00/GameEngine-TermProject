"""Bounded UAT package attempt using installed Blueprint-game binaries; no release signoff."""
import datetime,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT=ROOT/'Saved/MVPCompletion'/(STAMP+'-ending-package');OUT.mkdir(parents=True)
engine=pathlib.Path('C:/Program Files/Epic Games/UE_5.8/Engine')
env=os.environ.copy();env['uebp_LogFolder']=str(OUT/'UATLogs');env['uebp_EngineSavedFolder']=str(OUT/'EngineSaved')
dotnet=engine/'Binaries/ThirdParty/DotNet/10.0/win-x64';env.update(DOTNET_ROOT=str(dotnet),DOTNET_MULTILEVEL_LOOKUP='0',DOTNET_ROLL_FORWARD='LatestMajor')
extra='-SkipZenStore -DDC-ForceMemoryCache -UserDir="'+str(OUT/'CookUser')+'" -ddc=(Local=(Type=FileSystem,Path='+str(ROOT/'DerivedDataCache')+'))'
args=[str(engine/'Build/BatchFiles/RunUAT.bat'),'-ScriptsForProject='+str(ROOT/'RecordShop.uproject'),'-nocompile','-nocompileuat','BuildCookRun','-project='+str(ROOT/'RecordShop.uproject'),'-unattended','-nop4','-utf8output','-platform=Win64','-clientconfig=Development','-nocompileeditor','-cook','-stage','-pak','-package','-archive','-archivedirectory='+str(OUT/'Archive'),'-stagingdirectory='+str(OUT/'Stage'),'-map=/Game/RecordShop/Maps/Greybox/L_RecordShop_Greybox','-AdditionalCookerOptions='+extra]
args=[str(dotnet/'dotnet.exe'),str(engine/'Binaries/DotNET/AutomationTool/AutomationTool.dll'),*args[1:]]
(OUT/'command.json').write_text(json.dumps(args,indent=2),encoding='utf8');print('ENDING_PACKAGE',OUT,flush=True)
with (OUT/'stdout.txt').open('w',encoding='utf8')as log:
 process=subprocess.Popen(args,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 try:code=process.wait(timeout=1800);timed_out=False
 except subprocess.TimeoutExpired:
  # Terminate only this UAT process tree, never a user's Editor session.
  subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True);code=process.wait();timed_out=True
executables=[str(p.relative_to(OUT))for p in (OUT/'Archive').rglob('*.exe')if p.name.lower()=='recordshop.exe']
licenses=[str(p.relative_to(OUT))for p in (OUT/'Archive').rglob('*OFL*')]
license_ok=any((OUT/p).read_bytes()==(ROOT/'Content/RecordShop/Licenses/NanumGothic_OFL_Full.txt').read_bytes()for p in licenses if(OUT/p).is_file())
result=dict(exit_code=code,timed_out=timed_out,executables=executables,licenses=licenses,full_font_notice_included=license_ok,**{'pass':code==0 and bool(executables)and license_ok},scope='technical package only; external rights remain CREDIT_VERIFICATION_REQUIRED',launch='NOT_RUN')
(OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2),flush=True);sys.exit(0 if result['pass']else 1)
