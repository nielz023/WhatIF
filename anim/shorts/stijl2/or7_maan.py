"""OR7 · What if the Moon came twice as close? · nieuwe stijl: zonnig-speelgoedstrand 's nachts met boulevard.

Wetenschap: op de helft van de afstand lijkt de maan 2x zo breed (4x zoveel oppervlak) en trekt hij 2^3 = 8x zo hard
aan de oceanen (getijdekracht ~ 1/d^3).

1  hook: jij op het strand; de maan boven zee zwelt op tot een reus.
2  HOUR 1: hij vult de lucht. Vier keer groter. Close: jij kijkt met open mond omhoog.
3  HOUR 6: het water stijgt (8x hogere getijden); jij loopt achteruit, het water tot je knieën.
4  DAY 2: vanaf de boulevard: aan de horizon barsten vulkanen uit (lavagloed, rook).
5  DAY 3: close, je kijkt omhoog...
6  ...en de maan komt nog steeds dichterbij.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or7")
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W
r2, r3, r4, r5, r6 = (r(n) for n in (2, 3, 4, 5, 6))

# ------------------------------------------------------------------------------------------------ strand, zee, boulevard
sand = mat("Zand", (240, 212, 150), rough=0.85, coat=0, sheen=0.3)
sea_m = mat("Zee", (30, 120, 190), rough=0.06, coat=0.9)
stone = mat("Boulevardsteen", (215, 200, 180), rough=0.6, coat=0.2)
tiles = tile_mat("Boulevardtegels", (205, 190, 170), (225, 212, 192), axis="z", scale=3.0)
rail_m = mat("Reling", (245, 245, 250), rough=0.3, coat=0.6)

ground("Strand", (0, 2.0, 0.0), (140, 20), sand)                       # y -8 .. 12
sea = ground("Zee", (0, -400, -0.12), (3000, 3000), sea_m)
# zachte zandheuveltjes en schelpjes
rnd = random.Random(7)
for k in range(14):
    ball(f"Duintje_{k}", (rnd.uniform(-30, 30), rnd.uniform(-4, 10), -0.25), 1.0, sand,
         scale=(rnd.uniform(1.2, 2.6), rnd.uniform(0.9, 1.8), 0.4))
for k in range(10):
    ball(f"Schelp_{k}", (rnd.uniform(-6, 6), rnd.uniform(-5, 4), 0.01), 0.06,
         mat(f"Schelp_{k % 3}", ((250, 200, 190), (250, 240, 220), (200, 220, 250))[k % 3], rough=0.3, coat=0.7),
         scale=(1, 0.8, 0.45))
# schuimranden op de vloedlijn
foam = mat("Schuim", (250, 252, 255), rough=0.5, coat=0, sheen=0.4)
FOAM = [box(f"Schuim_{k}", (k * 6.0 - 30, -8.1 + rnd.uniform(-0.3, 0.3), -0.06), (5.2, 0.35, 0.08), foam, bev=0.04)
        for k in range(11)]
# boulevard (achter je, +y)
BZ = 1.3
box("Boulevard_muur", (0, 12.4, BZ / 2), (140, 0.8, BZ), stone, bev=0.04)
box("Boulevard", (0, 18.0, BZ - 0.1), (140, 12.0, 0.2), tiles, bev=0.02)
for k in range(-16, 17):
    cyl(f"Relingpaal_{k}", (k * 1.6, 12.2, BZ), 0.04, 0.95, rail_m)
box("Reling_boven", (0, 12.2, BZ + 0.95), (54, 0.08, 0.08), rail_m, bev=0.03)
box("Reling_midden", (0, 12.2, BZ + 0.5), (54, 0.05, 0.05), rail_m, bev=0.02)
bulb_m = glow("Lantaarnlicht", (255, 225, 160), 8.0)
post_m = mat("Lantaarnpaal", (60, 70, 90), rough=0.35, coat=0.5)
for k, x in enumerate((-12, -4, 4, 12, 20)):
    cyl(f"Lantaarn_{k}", (x, 12.9, BZ), 0.06, 3.0, post_m)
    ball(f"Lantaarnbol_{k}", (x, 12.9, BZ + 3.1), 0.22, bulb_m)
    point(f"Lantaarnlicht_{k}", (x, 12.9, BZ + 2.8), 120, (1.0, 0.85, 0.6), 0.2)
WARM = glow("Raam_warm7", (255, 215, 140), 3.0)
for k, (x, col, h) in enumerate(((-14, (240, 190, 170), 7), (-7, (180, 210, 240), 8.5), (0, (250, 230, 160), 6.5),
                                  (7, (200, 230, 190), 8), (14, (240, 200, 220), 7.5))):
    house(f"Huis7_{k}", x, 27.0, w=6.0, d=5.0, h=h, wall=col, yaw=0, lit=WARM)
# strandstoel + parasol (speelgoed)
umb = mat("Parasol", (240, 80, 80), rough=0.5, coat=0.4)
cyl("Parasolstok", (4.2, 1.5, 0), 0.03, 2.1, rail_m)
cyl("Parasol", (4.2, 1.5, 2.0), 1.1, 0.35, umb, r2=0.05)
box("Strandlaken", (3.4, 0.6, 0.01), (0.9, 1.7, 0.02), mat("Laken", (90, 180, 240), rough=0.9, coat=0, sheen=0.5), bev=0.005)

# ------------------------------------------------------------------------------------------------ de maan
P = V(0.0, -3.0, 0.0)
EYE = P + V(0, 0, 1.4)
D = 800.0
DIR = V(0, -math.cos(R(22)), math.sin(R(22)))
MC = EYE + DIR * D
moon_m = mat("Maan", (238, 236, 226), rough=0.9, coat=0, emit=1.4)
crater_m = mat("Maankrater", (175, 175, 172), rough=0.9, coat=0, emit=0.9)
moon = ball("Maan", MC, 1.0, moon_m)
nrm = -DIR
ux = V(1, 0, 0)
uz = nrm.cross(ux).normalized()
for k in range(16):
    a, bb = rnd.uniform(0, 6.283), rnd.uniform(0.0, 0.8)
    off = ux * (math.cos(a) * bb) + uz * (math.sin(a) * bb) + nrm * math.sqrt(max(0.0, 1 - bb * bb)) * 0.97
    c = ball(f"Maankrater_{k}", (0, 0, 0), rnd.uniform(0.06, 0.17), crater_m)
    c.parent = moon
    c.location = off
for o in [moon] + list(moon.children):
    o.visible_shadow = False


def moon_r(deg):
    return D * math.tan(R(deg))


MOON = ((0.0, 1.0), (0.4, 1.2), (e(1), 10.0), (r2, 10.0), (e(2), 11.5), (r6, 12.0), (Wd(6, 5), 18.0), (END, 26.0))
for t, deg in MOON:
    key(moon, "scale", FR(t), Vector((moon_r(deg),) * 3))

# sterren
star_m = glow("Ster", (255, 250, 235), 9.0)
for k in range(140):
    az, el = rnd.uniform(-1.4, 1.4), rnd.uniform(0.08, 1.2)
    d_ = V(math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))
    st = ball(f"Ster_{k}", EYE + d_ * 1500, rnd.uniform(0.9, 2.4), star_m)
    st.visible_shadow = False

# ------------------------------------------------------------------------------------------------ het water stijgt
for t, z in ((0.0, -0.12), (Wd(3, 4) - 0.3, -0.12), (e(3), 0.42), (r4, 0.55), (END, 0.95)):
    key(sea, "location", FR(t), V(0, -400, z))
for k, fo in enumerate(FOAM):
    x0 = fo.location.copy()
    for t, dy in ((0.0, 0.0), (1.4 + 0.1 * k, 0.6), (2.8 + 0.1 * k, 0.0), (Wd(3, 4) - 0.3, 0.0)):
        key(fo, "location", FR(t), x0 + V(0, dy, 0))
    key(fo, "location", FR(e(3)), x0 + V(0, 11.0, 0.5))
    show(fo, 0.0, r4)

# ------------------------------------------------------------------------------------------------ vulkanen aan de horizon
rock = mat("Vulkaansteen", (70, 58, 56), rough=0.8, coat=0)
lava = glow("Lava", (255, 110, 20), 12.0)
smoke = (60, 52, 52)
for k, (x, y, h, rr) in enumerate(((-160, -480, 110, 130), (60, -600, 150, 160), (240, -470, 95, 110), (-320, -560, 125, 140))):
    cone = cyl(f"Vulkaan_{k}", (x, y, -2), rr, h, rock, r2=rr * 0.12)
    top = cyl(f"Vulkaan_lava_{k}", (x, y, h - 3), rr * 0.13, 4, lava, r2=rr * 0.09)
    for o in (cone, top):
        show(o, r4)
    for j in range(3):
        st = box(f"Lavastroom_{k}_{j}", (x + (j - 1) * rr * 0.12, y + rr * 0.35, h * 0.45), (3.5, 1.2, h * 0.55), lava,
                 bev=0, rot=(28, (j - 1) * 14, 0))
        show(st, r4 + 0.3 + 0.2 * j)
    for q, t in enumerate(frange(r4 + 0.1 + 0.15 * k, END, 0.45)):
        puff(f"Rook_{k}_{q}", V(x, y, h + 6), t, dur=2.6, r=18 + 6 * (q % 3), rise=90, color=smoke, grow=2.4,
             drift=(rnd.uniform(-25, 25), 20, 0))
    lg = point(f"Lavagloed_{k}", (x, y + 30, h + 30), 0, (1.0, 0.38, 0.08), 15)
    key_energy(lg, [(0.0, 0), (r4 - 0.02, 0), (r4 + 0.3, 4.0e6), (END, 4.0e6)])

# ------------------------------------------------------------------------------------------------ jij
S.place(b, 0.0, P, 0)                               # yaw 0 = kijkt naar zee (-y)
S.beat(b, 0.0, face="verbaasd", amt=0.7, head=dict(up=14))
S.beat(b, e(1) - 0.3, face="geschrokken", amt=0.9, arms="schrik", head=dict(up=20), body=dict(lean=-4))
S.beat(b, r2, face="verbaasd", amt=1.0, arms="los", head=dict(up=24), body=dict(lean=-6))
S.beat(b, Wd(2, 3), face="verbaasd", amt=1.0, arms="hoofd", head=dict(up=26), body=dict(lean=-6))
S.beat(b, e(2), face="verbaasd", amt=1.0, arms="hoofd", head=dict(up=26), body=dict(lean=-6))
# regel 3: het water komt; achteruit lopen, blik naar zee
B1 = P + V(0.3, 4.5, 0)
S.beat(b, r3, face="nerveus", amt=0.8, arms="rust", head=dict(up=-8))
S.walk(b, Wd(3, 4), e(3) - 0.1, [P, B1], back=True, theta=18, face_dir=0)
S.beat(b, Wd(3, 4) + 0.05, face="bang", arms="schrik", head=dict(up=-12))
S.beat(b, e(3) - 0.1, face="bang", arms="schrik", head=dict(up=-14))
S.place(b, e(3), B1, 0)
# regel 4-6: op de boulevard
BV = V(1.5, 14.0, BZ)
S.teleport(b, r4, BV, 0)
S.beat(b, r4, face="bang", amt=0.9, arms="rust", head=dict(up=4, turn=-10))
S.beat(b, Wd(4, 3), face="geschrokken", arms="hoofd", head=dict(up=4, turn=-14))
S.beat(b, e(4), face="geschrokken", arms="hoofd", head=dict(up=4, turn=10))
S.beat(b, r5, face="nerveus", amt=0.8, arms="rust", head=dict(up=-4))
S.beat(b, Wd(5, 3), face="verbaasd", amt=0.9, arms="rust", head=dict(up=26), body=dict(lean=-6))
S.beat(b, r6 + 0.4, face="bang", arms="schrik", head=dict(up=30), body=dict(lean=-8))
S.beat(b, END, face="bang", arms="schrik", head=dict(up=32), body=dict(lean=-9))
S.blink(b, r5 + 0.3)

# ------------------------------------------------------------------------------------------------ camera's
MOONAIM = EYE + DIR * 40
S.shot(0.0, ((P.x + 1.6, P.y + 5.0, 0.5), tuple(MOONAIM + V(0, 0, -9)), 22),
       ((P.x + 1.5, P.y + 4.7, 0.55), tuple(MOONAIM + V(0, 0, -7)), 24), focus=P + V(0, 0, 1.2))
HB = P + V(0, 0, 1.45)
S.shot(r2, ((HB.x + 0.55, HB.y - 1.35, HB.z - 0.5), tuple(HB + V(0, 0, 0.05)), 26),
       ((HB.x + 0.45, HB.y - 1.15, HB.z - 0.45), tuple(HB + V(0, 0, 0.05)), 28), focus="aim")
S.shot(Wd(2, 6) - 0.1, ((P.x - 1.2, P.y + 5.8, 0.35), tuple(MOONAIM + V(0, 0, -5)), 18),
       ((P.x - 1.1, P.y + 5.5, 0.4), tuple(MOONAIM + V(0, 0, -4)), 19), focus=P + V(0, 0, 1.2))
S.shot(r3, ((P.x + 1.8, P.y - 3.2, 1.25), (P.x, P.y + 1.5, 0.75), 22),
       ((P.x + 1.6, P.y - 1.4, 1.25), (P.x + 0.2, P.y + 4.0, 0.8), 22), focus="bram")
S.shot(r4, ((BV.x + 1.0, BV.y + 3.0, BV.z + 1.3), (BV.x - 30, BV.y - 500, 70), 20),
       ((BV.x + 0.9, BV.y + 2.7, BV.z + 1.25), (BV.x - 30, BV.y - 500, 64), 22), focus="bram")
HV = BV + V(0, 0, 1.45)
S.shot(r5, ((HV.x + 0.5, HV.y - 1.35, HV.z - 0.3), tuple(HV + V(0, 0, 0.2)), 28),
       ((HV.x + 0.45, HV.y - 1.2, HV.z - 0.28), tuple(HV + V(0, 0, 0.22)), 30), focus="aim")
S.shot(r6, ((BV.x + 1.2, BV.y + 2.6, BV.z + 0.3), tuple(MOONAIM + V(0, 18, 6)), 17),
       ((BV.x + 1.1, BV.y + 2.3, BV.z + 0.3), tuple(MOONAIM + V(0, 18, 8)), 16), focus=BV + V(0, 0, 1.2))


def world():
    sky("nacht", 0.45)
    ml = sun(0.6, color=(0.75, 0.84, 1.0), d=tuple(DIR), angle=2.0, name="Maanlicht")
    key_energy(ml, [(0.0, 0.5), (e(1), 1.6), (r6, 1.8), (END, 2.8)])
    three_point("Strand", P, 0, scale=1.3, warm=0.9)
    three_point("Boulevard", BV, 0, scale=1.3, warm=0.9)


S.world_fn = world
S.done()
