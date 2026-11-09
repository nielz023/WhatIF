"""OR5b · What if you turned invisible? · stad (middag) + kluis, regel 3-7.

3  MINUTE 1: je loopt (als glas) over een vol zebrapad; niemand kijkt naar je.
4  HOUR 1: je wandelt de open bankkluis in, tussen de goudstaven. Je grijnst.
5  "Then... everything goes black." Zwart beeld.
6  Licht gaat dwars door je ogen: een lichtstraal schiet door je doorzichtige hoofd heen.
7  "You're invisible. And completely blind." In de kluis: jij, tastend, bang.

    python3 anim/shorts/or5b_stad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or5", "b", "stad", "middag", lines=(3, 4, 5, 6, 7))
L = S.L
T0, END = S.t0, S.t1
W = lambda n, i: L[n][0] + S.words[f"OR5-{n:02d}"][i]["s"]
S.clip = (0.05, 3000)
r3, r4, r5, r6, r7 = (L[n][0] for n in (3, 4, 5, 6, 7))

# -- jij: helemaal glas (op je ogen en mond na) --------------------------------------------------------
A0 = V(-6.4, -8.3, 0.15)
held = S.actor("hoofdpersonage", A0, 90)
full = bpy.data.objects.new("Onzichtbaar_heel", None)
T._link(full)
attach(full, held, "chest")
full.scale = (3, 3, 3)
material_spread(held, [("glas", full)])

# -- regel 3: druk zebrapad -----------------------------------------------------------------------------
S.walk(held, r3 + 0.05, L[3][1] + 0.1, [A0, V(-1.0, -8.3, 0.0), V(2.6, -8.2, 0.0)], stride=0.42, arms=0.5)
S.beat(held, r3 + 0.1, "staan", face="lach", face_amt=0.7, look=(0.5, 0.1), feet="keep")
S.beat(held, W(3, 6), "staan", face="zelfverzekerd", face_amt=0.9, look=(-0.5, 0.1), feet="keep", body={"head": (0, 0, -25)})
S.beat(held, L[3][1] + 0.1, "staan", face="grijns", face_amt=0.9, look=(0, 0.1), feet="keep")
rnd = random.Random(7)
crowd = []
for k in range(8):
    y = -9.2 + 0.4 * (k % 5)
    east = k % 2 == 0
    x0, x1 = (-6.6, 6.6) if east else (6.6, -6.6)
    off = rnd.uniform(-3.5, 3.5)
    a, b = V(x0 + (off if east else -off) * 0.5, y, 0.0), V(x1, y, 0.0)
    ex = S.extra(k, a, 90 if east else -90)
    crowd.append(ex)
    S.walk(ex, r3 - 0.3 - rnd.uniform(0, 0.6), L[3][1] + 1.0, [a, a.lerp(b, 0.75)], stride=0.45, arms=0.5)
    S.beat(ex, r3, "staan", face="neutraal", look=(rnd.uniform(-0.3, 0.3), 0.0), feet="keep")
    S.beat(ex, L[3][1], "staan", face="neutraal", look=(rnd.uniform(-0.3, 0.3), 0.0), feet="keep")
S.cam(r3, ((5.5, -10.6, 1.0), (-1.5, -8.2, 1.0), 24), ((5.2, -10.4, 1.0), (0.5, -8.2, 1.0), 26))
S.ambience("sfx_stad_dag", r3, r4, vol=0.12)
S.sfx("sfx_menigte_mompel", r3, 0.2, cut=r4)

# -- de kluis (ver weg gebouwd, gesloten ruimte) --------------------------------------------------------
KX = 300.0
K = V(KX, 0, 0)
steel = S.mat("kluis_staal", (0.32, 0.34, 0.37))
dark = S.mat("kluis_muur", (0.12, 0.13, 0.15))
gold_m = S.mat("goud", (1.0, 0.72, 0.18), 0.25)
T.box("Kluis_vloer", tuple(K + V(0, 0, -0.1)), (6, 7, 0.1), dark, bevel=0, ol=0)
T.box("Kluis_plafond", tuple(K + V(0, 0, 3.0)), (6, 7, 0.1), dark, bevel=0, ol=0)
for nm, c, s in (("l", V(-3, 0, 0), (0.15, 7, 3)), ("r", V(3, 0, 0), (0.15, 7, 3)), ("achter", V(0, 3.5, 0), (6, 0.15, 3))):
    T.box(f"Kluis_muur_{nm}", tuple(K + c), s, dark, bevel=0, ol=0)
for nm, x0, x1 in (("vl", -3, -0.9), ("vr", 0.9, 3)):
    T.box(f"Kluis_voor_{nm}", (KX + (x0 + x1) / 2, -3.5, 0), (x1 - x0, 0.6, 3), steel, bevel=0.01, ol=0)
T.box("Kluis_voor_boven", (KX, -3.5, 2.1), (1.8, 0.6, 0.9), steel, bevel=0.01, ol=0)
door = T.cyl("Kluisdeur", (0, 0, 0), 1.05, 0.45, steel, rot=(90, 0, 0), seg=40, ol=0.004)
door.location = (KX - 1.95, -4.6, 1.05)
door.rotation_euler = (math.radians(90), 0, math.radians(-70))
for k in range(8):
    a = k / 8 * 6.283
    T.cyl(f"Kluisbout_{k}", (0, 0, 0), 0.06, 0.2, steel, rot=(0, 90, 0), seg=10, ol=0).parent = door
# goudstaven op rekken
for side in (-1, 1):
    for lvl in range(3):
        T.box(f"Kluisrek_{side}_{lvl}", (KX + side * 2.5, 0.8, 0.45 + lvl * 0.7), (0.8, 4.0, 0.05), steel, bevel=0, ol=0)
        for j in range(10):
            for q in range(2):
                T.box(f"Goud_{side}_{lvl}_{j}_{q}", (KX + side * 2.5 + (q - 0.5) * 0.3, -0.9 + j * 0.38, 0.5 + lvl * 0.7),
                      (0.24, 0.12, 0.08), gold_m, bevel=0.01, ol=0)
for j in range(6):
    T.box(f"Goud_stapel_{j}", (KX + 0.4 + (j % 3) * 0.28, 2.2, 0.0 + (j // 3) * 0.09), (0.24, 0.12, 0.08), gold_m, bevel=0.01, ol=0)
T.area_light("Kluis_licht", (KX, 0.5, 2.9), (KX, 0.5, 0), size=(3, 4), color=(1.0, 0.85, 0.65), energy=160)
T.point_light("Kluis_goudgloed_l", (KX - 2.0, 0.8, 1.2), color=(1.0, 0.75, 0.3), energy=40, radius=0.3)
T.point_light("Kluis_goudgloed_r", (KX + 2.0, 0.8, 1.2), color=(1.0, 0.75, 0.3), energy=40, radius=0.3)

# regel 4: je wandelt naar binnen
IN0, IN1 = V(KX - 0.2, -5.2, 0), V(KX + 0.1, 0.6, 0)
S.teleport(held, r4, IN0, 180)
S.walk(held, r4 + 0.05, L[4][1] - 0.2, [IN0, V(KX, -3.0, 0), IN1], stride=0.45, arms=0.55)
S.beat(held, r4 + 0.1, "staan", face="grijns", face_amt=0.9, look=(0.3, 0.2), feet="keep")
S.beat(held, W(4, 7), "staan", face="lach", face_amt=1.0, look=(-0.4, 0.2), feet="keep", body={"head": (0, 0, 20)})
S.beat(held, L[4][1] - 0.2, "juichen", amount=0.6, face="lach", face_amt=1.0, look=(0, 0.3))
S.beat(held, r5 + 0.6, "juichen", amount=0.6, face="lach", face_amt=1.0, look=(0, 0.3))
S.cam(r4, ((KX + 1.3, 2.6, 1.3), (KX - 0.3, -3.6, 0.9), 22), ((KX + 1.1, 2.4, 1.25), (KX, -1.0, 0.95), 24))
S.sfx("sfx_kluisje", r4 + 0.2, 0.3)
S.sfx("sfx_diamant", W(4, 7), 0.25)

# regel 5: alles wordt zwart
BLACK = W(5, 3) + 0.15
S.cam(r5, ((KX + 0.9, 2.0, 1.25), (KX + 0.05, 0.5, 1.1), 26), ((KX + 0.8, 1.8, 1.25), (KX + 0.05, 0.5, 1.15), 30))
S.beat(held, W(5, 1), "staan", face="verbaasd", face_amt=0.8, look=(0, 0.2))
S.card("", BLACK, r6 - 0.02, dim=1.0, bg=(0, 0, 0), fin=1, fout=1)
S.sfx("sfx_stroom_thunk", BLACK, 0.35)
S.sfx("sfx_hartslag", BLACK, 0.3, cut=END)

# regel 6: licht schiet door je ogen heen (doorsnede in profiel)
HEAD = S.head(held, r6)
beam_m = S.mat("lichtstraal", (1.0, 0.95, 0.75), 12.0)
beams = []
for k, dz in enumerate((0.05, 0.0, -0.05)):
    b = T.cyl(f"Lichtstraal_{k}", (0, 0, 0), 0.016, 3.2, beam_m, rot=(-90, 0, 0), seg=8, ol=0)
    b.location = HEAD + V(0.0, -1.6, dz + 0.02)
    key(b, 0.0, scale=(1, 1, 0.001))
    key(b, W(6, 1) - 0.02 + 0.06 * k, scale=(1, 1, 0.001))
    key(b, W(6, 3) + 0.06 * k, scale=(1, 1, 1))
    beams.append(b)
S.beat(held, r6 - 0.02, "staan", face="neutraal", look=(0, 0.0))
S.beat(held, r6 + 0.1, "staan", face="neutraal", look=(0, 0.0))
S.cam(r6, ((HEAD.x + 1.1, HEAD.y + 1.0, HEAD.z + 0.08), (HEAD.x, HEAD.y + 0.05, HEAD.z), 30),
      ((HEAD.x + 0.95, HEAD.y + 0.85, HEAD.z + 0.08), (HEAD.x, HEAD.y + 0.05, HEAD.z), 34))
S.sfx("sfx_hologram", W(6, 1), 0.3)

# regel 7: tastend in de kluis
for b in beams:
    visible(b, 0.0, True)
    visible(b, r7, False)
S.beat(held, r7, "staan", face="bang", face_amt=0.9, look=(0.5, 0.0), body={"head": (0, 0, 20)})
S.reach(held, r7, "L", None, 0.0)
S.reach(held, r7, "R", None, 0.0)
FR = HEAD + V(0, 0.55, -0.3)
S.reach(held, r7 + 0.4, "L", FR + V(0.25, 0, 0.05))
S.reach(held, r7 + 0.4, "R", FR + V(-0.25, 0, 0.0))
S.reach(held, W(7, 2) + 0.2, "L", FR + V(0.3, 0.05, -0.05))
S.reach(held, W(7, 2) + 0.2, "R", FR + V(-0.2, 0.08, 0.08))
S.reach(held, END, "L", FR + V(0.25, 0.1, 0.0))
S.reach(held, END, "R", FR + V(-0.3, 0.05, 0.05))
S.beat(held, W(7, 3), "staan", face="bang", face_amt=1.0, look=(-0.6, 0.0), body={"head": (0, 0, -25)})
S.beat(held, END, "staan", face="bang", face_amt=1.0, look=(0.6, 0.0), body={"head": (0, 0, 20)})
S.cam(r7, ((KX - 0.9, 2.3, 1.5), (KX + 0.1, 0.6, 1.1), 24), ((KX - 0.7, 2.0, 1.45), (KX + 0.1, 0.6, 1.15), 28))

S.counter("MINUTE 1", r3, L[3][1])
S.counter("HOUR 1", r4, L[4][1])
S.done()
