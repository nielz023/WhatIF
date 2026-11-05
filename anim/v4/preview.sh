#!/bin/bash
# Snelle workbench-controle: anim/v4/preview.sh d02_slaapkamer [tijden|auto] [pct]
# -> out/<code>/sheet.jpg (contactvel) en de QC-meldingen
set -e
cd "$(dirname "$0")/../.."
S=$1; TIMES=${2:-auto}; PCT=${3:-30}
CODE=${S%%_*}
rm -rf out/$CODE/stills
WHATIF_ENGINE=WORKBENCH python3 anim/v4/scenes/$S.py -- --stills $TIMES --pct $PCT --nosave > out/$CODE.log 2>&1 || { tail -30 out/$CODE.log; exit 1; }
grep "QC " out/$CODE.log | head -40
N=$(ls out/$CODE/stills/*.png | wc -l)
C=4; [ $N -le 4 ] && C=$N
R=$(( (N + C - 1) / C ))
ffmpeg -v error -y -pattern_type glob -i "out/$CODE/stills/*.png" -vf "drawtext=text='%{metadata\:lavf.image2dec.source_basename\:NA}':x=5:y=5:fontsize=14:fontcolor=yellow,tile=${C}x${R}" -frames:v 1 out/$CODE/sheet.jpg 2>/dev/null || ffmpeg -v error -y -pattern_type glob -i "out/$CODE/stills/*.png" -vf "tile=${C}x${R}" -frames:v 1 out/$CODE/sheet.jpg
echo "SHEET out/$CODE/sheet.jpg ($N beelden)"
