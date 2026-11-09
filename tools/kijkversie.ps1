# Snelle kijkversie (lessen video 3, 2026-11-08): eerst de BEWEGING bekijken, dan pas de echte render.
# Rendert elke scène in WORKBENCH op lage resolutie (seconden per scène i.p.v. uren), maakt er mp4's van,
# draait de videocheck en zet alles met stem en muziek in één kijkversie van de hele video.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\kijkversie.ps1 -Video "C:\Users\niels\Documents\WHAT IF\video4" -Scenes anim\v4\scenes
#   ... -Codes d04,d05          (alleen deze scènes)
#
# Uitvoer: <Video>\kijk\scenes\<code>_kijk.mp4, <Video>\kijk\KIJKVERSIE.mp4 en per scène kijk\<code>\qc.txt + videocheck.
# De kijkversie is grijs en zonder glans; hij is alleen om schokken, botsingen, camera en timing te zien.
param(
    [Parameter(Mandatory = $true)][string]$Video,
    [string]$Scenes = "anim\v4\scenes",
    [string]$Codes = "",
    [int]$Pct = 40,
    [string]$Blender = $env:BLENDER,
    [string]$Assemble = "anim\edit\assemble_v3.py"
)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
if (-not $Blender) {
    $Blender = (Get-ChildItem "C:\Program Files\Blender Foundation" -Recurse -Filter blender.exe -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1).FullName
}
if (-not $Blender) { throw "blender.exe niet gevonden; geef -Blender of zet BLENDER" }
$Kijk = Join-Path $Video "kijk"
$Out = Join-Path $Kijk "scenes"
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$want = @($Codes.Split(",") | Where-Object { $_ })
$scripts = Get-ChildItem (Join-Path $Repo $Scenes) -Filter "*.py" | Sort-Object Name
$fouten = @()
foreach ($s in $scripts) {
    $code = $s.BaseName.Split("_")[0]
    if ($want.Count -gt 0 -and -not ($want -contains $code)) { continue }
    $dir = Join-Path $Kijk $code
    if (Test-Path (Join-Path $dir "frames")) { Remove-Item -Recurse -Force (Join-Path $dir "frames") }
    Write-Host "== $code"
    $env:WHATIF_ENGINE = "WORKBENCH"
    $log = Join-Path $Kijk "$code.log"
    & $Blender -b -P $s.FullName -- --render --nosave --pct $Pct --samples 1 --out $dir *> $log
    Remove-Item Env:\WHATIF_ENGINE
    if (Select-String -Path $log -Pattern "Traceback" -Quiet) { $fouten += "$code CRASH (zie $log)"; continue }
    $qc = Join-Path $dir "qc.txt"
    if ((Test-Path $qc) -and -not ((Get-Content $qc -Raw).Trim() -eq "OK")) { $fouten += "$code QC: " + ((Get-Content $qc) -join " | ") }
    $mp4 = Join-Path $Out "$($s.BaseName)_kijk.mp4"
    ffmpeg -v error -y -framerate 30 -start_number 1 -i (Join-Path $dir "frames\%04d.png") -c:v libx264 -pix_fmt yuv420p -crf 26 $mp4
    if (-not (Test-Path $mp4)) {   # frames beginnen niet altijd op 1 (30 fps-offset)
        $first = (Get-ChildItem (Join-Path $dir "frames") -Filter *.png | Sort-Object Name | Select-Object -First 1).BaseName
        ffmpeg -v error -y -framerate 30 -start_number ([int]$first) -i (Join-Path $dir "frames\%04d.png") -c:v libx264 -pix_fmt yuv420p -crf 26 $mp4
    }
    python (Join-Path $Repo "anim\edit\videocheck.py") $mp4 --geen-geluid --uit (Join-Path $dir "videocheck") | Out-Null
    if ($LASTEXITCODE -ne 0) { $fouten += "$code VIDEOCHECK: zie $dir\videocheck\videocheck.txt" }
}
# hele video met stem en muziek (ontbrekende scènes worden overgeslagen)
& $Blender -b -P (Join-Path $Repo $Assemble) -- --scenes $Out --json $Kijk --allow-missing --preview 0-99999 --out (Join-Path $Kijk "KIJKVERSIE.mp4") *> (Join-Path $Kijk "montage.log")
$rapport = Join-Path $Kijk "rapport.txt"
if ($fouten.Count -eq 0) { "ALLES SCHOON" | Set-Content $rapport } else { $fouten | Set-Content $rapport }
Get-Content $rapport
