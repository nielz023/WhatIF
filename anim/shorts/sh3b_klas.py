"""SH3b · 1 jaar vooruit kijken · klaslokaal (visioen 'morgen'): overhoring, hij weet alles, 100%.

    blender -b -P anim/shorts/sh3b_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh3", "b", "school", "klaslokaal", lines=(2,))
l2 = S.L[2]
T0, END = S.t0, S.t1


def seat(r, c, s):
    return V(-1.6 + 1.5 * r + 0.48, -2.4 + 2.2 * c + 0.38 * s, 0)


for o in bpy.data.objects:
    if o.name.startswith("Schoolstoel_"):
        o.rotation_euler.z = math.radians(-90)

HERO_SEAT = seat(1, 1, 1)
held = S.actor("hoofdpersonage", HERO_SEAT, -90)
SEATS = [(0, 1, -1), (1, 1, -1), (2, 1, 1), (2, 1, -1), (1, 0, 1), (1, 2, -1)]
klas = [S.extra(k, seat(*rcs), -90, energy=0.8) for k, rcs in enumerate(SEATS)]
TEACH = V(-3.3, 0.6, 0)
leraar = S.actor("gymleraar", TEACH, 90, label="leraar", drop=("fluitje", "koord"),
                 outfit=dict(shirt=(0.35, 0.45, 0.62), broek=(0.22, 0.2, 0.18)))
SIT = {}
for ch in klas + [held]:
    spec, z = sit(ch)
    SIT[ch.rig.name] = spec
    S.place(ch, 0, ch.rig.location.copy() + V(0, 0, z), -90)

paper_m = S.mat("papier", (0.97, 0.97, 0.94))
ink = S.mat("inkt", (0.15, 0.2, 0.5))
red = S.mat("rood_cijfer", (0.9, 0.08, 0.06))
for k, rcs in enumerate(SEATS):
    p = seat(*rcs) + V(-0.45, 0, 0.735)
    T.box(f"Toets_{k}", tuple(p), (0.21, 0.29, 0.002), paper_m, bevel=0, ol=0.002, rot=(0, 0, 90))
PAPER = HERO_SEAT + V(-0.45, 0, 0.735)
paper = T.box("Zijn_toets", (0, 0, 0), (0.21, 0.29, 0.003), paper_m, bevel=0, ol=0.002, base=False)
paper.location = PAPER
paper.rotation_euler = (0, 0, math.radians(90))
lines_ = []
for j in range(7):
    ln = T.box(f"Toets_regel_{j}", (0.0, 0.11 - j * 0.032, 0.002), (0.14, 0.006, 0.001), ink, bevel=0, ol=0, base=False)
    ln.parent = paper
    lines_.append(ln)
score = T.text("Toets_score", "100%", (0.0, -0.105, 0.003), 0.06, red, rot=(0, 0, 0), extrude=0.001)
score.parent = paper
pen = T.cyl("Pen", (0, 0, 0), 0.006, 0.13, S.mat("pen", (0.1, 0.25, 0.8)), seg=8, ol=0.002)

WRITE0, WRITE1 = T0 + 0.6, l2[0] + 3.4
for j, ln in enumerate(lines_):
    show(ln, WRITE0 + (WRITE1 - WRITE0) * (j + 0.5) / len(lines_))
SCORE = l2[1] - 1.6
show(score, SCORE)

S.counter("TOMORROW", T0 + 0.1, None, color=(0.75, 0.9, 1.0, 1), sub="POP QUIZ")
S.card("", T0, END, dim=0.12, bg=(0.85, 0.95, 1.0), fin=0, fout=0)
S.card("", T0, T0 + 0.35, dim=1.0, bg=(1, 1, 1), fin=0, fout=8)
S.ambience("sfx_klas_geroezemoes", T0, END, vol=0.08)
for t in frange(WRITE0, WRITE1, 0.5):
    S.sfx("sfx_naald", t, 0.08)
S.sfx("sfx_titel", SCORE, 0.35)

# acteren
HS = SIT[held.rig.name]
S.beat(held, T0, **HS, pose="ontspannen", face="grijns", face_amt=0.9, at=PAPER, mouth=0.0)
grab(S, pen, held, T0, "hand.R", mode="full", rot=(90, 0, 0))
for k, t in enumerate(frange(WRITE0, WRITE1, 0.16)):
    S.reach(held, t, "R", PAPER + V(0.04, -0.06 + 0.12 * ((k * 0.37) % 1), 0.03 + 0.015 * (k % 2)))
S.reach(held, WRITE1 + 0.2, "R", None, 0.0)
S.beat(held, WRITE1, **HS, pose="armen_over", face="zelfverzekerd", face_amt=1.0, look=(0.4, 0))
for k, ch in enumerate(klas):
    S.beat(ch, T0, **SIT[ch.rig.name], pose="ontspannen", face=("nerveus", "twijfel", "verdrietig")[k % 3], face_amt=0.7,
           look=(0, -0.6), body={"head": (16, 0, 0)})
    S.beat(ch, WRITE1 + 0.3 + 0.1 * k, **SIT[ch.rig.name], pose="ontspannen", face="verbaasd", face_amt=0.8,
           at=HERO_SEAT + V(0, 0, 1.2))
# 100%: hij houdt de toets omhoog
UP = SCORE + 0.1
S.reach(held, UP, "L", PAPER + V(0.02, 0.1, 0.02))
grab(S, paper, held, UP + 0.15, "hand.L", mode="full", rot=(90, 0, 0))
S.reach(held, UP + 0.6, "L", S.head(held, T0) + V(-0.32, 0.18, 0.18))
S.beat(held, UP + 0.6, **HS, pose="juichen", face="lach", face_amt=1.0, look=(0, 0), mouth=0.5)
S.beat(leraar, T0, "armen_over", face="neutraal", at=HERO_SEAT + V(0, 0, 1.2))
S.beat(leraar, UP + 0.5, "schrik", amount=0.7, face="geschrokken", face_amt=1.0, at=HERO_SEAT + V(0, 0, 1.2), mouth=0.6)
S.hold(held, END)

S.cam(T0, ((-1.2, 1.25, 1.55), (0.3, 0.2, 1.0), 26), ((-1.1, 1.2, 1.52), (0.3, 0.2, 1.0), 28))
S.cam(WRITE0 + 1.2, (PAPER + V(-0.3, 0.32, 0.42), PAPER + V(0.02, 0, 0.0), 34), (PAPER + V(-0.27, 0.3, 0.38), PAPER + V(0.02, 0, 0), 38))
S.cam(SCORE - 0.3, ((-1.0, 1.1, 1.45), (0.3, 0.2, 1.3), 28), ((-0.95, 1.08, 1.45), (0.3, 0.2, 1.3), 30))

S.done()
