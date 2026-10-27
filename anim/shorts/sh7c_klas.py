"""SH7c · teleport-kopieën · klaslokaal: school in nul seconden.

    blender -b -P anim/shorts/sh7c_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "c", "school", "klaslokaal", lines=(2,), t0=5.8, t1=7.5)
T0, END = S.t0, S.t1
for o in bpy.data.objects:
    if o.name.startswith("Schoolstoel_"):
        o.rotation_euler.z = math.radians(-90)
HP = V(-3.2, 0.9, 0)
held = S.actor("hoofdpersonage", HP, 90)
tele_fx(S, HP, T0 + 0.02, sound=False)
S.counter("JUMPS: 2", T0 + 0.1, None, color=(0.6, 0.85, 1.0, 1))
S.beat(held, T0, "juichen", face="lach", face_amt=1.0, look=(0, 0), mouth=0.5)
S.beat(held, T0 + 0.8, "wijzen", face="grijns", face_amt=1.0, look=(0, 0), mouth=0.0)
show(held.rig, 0, END - 0.1)
tele_fx(S, HP, END - 0.1)
S.cam(T0, ((-0.6, -0.6, 1.4), (-3.2, 0.9, 1.1), 26), ((-0.7, -0.5, 1.38), (-3.2, 0.9, 1.1), 28))
S.done()
