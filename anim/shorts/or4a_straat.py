"""OR4a · What if gravity switched off for one second? · woonstraat (zonnig), één deel.

1  hook: de hele straat zweeft al: auto's, bomen, mensen en jij, langzaam omhoog.
2  0.1 s: je voeten komen los van de stoep.
3  0.4 s: het water klimt in bolletjes uit je glas.
4  0.7 s: auto's, bomen, mensen... alles drijft omhoog.
5  0.9 s: je hangt hoog boven de daken; de straat ligt ver onder je.
6  "And then... gravity comes back." Je valt.

    python3 anim/shorts/or4a_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or4", "a", "straat", "zonnig", lines=(1, 2, 3, 4, 5, 6))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR4-{n:02d}"][i]["s"]
S.clip = (0.05, 3000)
r2, r3, r4, r5, r6 = (L[n][0] for n in (2, 3, 4, 5, 6))
HIGH = 40.0


def ease(u, p=1.7):
    return max(0.0, min(1.0, u)) ** p


# -- jij, met een glas water ---------------------------------------------------------------------------
P = V(-4.0, 7.2, 0.12)
held = S.actor("hoofdpersonage", P, 0)            # kijkt naar -y, de straat in
HOLD = P + V(0.24, -0.3, 0.74)
glass = T.cyl("Waterglas", tuple(HOLD + V(0, 0, 0.02)), 0.04, 0.12, T.glass("glas_or4", (0.85, 0.93, 1.0), alpha=0.25), seg=20, ol=0.002)
water_m = S.mat("water_or4", (0.35, 0.65, 1.0), 0.4)
water = T.cyl("Water_in_glas", (0, 0, 0.005), 0.036, 0.085, water_m, seg=20, ol=0)
water.parent = glass
water.location = (0, 0, 0.005)
S.reach(held, 0.0, "R", HOLD)
attach_keep(glass, held, "hand.R", 0.0)


def hero_z(t):
    """Hoogte van je voeten boven de stoep (regel 2-4); daarna hoog in de lucht."""
    if t < r2 + 0.9:
        return 0.0
    if t < r3:
        return 0.3 * ease((t - r2 - 0.9) / (r3 - r2 - 0.9), 1.4)
    if t < r4:
        return 0.3 + 0.6 * (t - r3) / (r4 - r3)
    if t < r5:
        return 0.9 + 3.2 * ease((t - r4) / (r5 - r4), 1.3)
    return 0.0


for t in frange(r2, r5 - 0.02, 0.1):
    S.place(held, t, P + V(0, 0, hero_z(t)), 0)
S.place(held, r5 - 0.01, P + V(0, 0, 4.1), 0)
# hoog in de lucht; bij "back" val je
fall0 = W(6, 4) + 0.05
S.teleport(held, r5, P + V(0, 0, HIGH), 0)
for t in frange(r5, fall0, 0.2):
    S.place(held, t, P + V(0, 0, HIGH + 1.2 * (t - r5) / (fall0 - r5)), 0)
for t in frange(fall0, END + 0.1, 0.05):
    dt = t - fall0
    S.place(held, t, P + V(0, 0, HIGH + 1.2 - 0.5 * 9.81 * dt * dt), 0)

# acteren
S.beat(held, r2, "staan", face="neutraal", look=(0, -0.3), body={"head": (10, 0, 0)})
S.beat(held, r2 + 0.9, "staan", face="verbaasd", face_amt=0.7, look=(0, -0.9), body={"head": (25, 0, 0)})
S.beat(held, r3 - 0.1, "schrap", amount=0.5, face="verbaasd", face_amt=1.0, look=(0, -0.9), body={"head": (25, 0, 0)})
S.reach(held, r3 - 0.1, "R", HOLD + V(0, 0, hero_z(r3 - 0.1)))
S.beat(held, W(3, 4), "staan", face="verbaasd", face_amt=1.0, look=(0, -0.4), body={"head": (18, 0, 0)})
for t in frange(r3, r4, 0.25):
    S.reach(held, t, "R", HOLD + V(0, 0, hero_z(t)))
S.reach(held, r4 - 0.05, "R", HOLD + V(0, 0, hero_z(r4 - 0.05)))
S.reach(held, r4 + 0.3, "R", None, 0.0)
S.beat(held, r4 + 0.3, "schrik", face="geschrokken", face_amt=0.9, look=(0.4, 0.2), body={"spine": (-6, 0, 8)})
S.beat(held, W(4, 6), "armen_omhoog", amount=0.7, face="bang", face_amt=0.9, look=(-0.4, 0.2), body={"spine": (-8, 0, -8)})
S.beat(held, r5, "handen_zij", face="bang", face_amt=0.8, look=(0, -0.9), body={"head": (28, 0, 0), "spine": (12, 0, 0)})
S.beat(held, W(5, 5), "handen_zij", face="bang", face_amt=1.0, look=(0, -1.0), body={"head": (32, 0, 0), "spine": (14, 0, 0)})
S.beat(held, fall0, "schrik", face="schreeuw", face_amt=1.0, look=(0, -1.0), body={"head": (-10, 0, 0), "spine": (-14, 0, 0)})
S.beat(held, END, "armen_omhoog", face="schreeuw", face_amt=1.0, look=(0, -1.0), body={"head": (-12, 0, 0)})
visible(glass, r4 + 0.25, False)

# -- het water klimt uit je glas (bolletjes, aan het glas gehangen) ------------------------------------
rnd = random.Random(4)
for k in range(9):
    b = T.sphere(f"Waterbol_{k}", (0, 0, 0), 1.0, water_m, seg=16, ol=0.0)
    b.parent = glass
    t0 = W(3, 4) - 0.1 + k * 0.07
    x, y = rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02)
    r = rnd.uniform(0.012, 0.026)
    key(b, 0.0, loc=(x, y, 0.07), scale=0.001)
    key(b, t0, loc=(x, y, 0.07), scale=0.001)
    key(b, t0 + 0.15, loc=(x, y, 0.1), scale=r)
    key(b, r4 + 0.2, loc=(x * 4 + rnd.uniform(-0.05, 0.05), y * 4 + rnd.uniform(-0.05, 0.05), 0.16 + 0.35 * rnd.random()), scale=r * 1.1)
key(water, 0.0, scale=(1, 1, 1))
key(water, W(3, 4) - 0.1, scale=(1, 1, 1))
key(water, r4, scale=(1, 1, 0.08))
S.sfx("sfx_naald", W(3, 4) - 0.1, 0.2)

# -- auto's, bomen, mensen drijven omhoog --------------------------------------------------------------
FLOAT = []


def drift(obj, t0, t1, h, spin, seed):
    rr = random.Random(seed)
    p0 = obj.location.copy()
    r0 = V(*obj.rotation_euler)
    sp = V(rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1)) * spin
    for t in frange(t0, t1 + 0.01, 0.2):
        u = (t - t0) / (t1 - t0)
        e = ease(u, 1.6)
        rot = tuple(math.degrees(r0[i]) + sp[i] * e for i in range(3))
        key(obj, t, loc=tuple(p0 + V(0, 0, h * e)), rot=rot)
    FLOAT.append(obj)


L4A, L6B = r2 + 0.9, fall0
names = [("Auto_geparkeerd_2", 3.5, 25), ("Auto_overkant_2", 4.5, 35), ("Auto_geparkeerd_3", 3.0, 20),
         ("Auto_overkant_1", 4.0, 30), ("Straatboom_-3_-5.4", 2.5, 15), ("Straatboom_-13_-5.4", 3.0, 18),
         ("Straatboom_-13_7.9", 2.2, 12), ("Lantaarn_z_0", 1.2, 25)]
for k, (nm, h, sp) in enumerate(names):
    o = S.obj(nm)
    if o:
        drift(o, L4A, L6B, h * 1.6, sp, k)
people = []
for k, (loc, rot) in enumerate((((-9.0, -4.6, 0.12), 20), ((1.5, -4.8, 0.12), -30), ((-12.0, 7.0, 0.12), 160))):
    ex = S.extra(k + 2, loc, rot)
    people.append(ex)
    S.beat(ex, 0.0, "staan", face="neutraal")
    S.beat(ex, r4 + 0.2, "schrik", face="geschrokken", face_amt=1.0, body={"spine": (-10, 0, 0)})
    S.beat(ex, END, "armen_omhoog", face="schreeuw", face_amt=1.0)
    for t in frange(L4A, L6B + 0.01, 0.2):
        u = (t - L4A) / (L6B - L4A)
        S.place(ex, t, V(*loc) + V(0, 0, 4.5 * ease(u, 1.6)), rot + 40 * u * (1 if k % 2 else -1))

# -- hook: de zwevende straat (kopie van het eind van regel 4) -----------------------------------------
copy_anim([held.rig] + FLOAT + [p.rig for p in people], r4 + 0.5, L[4][1], 0.0, L[1][1])
S.reach(held, 0.0, "R", None, 0.0)
S.face(held, 0.0, "bang", 0.9, look=(0.3, 0.2))
S.face(held, L[1][1], "bang", 1.0, look=(-0.3, 0.2))
visible(glass, 0.0, False)
visible(glass, r2, True)
S.place(held, r2 - 0.01, P + V(0, 0, 4.0), 0)
S.place(held, r2, P, 0)

# -- tellers, geluid -----------------------------------------------------------------------------------
S.counter("0.1 s", r2, L[2][1], sub="GRAVITY: OFF")
S.counter("0.4 s", r3, L[3][1])
S.counter("0.7 s", r4, L[4][1])
S.counter("0.9 s", r5, L[5][1])
S.counter("1.0 s", r6, END, color=RED, sub="GRAVITY: ON")
S.ambience("sfx_wind_hoog", 0.0, END, vol=0.08)
S.music_all("m_twist", vol=0.22)
S.sfx("sfx_slowmo", r2 + 0.8, 0.3)
S.sfx("sfx_zand_opstijgen", r4 + 0.3, 0.25)
S.sfx("sfx_wind_hoog", r5, 0.25, cut=END)
S.sfx("sfx_dreun", fall0 - 0.05, 0.45)
S.sfx("sfx_vrije_val", fall0, 0.4, cut=END)

# -- camera's ------------------------------------------------------------------------------------------
S.cam(0.0, ((-4.5, -9.0, 1.0), (-4.5, 4.0, 5.5), 18), ((-4.5, -8.4, 1.4), (-4.5, 4.0, 6.0), 19))
# voeten die loskomen (laag), dan het glas
S.cam(r2, ((P.x + 0.9, P.y - 1.6, 0.25), (P.x, P.y, 0.35), 24), ((P.x + 0.85, P.y - 1.5, 0.3), (P.x, P.y, 0.45), 26))
S.cam(r3, ((P.x + 0.7, P.y - 1.15, 1.1 + 0.3), tuple(HOLD + V(0, 0, 0.35 + 0.15)), 26),
      ((P.x + 0.7, P.y - 1.15, 1.1 + 0.9), tuple(HOLD + V(0, 0, 0.9 + 0.15)), 28))
S.cam(r4, ((-4.5, -9.5, 1.0), (-4.5, 4.0, 3.0), 18), ((-4.5, -9.0, 2.6), (-4.5, 4.0, 5.5), 18))
# hoog: boven en achter je, de straat ver beneden
S.cam(r5, ((P.x + 1.2, P.y + 3.2, HIGH + 3.6), (P.x - 0.6, P.y - 4.0, 0.0), 24),
      ((P.x + 1.0, P.y + 2.8, HIGH + 3.9), (P.x - 0.6, P.y - 4.0, 0.0), 26))
S.cam(r6, ((P.x + 1.0, P.y + 2.8, HIGH + 3.9), (P.x - 0.6, P.y - 4.0, 0.0), 26),
      ((P.x + 0.9, P.y + 2.6, HIGH + 4.2), (P.x - 0.6, P.y - 4.0, 0.0), 28))
S.done()
