"""F04b · Dag 2 · 10x · keuken bij dageraad. De klok tikt veel te langzaam, de broodrooster duurt twintig minuten.
Hij schenkt cornflakes in: ze dwarrelen als sneeuw. Kom na kom, dan de hele doos. Energie: honderd keer.

    blender -b -P anim/v2/scenes/f04b_ontbijt_traag.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f04b", "keuken", "dageraad")
rnd = random.Random(4)

TX, TY, TZ = 0.2, -0.6, 0.76
TOAST_AT = V(-1.55, 1.12, 0)                     # voor de broodrooster op het aanrecht
TABLE_AT = V(0.2, -1.32, 0)                      # aan de voorkant van de tafel
BOWL = V(0.2, -0.86, TZ)
CLOCK = V(1.0, 2.07, 2.02)                       # wandklok boven het mokkenrek

# kraanvogels en papier zijn voor later (F05a): hier nog niet
for o in bpy.data.objects:
    if o.name.startswith(("Kraanvogel", "Origamipapier", "Gevouwen_papiertje")):
        o.hide_render = True
for k in (1, 2):
    S.obj(f"Stoel_{k}").hide_render = True
S.obj("Waterkoker").location.x = -0.45                # uit het shot bij de broodrooster

# ---------------------------------------------------------------- rekwisieten
face = T.cyl("Wandklok", CLOCK, 0.2, 0.04, S.mat("wandklok", (0.97, 0.96, 0.92)), rot=(90, 0, 0), seg=40, ol=0.004)
T.torus("Wandklok_rand", CLOCK + V(0, -0.045, 0), 0.2, 0.018, S.mat("wandklok_rand", (0.15, 0.15, 0.18)), rot=(90, 0, 0), seg=40, seg2=8, ol=0)
for k in range(12):
    a = math.radians(k * 30)
    T.box(f"Wandklok_streep{k}", CLOCK + V(0.165 * math.sin(a), -0.046, 0.165 * math.cos(a) - 0.012), (0.012, 0.004, 0.024 if k % 3 else 0.04),
          P.m("zwart"), rot=(0, -k * 30, 0), bevel=0, ol=0)


def hand(name, length, width, color, angle):
    piv = bpy.data.objects.new(name + "_as", None)
    T._link(piv)
    piv.location = CLOCK + V(0, -0.05, 0)
    h = T.box(name, (0, 0, -0.02), (width, 0.004, length), color, bevel=0, ol=0)
    h.parent = piv
    piv.rotation_euler = (0, math.radians(angle), 0)
    return piv


hour = hand("Wandklok_uur", 0.1, 0.016, P.m("zwart"), 6 * 30 + 41 * 0.5)
minute = hand("Wandklok_min", 0.15, 0.011, P.m("zwart"), 41 * 6)
sec = hand("Wandklok_sec", 0.16, 0.005, S.mat("wandklok_sec", (0.85, 0.1, 0.1)), 12 * 6)

bowl = T.cyl("Kom_cornflakes", BOWL, 0.08, 0.07, S.mat("kom_blauw", (0.3, 0.55, 0.9)), r2=0.1, seg=20, ol=0)
fill = T.cyl("Kom_vulling", BOWL + V(0, 0, 0.045), 0.085, 0.02, S.mat("cornflakes", (0.95, 0.72, 0.25)), seg=20, ol=0)
cbox = T.box("Cornflakes_doos_v2", (0, 0, 0), (0.2, 0.07, 0.28), S.mat("cornflakesdoos", (0.95, 0.45, 0.1)), bevel=0.01, ol=0)
T.box("Cornflakes_label_v2", (0, -0.037, 0.12), (0.15, 0.004, 0.1), S.mat("cornflakeslabel", (0.98, 0.85, 0.2)), bevel=0, ol=0).parent = cbox
cbox.location = V(-0.25, -0.85, TZ)
spoon = T.cyl("Lepel", (0, 0, 0), 0.006, 0.15, P.m("metaal"), seg=6, ol=0)
spoon.location = BOWL + V(0.13, 0, 0.01)
spoon.rotation_euler = (0, math.radians(90), 0)
empties = [T.cyl(f"Kom_leeg_{k}", BOWL + V(0.32, 0.12, 0.072 * k), 0.08, 0.07, S.mat("kom_blauw", (0.3, 0.55, 0.9)), r2=0.1, seg=20, ol=0)
           for k in range(3)]

held = S.actor("hoofdpersonage", TOAST_AT, 180)

# ---------------------------------------------------------------- tijdlijn
S.hud2(2, "10x", clock=clock(6 * 3600 + 41 * 60 + 12, 0.1, dec=1, day="TUE"), t0=0.4)
S.ambience("sfx_dageraad_straat", 0.0, 40, vol=0.06)
l1 = S.say("F04-04", gap=0.8)
TICK1, TICK2 = l1[0] + 2.9, l1[0] + 5.3
CUT = l1[1] + 0.3                                # van de broodrooster naar de tafel
l2 = S.say("F04-05", gap=0.6)
POUR = l2[0] + 0.4
MONT = l2[0] + 4.6                               # 'moving ten times faster...': de kommen staan al op elkaar
END = l2[1] + 1.0
S.music("ochtend", 0.0, END + 1, vol=0.18, fade_in=0.8, fade_out=1.0, start=8.0)
for t in (TICK1, TICK2):
    S.sfx("sfx_klok_tik", t, 0.7)
S.sfx("sfx_cornflakes", POUR + 0.2, 0.35)
S.gauge2("ENERGY: 100x", l2[1] - 2.2, END, color=GOLD)

# secondewijzer: één tik per keer (de wereld loopt tien keer te langzaam)
key(sec, 0.0, rot=(0, 12 * 6, 0))
key(sec, TICK1, rot=(0, 12 * 6, 0))
key(sec, TICK1 + 0.06, rot=(0, 13 * 6, 0))
key(sec, TICK2, rot=(0, 13 * 6, 0))
key(sec, TICK2 + 0.06, rot=(0, 14 * 6, 0))
for fc in A._fcurves(sec):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# ---------------------------------------------------------------- bij de broodrooster
TOASTER = S.obj("Broodrooster").location + V(0, 0, 0.12)
S.beat(held, 0.0, "staan", face="twijfel", face_amt=0.6, at=TOASTER)
S.beat(held, l1[0] + 1.2, "staan", face="verbaasd", face_amt=0.6, at=CLOCK + V(0, -0.1, 0))
S.beat(held, l1[0] + 5.8, "armen_over", face="twijfel", face_amt=0.9, at=TOASTER + V(0, 0, 0.3))
for k, t in enumerate(frange(l1[0] + 6.4, CUT - 0.2, 0.22)):     # ongeduldig met zijn vingers trommelen
    S.reach(held, t, "R", TOASTER + V(0.12 + 0.02 * (k % 2), -0.18, -0.08 + 0.025 * (k % 2)))
S.reach(held, CUT, "R", None, 0.0)

# ---------------------------------------------------------------- aan tafel: cornflakes, kom na kom
S.teleport(held, CUT, TABLE_AT, 180)
S.beat(held, CUT, "staan", face="blij", face_amt=0.6, at=BOWL)
S.reach(held, CUT, "L", None, 0.0)
grab(S, cbox, held, POUR - 0.3, "hand.R", mode="loc", offset=(0.0, 0.0, 0.05), release=MONT - 0.2)
S.reach(held, POUR - 0.5, "R", Vector(cbox.location) + V(0, 0, 0.16))
S.reach(held, POUR, "R", BOWL + V(-0.1, 0.02, 0.5))
key(cbox, POUR - 0.3, rot=(0, 0, 0))
key(cbox, POUR + 0.2, rot=(0, 115, 0))
S.reach(held, MONT - 0.4, "R", BOWL + V(-0.1, 0.02, 0.5))
key(cbox, MONT - 0.4, rot=(0, 115, 0))
key(cbox, MONT - 0.2, loc=BOWL + V(0.2, 0.16, 0), rot=(90, 0, 70))   # leeg, omgevallen
show(fill, POUR + 1.6)
# de vlokken: dwarrelen als sneeuw (in zijn tijd vallen ze tien keer te langzaam)
MOUTH = BOWL + V(-0.02, 0.02, 0.42)
for k in range(46):
    fl = T.box(f"Vlok_{k}", (0, 0, 0), (0.024, 0.02, 0.004), S.mat("cornflakes", (0.95, 0.72, 0.25)), bevel=0, ol=0)
    t0 = POUR + 0.25 + k * 0.045
    t1 = t0 + rnd.uniform(1.6, 2.6)
    if t1 > MONT - 0.3:
        t1 = MONT - 0.3
    show(fl, t0, t1)
    key(fl, t0, loc=MOUTH + V(rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), 0), rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), 0))
    end = BOWL + V(rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06), 0.06)
    key(fl, t1, loc=end, rot=(rnd.uniform(0, 360), rnd.uniform(0, 360), rnd.uniform(0, 360)))
    for fc in A._fcurves(fl):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
S.beat(held, POUR + 0.6, "staan", face="verbaasd", face_amt=0.8, at=MOUTH + V(0, 0, -0.12))
# montage: drie lege kommen op elkaar, hij lepelt door
for e in empties:
    show(e, MONT)
grab(S, spoon, held, MONT, "hand.L", loc=(0, 0.05, 0.0), rot=(90, 0, 0))
S.beat(held, MONT, "staan", face="blij", face_amt=0.8, at=BOWL)
MOUTH_H = S.head(held, MONT) + V(0, -0.24, -0.18)
t = MONT + 0.1
while t < END - 0.3:                             # snel eten
    S.reach(held, t, "L", BOWL + V(0.0, 0.0, 0.08))
    S.reach(held, t + 0.22, "L", MOUTH_H)
    A.key_prop(held.rig, "mond_open", 0.5, F(t + 0.18))
    A.key_prop(held.rig, "mond_open", 0.05, F(t + 0.32))
    t += 0.45
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.9, -1.9, 1.65), (-0.8, 0.9, 1.0), 22), ((1.75, -1.75, 1.6), (-0.9, 1.0, 1.0), 23))
S.cam(l1[0] + 2.3, (CLOCK + V(-0.15, -0.9, -0.12), CLOCK, 38), (CLOCK + V(-0.12, -0.75, -0.1), CLOCK, 42), dof=1.2)
S.cam(l1[0] + 5.6, ((-0.85, 1.95, 1.18), (-1.5, 1.25, 1.2), 22), ((-0.9, 1.95, 1.18), (-1.5, 1.25, 1.2), 24), dof=1.4)
S.cam(CUT, (BOWL + V(0.3, 0.62, 0.08), BOWL + V(0.0, 0.0, 0.24), 28), (BOWL + V(0.27, 0.56, 0.08), BOWL + V(0.0, 0.0, 0.24), 30), dof=1.2)
S.cam(MONT, S.shot(held, MONT + 0.5, "med", az=-30, lens=30), S.shot(held, END, "mcu", az=-25, lens=34))
S.wall(MONT, END + 1)

S.finish(length=END)
