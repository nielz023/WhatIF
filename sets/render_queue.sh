#!/bin/sh
# Bouwt en rendert sets na elkaar. Gebruik: sh render_queue.sh "pretpark zonsondergang" "slaapkamer nacht" ...
# Met Blender:  BLENDER=blender sh render_queue.sh ...   (standaard: python3 met het bpy-pakket)
cd "$(dirname "$0")"
for job in "$@"; do
  set -- $job
  if [ -n "$BLENDER" ]; then
    "$BLENDER" -b -P "build_$1.py" -- "$2" ${3:-} 2>&1 | grep -E "KLAAR|Error|Traceback"
  else
    python3 "build_$1.py" "$2" ${3:-} 2>&1 | grep -E "KLAAR|Error|Traceback"
  fi
done
