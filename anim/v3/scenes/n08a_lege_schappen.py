"""N08a · Dag 2: lege schappen (script scène 8a). De teller klikt zwaar van DAY 1 naar DAY 2 terwijl de camera
langs lege schappen schiet. Eén blikje rolt over de vloer.
VO: "This part is real too: a supermarket only holds enough food for about three days."

    blender -b -P anim/v3/scenes/n08a_lege_schappen.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n08a", "supermarkt", "nr_leeg", exposure=0.0)
sh = S.cuts([2.4, 3.3])
END = sh[-1][1]
t_b = sh[1][0]
rnd = random.Random(8)

# losse blikjes en dozen alleen midden in de gangpaden (nooit in een schap)
AISLES = (-6.75, -2.25, 2.25, 6.75)
for i, o in enumerate([o for o in bpy.data.objects if o.name.startswith("Los_blik_")]):
    o.location.x = AISLES[i % 4] + rnd.uniform(-0.5, 0.5)
    o.location.y = rnd.uniform(-4.0, 10.0)
for i, o in enumerate([o for o in bpy.data.objects if o.name.startswith("Lege_doos_")]):
    o.location.x = AISLES[(i + 1) % 4] + rnd.uniform(-0.4, 0.4)
    o.location.y = rnd.uniform(-4.0, 10.0)
    o.location.z = 0.0

# het rollende blikje in gang -2.25: rolt dwars over de vloer en tikt tegen het schap
blik = T.cyl("Blikje_rolt", (0, 0, 0), 0.045, 0.12, S.mat("blik_rood", (0.85, 0.12, 0.10)), seg=16, ol=0.004)
blik.rotation_mode = "XYZ"
P0, P1 = V(-1.4, 3.0, 0.045), V(-3.45, 4.3, 0.045)
T0, T1 = t_b + 0.4, t_b + 2.9
ang = math.atan2(P1.y - P0.y, P1.x - P0.x)
dist = (P1 - P0).length
for k in range(11):
    u = k / 10
    e = 1 - (1 - u) ** 2                                  # rolt uit
    blik.location = P0.lerp(P1, e) + V(0, 0, 0)
    blik.rotation_euler = (math.radians(90), dist * e / 0.045, ang + math.radians(90))
    blik.keyframe_insert("location", frame=F(T0 + (T1 - T0) * u))
    blik.keyframe_insert("rotation_euler", frame=F(T0 + (T1 - T0) * u))
blik.location, blik.rotation_euler = P0, (math.radians(90), 0, ang + math.radians(90))
blik.keyframe_insert("location", frame=F(0.0))
blik.keyframe_insert("rotation_euler", frame=F(0.0))

# ---------------------------------------------------------------- camera's
# 8a-1 snelle track langs het lege schap (gang x = 2.25), schuin op het schap, laag
S.cam(0.0, ((2.9, -3.5, 1.15), (1.0, 2.5, 1.0), 22), ((2.9, 6.5, 1.15), (1.0, 11.0, 1.0), 22), ease=False, handheld=0.2)
# 8a-2 laag in gang -2.25, het blikje rolt het beeld in; trage push-in, SORRY - EMPTY op de achtergrond
S.cam(t_b, ((-2.0, 0.5, 0.35), (-2.5, 6.0, 0.5), 26), ((-2.05, 1.0, 0.33), (-2.5, 6.0, 0.45), 28), handheld=0.15)

# ---------------------------------------------------------------- HUD: DAY 1 -> DAY 2 met een zware klik
S.counter("DAY 1", 0, t0=0.0, t1=0.45)
S.counter("DAY 2", 0, t0=0.45, big=True)
S.sfx("sfx_dreun", 0.45, 0.5)
S.sfx("sfx_whoosh", 0.0, 0.35)
S.sfx("sfx_blik_plop", T0 - 0.05, 0.35)
S.ambience("sfx_supermarkt_sfeer", 0.0, END, vol=0.05)
S.say("N08-01", at=0.3)
S.finish(length=END, tail=0.0)
