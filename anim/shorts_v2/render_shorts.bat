@echo off
rem Shorts uit video 2: staande renders van de scene-stukken en daarna de 7 shorts.
rem Gebruik (in de repo-map):  anim\shorts_v2\render_shorts.bat "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
setlocal
set BL=%~1
if "%BL%"=="" set BL=blender
set WHATIF_VERTICAL=1
set WHATIF_VZOOM=1.3
set WHATIF_FPS=30
set WHATIF_ENGINE=EEVEE

if exist out\f01_staand\KLAAR.txt goto na_f01
set WHATIF_VSHIFT=
set WHATIF_RANGES=0.00-18.55
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f01_cold_open.py -- --render --nosave --out out\f01_staand || goto fout
echo klaar> out\f01_staand\KLAAR.txt
:na_f01

if exist out\f04a_staand\KLAAR.txt goto na_f04a
set WHATIF_VSHIFT=
set WHATIF_RANGES=8.00-15.15
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f04a_glas.py -- --render --nosave --out out\f04a_staand || goto fout
echo klaar> out\f04a_staand\KLAAR.txt
:na_f04a

if exist out\f04b_staand\KLAAR.txt goto na_f04b
set WHATIF_VSHIFT=
set WHATIF_RANGES=10.40-16.65
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f04b_ontbijt_traag.py -- --render --nosave --out out\f04b_staand || goto fout
echo klaar> out\f04b_staand\KLAAR.txt
:na_f04b

if exist out\f04c_staand\KLAAR.txt goto na_f04c
set WHATIF_VSHIFT=
set WHATIF_RANGES=0.20-22.45
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f04c_hardlopen.py -- --render --nosave --out out\f04c_staand || goto fout
echo klaar> out\f04c_staand\KLAAR.txt
:na_f04c

if exist out\f05b_staand\KLAAR.txt goto na_f05b
set WHATIF_VSHIFT=
set WHATIF_RANGES=0.00-30.15,47.60-53.55
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f05b_regen.py -- --render --nosave --out out\f05b_staand || goto fout
echo klaar> out\f05b_staand\KLAAR.txt
:na_f05b

if exist out\f06_staand\KLAAR.txt goto na_f06
set WHATIF_VSHIFT=
set WHATIF_RANGES=7.10-44.15
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f06_mama.py -- --render --nosave --out out\f06_staand || goto fout
echo klaar> out\f06_staand\KLAAR.txt
:na_f06

if exist out\f07_staand\KLAAR.txt goto na_f07
set WHATIF_VSHIFT=55.5-62.3:0.5
set WHATIF_RANGES=12.90-18.55,30.70-62.15
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f07_natuurkundige.py -- --render --nosave --out out\f07_staand || goto fout
echo klaar> out\f07_staand\KLAAR.txt
:na_f07

if exist out\f08a_staand\KLAAR.txt goto na_f08a
set WHATIF_VSHIFT=
set WHATIF_RANGES=7.60-36.75
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f08a_knal.py -- --render --nosave --out out\f08a_staand || goto fout
echo klaar> out\f08a_staand\KLAAR.txt
:na_f08a

if exist out\f08b_staand\KLAAR.txt goto na_f08b
set WHATIF_VSHIFT=
set WHATIF_RANGES=3.90-12.15
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f08b_stoeprand.py -- --render --nosave --out out\f08b_staand || goto fout
echo klaar> out\f08b_staand\KLAAR.txt
:na_f08b

if exist out\f09_staand\KLAAR.txt goto na_f09
set WHATIF_VSHIFT=
set WHATIF_RANGES=16.70-37.75
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f09_redding.py -- --render --nosave --out out\f09_staand || goto fout
echo klaar> out\f09_staand\KLAAR.txt
:na_f09

if exist out\f11_staand\KLAAR.txt goto na_f11
set WHATIF_VSHIFT=
set WHATIF_RANGES=39.70-49.85
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f11_feest.py -- --render --nosave --out out\f11_staand || goto fout
echo klaar> out\f11_staand\KLAAR.txt
:na_f11

if exist out\f12_staand\KLAAR.txt goto na_f12
set WHATIF_VSHIFT=77.0-80.3:0.8
set WHATIF_RANGES=0.50-22.15,71.10-80.15
"%BL%" -b --python-exit-code 1 -P anim\v2\scenes\f12_licht.py -- --render --nosave --out out\f12_staand || goto fout
echo klaar> out\f12_staand\KLAAR.txt
:na_f12

set WHATIF_RANGES=
set WHATIF_VERTICAL=
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s1 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s2 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s3 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s4 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s5 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s6 || goto fout
"%BL%" -b --python-exit-code 1 -P anim\shorts_v2\shorts.py -- build v2s7 || goto fout
echo ALLES KLAAR
exit /b 0
:fout
echo FOUT bij het renderen, zie hierboven
exit /b 1
