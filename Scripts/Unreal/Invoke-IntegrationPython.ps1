param(
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$Name = 'integration',
    [switch]$Editor,
    [switch]$Rendered
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$scriptPath = (Resolve-Path -LiteralPath $Script).Path
$evidence = Join-Path $projectRoot 'Saved/OvernightIntegration/Round1'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$engine = 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$arguments = @(
    ('"' + (Join-Path $projectRoot 'RecordShop.uproject') + '"'),
    '-EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities',
    '-unattended', '-nosound', '-nop4', '-nosplash',
    ('"-ddc=(Local=(Type=FileSystem,Path=' + (Join-Path $projectRoot 'DerivedDataCache') + '))"'),
    '-DDC-ForceMemoryCache',
    ('"-UserDir=' + (Join-Path $evidence 'User') + '"'),
    ('"-abslog=' + (Join-Path $evidence ($Name + '.log')) + '"')
)
if (-not $Rendered) { $arguments += '-nullrhi' }
if ($Editor) {
    $arguments += @('-RenderOffscreen', '-NoLoadStartupPackages', ('"-ExecutePythonScript=' + $scriptPath + '"'))
} else {
    $arguments += @('-run=pythonscript', ('"-script=' + $scriptPath + '"'))
}
$process = Start-Process -FilePath $engine -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait
Write-Output ('Unreal exit code: ' + $process.ExitCode)
exit $process.ExitCode
