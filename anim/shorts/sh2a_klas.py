"""SH2a · What if time stopped and only you could move? · klaslokaal: hij niest en alles staat stil. Een potlood
(van de pestkop, naar zijn hoofd gegooid) hangt in de lucht, de leraar bevroren midden in een woord. Gratis snoep,
en de pestkop krijgt een snor.

    blender -b -P anim/shorts/sh2a_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh2", "a", "school", "klaslokaal", lines=(1, 2, 3))
l1, l2, l3 = S.L[1], S.L[2], S.L[3]
FREEZE = l1[0] + 2.9                            # '... stops'


def seat(r, c, s):
    return V(-1.6 + 1.5 * r + 0.48, -2.4 + 2.2 * c + 0.38 * s, 0)


for o in bpy.data.objects:
    if o.name.startswith("Schoolstoel_"):
        o.rotation_euler.z = math.radians(-90)

# ---------------------------------------------------------------- figuren
HERO_SEAT = seat(1, 1, 1)
BULLY_SEAT = seat(2, 1, 1)
held = S.actor("hoofdpersonage", HERO_SEAT, -90)
pest = S.actor("pestkop", BULLY_SEAT, -90)
TEACH = V(-3.55, 0.6, 0)
leraar = S.actor("gymleraar", TEACH, 90, label="leraar", drop=("fluitje", "koord"),
                 outfit=dict(shirt=(0.35, 0.45, 0.62), broek=(0.22, 0.2, 0.18)))
SEATS = [(0, 0, -1), (0, 1, 1), (0, 2, -1), (1, 0, 1), (1, 2, -1), (2, 0, -1), (2, 2, 1), (3, 1, -1), (3, 2, 1)]
klas = [S.extra(k, seat(*rcs), -90, energy=0.8) for k, rcs in enumerate(SEATS)]
SIT = {}
for ch in klas + [pest, held]:
    spec, z = sit(ch)
    SIT[ch.rig.name] = spec
    S.place(ch, 0, ch.rig.location.copy() + V(0, 0, z), -90)
for ch in klas + [pest, leraar]:
    ch.frozen = FREEZE

# ---------------------------------------------------------------- props
pencil = T.cyl("Potlood", (0, 0, 0), 0.007, 0.17, S.mat("potlood", (0.98, 0.78, 0.1)), seg=6, ol=0.002)
T.cyl("Potlood_punt", (0, 0, 0.17), 0.007, 0.025, S.mat("hout_licht", (0.9, 0.72, 0.5)), r2=0.001, seg=6, ol=0.001).parent = pencil
P_FROM = BULLY_SEAT + V(-0.25, 0.12, 1.05)
P_STOP = HERO_SEAT + V(0.42, 0.04, 1.3)        # vlak achter zijn hoofd
for k, t in enumerate(frange(FREEZE - 0.55, FREEZE + 0.01, 1 / FPS)):
    u = (t - (FREEZE - 0.55)) / 0.55 * 0.62     # bij de bevriezing is hij op 62% van zijn baan
    p = P_FROM.lerp(HERO_SEAT + V(0, 0.04, 1.25), u) + V(0, 0, 0.35 * u * (1 - u) * 2)
    key(pencil, t, loc=tuple(p), rot=(0, -90 + 20 * u, 720 * u))
show(pencil, FREEZE - 0.55)
chips = T.box("Chips", (-1.6, 0.4, 0.73), (0.17, 0.05, 0.24), S.mat("chipszak", (0.9, 0.12, 0.12)), bevel=0.02, ol=0.004)
T.box("Chips_label", (0, -0.027, 0.07), (0.1, 0.004, 0.09), S.mat("chipslabel", (1.0, 0.85, 0.1)), bevel=0, ol=0).parent = chips
marker = T.cyl("Stift", (0, 0, 0), 0.01, 0.13, S.mat("stift", (0.08, 0.08, 0.1)), seg=8, ol=0.002)

# ---------------------------------------------------------------- muziek en geluid
S.music_all("piano_hol", vol=0.22)
S.ambience("sfx_klas_geroezemoes", 0.0, FREEZE, vol=0.16)
S.ambience("sfx_klok_tik", 0.0, FREEZE, vol=0.12)
S.sfx("sfx_nies_boem", l1[0] + 0.55, 0.22)
S.sfx("sfx_tijd_stop", FREEZE - 0.05, 0.6)
S.sfx("sfx_whoosh", FREEZE - 0.5, 0.25)
S.counter("DAY 1", FREEZE + 0.3, None, sub="TIME: STOPPED")
S.card("", FREEZE, S.t1, dim=0.1, bg=(0.35, 0.5, 0.95), fin=3, fout=0)

# ---------------------------------------------------------------- vóór de stilstand: de klas leeft
for k, ch in enumerate(klas):
    S.beat(ch, 0.0, **SIT[ch.rig.name], pose="ontspannen", face="neutraal", look=(0, 0), at=TEACH + V(0, 0, 1.6))
S.beat(klas[1], 0.0, **SIT[klas[1].rig.name], pose="ontspannen", face="lach", face_amt=0.7, look=(0.5, 0))
S.beat(klas[4], FREEZE - 0.4, **SIT[klas[4].rig.name], pose="armen_omhoog", amount=0.7, face="neutraal", mouth=0.9)  # gaapt
S.beat(leraar, 0.0, "wijzen", face="neutraal", look=(0.2, 0), at=HERO_SEAT + V(0, 0, 1.2))
for k, t in enumerate(frange(0.1, FREEZE, 0.13)):
    A.key_prop(leraar.rig, "mond_open", (0.1, 0.5, 0.25, 0.6, 0.0)[k % 5], F(t))
A.key_prop(leraar.rig, "mond_open", 0.65, F(FREEZE))
S.beat(leraar, FREEZE - 0.3, "wijzen", face="boos", face_amt=0.5, at=HERO_SEAT + V(0, 0, 1.2))
# de pestkop gooit
S.beat(pest, 0.0, **SIT[pest.rig.name], pose="ontspannen", face="grijns", face_amt=0.8, at=HERO_SEAT + V(0, 0, 1.2))
S.beat(pest, FREEZE - 0.8, **SIT[pest.rig.name], pose="ontspannen", face="grijns", face_amt=1.0, at=HERO_SEAT + V(0, 0, 1.2))
S.reach(pest, FREEZE - 0.8, "R", BULLY_SEAT + V(0.1, -0.1, 1.35))
S.reach(pest, FREEZE - 0.25, "R", BULLY_SEAT + V(-0.35, 0.05, 1.05))
S.reach(pest, FREEZE, "R", BULLY_SEAT + V(-0.42, 0.06, 1.0))

# ---------------------------------------------------------------- hij: niezen, stilte, opstaan
HS = SIT[held.rig.name]
S.beat(held, 0.0, **HS, pose="ontspannen", face="neutraal", look=(0, 0))
S.reach(held, 0.0, "R", None, 0.0)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, l2[0] + 1.3, "R", None, 0.0)
S.beat(held, l1[0] + 0.3, **HS, pose="ontspannen", face="inspanning", face_amt=0.5, look=(0, 0.4), mouth=0.4,
       body={"head": (-18, 0, 0), "chest": (-6, 0, 0)})
S.beat(held, l1[0] + 0.6, **HS, pose="schrik", amount=0.5, face="inspanning", face_amt=1.0, look=(0, -0.4), mouth=0.7,
       body={"head": (22, 0, 0), "chest": (12, 0, 0)})
S.beat(held, l1[0] + 1.2, **HS, pose="ontspannen", face="neutraal", look=(0, 0), mouth=0.0)
S.beat(held, FREEZE + 0.3, **HS, pose="ontspannen", face="verbaasd", face_amt=0.7, look=(0.5, 0), mouth=0.15,
       body={"head": (0, 0, -25)})
S.beat(held, l1[1] - 0.3, **HS, pose="ontspannen", face="verbaasd", face_amt=1.0, look=(-0.5, 0), mouth=0.2,
       body={"head": (0, 0, 25)})
# opstaan, omdraaien: het potlood hangt vlak achter hem
UP = l2[0] + 0.1
S.place(held, UP, HERO_SEAT + V(0.05, 0.42, 0), -90)
S.beat(held, UP + 0.3, "staan", face="verbaasd", face_amt=0.9, look=(0, 0), mouth=0.2)
S.turn(held, UP + 0.35, UP + 0.9, 90)
S.beat(held, UP + 1.0, "staan", face="geschrokken", face_amt=0.9, at=P_STOP, mouth=0.35)
S.reach(held, UP + 1.4, "R", P_STOP + V(-0.08, -0.03, -0.02))
S.reach(held, UP + 1.6, "R", P_STOP + V(-0.03, -0.01, 0.0))
S.reach(held, UP + 1.9, "R", None, 0.0)
# naar de leraar, zwaaien voor zijn gezicht
W0, W1 = UP + 2.0, l2[0] + 3.5
TEACH_FACE = S.head(leraar, 0.0)
NEAR_T = V(-2.95, 0.95, 0)
S.walk(held, W0, W1, [HERO_SEAT + V(0.05, 0.42, 0), V(0.0, 0.92, 0), NEAR_T], stride=0.5, end_rot=240)
S.beat(held, W0, "staan", face="neutraal", look=(0.3, 0), feet="keep", mouth=0.0)
S.beat(held, W1 + 0.1, "staan", face="grijns", face_amt=0.6, at=TEACH_FACE, mouth=0.0)
for k, t in enumerate(frange(W1 + 0.2, l2[1], 0.22)):
    S.reach(held, t, "R", TEACH_FACE + V(0.32, 0.12 * (1 if k % 2 else -1), 0.0))
S.reach(held, l2[1] + 0.05, "R", None, 0.0)

# ---------------------------------------------------------------- 3 · eerst geweldig
JUMP = l3[0]
S.teleport(held, JUMP, V(-0.85, 0.92, 0), 0)
S.beat(held, JUMP, "juichen", face="lach", face_amt=1.0, look=(0, 0), mouth=0.5)
S.beat(held, JUMP + 0.6, "armen_omhoog", face="lach", face_amt=1.0, look=(0, 0.2), mouth=0.4)
SNACK = l3[0] + 1.4
S.teleport(held, SNACK, V(-1.6, 0.98, 0), 0)
S.beat(held, SNACK, "staan", face="grijns", face_amt=1.0, at=V(-1.6, 0.4, 0.8), mouth=0.0)
S.reach(held, SNACK + 0.1, "R", V(-1.6, 0.42, 0.95))
grab(S, chips, held, SNACK + 0.35, "hand.R", mode="full", offset=(0, 0, 0))
S.reach(held, SNACK + 0.7, "R", S.head(held, SNACK) + V(0.12, -0.32, -0.25))
S.beat(held, SNACK + 0.8, "staan", face="lach", face_amt=0.8, look=(0, 0), mouth=0.5)
for k, t in enumerate(frange(SNACK + 0.9, SNACK + 1.5, 0.12)):
    A.key_prop(held.rig, "mond_open", 0.45 if k % 2 else 0.05, F(t))
# de snor
STACHE = l3[0] + 2.8
BF = BULLY_SEAT + V(0, 0.72, 0)
S.teleport(held, STACHE, BF, 200)
grab(S, marker, held, STACHE, "hand.R", mode="full", rot=(90, 0, 0))
show(chips, 0, STACHE)
show(marker, STACHE)
face_c = S.head(pest, FREEZE)
fwd = V(-1, 0, 0)
hit = face_points(S, pest, FREEZE, fwd, lambda u, v: abs(u) < 0.012 and abs(v + 0.2) < 0.012, step=0.01)
lip = (hit[0] if hit else face_c + fwd * 0.28 + V(0, 0, -0.2)) + fwd * 0.01
S.beat(held, STACHE, "staan", face="grijns", face_amt=1.0, at=lip, mouth=0.0)
for k, t in enumerate(frange(STACHE + 0.3, l3[1] - 0.9, 0.18)):
    s_ = math.sin(k * 1.3)
    S.reach(held, t, "R", lip + V(-0.08, 0.1 * s_, 0.02 * math.cos(k)))
S.reach(held, l3[1] - 0.8, "R", None, 0.0)
S.beat(held, l3[1] - 0.8, "armen_over", face="grijns", face_amt=1.0, look=(0.3, 0), mouth=0.0)
mu = S.mat("snor", (0.05, 0.04, 0.04))
for s_ in (-1, 1):
    pts = [lip + V(-0.02, 0.0, 0.0), lip + V(-0.03, 0.06 * s_, -0.005), lip + V(-0.02, 0.11 * s_, 0.0),
           lip + V(-0.01, 0.13 * s_, 0.03), lip + V(-0.01, 0.11 * s_, 0.045)]
    o = T.tube(f"Snor_{s_}", [tuple(p) for p in pts], 0.012, mu, ol=0)
    show(o, STACHE + (0.8 if s_ < 0 else 1.6))
S.sfx("sfx_naald", STACHE + 0.3, 0.15)

# ---------------------------------------------------------------- camera (staand)
S.cam(0.0, ((-1.0, -0.55, 1.3), (0.38, 0.18, 1.1), 30), ((-0.95, -0.5, 1.28), (0.38, 0.18, 1.1), 32))
S.cam(FREEZE - 0.15, ((-4.1, -3.6, 2.5), (0.9, 0.6, 0.9), 18), ((-4.0, -3.5, 2.45), (0.9, 0.6, 0.9), 19))
S.cam(UP, ((1.5, -0.9, 1.45), (0.7, 0.4, 1.2), 26), ((1.45, -0.85, 1.42), (0.7, 0.4, 1.2), 28))
S.cam(UP + 2.1, ((-1.9, 0.0, 1.55), TEACH_FACE + V(0, 0, -0.1), 26), ((-2.1, 0.05, 1.55), TEACH_FACE + V(0, 0, -0.1), 28))
S.cam(l2[1] - 1.7, (TEACH_FACE + V(0.7, -0.5, 0.0), TEACH_FACE + V(0, 0, 0.02), 40), (TEACH_FACE + V(0.65, -0.46, 0.0), TEACH_FACE + V(0, 0, 0.02), 44))
S.cam(JUMP, ((-3.1, 1.25, 1.6), (-0.85, 0.92, 1.1), 24), ((-3.0, 1.22, 1.58), (-0.85, 0.92, 1.1), 25))
S.cam(SNACK, ((-2.75, 1.7, 1.45), (-1.6, 0.9, 1.1), 26), ((-2.7, 1.68, 1.43), (-1.6, 0.9, 1.1), 28))
S.cam(STACHE, ((0.75, 0.55, 1.3), face_c + V(0, 0.2, -0.05), 26), ((0.8, 0.55, 1.28), face_c + V(0, 0.2, -0.05), 28))
S.cam(l3[1] - 1.0, (face_c + fwd * 0.95 + V(0, 0.08, 0.05), face_c + V(0, 0, -0.08), 40), (face_c + fwd * 0.88 + V(0, 0.08, 0.05), face_c + V(0, 0, -0.08), 42))

S.done()
