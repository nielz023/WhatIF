"""F08b · Dag 3 · 100x · straat in de grijze ochtend. Hij loopt heel langzaam het tuinpad af en gaat op de
stoeprand zitten, tien meter van zijn huis. Zijn hoofd zakt, hij dommelt in.

    blender -b -P anim/v2/scenes/f08b_stoeprand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f08b", "straat", "grijs")

DOOR = V(-1.4, 12.35, 0.12)                      # op het stoepje voor de voordeur
PATH = V(-1.4, 9.2, 0.12)
CURB = V(-10.0, 6.02, 0.0)                       # Markering_stoeprand_dag3: hij zit op de stoeprand
HOUSE = V(-1.4, 13.0, 2.0)

# dag 3, 08:45: de vuilniswagen komt pas morgen (voor hem), geen kraai of zak in de lucht, nog geen tekst op het raam
for nm in ("Vuilniswagen", "Kraai", "Plastic_zak"):
    o = S.obj(nm)
    o.hide_render = True
    for c in o.children_recursive:
        c.hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Raamtekst"):
        o.hide_render = True
for o in [o for o in bpy.data.objects if o.name.startswith("Auto_geparkeerd") and o.parent is None]:
    if abs(o.location.x - CURB.x) < 9.0:                # vrij zicht op de stoeprand
        o.location.x = CURB.x - 13.0 if o.location.x < CURB.x else CURB.x + 13.0

held = S.actor("hoofdpersonage", DOOR, 0)
SIT_H, zh = sit(held, seat_top=0.13)

# ---------------------------------------------------------------- tijdlijn
S.hud2(3, "100x", clock=clock(8 * 3600 + 44 * 60 + 52, 0.01, dec=2, day="TUE"), t0=0.3,
       awake=awake(20 + 43 / 60, rate=1 / 3600, t0=0.0, secs=True), awake_t0=0.5)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.05)
WALK1 = 3.6
SITT = WALK1 + 0.2                               # snede: hij zit
l1 = S.say("F08-05", at=SITT + 0.8)
NOD = l1[1] + 0.8                                # zijn hoofd zakt
END = NOD + 4.0
S.music("strijkers_emo", 0.0, END, vol=0.17, fade_in=1.5, fade_out=2.5)
S.card("", END - 1.0, END + 0.5, dim=1.0, fin=20, fout=1)

# ---------------------------------------------------------------- hij
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.7, look=(0, -0.3))
S.walk(held, 0.2, WALK1, [DOOR, DOOR + V(0, -0.65, 0)], stride=0.2)                # elke stap voorzichtig
S.teleport(held, SITT, CURB + V(0, 0, zh), 0)
S.beat(held, SITT, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.7, look=(0.0, -0.1),
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(held, l1[0] + 3.0, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.8, at=HOUSE,
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(held, l1[1] - 1.2, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=1.0, look=(0.0, -0.2),
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(held, NOD, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, look=(0.0, -0.2), body={"head": (8, 0, 0)},
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(held, NOD + 1.4, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.3, look=(0.0, -0.4), body={"head": (30, 0, 0), "neck": (12, 0, 0)},
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.eyes_closed(held, NOD + 0.8, END + 1)
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-0.9, 9.6, 1.35), DOOR + V(0, 0, 1.0), 30), ((-0.95, 9.8, 1.35), DOOR + V(0, -0.3, 1.0), 32))
S.cam(SITT, ((-14.0, 0.6, 1.4), (-5.2, 9.0, 1.4), 26), ((-13.8, 0.8, 1.4), (-5.4, 9.0, 1.4), 27))
HH = S.headpos(held, l1[0] + 4.0)
S.cam(l1[0] + 3.4, (HH + V(0.55, -1.15, -0.05), HH, 32), (HH + V(0.5, -1.0, -0.05), HH, 36), dof=1.6)
S.cam(NOD - 0.4, ((-10.0, 2.2, 1.0), CURB + V(0, 0, 0.6), 30), ((-10.0, 1.2, 5.5), CURB + V(0, 0, 0.4), 30))

S.finish(length=END)
