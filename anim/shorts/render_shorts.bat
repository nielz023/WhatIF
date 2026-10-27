@echo off
rem Rendert alle teaser-shorts (alle delen) en monteert ze tot MP4 in out\shX\SHX.mp4.
rem Gebruik (vanuit de repo-map):  anim\shorts\render_shorts.bat            (alles)
rem                                 anim\shorts\render_shorts.bat sh4        (alleen short 4)
setlocal enabledelayedexpansion
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set ONLY=%1

for %%S in (sh1 sh2 sh3 sh4 sh5 sh7 sh8) do (
  if "%ONLY%"=="" (set DO=1) else (if /I "%ONLY%"=="%%S" (set DO=1) else (set DO=0))
  if "!DO!"=="1" (
    for %%F in (anim\shorts\%%S*.py) do (
      echo === %%F ===
      %BLENDER% -b -P %%F -- --render --nosave
    )
    echo === montage %%S ===
    %BLENDER% -b -P anim\edit\montage.py -- %%S
  )
)
echo KLAAR
