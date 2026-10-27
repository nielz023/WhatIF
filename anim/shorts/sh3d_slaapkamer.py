"""SH3d · 1 jaar vooruit kijken · slaapkamer (nacht): hij kijkt een jaar vooruit. Zijn kamer is leeg, mama zit op
zijn bed met zijn foto en huilt. Terug in het nu: over een jaar ben je weg. 365 dagen.

    blender -b -P anim/shorts/sh3d_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh3", "d", "slaapkamer", "nacht", lines=(5, 6, 7, 8))
l5, l6, l7, l8 = (S.L[n] for n in (5, 6, 7, 8))
T0, END = S.t0, S.t1
BED = V(-1.52, 1.25, 0.6)
for n in ("Telefoon", "Telefoon_scherm", "Laptop"):
    o = S.obj(n)
    if o:
        o.hide_render = True
lap = S.obj("Laptop")
if lap:
    for o in lap.children_recursive:
        o.hide_render = True

VIS0, VIS1 = l6[0] - 0.4, l7[0] - 0.1          # het visioen: een jaar later
held = S.actor("hoofdpersonage", BED, 0)
SIT, _ = sit(held, seat_top=0.0, lean=-8, spread=0.12)
eye_glow(held, [(T0, 0.3), (l5[0] + 0.6, 0.6), (VIS0 - 0.1, 1.0), (VIS1, 1.0), (VIS1 + 0.8, 0.0)])
visible(held.rig, 0, True)
visible(held.rig, VIS0, False)
visible(held.rig, VIS1, True)

MOM = V(-0.92, 0.35, 0)
mama = S.actor("mama", MOM, 90, energy=0.6)
mspec, mz = sit(mama, seat_top=0.52)
S.place(mama, 0, MOM + V(0, 0, mz), 90)
show(mama.rig, VIS0, VIS1)

# de foto in een lijstje
frame_m = S.mat("fotolijst", (0.35, 0.22, 0.12))
photo = T.box("Fotolijst", (0, 0, 0), (0.2, 0.02, 0.25), frame_m, bevel=0.005, ol=0.003, base=False)
T.box("Foto_achter", (0, -0.011, 0), (0.17, 0.002, 0.22), S.mat("foto_lucht", (0.55, 0.75, 0.95)), bevel=0, ol=0,
      base=False).parent = photo
T.box("Foto_trui", (0, -0.013, -0.07), (0.1, 0.002, 0.08), S.mat("foto_trui", (0.84, 0.19, 0.03)), bevel=0, ol=0,
      base=False).parent = photo
T.cyl("Foto_hoofd", (0, -0.013, 0.02), 0.045, 0.002, S.mat("foto_huid", (0.89, 0.6, 0.42)), rot=(90, 0, 0), seg=20,
      ol=0).parent = photo
MH = S.head(mama, VIS0)
HANDS = MOM + V(0.34, 0, 0.98 + mz)
photo.location = HANDS + V(0.04, 0, 0.12)
photo.rotation_euler = (math.radians(70), 0, math.radians(-90))
show(photo, VIS0, VIS1)
tear_m = S.mat("traan", (0.6, 0.85, 1.0))
for s_ in (-1, 1):
    for k, t in enumerate(frange(l6[1] - 1.9, VIS1, 0.7)):
        tr = T.sphere(f"Traan_{s_}_{k}", (0, 0, 0), 0.014, tear_m, scale=(1, 1, 1.4), ol=0.002)
        p0 = MH + V(0.27, 0.11 * s_, -0.02)
        key(tr, t, loc=tuple(p0))
        key(tr, t + 0.65, loc=tuple(p0 + V(0.02, 0.02 * s_, -0.17)))
        show(tr, t, t + 0.65)

# ---------------------------------------------------------------- muziek, geluid, kaarten
S.music("strijkers_emo", l6[0] - 0.2, END, vol=0.2, fade_in=1.5)
S.sfx("sfx_visioen", l5[0] + 0.4, 0.5)
S.sfx("sfx_hartslag", VIS1 + 0.2, 0.35, loop_to=END)
S.sfx("sfx_cliffhanger", l7[1] - 1.6, 0.75)
S.card("", VIS0 - 0.3, VIS0 + 0.1, dim=1.0, bg=(1, 1, 1), fin=6, fout=6)
S.card("", VIS0, VIS1, dim=0.22, bg=(0.55, 0.62, 0.8), fin=0, fout=0)
S.card("", VIS1 - 0.15, VIS1 + 0.15, dim=1.0, bg=(1, 1, 1), fin=3, fout=5)
S.counter("1 YEAR", VIS0 + 0.2, VIS1, color=RED, sub="FROM NOW")
S.counter("365 DAYS", l7[1] - 1.0, None, color=RED, sub="TO FIND OUT WHY")

# ---------------------------------------------------------------- acteren
S.beat(held, T0, **SIT, pose="ontspannen", face="verbaasd", face_amt=0.6, look=(0, 0), mouth=0.1)
S.beat(held, l5[0] + 0.6, **SIT, pose="ontspannen", face="vastberaden", face_amt=0.8, look=(0, 0), mouth=0.0,
       body={"head": (-6, 0, 0)})
S.beat(held, VIS1 + 0.2, **SIT, pose="schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, 0), mouth=0.5)
S.beat(held, l7[0] + 2.0, **SIT, pose="handen_hoofd", face="bang", face_amt=1.0, look=(0, -0.3), mouth=0.3)
S.beat(held, l7[1] - 0.6, **SIT, pose="armen_over", face="bang", face_amt=1.0, look=(0, 0), mouth=0.2,
       body={"head": (4, 0, 0)})
S.hold(held, END)
S.beat(mama, VIS0, **mspec, pose="ontspannen", face="verdrietig", face_amt=1.0, at=photo.location, mouth=0.0)
S.reach(mama, VIS0, "R", HANDS + V(0, -0.1, 0))
S.reach(mama, VIS0, "L", HANDS + V(0, 0.1, 0))
S.beat(mama, l6[1] - 1.8, **mspec, pose="ontspannen", face="verdrietig", face_amt=1.0, at=photo.location, mouth=0.15,
       body={"head": (6, 0, 0), "chest": (8, 0, 0)})
for k, t in enumerate(frange(l6[1] - 1.6, VIS1, 0.35)):
    S.beat(mama, t, **mspec, pose="ontspannen", face="verdrietig", face_amt=1.0, at=photo.location, mouth=0.2,
           body={"head": (6, 0, 0), "chest": (8 + (2 if k % 2 else -2), 0, 0)})

# ---------------------------------------------------------------- camera
S.cam(T0, S.shot(held, T0 + 0.3, "mcu", az=6, lens=34, h=-0.05), S.shot(held, VIS0, "cu", az=2, lens=52, h=-0.05))
S.cam(VIS0, ((0.7, -1.5, 1.75), (-1.1, 0.6, 0.8), 20), ((0.65, -1.4, 1.72), (-1.1, 0.6, 0.8), 21))
S.cam(l6[0] + 1.6, (MH + V(1.3, -0.55, -0.45), MH + V(0.2, 0, -0.3), 28), (MH + V(1.2, -0.5, -0.45), MH + V(0.2, 0, -0.3), 30))
S.cam(l6[1] - 1.9, (MH + V(0.75, -0.25, -0.4), MH + V(0, 0, -0.08), 40), (MH + V(0.7, -0.22, -0.38), MH + V(0, 0, -0.08), 44))
S.cam(VIS1, S.shot(held, VIS1 + 0.3, "mcu", az=8, lens=32, h=-0.05), S.shot(held, l8[0], "cu", az=4, lens=46, h=-0.05),
      shake=lambda t: 0.6 * max(0, 1 - (t - VIS1) / 1.0))
S.cam(l8[0], S.shot(held, l8[0], "cu", az=3, lens=46, h=-0.05), S.shot(held, END, "cu", az=0, lens=56, h=-0.05))

S.done()
