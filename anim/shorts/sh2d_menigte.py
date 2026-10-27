"""SH2d · tijd stopt · straat, jaar 3: hij loopt door een bevroren menigte... en iemand knippert. Die ogen draaien
naar hem toe.

    blender -b -P anim/shorts/sh2d_menigte.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh2", "d", "straat", "zonnig", lines=(7, 8))
l7, l8 = S.L[7], S.L[8]
T0, END = S.t0, S.t1
for n in ("Auto_overkant_2",):
    o = S.obj(n)
    if o:
        o.hide_render = True

# ---------------------------------------------------------------- de menigte (bevroren midden op straat)
rnd = random.Random(7)
crowd = []
POSES = ["staan", "filmen", "wijzen", "armen_over", "staan", "zwaaien_a", "staan", "handen_zij", "staan", "schouders_op",
         "staan", "filmen", "staan"]
spots = []
for k in range(13):
    while True:
        p = V(rnd.uniform(-1.5, 7.5), rnd.uniform(-2.2, 3.4), 0)
        if abs(p.y - 0.6) > 0.55 and all((p - q).length > 1.0 for q in spots):
            break
    spots.append(p)
BLINKER = 5
spots[BLINKER] = V(5.6, 1.45, 0)
for k, p in enumerate(spots):
    rot = rnd.uniform(-180, 180) if k != BLINKER else -40
    ch = S.extra(k, p, rot, energy=0.8)
    S.beat(ch, T0, POSES[k], face=("neutraal", "lach", "verbaasd", "blij")[k % 4], face_amt=0.6, look=(0, 0),
           feet=((0.0, 0.24, 0.0), (0.0, -0.2, 0.09)) if k % 3 == 0 else None)
    ch.frozen = T0
    crowd.append(ch)
blinker = crowd[BLINKER]
S.beat(blinker, T0, "staan", face="neutraal", look=(0, 0))
BLINK = l7[1] - 0.45                            # '... someone blinks'
A.key_prop(blinker.rig, "knipper", 0.0, F(T0))
A.key_prop(blinker.rig, "knipper", 0.0, F(BLINK) - 2)
A.key_prop(blinker.rig, "knipper", 1.0, F(BLINK))
A.key_prop(blinker.rig, "knipper", 1.0, F(BLINK) + 3)
A.key_prop(blinker.rig, "knipper", 0.0, F(BLINK) + 6)
A.look(blinker, F(T0), 0, 0)
A.look(blinker, F(l8[0] - 0.3), 0, 0)
A.look(blinker, F(l8[0] + 0.3), -0.85, -0.1)      # zijn ogen draaien naar jou

# ---------------------------------------------------------------- hij, met stoppelbaard (jaar 3)
held = S.actor("hoofdpersonage", (-3.0, 0.6, 0), 90)
S.beat(held, 0.0, "staan", face="neutraal", look=(0, 0))


def jaw(u, v):
    if v > -0.05 or (u * u) / 0.09 + ((v + 0.05) ** 2) / 0.1 > 1:
        return False
    return not (abs(u) < 0.07 and v > -0.15)


S.place(held, 0.0, (-3.0, 0.6, 0), 180)
pts = face_points(S, held, 0.0, (0, 1, 0), jaw, step=0.014)
beard = P.points_mesh("Stoppels", pts, 0.009, S.mat("stoppels", (0.18, 0.12, 0.08)), seg=6)
attach_keep(beard, held, "head", 0.0)
S.place(held, 0.0, (-3.0, 0.6, 0), 90)

W1 = BLINK - 0.6
STOP = V(4.3, 0.6, 0)
S.walk(held, T0, W1, [V(-3.0, 0.6, 0), V(1.5, 0.75, 0), STOP], stride=0.42, arms=0.4, end_rot=90)
S.beat(held, T0, "staan", face="verdrietig", face_amt=0.6, look=(0.4, 0), feet="keep", mouth=0.0)
S.beat(held, T0 + 1.6, "staan", face="neutraal", look=(-0.4, 0.1), feet="keep", mouth=0.0, body={"head": (0, 0, 25)})
S.beat(held, W1, "staan", face="neutraal", look=(0.4, 0.1), mouth=0.0, body={"head": (0, 0, -20)})
S.beat(held, BLINK + 0.25, "schrik", amount=0.6, face="geschrokken", face_amt=1.0, at=S.head(blinker, T0), mouth=0.45)
S.beat(held, l8[0] + 0.6, "schrik", amount=0.8, face="bang", face_amt=1.0, at=S.head(blinker, T0), mouth=0.3)
S.hold(held, END)

# ---------------------------------------------------------------- geluid, kaart
S.music("strijk_noot", T0, END, vol=0.2, fade_in=0.8)
S.sfx("sfx_hartslag", T0 + 0.5, 0.3, loop_to=BLINK)
S.sfx("sfx_cliffhanger", BLINK - 0.05, 0.75)
S.card("", T0, END, dim=0.1, bg=(0.35, 0.5, 0.95), fin=0, fout=0)
S.counter("YEAR 3", T0 + 0.05, l8[0], sub="EVERYONE IS FROZEN")

# ---------------------------------------------------------------- camera
BH = S.head(blinker, T0)
S.cam(T0, ((-4.5, -2.6, 2.0), (2.0, 0.8, 1.3), 20), ((-4.0, -2.4, 1.95), (3.0, 0.8, 1.3), 21))
S.cam(T0 + 1.8, None, fn=lambda t: (S.head(held, t) + V(1.6, -0.9, 0.1), S.head(held, t) + V(0, 0, -0.1), 32))
S.cam(BLINK - 0.9, ((BH.x - 1.25, BH.y - 0.55, BH.z + 0.02), BH + V(0, 0, -0.03), 36),
      ((BH.x - 0.95, BH.y - 0.42, BH.z + 0.02), BH + V(0, 0, -0.03), 50))
S.cam(BLINK + 0.6, S.shot(held, BLINK + 0.8, "mcu", az=-10, lens=38), S.shot(held, l8[0], "mcu", az=-6, lens=42))
S.cam(l8[0] - 0.3, ((BH.x - 0.8, BH.y - 0.35, BH.z + 0.02), BH + V(0, 0, -0.03), 50),
      ((BH.x - 0.7, BH.y - 0.3, BH.z + 0.02), BH + V(0, 0, -0.03), 56))

S.done()
