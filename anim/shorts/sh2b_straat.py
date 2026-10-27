"""SH2b · tijd stopt · straat: dag 30, geen wind, geen geluid, vogels hangen in de lucht. Jaar 1: hij praat bij de
bushalte tegen een bevroren vrouw, gewoon om een stem te horen.

    blender -b -P anim/shorts/sh2b_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh2", "b", "straat", "zonnig", lines=(4, 5))
l4, l5 = S.L[4], S.L[5]
T0, END = S.t0, S.t1
RY = 0.6                                         # midden op de rijbaan

# ---------------------------------------------------------------- bevroren mensen en vogels
held = S.actor("hoofdpersonage", (-4.0, RY, 0), 90)
STRIDE = ((0.0, 0.24, 0.0), (0.0, -0.2, 0.09))
froze = []
for k, (x, y, rot, pose) in enumerate(((4.0, 6.0, 90, "staan"), (9.5, 5.6, -90, "zwaaien_a"), (2.0, -4.6, 90, "wijzen"),
                                       (12.5, -4.4, -90, "staan"))):
    ch = S.extra(k + 2, (x, y, 0.12), rot, energy=0.8)
    S.beat(ch, T0, pose, face=("lach", "blij", "verbaasd", "neutraal")[k], face_amt=0.7, feet=STRIDE if k % 2 == 0 else None,
           look=(0.3, 0.1))
    ch.frozen = T0
    froze.append(ch)
BUS = V(24.0, 7.6, 0.12)
vrouw = S.extra(1, BUS + V(-1.0, -0.5, 0), 20, energy=0.8)
S.beat(vrouw, T0, "armen_over", face="neutraal", look=(0.6, 0.1))
vrouw.frozen = T0
bird_m = S.mat("vogel", (0.22, 0.24, 0.3))


def bird(name, loc, rot, flap):
    e = bpy.data.objects.new(name, None)
    T._link(e)
    parts = [T.sphere(name + "_lijf", (0, 0, 0), 0.12, bird_m, scale=(1.0, 2.0, 0.8), ol=0.01),
             T.sphere(name + "_kop", (0, 0.22, 0.05), 0.07, bird_m, ol=0.01),
             T.cyl(name + "_snavel", (0, 0.28, 0.05), 0.02, 0.07, S.mat("snavel", (0.95, 0.7, 0.1)), r2=0.0, rot=(-90, 0, 0), seg=6, ol=0.003)]
    for s_ in (-1, 1):
        w = T.box(f"{name}_vleugel_{s_}", (0.2 * s_, 0, 0), (0.4, 0.18, 0.02), bird_m, bevel=0.01, ol=0.008, base=False)
        w.rotation_euler = (0, math.radians(-flap * s_), 0)
        parts.append(w)
    for o in parts:
        o.parent = e
    e.location = loc
    e.rotation_euler = (0, 0, math.radians(rot))
    return e


rnd = random.Random(4)
for k in range(9):
    bird(f"Vogel_{k}", (rnd.uniform(4, 20), rnd.uniform(-2, 9), rnd.uniform(5, 9)), rnd.uniform(60, 120), rnd.uniform(-35, 45))
PIGEON = V(6.2, RY + 0.35, 1.45)
bird("Duif_vlakbij", tuple(PIGEON), 100, 30)
ball = T.sphere("Bal", (3.0, -4.0, 1.1), 0.11, S.mat("bal", (0.9, 0.2, 0.2)), ol=0.005)

# ---------------------------------------------------------------- muziek en geluid (stilte)
S.music("strijkers_emo", l5[0] - 0.3, END + 6, vol=0.2, fade_in=1.5)
S.counter("DAY 30", l4[0] + 0.05, l5[0] - 0.05, sub="NO WIND. NO SOUND.")
S.counter("YEAR 1", l5[0] + 0.05, None, sub="365 DAYS ALONE")
S.card("", T0, END, dim=0.1, bg=(0.35, 0.5, 0.95), fin=0, fout=0)

# ---------------------------------------------------------------- dag 30: hij loopt door een stille straat
W1 = l4[1] - 0.9
S.walk(held, T0, W1, [V(-4.0, RY, 0), V(5.3, RY, 0)], stride=0.5, arms=0.5, end_rot=90)
S.beat(held, T0, "staan", face="neutraal", look=(0.3, 0.3), feet="keep", mouth=0.0)
S.beat(held, l4[0] + 2.0, "staan", face="verdrietig", face_amt=0.4, look=(0.3, 0.6), feet="keep", mouth=0.0,
       body={"head": (-15, 0, 0)})
S.beat(held, W1, "staan", face="verbaasd", face_amt=0.6, at=PIGEON, mouth=0.1)
S.reach(held, W1 + 0.2, "R", PIGEON + V(-0.22, -0.02, -0.02))
S.reach(held, l4[1] + 0.1, "R", None, 0.0)

# ---------------------------------------------------------------- jaar 1: bij de bushalte
SITP = BUS + V(0.1, 0.3, 0)
S.teleport(held, l5[0], SITP, -20)
spec, z = sit(held, seat_top=0.45)
S.place(held, l5[0], SITP + V(0, 0, z), -20)
S.beat(held, l5[0], **spec, pose="ontspannen", face="verdrietig", face_amt=0.5, at=S.head(vrouw, T0), mouth=0.0)
for k, t in enumerate(frange(l5[0] + 0.6, l5[1] - 1.8, 0.14)):
    A.key_prop(held.rig, "mond_open", (0.35, 0.05, 0.5, 0.15, 0.0, 0.4)[k % 6], F(t))
S.beat(held, l5[0] + 1.4, **spec, pose="schouders_op", face="blij", face_amt=0.4, at=S.head(vrouw, T0))
S.beat(held, l5[0] + 2.8, **spec, pose="wijzen", face="lach", face_amt=0.5, at=S.head(vrouw, T0))
S.beat(held, l5[1] - 1.6, **spec, pose="ontspannen", face="verdrietig", face_amt=0.9, look=(0, -0.6), mouth=0.0,
       body={"head": (18, 0, 0), "chest": (8, 0, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- camera (staand)
S.cam(T0, ((7.5, -1.6, 1.0), (0.0, RY, 1.6), 22), ((7.3, -1.5, 1.0), (2.0, RY, 1.7), 22))
S.cam(l4[0] + 1.9, ((2.0, -2.5, 0.6), (10.0, 4.0, 6.0), 18), ((2.3, -2.4, 0.6), (10.0, 4.0, 6.5), 18))
S.cam(W1 - 0.4, ((7.4, RY - 1.3, 1.5), (5.6, RY + 0.2, 1.4), 30), ((7.3, RY - 1.25, 1.5), (5.6, RY + 0.2, 1.4), 32))
S.cam(l5[0], ((BUS.x + 2.6, BUS.y - 4.0, 1.3), (BUS.x - 0.6, BUS.y - 0.4, 1.1), 26), ((BUS.x + 2.4, BUS.y - 3.6, 1.3), (BUS.x - 0.6, BUS.y - 0.4, 1.1), 28))
S.cam(l5[1] - 2.2, S.shot(held, l5[1] - 1.8, "mcu", az=-15, lens=36), S.shot(held, END, "mcu", az=-10, lens=40))

S.done()
