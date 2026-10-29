#!/bin/bash
# haal.sh <regel-id> <spreker> <url>: zet een ElevenLabs-take in assets/audio/<Fnn>/
id=$1; who=$2; url=$3
d=/home/user/WhatIF/assets/audio/${id:0:3}; mkdir -p $d
f=$d/${id}_${who}.mp3
for k in 1 2 3; do curl -sSf -o "$f" "$url" && break; sleep 2; done
printf "%s %s %.2fs\n" "$id" "$who" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")"
