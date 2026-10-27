"""SH7d · teleport-kopieën · pretpark: geen rij.

    blender -b -P anim/shorts/sh7d_pretpark.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "d", "pretpark", "dag", lines=(), t0=7.5, t1=9.5)
T0, END = S.t0, S.t1
HP = V(-9.3, -20.6, 0)
held = S.actor("hoofdpersonage", HP, 50)
tele_fx(S, HP, T0 + 0.02, sound=False)
S.counter("JUMPS: 3", T0 + 0.1, None, color=(0.6, 0.85, 1.0, 1))
S.sfx("sfx_pretpark_sfeer", T0, 0.15)
S.beat(held, T0, "armen_omhoog", face="lach", face_amt=1.0, look=(0, 0.3), mouth=0.6)
S.beat(held, T0 + 0.9, "juichen", face="lach", face_amt=1.0, look=(0, 0), mouth=0.4)
show(held.rig, 0, END - 0.1)
tele_fx(S, HP, END - 0.1)
S.cam(T0, ((-5.6, -23.4, 1.25), (-9.3, -20.6, 1.25), 26), ((-6.0, -23.0, 1.25), (-9.3, -20.6, 1.25), 28))
S.done()
