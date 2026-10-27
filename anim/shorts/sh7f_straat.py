"""SH7f · teleport-kopieën · straat: de hele straat is hij. Ze draaien zich allemaal tegelijk om. En elk van hen
denkt dat hij de echte is.

    blender -b -P anim/shorts/sh7f_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "f", "straat", "zonnig", lines=(5, 6, 7))
l5, l6, l7 = S.L[5], S.L[6], S.L[7]
T0, END = S.t0, S.t1
for n in ("Auto_geparkeerd_2", "Auto_geparkeerd_3", "Auto_overkant_2"):
    o = S.obj(n)
    if o:
        o.hide_render = True
Z = 0.12
DOOR = V(1.2, 12.3, Z)
STOP = V(1.2, 8.6, Z)
held = S.actor("hoofdpersonage", DOOR, 0)
S.walk(held, T0 + 0.2, l5[0] + 2.0, [DOOR, STOP], stride=0.5, end_rot=0)
S.beat(held, T0, "staan", face="neutraal", look=(0, 0), feet="keep", mouth=0.0)
S.beat(held, l5[0] + 2.1, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, -0.1), mouth=0.6)
S.beat(held, l6[0] + 1.0, "schrik", amount=1.0, face="bang", face_amt=1.0, look=(0, 0), mouth=0.4)
S.beat(held, l7[0], "handen_zij", face="bang", face_amt=1.0, look=(0.3, 0), mouth=0.2)
S.hold(held, END)

# de menigte: allemaal hij, met de rug naar hem toe
rnd = random.Random(9)
copies, spots = [], []
while len(spots) < 26:
    p = V(rnd.uniform(-7, 9), rnd.uniform(-2.8, 7.4), 0)
    if (p - STOP).length < 1.6 or any((p - q).length < 1.05 for q in spots):
        continue
    spots.append(p)
TURN0 = l6[0] + 0.35
STEP = l6[1] - 3.0
for k, p in enumerate(spots):
    z = Z if p.y > 4.5 else 0.0
    p = V(p.x, p.y, z)
    c = S.actor("hoofdpersonage", p, rnd.uniform(-15, 15), label=f"kopie_{k}")
    copies.append(c)
    face_him = math.degrees(math.atan2((STOP - p).x, -(STOP - p).y))
    S.beat(c, T0, "staan", face="neutraal", face_amt=0.5, look=(0, 0))
    S.hold(c, TURN0)
    S.turn(c, TURN0, TURN0 + 0.5, face_him)
    S.beat(c, TURN0 + 0.5, "staan", face="neutraal", face_amt=1.0, at=STOP + V(0, 0, 1.4), mouth=0.0)
    if k % 3 == 0:
        S.beat(c, STEP + 0.6, "wijzen", face="boos", face_amt=0.9, at=STOP + V(0, 0, 1.4), mouth=0.3)
    else:
        S.beat(c, STEP + 0.6, ("vuisten", "staan", "armen_over")[k % 3], face=("boos", "grijns", "twijfel")[k % 3],
               face_amt=0.9, at=STOP + V(0, 0, 1.4), mouth=0.0)
    # ze zetten allemaal tegelijk een stap naar hem toe
    d = (STOP - p)
    d.z = 0
    S.walk(c, STEP, STEP + 0.9, [p, p + d.normalized() * 0.55], stride=0.3, end_rot=face_him)
    S.hold(c, END)

S.music("strijk_noot", l6[0] - 0.4, END, vol=0.22, fade_in=1.0)
S.ambience("sfx_wind_hoog", T0, END, vol=0.08)
S.sfx("sfx_dreun", TURN0 + 0.35, 0.45)
S.sfx("sfx_whoosh", TURN0, 0.3)
S.sfx("sfx_dreun", STEP + 0.4, 0.35)
S.sfx("sfx_cliffhanger", l6[1] - 1.8, 0.75)
S.counter("COPIES: 47", T0 + 0.1, l6[0], color=RED)
S.counter("WHICH ONE IS REAL?", l6[1] - 1.2, None, color=RED, size=110)

# camera
S.cam(T0, ((STOP.x + 1.1, STOP.y + 3.6, 2.0), (STOP.x - 0.5, -2.0, 0.8), 22), ((STOP.x + 0.9, STOP.y + 3.4, 1.95), (STOP.x - 0.5, -2.0, 0.9), 22))
S.cam(l5[0] + 2.0, ((STOP.x + 0.5, STOP.y + 1.3, 1.55), (STOP.x - 1.0, 0.0, 1.0), 20), ((STOP.x + 0.4, STOP.y + 1.2, 1.55), (STOP.x - 1.0, 0.0, 1.0), 20))
S.cam(TURN0 - 0.2, ((STOP.x - 0.8, STOP.y - 1.3, 1.3), (STOP.x - 1.5, -2.0, 1.2), 20), ((STOP.x - 0.8, STOP.y - 1.2, 1.3), (STOP.x - 1.5, -2.0, 1.2), 21))
near = sorted(copies, key=lambda c: (c.rig.location - STOP).length)[:2]
S.cam(l6[0] + 2.4, S.shot(near[0], l6[0] + 2.6, "mcu", az=0, lens=34), S.shot(near[0], l6[0] + 3.6, "mcu", az=0, lens=40))
S.cam(l6[0] + 3.7, S.shot(held, l6[0] + 3.9, "mcu", az=0, lens=34), S.shot(held, STEP, "mcu", az=0, lens=38))
S.cam(STEP, ((STOP.x + 0.2, STOP.y - 9.0, 6.0), (STOP.x, STOP.y - 2.0, 0.8), 22), ((STOP.x + 0.2, STOP.y - 8.0, 7.0), (STOP.x, STOP.y - 1.5, 0.8), 22))
S.cam(l7[0], ((STOP.x, STOP.y + 1.5, 9.0), STOP + V(0, -0.3, 0), 18), ((STOP.x, STOP.y + 1.0, 11.0), STOP + V(0, -0.2, 0), 18))
S.done()
