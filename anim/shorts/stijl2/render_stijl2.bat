@echo off
rem Rendert de 7 originele shorts in de NIEUWE animatiestijl (OR1-OR7) en monteert ze tot MP4 in out\orN\ORN.mp4.
rem Gebruik (vanuit de repo-map):  anim\shorts\stijl2\render_stijl2.bat          (alles)
rem                                 anim\shorts\stijl2\render_stijl2.bat or4      (alleen short 4)
rem Nodig: cast-bestand glans_hoofdpersonage_volledig.blend in cast\glans\ (of pad in WHATIF_CAST).
rem Het cast-bestand wordt alleen geopend, NOOIT opgeslagen. Frames die al bestaan worden overgeslagen (hervatten kan).
rem LET OP: niet tegelijk met een andere render (video 4) draaien.
setlocal enabledelayedexpansion
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set CAST=%WHATIF_CAST%
if "%CAST%"=="" set CAST=cast\glans\glans_hoofdpersonage_volledig.blend
if not exist "%CAST%" (
  echo Cast-bestand niet gevonden: %CAST%
  exit /b 1
)
set ONLY=%1

for %%S in (or1 or2 or3 or4 or5 or6 or7) do (
  if "%ONLY%"=="" (set DO=1) else (if /I "%ONLY%"=="%%S" (set DO=1) else (set DO=0))
  if "!DO!"=="1" (
    for %%F in (anim\shorts\stijl2\%%S_*.py) do (
      echo === %%F ===
      %BLENDER% -b --disable-autoexec "%CAST%" -P %%F -- --render
    )
    echo === montage %%S ===
    %BLENDER% -b -P anim\edit\montage.py -- %%S
  )
)
echo KLAAR
