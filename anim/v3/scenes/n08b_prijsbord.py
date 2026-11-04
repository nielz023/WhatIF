"""N08b · Tankstation: het prijsbord (script scène 8b). Een hand schuift de cijfers van 1.89 naar 18.90.
VO: "No more rules means no more fair prices."

    blender -b -P anim/v3/scenes/n08b_prijsbord.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n08b", "snelweg", "tankstation", exposure=0.0)
sh = S.cuts([3.6])
END = sh[-1][1]

B = V(13.0, -8.5, 0.0)
RZ = math.radians(-20)
N = V(math.sin(RZ), -math.cos(RZ), 0)            # voorkant van het bord (lokaal -y)
TG = V(math.cos(RZ), math.sin(RZ), 0)             # lokaal +x
DIG = B + N * 0.16 + V(0, 0, 3.47)                # midden van de cijfers

old, new = S.obj("Prijsbord_prijs_oud"), S.obj("Prijsbord_prijs_nieuw")
T_OUT, T_IN = 1.25, 1.75
# oude prijs schuift opzij uit het veld, nieuwe schuift erin (lokaal x)
for o, keys in ((old, ((0.0, 0.0, True), (T_OUT, 0.0, True), (T_OUT + 0.3, 1.3, True), (T_OUT + 0.31, 1.3, False))),
                (new, ((0.0, -1.3, False), (T_IN - 0.01, -1.3, False), (T_IN, -1.3, True), (T_IN + 0.35, 0.0, True)))):
    x0 = o.location.x
    for t, dx, vis in keys:
        o.location.x = x0 + dx
        o.keyframe_insert("location", frame=F(t))
        o.hide_render = not vis
        o.keyframe_insert("hide_render", frame=F(t))
    for fc in A._fcurves(o):
        if fc.data_path == "hide_render":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

# trapje + pomphouder rechts naast het bord, reikt met zijn linkerhand naar de cijfers
STEP = 1.25
FOOT = B + N * 0.55 + TG * 0.85
T.box("Trapje", tuple(FOOT), (0.6, 0.5, STEP), S.mat("trapje_alu", (0.75, 0.76, 0.78)), rot=(0, 0, -20), bevel=0.02, ol=0.006)
man = S.actor("figurant_c", FOOT + V(0, 0, STEP), -20 + 180 - 25)
S.beat(man, 0.0, "staan", face="grijns", face_amt=0.6, at=DIG)
S.reach(man, 0.0, "L", inf=0.0)
S.reach(man, 0.6, "L", inf=0.0)
S.reach(man, 1.0, "L", DIG + TG * 0.35 + N * 0.06)
S.reach(man, T_OUT + 0.3, "L", DIG + TG * 0.75 + N * 0.06)
S.reach(man, T_IN - 0.05, "L", DIG - TG * 0.55 + N * 0.06)
S.reach(man, T_IN + 0.35, "L", DIG + TG * 0.05 + N * 0.06)
S.reach(man, T_IN + 0.75, "L", inf=0.0)
S.beat(man, T_IN + 0.8, "staan", face="grijns", face_amt=0.9, at=DIG)
S.hold(man, END)

# DETAIL: laag schuin onder het bord, lichte push-in
CAM0 = B + N * 2.9 - TG * 0.9 + V(0, 0, 2.6)
CAM1 = B + N * 2.5 - TG * 0.75 + V(0, 0, 2.7)
AIM = DIG + TG * 0.1 + V(0, 0, 0.3)
S.cam(0.0, (CAM0, AIM, 44), (CAM1, AIM, 46), handheld=0.15)

S.counter("DAY 2", 0, t0=0.0)
S.sfx("sfx_prijs_flip", T_OUT, 0.5)
S.sfx("sfx_prijs_flip", T_IN, 0.6)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.08)
S.say("N08-02", at=0.2)
S.finish(length=END, tail=0.0)
