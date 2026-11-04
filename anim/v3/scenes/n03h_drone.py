"""N03h · Dronebeeld boven de stad, late middag (script scène 3h). Klok tikt door naar MIDNIGHT IN 4:00:00.
VO: "In a few hours... all of them will be gone."

    blender -b -P anim/v3/scenes/n03h_drone.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n03h", "stad", "middag", exposure=0.15)
sh = S.cuts([4.2])
END = sh[-1][1]

# een rijdende auto en wat voetgangers, zodat de stad leeft
car = S.obj("Auto_rijdt")
for t, x in ((0.0, 38.0), (END, 4.0)):
    car.location = (x, 3.0, 0)
    car.keyframe_insert("location", frame=F(t))
for fc in A._fcurves(car):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
for k, (a, b) in enumerate((((-8, -14), (-8, -24)), ((8, 14), (8, 26)), ((14, -8), (26, -8)), ((-14, 8), (-26, 8)))):
    e = S.actor(f"figurant_{'abcd'[k]}", (a[0], a[1], 0.2), 0)
    S.walk(e, 0.0, END, [V(a[0], a[1], 0.2), V(b[0], b[1], 0.2)], stride=0.5)

# drone pull-back en omhoog, het kruispunt in het midden
S.cam(0.0, ((1.0, -16.0, 11.0), (0.0, 6.0, 1.0), 24), ((2.0, -44.0, 38.0), (0.0, 12.0, 0.0), 24))

S.countdown(0, 0.3, END, jumps=[(0.0, 4 * 3600 + 0 * 60 + 9), (3.0, 4 * 3600)], rate=3.0)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.18)
S.sfx("sfx_klok_tik", 0.0, 0.15, loop_to=END)
S.sfx("sfx_wind_hoog", 0.0, 0.2)
S.say("N03-06", at=0.5)
S.finish(length=END, tail=0.0)
