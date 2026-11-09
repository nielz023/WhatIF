@echo off
rem Rendert de 7 originele shorts (OR1-OR7, alle delen) en monteert ze tot MP4 in out\orN\ORN.mp4.
rem Gebruik (vanuit de repo-map):  anim\shorts\render_originelen.bat          (alles)
rem                                 anim\shorts\render_originelen.bat or4      (alleen short 4)
rem Een deel dat al klaar is (frames compleet) wordt opnieuw gerenderd; verwijder out\orN\frames om schoon te beginnen.
setlocal enabledelayedexpansion
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set ONLY=%1

for %%S in (or1 or2 or3 or4 or5 or6 or7) do (
  if "%ONLY%"=="" (set DO=1) else (if /I "%ONLY%"=="%%S" (set DO=1) else (set DO=0))
  if "!DO!"=="1" (
    for %%F in (anim\shorts\%%S?_*.py) do (
      echo === %%F ===
      %BLENDER% -b -P %%F -- --render --nosave
    )
    echo === montage %%S ===
    %BLENDER% -b -P anim\edit\montage.py -- %%S
  )
)
echo KLAAR
