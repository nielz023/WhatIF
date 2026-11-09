#!/bin/bash
# Stills-check video 4: per scène begin/midden/eind van elk shot + QC-momenten -> out/stillscheck/<code>.jpg + qc
cd "$(dirname "$0")/../.."
for S in "$@"; do
  CODE=${S%%_*}
  rm -rf out/$CODE/stills
  t0=$(date +%s)
  WHATIF_ENGINE=WORKBENCH timeout 3000 python3 anim/v4/scenes/$S.py -- --stills full --pct 25 --nosave > out/stillscheck/$CODE.log 2>&1
  rc=$?
  N=$(ls out/$CODE/stills/*.png 2>/dev/null | wc -l)
  python3 anim/v4/sheet.py $CODE; if false; then
    C=6; R=$(( (N + C - 1) / C ))
    ffmpeg -v error -y -pattern_type glob -i "out/$CODE/stills/*.png" -vf "drawtext=text='%{metadata\:lavf.image2dec.source_basename\:NA}':x=4:y=4:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.5,tile=${C}x${R}" -frames:v 1 -q:v 4 out/stillscheck/$CODE.jpg
  fi
  cp out/$CODE/qc.txt out/stillscheck/$CODE.qc.txt 2>/dev/null
  echo "$CODE rc=$rc stills=$N $(( $(date +%s) - t0 ))s" >> out/stillscheck/status.txt
done
