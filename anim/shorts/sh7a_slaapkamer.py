"""SH7a · What if every teleport made a copy of you? · slaapkamer: hij ligt nog in bed, knippert... en is weg.

    blender -b -P anim/shorts/sh7a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "a", "slaapkamer", "ochtend", lines=(), t0=0.0, t1=1.0)
BED = V(-1.52, 1.25, 0.6)
held = S.actor("hoofdpersonage", BED, 0)
SIT, _ = sit(held, seat_top=0.0, lean=-8, spread=0.12)
GONE = 0.75
S.beat(held, 0.0, **SIT, pose="ontspannen", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (-6, 0, 0)})
A.blink_at(held, F(GONE - 0.15), closed=3)
show(held.rig, 0, GONE)
tele_fx(S, BED + V(0, -0.3, 0), GONE)
S.music_all("pizz_spanning", vol=0.22)
S.cam(0.0, S.shot(held, 0.2, "mcu", az=10, lens=32, h=-0.05), S.shot(held, 1.0, "mcu", az=8, lens=34, h=-0.05))
S.done()
