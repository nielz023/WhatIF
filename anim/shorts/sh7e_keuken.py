"""SH7e · teleport-kopieën · keuken: thuis zit hij al aan tafel te ontbijten. Elke sprong laat een kopie achter...
en de keuken loopt vol.

    blender -b -P anim/shorts/sh7e_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh7", "e", "keuken", "ochtend", lines=(3, 4), t0=9.5)
l3, l4 = S.L[3], S.L[4]
T0, END = S.t0, S.t1
for n in ("Krant", "Stoel_1", "Stoel_2", "Ontbijt_broertje", "Ontbijt_bord"):
    o = S.obj(n)
    if o:
        o.hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Krant_kolom"):
        o.hide_render = True
for n, dx in (("Cornflakes_doos", -0.95), ("Cornflakes_label", -0.95), ("Melkpak", -0.6), ("Melkpak_band", -0.6)):
    S.obj(n).location.x += dx

TZ = 0.76
SEAT = V(0.58, 0.02, 0)
BOWL = V(0.58, -0.36, TZ)
HP = V(1.45, -0.75, 0)
held = S.actor("hoofdpersonage", HP, 135)
kopie = S.actor("hoofdpersonage", SEAT, 0, label="kopie_ontbijt")
SIT, zs = sit(kopie)
S.place(kopie, 0, (SEAT.x, SEAT.y, zs), 0)
bowl = T.cyl("Kom", tuple(BOWL), 0.055, 0.07, S.mat("kom", (0.25, 0.55, 0.9)), r2=0.085, seg=32, ol=0.004, cap=False)
T.cyl("Kom_bodem", tuple(BOWL + V(0, 0, 0.002)), 0.054, 0.004, S.mat("kom", (0.25, 0.55, 0.9)), seg=32, ol=0)
T.cyl("Melk", tuple(BOWL + V(0, 0, 0.055)), 0.078, 0.004, S.mat("melk", (0.97, 0.97, 0.94)), seg=32, ol=0)
spoon = T.box("Lepel", (0, 0, 0), (0.02, 0.15, 0.006), P.m("metaal"), bevel=0.003, ol=0.002)

tele_fx(S, HP, T0 + 0.1)
S.counter("COPIES: 2", l3[1] - 1.6, l4[0] + 1.6, color=(0.6, 0.85, 1.0, 1))
S.counter("COPIES: 9", l4[0] + 1.6, l4[1] - 1.2, color=(0.6, 0.85, 1.0, 1))
S.counter("COPIES: 47", l4[1] - 1.2, None, color=RED)
S.sfx("sfx_naald", l3[1] - 2.0, 0.2)

# hij komt binnen, de kopie eet gewoon door
S.beat(held, T0, "staan", face="blij", face_amt=0.7, look=(0, 0), mouth=0.0)
S.beat(held, l3[0] + 1.4, "schrik", amount=0.9, face="geschrokken", face_amt=1.0, at=S.head(kopie, 0.0), mouth=0.6)
S.beat(held, l3[1] - 0.8, "staan", face="verbaasd", face_amt=1.0, at=S.head(kopie, 0.0), mouth=0.3)
S.beat(kopie, 0.0, **SIT, pose="ontspannen", face="blij", face_amt=0.4, at=BOWL + V(0, 0, 0.05))
grab(S, spoon, kopie, 0.0, "hand.R", mode="full", offset=(0, 0.05, 0))
for k, t in enumerate(frange(T0, l3[0] + 2.0, 0.5)):
    S.reach(kopie, t, "R", BOWL + V(0.04, -0.02, 0.1) if k % 2 == 0 else S.head(kopie, 0.0) + V(0.06, -0.22, -0.14))
S.beat(kopie, l3[0] + 2.2, **SIT, pose="ontspannen", face="neutraal", face_amt=0.6, at=S.head(held, T0), mouth=0.0)
S.reach(kopie, l3[0] + 2.2, "R", S.head(kopie, 0.0) + V(0.12, -0.3, -0.2))
S.beat(kopie, l3[1] - 0.6, **SIT, pose="ontspannen", face="grijns", face_amt=0.6, at=S.head(held, T0), mouth=0.0)

# elke sprong een kopie: ze ploppen overal in de keuken op
SPOTS = [(V(-1.8, 0.95, 0), 90), (V(1.85, 0.75, 0), 220), (V(-0.9, 1.3, 0), 160), (V(-1.5, -1.3, 0), 45),
         (V(0.2, 1.25, 0), 180), (V(-0.35, -1.5, 0), 20), (V(1.95, -0.15, 0), 250)]
rnd = random.Random(2)
for k, (p, rot) in enumerate(SPOTS):
    c = S.actor("hoofdpersonage", p, rot, label=f"kopie_{k}")
    t = l4[0] + 0.4 + k * 0.45
    show(c.rig, t)
    tele_fx(S, p, t, sound=(k % 2 == 0), vol=0.22)
    S.beat(c, t, ("staan", "juichen", "zwaaien_a", "wijzen", "armen_over", "vuisten", "schouders_op")[k],
           face=("blij", "lach", "grijns", "verbaasd")[k % 4], face_amt=0.8, at=V(1.0, -0.2, 1.2))
    S.beat(c, l4[1] - 0.3, "staan", face="neutraal", face_amt=0.5, at=S.head(held, T0))
S.beat(held, l4[0] + 0.6, "handen_hoofd", face="geschrokken", face_amt=1.0, look=(0.6, 0.3), mouth=0.5)
S.beat(held, l4[1] - 0.6, "schrik", amount=0.8, face="bang", face_amt=1.0, look=(-0.6, 0.2), mouth=0.3)
S.hold(held, END)
show(held.rig, 0)

S.cam(T0, ((2.0, -1.6, 1.45), (0.7, 0.0, 0.95), 24), ((1.9, -1.5, 1.42), (0.7, 0.0, 0.95), 26))
S.cam(l3[0] + 1.3, S.shot(held, l3[0] + 1.5, "mcu", az=-20, lens=34), S.shot(held, l3[0] + 2.4, "mcu", az=-16, lens=36))
S.cam(l3[0] + 2.5, S.shot(kopie, l3[0] + 2.6, "mcu", az=10, lens=34), S.shot(kopie, l3[1], "mcu", az=6, lens=38))
S.cam(l4[0], ((2.2, -2.0, 2.1), (-0.2, 0.3, 0.9), 18), ((2.1, -1.9, 2.15), (-0.2, 0.3, 0.9), 19))
S.cam(l4[1] - 1.0, S.shot(held, l4[1] - 0.8, "mcu", az=-25, lens=34), S.shot(held, END, "mcu", az=-20, lens=38))
S.done()
