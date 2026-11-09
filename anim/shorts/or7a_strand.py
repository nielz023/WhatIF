"""OR7a · What if the Moon came twice as close? · strand 's nachts, één deel.

Wetenschap: op de helft van de afstand lijkt de maan 2x zo breed (4x zoveel oppervlak) en trekt hij 2^3 = 8x zo hard
aan de oceanen (getijdekracht ~ 1/d^3).

1  hook: jij op het strand; de maan boven zee zwelt op tot een reus.
2  HOUR 1: hij vult de lucht. Vier keer groter.
3  HOUR 6: het water stijgt (8x hogere getijden); de kust verdwijnt, jij loopt achteruit, het water tot je knieën.
4  DAY 2: vanaf de boulevard: aan de horizon barsten vulkanen uit (lavagloed, rook).
5  DAY 3: close, je kijkt omhoog...
6  ...en de maan komt nog steeds dichterbij.

    python3 anim/shorts/or7a_strand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or7", "a", "strand", "nacht", lines=(1, 2, 3, 4, 5, 6))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR7-{n:02d}"][i]["s"]
S.clip = (0.05, 5000)
r2, r3, r4, r5, r6 = (L[n][0] for n in (2, 3, 4, 5, 6))
for nm in ("Bord_NO_SWIMMING",):
    o = S.obj(nm)
    if o:
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# -- de maan ---------------------------------------------------------------------------------------------
P = V(2.0, -12.0, 0)
EYE = P + V(0, 0, 1.4)
D = 1200.0
DIR = V(0, -math.cos(math.radians(22)), math.sin(math.radians(22)))
MC = EYE + DIR * D
moon_m = S.mat("maan", (0.92, 0.92, 0.88), 1.6)
crater_m = S.mat("maan_krater", (0.62, 0.62, 0.62), 1.1)
moon = T.sphere("Maan", (0, 0, 0), 1.0, moon_m, seg=48, ol=0.0)
moon.location = MC
rnd = random.Random(3)
for k in range(16):
    a, b = rnd.uniform(0, 6.283), rnd.uniform(0.0, 0.85)
    off = V(math.cos(a) * b, 0, math.sin(a) * b)
    c = T.sphere(f"Maankrater_{k}", (0, 0, 0), rnd.uniform(0.06, 0.2), crater_m, scale=(1, 0.25, 1), seg=16, ol=0.0)
    c.parent = moon
    c.location = off + V(0, math.sqrt(max(0.0, 1 - b * b)) * 0.98, 0)        # op de kant naar jou (+y)
for o in [moon] + list(moon.children):
    o.visible_shadow = False


def moon_r(deg):
    return D * math.tan(math.radians(deg))


for t, deg in ((0.0, 1.0), (0.4, 1.2), (L[1][1], 11.0), (r3, 11.4), (r6, 12.0), (W(6, 5), 20.0), (END, 32.0)):
    key(moon, t, scale=moon_r(deg))
gl = T.point_light("Maangloed", tuple(EYE + DIR * 60), color=(0.75, 0.82, 1.0), energy=0, radius=5)
for t, e in ((0.0, 0), (END, 0)):
    gl.data.energy = e
    gl.data.keyframe_insert("energy", frame=F(t))

# -- het water stijgt ------------------------------------------------------------------------------------
flood = T.plane("Vloed", (0, -100, 0), (900, 270), T.toon("water_vloed", (0.04, 0.38, 0.62)))
key(flood, 0.0, loc=(0, -100, -0.3))
key(flood, W(3, 4) - 0.3, loc=(0, -100, -0.3))
key(flood, r4, loc=(0, -100, 0.75))
key(flood, END, loc=(0, -100, 1.1))
for nm in ("Branding",):
    o = S.obj(nm)
    if o:
        visible(o, W(3, 4), False)

# -- vulkanen aan de horizon -----------------------------------------------------------------------------
rock = S.mat("vulkaan_steen", (0.12, 0.1, 0.1))
lava = S.mat("lava", (1.0, 0.35, 0.05), 10.0)
VOLC = []
for k, (x, y, h, r) in enumerate(((-300, -900, 260, 300), (150, -1150, 340, 360), (520, -900, 220, 260), (-700, -1050, 280, 320))):
    cone = T.cyl(f"Vulkaan_{k}", (x, y, -5), r, h, rock, r2=r * 0.12, seg=24, ol=0)
    top = T.cyl(f"Vulkaan_lava_{k}", (x, y, h - 6), r * 0.13, 8, lava, r2=r * 0.08, seg=16, ol=0)
    VOLC.append((cone, top, V(x, y, h)))
    for o in (cone, top):
        show(o, r4)
    for j in range(3):
        st = T.box(f"Lavastroom_{k}_{j}", (x + (j - 1) * r * 0.12, y + r * 0.35, h * 0.45), (6, 2, h * 0.55), lava, rot=(28, (j - 1) * 14, 0), bevel=0, ol=0)
        show(st, r4 + 0.3 + 0.2 * j)
    for t in frange(r4 + 0.1 + 0.15 * k, END, 0.5):
        S.puff(V(x, y, h + 10), t, n=4, r=(30, 55), grow=2.0, dur=2.6, color=(0.1, 0.08, 0.08), rise=160, spread=60)
    T.point_light(f"Lavagloed_{k}", (x, y, h + 40), color=(1.0, 0.35, 0.08), energy=0, radius=20)
for k in range(4):
    lg = S.obj(f"Lavagloed_{k}")
    for t, e in ((0, 0), (r4 - 0.02, 0), (r4 + 0.3, 2.5e6), (END, 2.5e6)):
        lg.data.energy = e
        lg.data.keyframe_insert("energy", frame=F(t))

# -- jij -------------------------------------------------------------------------------------------------
held = S.actor("hoofdpersonage", P, 0)            # kijkt naar zee (-y)
S.beat(held, 0.0, "staan", face="verbaasd", face_amt=0.7, look=(0, 0.8), body={"head": (-18, 0, 0)})
S.beat(held, L[1][1], "staan", face="geschrokken", face_amt=0.9, look=(0, 0.9), body={"head": (-22, 0, 0)})
S.beat(held, W(2, 3), "staan", face="verbaasd", face_amt=1.0, look=(0, 1.0), body={"head": (-28, 0, 0), "spine": (-6, 0, 0)})
S.beat(held, L[2][1], "staan", face="verbaasd", face_amt=1.0, look=(0, 1.0), body={"head": (-28, 0, 0), "spine": (-6, 0, 0)})
# regel 3: het water komt; achteruit
B1 = P + V(0.2, 5.0, 0)
S.beat(held, r3, "staan", face="nerveus", face_amt=0.8, look=(0, -0.3), body={"head": (10, 0, 0)})
S.walk(held, W(3, 4), L[3][1] - 0.1, [P, B1], stride=0.32, turn=False, arms=0.45)
S.beat(held, W(3, 9), "schrik", face="bang", face_amt=1.0, look=(0, -0.6), feet="keep", body={"head": (14, 0, 0)})
S.beat(held, L[3][1] - 0.1, "schrik", face="bang", face_amt=1.0, look=(0, -0.6), feet="keep", body={"head": (14, 0, 0)})
# regel 4-6: op de boulevard
BV = V(2.0, 37.0, 1.6)
S.teleport(held, r4, BV, 0)
S.beat(held, r4, "staan", face="bang", face_amt=0.9, look=(0.3, 0.2), body={"head": (-4, 0, 0)})
S.beat(held, W(4, 3), "handen_hoofd", amount=0.7, face="geschrokken", face_amt=1.0, look=(-0.3, 0.2), body={"head": (-4, 0, -10)})
S.beat(held, L[4][1], "handen_hoofd", amount=0.7, face="geschrokken", face_amt=1.0, look=(0.3, 0.2), body={"head": (-4, 0, 8)})
S.beat(held, r5, "staan", face="nerveus", face_amt=0.8, look=(0, -0.2), body={"head": (6, 0, 0)})
S.beat(held, W(5, 4), "staan", face="verbaasd", face_amt=0.9, look=(0, 1.0), body={"head": (-30, 0, 0), "spine": (-6, 0, 0)})
S.beat(held, r6 + 0.4, "schrik", face="bang", face_amt=1.0, look=(0, 1.0), body={"head": (-32, 0, 0), "spine": (-8, 0, 0)})
S.beat(held, END, "schrik", face="bang", face_amt=1.0, look=(0, 1.0), body={"head": (-34, 0, 0), "spine": (-8, 0, 0)})

# -- tellers, geluid -------------------------------------------------------------------------------------
S.counter("HOUR 1", r2, L[2][1], sub="4x BIGGER")
S.counter("HOUR 6", r3, L[3][1], sub="TIDES 8x")
S.counter("DAY 2", r4, L[4][1])
S.counter("DAY 3", r5, END, color=RED)
S.music_all("m_twist", vol=0.22)
S.ambience("sfx_strand_sfeer", 0.0, r4, vol=0.1)
S.sfx("sfx_riser", 0.0, 0.3, cut=L[1][1] + 0.3)
S.sfx("sfx_zon_gebrul", r2 + 0.5, 0.2, cut=L[2][1])
S.sfx("sfx_wind_hoog", r3, 0.2, cut=r4)
S.sfx("sfx_aardbeving", r4, 0.3, cut=L[4][1] + 0.3)
S.sfx("sfx_inslag", r4 + 0.1, 0.35)
S.sfx("sfx_hartslag", r5, 0.3, cut=END)
S.sfx("sfx_aardbeving", r6, 0.3, cut=END)

# -- camera's --------------------------------------------------------------------------------------------
HOOKC = ((P.x + 1.6, P.y + 5.5, 0.5), tuple(EYE + DIR * 40 + V(0, 0, -8)), 22)
S.cam(0.0, HOOKC, ((P.x + 1.5, P.y + 5.2, 0.55), tuple(EYE + DIR * 40 + V(0, 0, -6)), 24))
HB = S.head(held, 0.0)
S.cam(r2, ((HB.x + 0.6, HB.y - 1.4, HB.z - 0.55), tuple(HB + V(0, 0, 0.05)), 26), ((HB.x + 0.5, HB.y - 1.2, HB.z - 0.5), tuple(HB + V(0, 0, 0.05)), 28))
S.cam(W(2, 6) - 0.1, ((P.x - 1.2, P.y + 6.5, 0.35), tuple(EYE + DIR * 40 + V(0, 0, -4)), 18), ((P.x - 1.1, P.y + 6.2, 0.4), tuple(EYE + DIR * 40 + V(0, 0, -3)), 19))
S.cam(r3, ((P.x + 2.2, P.y + 6.0, 1.3), (P.x, P.y + 1.0, 0.5), 22), ((P.x + 2.0, P.y + 7.5, 1.3), (P.x + 0.2, P.y + 3.0, 0.6), 22))
S.cam(r4, ((BV.x + 1.0, BV.y + 3.0, BV.z + 1.3), (BV.x - 40, BV.y - 900, 140), 20), ((BV.x + 0.9, BV.y + 2.7, BV.z + 1.25), (BV.x - 40, BV.y - 900, 130), 22))
HV = S.head(held, r5)
S.cam(r5, ((HV.x + 0.35, HV.y - 0.9, HV.z - 0.45), tuple(HV + V(0, 0, 0.05)), 28), ((HV.x + 0.3, HV.y - 0.8, HV.z - 0.45), tuple(HV + V(0, 0, 0.05)), 32))
S.cam(r6, ((BV.x + 1.2, BV.y + 2.6, BV.z + 0.3), tuple(EYE + DIR * 40 + V(0, 0, 4)), 17), ((BV.x + 1.1, BV.y + 2.3, BV.z + 0.3), tuple(EYE + DIR * 40 + V(0, 0, 6)), 16))
S.done()
